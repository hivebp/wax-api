import json
import os
from functools import wraps

import redis
from flask import Flask, request, Response, jsonify
from oto.adaptors.flask import flaskify
from oto import response as oto_response
from flask_cors import CORS

from app_runner import run_app
from config import PostgresConfig

import logging

import time

from flask_compress import Compress
from db import db
from cache import cache

from ddtrace import patch_all

import queue
import _thread

if not Flask.debug:
    patch_all()

compress = Compress()

app = Flask(__name__, static_folder='build', static_url_path='/')
app.config.from_object(PostgresConfig)

print(app.config)

#app.config["CACHE_TYPE"] = "simple"
app.config['CACHE_TYPE'] = 'redis'
app.config['CACHE_REDIS_HOST'] = '127.0.0.1'
app.config['CACHE_REDIS_PORT'] = 6379

cache.init_app(app)

db.init_app(app)

print(app.extensions["cache"])  # should not be empty
print(list(app.extensions["cache"].keys()))

import stats_v3
import legacy
import logic
import verify
import pfps

env = os.environ.get('FLASK_ENV')

Compress(app)

CORS(app, resources={
    r"/api/*": {
        "origins": [
            "*",
        ]
    },
    r"/legacy/*": {
        "origins": [
            "*",
        ]
    },
    r"/verify-api/*": {
        "origins": [
            "*",
        ]
    },
    r"/pfp-api/*": {
        "origins": [
            "*",
        ]
    },
    r"/v3/*": {
        "origins": [
            "*",
        ]
    }
})


class MessageAnnouncer:
    def __init__(self):
        self.listeners = {}

    status = {}

    def listen(self, key):
        if len(self.listeners.keys()) >= 100:
            return

        q = queue.Queue(maxsize=10)
        if key in self.listeners.keys():
            self.listeners[key].append(q)
        else:
            self.listeners[key] = [q]
        return q

    def announce(self, msg, key):
        for i in reversed(range(len(self.listeners[key]))):
            try:
                self.listeners[key][i].put_nowait(msg)
            except queue.Full:
                del self.listeners[key][i]

    def get_status(self, key):
        if len(self.status.keys()) >= 100 and not key in self.status.keys():
            return "full"
        if key in self.status.keys():
            return self.status[key]
        else:
            return "stopped"

    def format_sse(self, data: str, event=None) -> str:
        msg = f'data: {data}\n\n'
        if event is not None:
            msg = f'event: {event}\n{msg}'
        return msg

    def run_feed(self, key, collection, schema, template_id):
        while key in self.status.keys() and self.status[key] == 'started':
            time.sleep(2)
            if key in self.listeners.keys() and len(self.listeners[key]) > 0:
                self.announce(self.format_sse(logic.newest_listings(collection, schema, template_id)), key)
            else:
                del self.status[key]
                del self.listeners[key]

    def start(self, key, collection, schema, template_id):
        if key not in self.status.keys():
            self.status[key] = 'started'
        elif key in self.status.keys() and self.status[key] == 'started':
            return False
        elif key in self.status.keys() and self.status[key] == 'stopped':
            self.status[key] = 'started'

        _thread.start_new_thread(self.run_feed, (key, collection, schema, template_id))

    def stop(self, template_id):
        if template_id in self.status.keys():
            self.status[template_id] = 'stopped'


@app.route('/api/initial-listing-feed')
def initial_listing_feed():
    try:
        collection = request.args.get('collection', None)
        schema = request.args.get('schema', None)
        template_id = request.args.get('template_id', None)

        return flaskify(oto_response.Response(logic.newest_listings(collection, schema, template_id)))
    except Exception as err:
        logging.error(err)
        return flaskify(oto_response.Response('An unexpected Error occured', errors=err, status=500))


announcer = MessageAnnouncer()

redis_client = redis.Redis(host='127.0.0.1', port=6379, decode_responses=True)

@app.route('/test/cached-content')
def cached_content():
    try:
        cached_keys = redis_client.keys('*')
        return flaskify(oto_response.Response(cached_keys))
    except Exception as err:
        logging.error(err)
        return flaskify(oto_response.Response('Error retrieving Redis cache', errors=err, status=500))


@app.route('/api/listing-feed')
def stream_general():
    collection = request.args.get('collection', None)
    schema = request.args.get('schema', None)
    template_id = request.args.get('template_id', None)

    key = 'general'

    if collection:
        key = collection

    if schema:
        key += '-' + schema

    if template_id:
        key = template_id

    status = announcer.get_status(key)
    if status == "stopped":
        announcer.start(key, collection, schema, template_id)

    if status == "full":
        return flaskify(oto_response.Response("Streams Full", status=401))

    def event_stream():
        messages = announcer.listen(key)  # returns a queue.Queue
        while True and messages:
            msg = messages.get()
            yield msg

    return Response(event_stream(), mimetype="text/event-stream")


def _format_collection(collection):
    if not collection:
        return collection

    if '*' in collection:
        return None

    if ',' in collection:
        return tuple(map(lambda a: a, list(collection.split(','))))
    else:
        return collection


def catch_and_respond():
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                return f(*args, **kwargs)
            except Exception as err:
                logging.exception("Unhandled error in %s", f.__name__)
                return jsonify(error=str(err)), 500
        return decorated_function
    return decorator


@app.route('/api/health')
@catch_and_respond()
def get_health():
    return flaskify(oto_response.Response(logic.get_health()))


@app.route('/api/schemas/<collection>')
@catch_and_respond()
def schemas(collection):
    term = request.args.get('term')
    schema = request.args.get('schema')
    limit = request.args.get('limit', 40)
    offset = request.args.get('offset', 0)
    order_by = request.args.get('order_by') if request.args.get('order_by') else 'date_desc'
    exact_search = request.args.get('exact_search') == 'true'

    if not collection:
        raise Exception('Collection Required')
    else:
        collection = _format_collection(collection)

    try:
        limit = int(limit)
        offset = int(offset)
    except Exception as err:
        limit = 40
        offset = 0

    search_res = logic.schemas(
        term, collection, schema, limit, order_by, exact_search, offset
    )

    return flaskify(oto_response.Response(search_res))


@app.route('/api/templates')
@catch_and_respond()
def templates():
    term = request.args.get('term')
    collection = request.args.get('collection')
    schema = request.args.get('schema')
    tags = request.args.get('tags')
    limit = int(request.args.get('limit', 40))
    offset = int(request.args.get('offset', 0))
    recently_sold = request.args.get('recent')
    verified = request.args.get('verified', 'all')
    favorites = request.args.get('favorites', 'false') == 'true'
    user = request.args.get('user', '')
    order_by = request.args.get('order_by') if request.args.get('order_by') else 'date_desc'
    exact_search = request.args.get('exact_search') == 'true'
    search_type = request.args.get('search_type') if request.args.get('search_type') else ''
    attributes = request.args.get('attributes', None)

    template_ids = request.args.get('template_ids')
    template_ids = template_ids.split(',') if template_ids and ',' in template_ids else ([template_ids] if template_ids else [])

    if collection:
        collection = _format_collection(collection)

    if limit:
        try:
            limit = int(limit)
        except Exception as err:
            limit = 100
    else:
        limit = 100

    search_res = logic.templates(
        term, collection, schema, tags, limit, order_by,
        exact_search, search_type, offset, verified,
        user, favorites, recently_sold, attributes,
        template_ids
    )

    return flaskify(oto_response.Response(search_res))


@app.route('/api/asset/<asset_id>')
@catch_and_respond()
def get_asset(asset_id):
    search_res = logic.assets(
        term=asset_id, verified='all', burned='all'
    )

    if search_res:
        return flaskify(oto_response.Response(search_res[0]))

    return flaskify(oto_response.Response({}))


@app.route('/api/assets')
@catch_and_respond()
def assets():
    term = request.args.get('term')
    owner = request.args.get('owner')
    collection = request.args.get('collection')
    schema = request.args.get('schema')
    tags = request.args.get('tags')
    limit = int(request.args.get('limit', 40))
    offset = int(request.args.get('offset', 0))
    min_mint = int(request.args.get('min_mint', 0))
    max_mint = int(request.args.get('max_mint', 0))
    min_average = int(request.args.get('min_average', 0))
    max_average = int(request.args.get('max_average', 0))
    recently_sold = request.args.get('recent')
    verified = request.args.get('verified', 'verified')
    favorites = request.args.get('favorites', 'false') == 'true'
    backed = request.args.get('backed', 'false') == 'true'
    contract = request.args.get('contract')
    user = request.args.get('user', '')
    order_by = request.args.get('order_by') if request.args.get('order_by') else 'date_desc'
    exact_search = request.args.get('exact_search') == 'true'
    search_type = request.args.get('search_type') if request.args.get('search_type') else ''
    attributes = request.args.get('attributes', None)
    only = request.args.get('only', None)
    rwax_symbol = request.args.get('rwax_symbol', None)
    rwax_contract = request.args.get('rwax_contract', None)
    exclude_listings = request.args.get('exclude_listings', 'false') == 'true'

    asset_ids = request.args.get('asset_ids')
    asset_ids = asset_ids.split(',') if asset_ids and ',' in asset_ids else ([asset_ids] if asset_ids else [])

    if collection:
        collection = _format_collection(collection)

    if min_mint:
        try:
            min_mint = int(min_mint)
        except Exception as err:
            min_mint = None
    if max_mint:
        try:
            max_mint = int(max_mint)
        except Exception as err:
            max_mint = None
    if limit:
        try:
            limit = int(limit)
        except Exception as err:
            limit = 100
    else:
        limit = 100

    search_res = logic.assets(
        term, owner, collection, schema, tags, limit, order_by,
        exact_search, search_type, min_average, max_average, min_mint, max_mint, contract, offset, verified,
        user, favorites, backed, recently_sold, attributes, only, rwax_symbol, rwax_contract, 'not_burned',
        asset_ids, not exclude_listings
    )

    return flaskify(oto_response.Response(search_res))


@app.route('/api/craft-search')
@catch_and_respond()
def craft_search():
    try:
        owner = request.args.get('owner')
        collection = request.args.get('collection')
        schema = request.args.get('schema')
        term = request.args.get('term')
        attribute = request.args.get('attribute', None)

        if collection:
            collection = _format_collection(collection)

        search_type = 'inventory'
        verified = 'all'
        limit = request.args.get('limit')

        search_res = logic.assets(
            term=term, owner=owner, collection=collection, schema=schema, limit=limit, order_by='asset_id_desc',
            verified=verified, search_type=search_type, attributes=attribute
        )

        return flaskify(oto_response.Response(search_res))
    except Exception as err:
        logging.error(err)
        return flaskify(oto_response.Response(
            {'error': 'An unexpected Error occured: {}'.format(err)}, errors=err, status=500))


@app.route('/api/filter-attributes/<collection>')
@catch_and_respond()
def filter_attributes(collection):
    schema = request.args.get('schema')
    templates = request.args.get('templates')
    only = request.args.get('only')

    collection = _format_collection(collection)

    search_res = logic.filter_attributes(
        collection, schema, templates, only
    )

    return flaskify(oto_response.Response(search_res))


@app.route('/api/filter-attributes-simple/<collection>')
@catch_and_respond()
def filter_attributes_simple(collection):
    schema = request.args.get('schema')
    templates = request.args.get('templates')
    only = request.args.get('only')

    collection = _format_collection(collection)

    search_res = logic.filter_attributes_simple(
        collection, schema, templates, only
    )

    return flaskify(oto_response.Response(search_res))


@app.route('/api/collection-filters/<collection>')
@catch_and_respond()
def collection_filters(collection):
    collection = _format_collection(collection)

    search_res = logic.collection_filters(collection)

    return flaskify(oto_response.Response(search_res))


@app.route('/api/collection-fee/<collection>')
@catch_and_respond()
def collection_fee(collection):
    collection = _format_collection(collection)
    try:
        return flaskify(oto_response.Response(logic.get_collection_fee(collection)))
    except Exception as err:
        logging.error(err)
        return flaskify(oto_response.Response('An unexpected Error occured', errors=err, status=500))


@app.route('/api/buyoffers')
@catch_and_respond()
def buyoffers():
    term = request.args.get('term')
    buyer = request.args.get('buyer')
    collection = request.args.get('collection')
    schema = request.args.get('schema')
    limit = int(request.args.get('limit', 40))
    offset = int(request.args.get('offset', 0))
    verified = request.args.get('verified', 'verified')
    contract = request.args.get('contract')
    user = request.args.get('user', '')
    order_by = request.args.get('order_by') if request.args.get('order_by') else 'date_desc'
    exact_search = request.args.get('exact_search') == 'true'
    search_type = request.args.get('search_type') if request.args.get('search_type') else ''
    attributes = request.args.get('attributes', None)
    buyoffer_id = request.args.get('buyoffer_id', None)

    if collection:
        collection = _format_collection(collection)

    if limit:
        try:
            limit = int(limit)
        except Exception as err:
            limit = 100
    else:
        limit = 100

    search_res = logic.buyoffers(
        buyoffer_id, term, buyer, collection, schema, limit, offset, order_by,
        exact_search, search_type, contract, verified,
        user, attributes
    )

    return flaskify(oto_response.Response(search_res))


@app.route('/api/auctions')
@catch_and_respond()
def auctions():
    term = request.args.get('term')
    seller = request.args.get('seller')
    bidder = request.args.get('bidder')
    collection = request.args.get('collection')
    schema = request.args.get('schema')
    limit = int(request.args.get('limit', 40))
    offset = int(request.args.get('offset', 0))
    min_mint = int(request.args.get('min_mint', 0))
    max_mint = int(request.args.get('max_mint', 0))
    min_price = int(request.args.get('min_price', 0))
    max_price = int(request.args.get('max_price', 0))
    recently_sold = request.args.get('recent')
    verified = request.args.get('verified', 'verified')
    favorites = request.args.get('favorites', 'false') == 'true'
    contract = request.args.get('contract')
    user = request.args.get('user', '')
    order_by = request.args.get('order_by') if request.args.get('order_by') else 'date_desc'
    exact_search = request.args.get('exact_search') == 'true'
    search_type = request.args.get('search_type') if request.args.get('search_type') else ''
    attributes = request.args.get('attributes', None)
    only = request.args.get('only', None)
    rwax_symbol = request.args.get('rwax_symbol', None)
    rwax_contract = request.args.get('rwax_contract', None)
    auction_id = request.args.get('auction_id', None)
    market = request.args.get('market', None)

    if collection:
        collection = _format_collection(collection)

    if min_price:
        try:
            min_price = float(min_price)
        except Exception as err:
            min_price = None
    if max_price:
        try:
            max_price = float(max_price)
        except Exception as err:
            max_price = None
    if min_mint:
        try:
            min_mint = int(min_mint)
        except Exception as err:
            min_mint = None
    if max_mint:
        try:
            max_mint = int(max_mint)
        except Exception as err:
            max_mint = None
    if limit:
        try:
            limit = int(limit)
        except Exception as err:
            limit = 100
    else:
        limit = 100

    search_res = logic.auctions(
        auction_id, market, term, seller, bidder, collection, schema, limit, order_by,
        exact_search, search_type, min_price, max_price, min_mint, max_mint, contract, offset, verified,
        user, favorites, recently_sold, attributes, only, rwax_symbol, rwax_contract
    )

    return flaskify(oto_response.Response(search_res))


@app.route('/api/auction-bids')
@catch_and_respond()
def get_bids():
    auction_id = request.args.get('auction_id', '')
    market = request.args.get('market', '')
    return flaskify(oto_response.Response(logic.get_bids(auction_id, market)))


@app.route('/api/sales')
@catch_and_respond()
def sales():
    term = request.args.get('term')
    seller = request.args.get('seller')
    buyer = request.args.get('buyer')
    market = request.args.get('market')
    collection = request.args.get('collection')
    schema = request.args.get('schema')
    limit = int(request.args.get('limit', 40))
    offset = int(request.args.get('offset', 0))
    min_mint = int(request.args.get('min_mint', 0))
    max_mint = int(request.args.get('max_mint', 0))
    min_price = int(request.args.get('min_price', 0))
    max_price = int(request.args.get('max_price', 0))
    recently_sold = request.args.get('recent')
    verified = request.args.get('verified', 'verified')
    contract = request.args.get('contract')
    user = request.args.get('user', '')
    order_by = request.args.get('order_by') if request.args.get('order_by') else 'date_desc'
    exact_search = request.args.get('exact_search') == 'true'
    search_type = request.args.get('search_type') if request.args.get('search_type') else ''
    attributes = request.args.get('attributes', None)
    only = request.args.get('only', None)
    rwax_symbol = request.args.get('rwax_symbol', None)
    rwax_contract = request.args.get('rwax_contract', None)

    if collection:
        collection = _format_collection(collection)

    if min_price:
        try:
            min_price = float(min_price)
        except Exception as err:
            min_price = None
    if max_price:
        try:
            max_price = float(max_price)
        except Exception as err:
            max_price = None
    if min_mint:
        try:
            min_mint = int(min_mint)
        except Exception as err:
            min_mint = None
    if max_mint:
        try:
            max_mint = int(max_mint)
        except Exception as err:
            max_mint = None
    if limit:
        try:
            limit = int(limit)
        except Exception as err:
            limit = 100
    else:
        limit = 100

    search_res = logic.sales(
        term, seller, buyer, market, collection, schema, limit, offset, order_by,
        exact_search, search_type, min_price, max_price, min_mint, max_mint, contract, verified,
        user, recently_sold, attributes, only, rwax_symbol, rwax_contract
    )

    return flaskify(oto_response.Response(search_res))


@app.route('/api/sale/<market>/<listing_id>')
@catch_and_respond()
def sale(market, listing_id):
    result = logic.sales(
        market=market, listing_id=listing_id, verified='all'
    )

    if result:
        return flaskify(oto_response.Response(result[0]))

    return flaskify(oto_response.Response({}))


@app.route('/api/listings')
@catch_and_respond()
def listings():
    term = request.args.get('term')
    owner = request.args.get('seller')
    market = request.args.get('market')
    collection = request.args.get('collection')
    schema = request.args.get('schema')
    limit = int(request.args.get('limit', 40))
    offset = int(request.args.get('offset', 0))
    min_mint = int(request.args.get('min_mint', 0))
    max_mint = int(request.args.get('max_mint', 0))
    min_price = int(request.args.get('min_price', 0))
    max_price = int(request.args.get('max_price', 0))
    recently_sold = request.args.get('recent')
    verified = request.args.get('verified', 'verified')
    listing_id = request.args.get('listing_id', None)
    contract = request.args.get('contract')
    user = request.args.get('user', '')
    order_by = request.args.get('order_by') if request.args.get('order_by') else 'date_desc'
    exact_search = request.args.get('exact_search') == 'true'
    search_type = request.args.get('search_type') if request.args.get('search_type') else ''
    attributes = request.args.get('attributes', None)
    only = request.args.get('only', None)
    rwax_symbol = request.args.get('rwax_symbol', None)
    rwax_contract = request.args.get('rwax_contract', None)

    if collection:
        collection = _format_collection(collection)

    if min_price:
        try:
            min_price = float(min_price)
        except Exception as err:
            min_price = None
    if max_price:
        try:
            max_price = float(max_price)
        except Exception as err:
            max_price = None
    if min_mint:
        try:
            min_mint = int(min_mint)
        except Exception as err:
            min_mint = None
    if max_mint:
        try:
            max_mint = int(max_mint)
        except Exception as err:
            max_mint = None
    if limit:
        try:
            limit = int(limit)
        except Exception as err:
            limit = 100
    else:
        limit = 100

    search_res = logic.listings(
        term, owner, market, collection, schema, limit, offset, order_by,
        exact_search, search_type, min_price, max_price, min_mint, max_mint, contract, verified,
        user, listing_id, recently_sold, attributes, only, rwax_symbol, rwax_contract
    )

    return flaskify(oto_response.Response(search_res))


@app.route('/api/listing/<market>/<listing_id>')
@catch_and_respond()
def listing(market, listing_id):
    result = logic.listings(
        market=market, listing_id=listing_id, verified='all'
    )

    if result:
        return flaskify(oto_response.Response(result[0]))
    elif market == 'atomicmarket':
        result = logic.listings(
            market=market, listing_id=listing_id, verified='all', listings_table='removed_atomic_listings'
        )
        if result:
            return flaskify(oto_response.Response(result[0]))

    return flaskify(oto_response.Response({}))


@app.route('/api/collection/<collection>')
@catch_and_respond()
def get_collection(collection):
    result = logic.get_collections_overview(
        collection, None, None, 'all', None, None, None, None,
        None, None, None
    )

    if result:
        return flaskify(oto_response.Response(result[0]))

    return flaskify(oto_response.Response({}))


@app.route('/api/collections')
@catch_and_respond()
def get_collections():
    collection = request.args.get('collection', '*')
    collection = _format_collection(collection)
    type = request.args.get('type')
    tag_id = request.args.get('tag_id')
    limit = request.args.get('limit', 100)
    offset = request.args.get('offset', 0)
    verified = request.args.get('verified', 'verified')
    trending = request.args.get('trending', 'false') == 'true'
    authorized_account = request.args.get('authorized_account')
    market = request.args.get('market')
    owner = request.args.get('owner')
    only = request.args.get('only')

    return flaskify(oto_response.Response(logic.get_collections_overview(
        collection, type, tag_id, verified, trending, authorized_account, market, owner, only, limit, offset)))


@app.route('/api/crafts')
@catch_and_respond()
def get_crafts():
    craft_id = request.args.get('craft_id')
    collection = request.args.get('collection')
    offset = request.args.get('offset', 0)
    limit = request.args.get('limit', 40)
    order_by = request.args.get('order_by') if request.args.get('order_by') else 'craft_id_desc'
    verified = request.args.get('verified', 'verified')

    if collection:
        collection = _format_collection(collection)

    if limit:
        try:
            limit = int(limit)
        except Exception as err:
            limit = 40
    else:
        limit = 40

    if offset:
        try:
            offset = int(offset)
        except Exception as err:
            offset = 0
    else:
        offset = 0

    search_res = logic.get_crafts(
        craft_id, collection, limit, order_by, offset, verified
    )

    return flaskify(oto_response.Response(search_res))


@app.route('/api/drop-claims')
@catch_and_respond()
def get_drop_claims():
    drop_id = request.args.get('drop_id')
    contract = request.args.get('contract')
    referrals = request.args.get('referrals_only') == 'true'
    collection = request.args.get('collection')
    offset = request.args.get('offset', 0)
    order_by = request.args.get('order_by') if request.args.get('order_by') else 'date_desc'
    verified = request.args.get('verified')
    referrer = request.args.get('referrer')
    if offset and (isinstance(offset, int) or (isinstance(offset, str) and offset.isnumeric())):
        offset = int(offset)
    else:
        offset = 0
    limit = request.args.get('limit', 40)

    if collection:
        collection = _format_collection(collection)

    if limit:
        try:
            limit = int(limit)
        except Exception as err:
            limit = 40
    else:
        limit = 40

    search_res = logic.get_drop_claims(
        drop_id, collection, contract, referrals, limit, offset, order_by, verified, referrer
    )

    return flaskify(oto_response.Response(search_res))


@app.route('/api/drops')
@catch_and_respond()
def get_drops():
    drop_id = request.args.get('drop_id')
    term = request.args.get('term')
    collection = request.args.get('collection')
    market = request.args.get('market')
    offset = request.args.get('offset', 0)
    if offset and (isinstance(offset, int) or (isinstance(offset, str) and offset.isnumeric())):
        offset = int(offset)
    else:
        offset = 0
    limit = request.args.get('limit', 40)
    order_by = request.args.get('order_by') if request.args.get('order_by') else 'drop_id_desc'
    verified = request.args.get('verified')
    token = request.args.get('token')
    home = request.args.get('home') == 'home'
    upcoming = request.args.get('upcoming') == 'true'
    pfpsonly = request.args.get('pfpsonly') == 'true'
    user_name = request.args.get('user', None)
    currency = request.args.get('currency', None)

    if collection:
        collection = _format_collection(collection)

    if limit:
        try:
            limit = int(limit)
        except Exception as err:
            limit = 40
    else:
        limit = 40

    search_res = logic.get_drops(
        drop_id, collection, term, limit, order_by, offset, verified, market, token, upcoming,
        pfpsonly, user_name, currency, home
    )

    return flaskify(oto_response.Response(search_res))


@app.route('/api/collection-schemas/<collection>')
@catch_and_respond()
def get_collection_schemas(collection):
    only = request.args.get('only', None)
    return flaskify(oto_response.Response(logic.get_collection_schemas(collection, only)))


@app.route('/api/tags/<collection>')
@catch_and_respond()
def get_tags(collection):
    return flaskify(oto_response.Response(logic.get_tags(collection)))


@app.route('/api/user-country/<user>')
@catch_and_respond()
def get_user_country(user):
    return flaskify(oto_response.Response(logic.get_user_country(user)))


@app.route('/api/missing-tags/<collection>')
@catch_and_respond()
def get_missing_tags(collection):
    return flaskify(oto_response.Response(logic.get_missing_tags(collection)))


@app.route('/api/calc-rwax')
@catch_and_respond()
def calc_rwax_tokens():
    return flaskify(oto_response.Response(logic.test_rwax_stuff()))


@app.route('/api/rwax-tokens')
@catch_and_respond()
def get_rwax_tokens():
    collection = request.args.get('collection', None)
    symbol = request.args.get('symbol', None)
    contract = request.args.get('contract', None)
    return flaskify(oto_response.Response(logic.get_rwax_tokens(collection, symbol, contract)))


@app.route('/api/template/<template_id>')
@catch_and_respond()
def get_template(template_id):
    templates = logic.templates(
        template_id, verified='all'
    )

    if templates and len(templates) == 1:
        return flaskify(oto_response.Response(templates[0]))
    return flaskify(oto_response.Response({}))


@app.route('/v3/collection-stats/<collection>')
@catch_and_respond()
def collection_stats(collection):
    return flaskify(oto_response.Response(stats_v3.collection_stats(collection)))


@app.route('/v3/user-stats/<user>')
@catch_and_respond()
def user_stats(user):
    return flaskify(oto_response.Response(stats_v3.user_stats(user)))


@app.route('/v3/top-markets/<days>')
@catch_and_respond()
def market_table(days=1):
    type = request.args.get('type', default=None)
    collection = request.args.get('collection', default=None)
    return flaskify(oto_response.Response(stats_v3.get_market_table(days, _format_collection(collection), type)))


@app.route('/v3/top-collections/<days>')
@catch_and_respond()
def top_collection_table(days):
    type = request.args.get('type', default=None)
    term = request.args.get('term', default=None)
    verified = request.args.get('verified', default='all')
    limit = request.args.get('limit', default=0, type=int)
    offset = request.args.get('offset', default=0, type=int)

    collections = stats_v3.get_collection_table(days, type, term, verified)
    if limit:
        return flaskify(oto_response.Response(
            collections[min(offset, len(collections)):min(offset + limit, len(collections))])
        )
    return flaskify(oto_response.Response(collections))


@app.route('/v3/top-templates/<days>')
@app.route('/v3/top-templates/<days>/<collection>')
@catch_and_respond()
def top_templates_table(days, collection=None):
    limit = request.args.get('limit', default=20, type=int)
    offset = request.args.get('offset', default=0, type=int)
    return flaskify(oto_response.Response(stats_v3.get_template_table(days, collection, limit, offset)))


@app.route('/v3/top-drops/<days>')
@catch_and_respond()
def top_drops_table(days):
    limit = request.args.get('limit', default=20, type=int)
    offset = request.args.get('offset', default=0, type=int)
    return flaskify(oto_response.Response(stats_v3.get_drops_table(days, limit, offset)))


@app.route('/v3/top-users/<days>')
@app.route('/v3/top-users/<days>/<collection>')
@catch_and_respond()
def top_users(days, collection=None):
    actor = request.args.get('actor', default='all', type=str)
    term = request.args.get('term', default='', type=str)
    type = request.args.get('type', default='', type=str)
    limit = request.args.get('limit', default=20, type=int)
    offset = request.args.get('offset', default=0, type=int)
    users = stats_v3.get_users_table(days, collection, actor, type, term)
    if limit:
        return flaskify(oto_response.Response(
            users[min(offset, len(users)):min(offset + limit, len(users))])
        )
    return flaskify(oto_response.Response(users))


@app.route('/v3/top-sales')
@app.route('/v3/top-sales/<days>')
@app.route('/v3/top-sales/<days>/<collection>')
@catch_and_respond()
def top_sales_table(days=None, collection=None):
    limit = request.args.get('limit', default=20, type=int)
    offset = request.args.get('offset', default=0, type=int)
    return flaskify(oto_response.Response(stats_v3.get_top_sales_table(days, collection, limit, offset)))


@app.route('/v3/top-template-sales/<template_id>/<days>')
@catch_and_respond()
def top_template_sales_table(template_id, days=None):
    limit = request.args.get('limit', default=20, type=int)
    offset = request.args.get('offset', default=0, type=int)
    sales = stats_v3.get_top_template_sales(days, template_id, limit, offset)
    if limit:
        return flaskify(oto_response.Response(
            sales[min(offset, len(sales)):min(offset + limit, len(sales))])
        )
    return flaskify(oto_response.Response(sales))


@app.route('/v3/num-assets')
@app.route('/v3/num-assets/<collection>')
@catch_and_respond()
def get_num_assets(collection=None):
    return flaskify(oto_response.Response(stats_v3.get_number_of_assets(None, collection)))


@app.route('/v3/user-assets/<user>')
@app.route('/v3/user-assets/<user>/<collection>')
@catch_and_respond()
def get_user_assets(user=None, collection=None):
    return flaskify(oto_response.Response(stats_v3.get_number_of_assets(user, collection)))


@app.route('/v3/num-users/<collection>')
@catch_and_respond()
def get_num_users(collection):
    return flaskify(oto_response.Response(stats_v3.get_number_of_users(collection)))


@app.route('/v3/price-history/<asset_id>')
@catch_and_respond()
def get_price_history(asset_id):
    return flaskify(oto_response.Response(stats_v3.get_price_history(asset_id)))


@app.route('/v3/price-history-template/<template_id>')
@catch_and_respond()
def get_price_history_template(template_id):
    return flaskify(oto_response.Response(stats_v3.get_price_history(None, template_id)))


@app.route('/v3/monthly-volume/<days>')
@catch_and_respond()
def get_monthly_volume(days):
    type = request.args.get('type', default=None)
    collection = request.args.get('collection')
    collection = _format_collection(collection)
    return flaskify(oto_response.Response(stats_v3.get_monthly_volume(collection, days, type)))


@app.route('/v3/sales-volume-graph')
@app.route('/v3/sales-volume-graph/<days>')
@app.route('/v3/sales-volume-graph/<days>/<collection>')
@catch_and_respond()
def get_sales_volume_graph(days=60, collection=None):
    type = request.args.get('type', default=None)
    return flaskify(oto_response.Response(stats_v3.get_sales_volume_graph(days, None, collection, type)))


@app.route('/v3/template-sales-volume-graph/<template_id>')
@app.route('/v3/template-sales-volume-graph/<template_id>/<days>')
@catch_and_respond()
def get_template_sales_volume_graph(template_id, days=60):
    type = request.args.get('type', default=None)
    return flaskify(oto_response.Response(stats_v3.get_sales_volume_graph(days, template_id, None, type)))


@app.route('/v3/similar-collections/<collection>')
@catch_and_respond()
def get_similar_collections(collection):
    return flaskify(oto_response.Response(stats_v3.get_similar_collections(collection)))


@app.route('/v3/pfp-analytics/<template_id>')
@app.route('/v3/pfp-analytics')
@catch_and_respond()
def get_pfp_asset_analyics(template_id=None):
    asset_id = request.args.get('asset_id')
    if not template_id:
        template_id = request.args.get('template_id')
    return flaskify(oto_response.Response(stats_v3.get_pfp_asset_analytics(asset_id, template_id)))


@app.route('/v3/user-info/<user>')
@catch_and_respond()
def get_user_info(user):
    return flaskify(oto_response.Response(stats_v3.get_user_info(user)))


@app.route('/v3/collection-volume-graph')
@app.route('/v3/collection-volume-graph/<days>')
@app.route('/v3/collection-volume-graph/<days>/<topx>')
@catch_and_respond()
def get_collection_volume_graph(days=60, topx=10):
    type = request.args.get('type', default=None)
    collection = request.args.get('collection')
    collection = _format_collection(collection)
    return flaskify(oto_response.Response(stats_v3.get_collection_volume_graph(days, topx, type, collection)))


@app.route('/v3/attribute-analytics/<collection>/<schema>')
@catch_and_respond()
def get_attribute_asset_analyics_schema(collection, schema):
    asset_id = request.args.get('asset_id')
    return flaskify(oto_response.Response(stats_v3.get_attribute_asset_analytics_schema(asset_id, collection, schema)))


@app.route('/v3/floor/<template_id>')
@catch_and_respond()
def get_floor(template_id):
    return flaskify(oto_response.Response(stats_v3.get_floor(template_id)))


@app.route('/v3/volume/<days>')
@app.route('/v3/volume/<days>/<collection>')
@catch_and_respond()
def get_volume(days, collection=None):
    collection = _format_collection(collection)
    type = request.args.get('type', default=None)
    return flaskify(oto_response.Response(stats_v3.get_volume(collection, days, type)))


@app.route('/v3/buy-volume/<user>/<days>')
@catch_and_respond()
def get_buy_volume(user, days):
    type = request.args.get('type', default=None)
    return flaskify(oto_response.Response(stats_v3.get_buy_volume(user, days, type)))


@app.route('/v3/sell-volume/<user>/<days>')
@catch_and_respond()
def get_sell_volume(user, days):
    type = request.args.get('type', default=None)
    return flaskify(oto_response.Response(stats_v3.get_sell_volume(user, days, type)))


@app.route('/v3/change')
@app.route('/v3/change/<collection>')
@catch_and_respond()
def get_change(collection=None):
    type = request.args.get('type', default=None)
    collection = _format_collection(collection)
    return flaskify(oto_response.Response(stats_v3.get_change(collection, type)))


@app.route('/v3/marketcap')
@app.route('/v3/marketcap/<collection>')
@catch_and_respond()
def get_marketcap(collection=None):
    return flaskify(oto_response.Response(stats_v3.get_market_cap(collection)))


@app.route('/v3/initial-sales-feed')
def initial_sales_feed():
    return flaskify(oto_response.Response(stats_v3.get_newest_sales()))


class StatsAnnouncer:
    def __init__(self):
        self.listeners = []

    status = 'stopped'

    def listen(self):
        q = queue.Queue(maxsize=500)
        self.listeners.append(q)
        return q

    def announce(self, msg):
        for i in reversed(range(len(self.listeners))):
            try:
                self.listeners[i].put_nowait(msg)
            except queue.Full:
                del self.listeners[i]

    def get_status(self):
        return self.status

    def get_listeners(self):
        return self.listeners

    def format_sse(self, data: str, event=None) -> str:
        msg = f'data: {data}\n\n'
        if event is not None:
            msg = f'event: {event}\n{msg}'
        return msg

    def run_feed(self):
        while self.status == 'started':
            time.sleep(1.0)

            self.announce(self.format_sse(stats_v3.get_newest_sales()))

    def start(self):
        if self.status == 'started':
            return False
        self.status = 'started'

        _thread.start_new_thread(self.run_feed, ())

    def stop(self):
        self.status = 'stopped'


stats_announcer = StatsAnnouncer()


@app.route('/v3/sales-feed')
def stream():
    if not stats_announcer.get_status() == 'started':
        stats_announcer.start()

    def event_stream():
        messages = stats_announcer.listen()  # returns a queue.Queue
        while True:
            msg = messages.get()
            yield msg

    return Response(event_stream(), mimetype="text/event-stream")


@app.route('/v3/sales-feed-status')
def feed_status():
    return flaskify(oto_response.Response(
        {'status': stats_announcer.get_status(), 'listeners': stats_announcer.get_listeners()}
    ))


# PFP API
@app.route('/pfp-api/asset/<asset_id>')
def get_pfp_asset(asset_id):
    try:
        return flaskify(oto_response.Response(pfps.get_pfp_asset(
            asset_id
        )))
    except Exception as err:
        logging.error(err)
        return flaskify(oto_response.Response('An unexpected Error occured', errors=err, status=500))


@app.route('/pfp-api/trait-list/<collection>/<schema>')
def get_pfp_trait_list(collection, schema):
    try:
        limit = request.args.get('limit', 20)
        offset = request.args.get('offset', 0)
        return flaskify(oto_response.Response(pfps.get_pfp_trait_list(
            collection, schema, limit, offset
        )))
    except Exception as err:
        logging.error(err)
        return flaskify(oto_response.Response('An unexpected Error occured', errors=err, status=500))


@app.route('/pfp-api/top-holders/<collection>/<schema>')
def get_pfp_top_holders(collection, schema):
    try:
        limit = request.args.get('limit', 20)
        offset = request.args.get('offset', 0)
        return flaskify(oto_response.Response(pfps.get_pfp_top_holders(
            collection, schema, limit, offset
        )))
    except Exception as err:
        logging.error(err)
        return flaskify(oto_response.Response('An unexpected Error occured', errors=err, status=500))


@app.route('/pfp-api/ranking/<collection>/<schema>')
def get_pfp_ranking(collection, schema):
    try:
        limit = request.args.get('limit', 20)
        offset = request.args.get('offset', 0)
        return flaskify(oto_response.Response(pfps.get_pfp_ranking(
            collection, schema, limit, offset
        )))
    except Exception as err:
        logging.error(err)
        return flaskify(oto_response.Response('An unexpected Error occured', errors=err, status=500))


@app.route('/pfp-api/collection/<collection>')
def get_pfp_collection_info(collection):
    try:
        limit = request.args.get('limit', 20)
        offset = request.args.get('offset', 0)
        return flaskify(oto_response.Response(pfps.get_pfp_collections_info(
            collection, limit, offset
        )))
    except Exception as err:
        logging.error(err)
        return flaskify(oto_response.Response('An unexpected Error occured', errors=err, status=500))


@app.route('/pfp-api/collections')
def get_pfp_collections():
    try:
        limit = request.args.get('limit', 20)
        offset = request.args.get('offset', 0)
        collection = request.args.get('collection', '')
        return flaskify(oto_response.Response(pfps.get_pfp_collections_info(
            collection, limit, offset
        )))
    except Exception as err:
        logging.error(err)
        return flaskify(oto_response.Response('An unexpected Error occured', errors=err, status=500))


# Verify API
@app.route('/verify-api/status/<collection>')
def get_verify_status(collection):
    try:
        return flaskify(oto_response.Response(verify.get_verify_status(
            collection
        )))
    except Exception as err:
        logging.error(err)
        return flaskify(oto_response.Response('An unexpected Error occured', errors=err, status=500))


@app.route('/verify-api/votes/<collection>')
def get_votes(collection):
    try:
        return flaskify(oto_response.Response(verify.get_voting_status(
            collection
        )))
    except Exception as err:
        logging.error(err)
        return flaskify(oto_response.Response('An unexpected Error occured', errors=err, status=500))


@app.route('/verify-api/top-voted-collections')
def top_voted_collections():
    try:
        limit = request.args.get('limit', 20)
        offset = request.args.get('offset', 0)

        return flaskify(oto_response.Response(verify.get_top_voted_collections(
            limit, offset
        )))
    except Exception as err:
        logging.error(err)
        return flaskify(oto_response.Response('An unexpected Error occured', errors=err, status=500))


@app.route('/verify-api/top-voted-collections-total-rows')
def top_voted_collections_total_rows():
    try:
        return flaskify(oto_response.Response(verify.get_top_voted_collections_total_rows()))
    except Exception as err:
        logging.error(err)
        return flaskify(oto_response.Response('An unexpected Error occured', errors=err, status=500))


@app.route('/legacy/collection-table')
@app.route('/legacy/collection-table/<verified>')
def get_collection_table(verified=True):
    try:
        term = request.args.get('term')
        market = request.args.get('market')
        type = request.args.get('type')
        owner = request.args.get('owner')
        collection = request.args.get('collection')
        pfps_only = request.args.get('pfps_only', 'false') == 'true'
        return flaskify(oto_response.Response(legacy.get_collection_table(
            verified, term, market, type, owner, collection, pfps_only)))
    except Exception as err:
        logging.error(err)
        return flaskify(oto_response.Response('An unexpected Error occured', errors=err, status=500))


@app.route('/legacy/usd-wax')
def usd_wax():
    try:
        return flaskify(oto_response.Response(legacy.get_usd_wax()))
    except Exception as err:
        logging.error(err)
        return flaskify(oto_response.Response('An unexpected Error occured', errors=err, status=500))


@app.route('/legacy/schema-templates/<collection>/<schema>')
def get_schema_templates(collection, schema):
    try:
        return flaskify(oto_response.Response(legacy.get_schema_templates(collection, schema)))
    except Exception as err:
        logging.error(err)
        return flaskify(oto_response.Response('An unexpected Error occured', errors=err, status=500))


@app.route('/legacy/collection-drops/<collection>')
def get_collection_drops(collection):
    try:
        offset = request.args.get('offset', 0)
        limit = request.args.get('limit', 40)
        include_erased = request.args.get('include_erased', 'false') == 'true'

        collection = _format_collection(collection)

        if limit:
            try:
                limit = int(limit)
            except Exception as err:
                limit = 40
        else:
            limit = 40

        search_res = legacy.get_collection_drops(
            collection, limit, offset if isinstance(offset, int) or (isinstance(offset, str) and offset.isnumeric()) else 0,
            include_erased
        )

        return flaskify(oto_response.Response(search_res))
    except Exception as err:
        logging.error(err)
        return flaskify(oto_response.Response('An unexpected Error occured', errors=err, status=500))


@app.route('/legacy/collection-total-drops/<collection>')
def get_collection_total_drops(collection):
    try:
        collection = _format_collection(collection)

        search_res = legacy.get_collection_total_drops(
            collection
        )

        return flaskify(oto_response.Response(search_res))
    except Exception as err:
        logging.error(err)
        return flaskify(oto_response.Response('An unexpected Error occured', errors=err, status=500))


@app.route('/legacy/get-all-owned/<asset_id>')
def get_all_owned(asset_id):
    try:
        return flaskify(oto_response.Response(legacy.get_all_owned(asset_id)))
    except Exception as err:
        logging.error(err)
        return flaskify(oto_response.Response('An unexpected Error occured', errors=err, status=500))


@app.route('/legacy/get-all-for-sale/<template_id>')
def get_all_for_sale(template_id):
    try:
        return flaskify(oto_response.Response(legacy.get_all_for_sale(template_id)))
    except Exception as err:
        logging.error(err)
        return flaskify(oto_response.Response('An unexpected Error occured', errors=err, status=500))


@app.route('/legacy/top-honey-earner/<days>')
def get_top_honey_earner(days):
    try:
        return flaskify(oto_response.Response(legacy.get_top_honey_earner(days)))
    except Exception as err:
        logging.error(err)
        return flaskify(oto_response.Response('An unexpected Error occured', errors=err, status=500))


@app.route('/legacy/active-sales')
def get_active_sales():
    try:
        sale_ids = request.args.get('sales', None)
        if sale_ids:
            sale_ids = sale_ids.split(',')
        return flaskify(oto_response.Response(legacy.get_active_sales(sale_ids)))
    except Exception as err:
        logging.error(err)
        return flaskify(oto_response.Response('An unexpected Error occured', errors=err, status=500))


@app.route('/legacy/collection-crafts/<collection>')
def get_collection_crafts(collection):
    try:
        offset = request.args.get('offset', 0)
        limit = request.args.get('limit', 40)
        include_erased = request.args.get('include_erased', 'false') == 'true'

        collection = _format_collection(collection)

        if limit:
            try:
                limit = int(limit)
            except Exception as err:
                limit = 40
        else:
            limit = 40

        search_res = legacy.get_collection_crafts(
            collection, limit,
            offset if isinstance(offset, int) or (isinstance(offset, str) and offset.isnumeric()) else 0,
            include_erased
        )

        return flaskify(oto_response.Response(search_res))
    except Exception as err:
        logging.error(err)
        return flaskify(oto_response.Response('An unexpected Error occured', errors=err, status=500))


@app.route('/legacy/get-minting-state/<contract>/<id>')
def get_minting_state_api1(contract, id):
    try:
        if contract == 'nfthivedrops':
            return flaskify(oto_response.Response(legacy.get_minting_state(id)))
        else:
            return flaskify(oto_response.Response(legacy.get_minting_state_craft(id)))
    except Exception as err:
        logging.error(err)
        return flaskify(oto_response.Response('An unexpected Error occured', errors=err, status=500))


@app.route('/legacy/drops-data/<contract>')
def get_drops_data(contract):
    try:
        drop_ids = request.args.get('drop_ids')
        drop_ids = drop_ids.split(',') if drop_ids and ',' in drop_ids else ([drop_ids] if drop_ids else [])

        search_res = logic.get_drops(
            drop_ids=drop_ids, market=contract, limit=len(drop_ids)
        )

        return flaskify(oto_response.Response(search_res))
    except Exception as err:
        logging.error(err)
        return flaskify(oto_response.Response('An unexpected Error occured', errors=err, status=500))


@app.route('/legacy/get-users')
def get_users():
    try:
        collection = request.args.get('collection', None)
        limit = request.args.get('limit', 40)
        term = request.args.get('term', None)
        return flaskify(oto_response.Response(legacy.get_users(collection, term, limit)))
    except Exception as err:
        logging.error(err)
        return flaskify(oto_response.Response('An unexpected Error occured', errors=err, status=500))


@app.route('/legacy/claimable-packs')
def get_claimable_packs():
    start_time = time.time()
    asset_ids = request.args.get('asset_ids')

    if asset_ids:
        asset_ids = asset_ids.split(',')
    else:
        return flaskify(oto_response.Response('An unexpected Error occured', errors='Invalid Assets', status=500))
    try:
        return flaskify(oto_response.Response(logic.assets(asset_ids=asset_ids, verified='all', burned='all')))
    except Exception as err:
        logging.error(err)
        return flaskify(oto_response.Response('An unexpected Error occured', errors=err, status=500))
    finally:
        end_time = time.time()
        print('get_my_packs({}): {}'.format(asset_ids, end_time - start_time))


@app.route('/legacy/craft-data')
def get_crafts_data():
    try:
        craft_ids = request.args.get('craft_ids')
        craft_ids = craft_ids.split(',') if craft_ids and ',' in craft_ids else ([craft_ids] if craft_ids else [])

        search_res = logic.get_crafts(
            craft_ids=craft_ids, limit=len(craft_ids)
        )

        return flaskify(oto_response.Response(search_res))
    except Exception as err:
        logging.error(err)
        return flaskify(oto_response.Response('An unexpected Error occured', errors=err, status=500))


@app.route('/legacy/buy-offer-assets')
def get_buy_offer_assets():
    seller = request.args.get('seller')
    offer_id = request.args.get('offer_id')
    try:
        return flaskify(oto_response.Response(legacy.get_buy_offer_assets(seller, offer_id)))
    except Exception as err:
        logging.error(err)
        return flaskify(oto_response.Response('An unexpected Error occured', errors=err, status=500))


@app.route('/legacy/get-wax-tokens')
def get_wax_tokens():
    try:
        return flaskify(oto_response.Response(legacy.get_wax_tokens()))
    except Exception as err:
        logging.error(err)
        return flaskify(oto_response.Response('An unexpected Error occured', errors=err, status=500))


@app.route('/legacy/currencies')
def get_currencies():
    try:
        tokens = legacy.get_currencies()

        return flaskify(oto_response.Response(tokens))
    except Exception as err:
        logging.error(err)
        return flaskify(oto_response.Response('An unexpected Error occured', errors=err, status=500))


# Legacy Endpoints, Retiring NFTHive API
@app.route('/legacy/collection-minimal/<collection>')
@catch_and_respond()
def get_collection_minimal(collection):
    return flaskify(oto_response.Response(legacy.get_collection(collection)))


@app.route('/legacy/auction-minimal/<market>/<auction_id>')
def minimal_auction(market, auction_id):
    try:
        return flaskify(oto_response.Response(legacy.get_minimal_auction(market, auction_id)))
    except Exception as err:
        logging.error(err)
        return flaskify(oto_response.Response('An unexpected Error occured', errors=err, status=500))


@app.route('/legacy/asset-minimal/<asset_id>')
def show_minimal_asset(asset_id):
    try:
        return flaskify(oto_response.Response(legacy.get_minimal_asset(asset_id)))
    except Exception as err:
        logging.error(err)
        return flaskify(oto_response.Response('An unexpected Error occured', errors=err, status=500))


@app.route('/legacy/template-minimal/<template_id>')
def show_minimal_template(template_id):
    try:
        return flaskify(oto_response.Response(legacy.get_minimal_template(template_id)))
    except Exception as err:
        logging.error(err)
        return flaskify(oto_response.Response('An unexpected Error occured', errors=err, status=500))


@app.route('/legacy/drop-minimal')
def show_minimal_drop():
    try:
        drop_id = request.args.get('drop_id')
        contract = request.args.get('contract')
        return flaskify(oto_response.Response(legacy.get_minimal_drop(drop_id, contract)))
    except Exception as err:
        logging.error(err)
        return flaskify(oto_response.Response('An unexpected Error occured', errors=err, status=500))


@app.route('/legacy/ownership-info')
def get_ownership_info():
    try:
        asset_id = request.args.get('asset_id')
        owner = request.args.get('owner')
        return flaskify(oto_response.Response(legacy.get_ownership_info(asset_id, owner)))
    except Exception as err:
        logging.error(err)
        return flaskify(oto_response.Response('An unexpected Error occured', errors=err, status=500))


@app.route('/legacy/ownership-info-template')
def get_ownership_info_template():
    try:
        template_id = request.args.get('template_id')
        owner = request.args.get('owner')
        return flaskify(oto_response.Response(legacy.get_ownership_info_template(template_id, owner)))
    except Exception as err:
        logging.error(err)
        return flaskify(oto_response.Response('An unexpected Error occured', errors=err, status=500))


@app.route('/legacy/get-wuffi-airdrop/<airdrop_id>')
def get_wuffi_airdrop(airdrop_id):
    username = request.args.get('username')
    try:
        return flaskify(oto_response.Response(legacy.get_wuffi_airdrop(airdrop_id, username)))
    except Exception as err:
        logging.error(err)
        return flaskify(oto_response.Response('An unexpected Error occured', errors=err, status=500))


@app.route('/legacy/banners')
def get_banners():
    try:
        return flaskify(oto_response.Response(legacy.get_banners()))
    except Exception as err:
        logging.error(err)
        return flaskify(oto_response.Response('An unexpected Error occured', errors=err, status=500))


@app.route('/legacy/get-personal-blacklist')
def get_personal_blacklist():
    try:
        user = request.args.get('user', None)
        limit = request.args.get('limit', 40)
        term = request.args.get('term', None)
        return flaskify(oto_response.Response(legacy.get_personal_blacklist(user, term, limit)))
    except Exception as err:
        logging.error(err)
        return flaskify(oto_response.Response('An unexpected Error occured', errors=err, status=500))


@app.route('/legacy/get-wuffi-airdrops')
def get_wuffi_airdrops():
    try:
        ready = request.args.get('ready')
        creator = request.args.get('creator')
        username = request.args.get('username')
        contract = request.args.get('contract')
        return flaskify(oto_response.Response(legacy.get_wuffi_airdrops(ready, creator, username, contract)))
    except Exception as err:
        logging.error(err)
        return flaskify(oto_response.Response('An unexpected Error occured', errors=err, status=500))


@app.route('/legacy/user-picture/<user>')
def get_user_picture(user):
    try:
        return flaskify(oto_response.Response(legacy.get_user_picture(user)))
    except Exception as err:
        logging.error(err)
        return flaskify(oto_response.Response('An unexpected Error occured', errors=err, status=500))


@app.route('/legacy/pfps/<collection>')
def get_pfps(collection):
    try:
        return flaskify(oto_response.Response(legacy.get_pfps(collection)))
    except Exception as err:
        logging.error(err)
        return flaskify(oto_response.Response('An unexpected Error occured', errors=err, status=500))


@app.route('/legacy/num-auctions/<collection>')
def get_num_auctions(collection):
    try:
        return flaskify(oto_response.Response(legacy.get_num_auctions(collection)))
    except Exception as err:
        logging.error(err)
        return flaskify(oto_response.Response('An unexpected Error occured', errors=err, status=500))


@app.route('/legacy/num-drops/<collection>')
def get_num_drops(collection):
    try:
        return flaskify(oto_response.Response(legacy.get_num_drops(collection)))
    except Exception as err:
        logging.error(err)
        return flaskify(oto_response.Response('An unexpected Error occured', errors=err, status=500))


@app.route('/legacy/num-crafts/<collection>')
def get_num_crafts(collection):
    try:
        return flaskify(oto_response.Response(legacy.get_num_crafts(collection)))
    except Exception as err:
        logging.error(err)
        return flaskify(oto_response.Response('An unexpected Error occured', errors=err, status=500))


@app.route('/legacy/quick-search/<term>')
def quick_search(term):
    try:
        return flaskify(oto_response.Response(legacy.quick_search(term)))
    except Exception as err:
        logging.error(err)
        return flaskify(oto_response.Response('An unexpected Error occured', errors=err, status=500))


@app.route('/legacy/search-term/<term>/<name>')
def search_term(term, name):
    try:
        return flaskify(oto_response.Response(legacy.search_term(term, name)))
    except Exception as err:
        logging.error(err)
        return flaskify(oto_response.Response('An unexpected Error occured', errors=err, status=500))


@app.route('/legacy/add-token', methods=['POST'])
def add_token():
    auth_check_res = check_authorization(request)
    if auth_check_res is not None:
        return auth_check_res
    data = json.loads(request.data.decode('utf-8'))
    symbol = data['symbol'] if 'symbol' in data.keys() else None
    contract = data['contract'] if 'contract' in data.keys() else None
    try:
        legacy.add_token(symbol, contract)
        return flaskify(oto_response.Response('Banner Created', status=200))
    except Exception as err:
        print(err)
        return flaskify(oto_response.Response("An unexpected Error occured", status=500))


def check_authorization(request):
    auth_header = request.headers.get('Authorization')
    try:
        if not auth_header:
            return flaskify(oto_response.Response("Permission Denied", status=401))
        split = auth_header.split(' ')
        [bearer, token] = split[0], ' '.join(split[1:])
        if bearer != 'Bearer':
            return flaskify(oto_response.Response("Permission Denied", status=401))
        if not legacy.check_password(token):
            return flaskify(oto_response.Response("Permission Denied", status=401))

        return None
    except Exception as err:
        print(err)
        return flaskify(oto_response.Response("An unexpected Error occured", status=500))


if __name__ == '__main__':
    compress.init_app(app)
    logging.basicConfig(filename='app.err', level=logging.ERROR)
    run_app(app)
