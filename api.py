import os
from functools import wraps

from flask import Flask, request, Response
from oto.adaptors.flask import flaskify
from oto import response as oto_response
from flask_cors import CORS

from flask_executor import Executor
from flask_sqlalchemy import SQLAlchemy
from app_runner import run_app
from config import PostgresConfig

import logging

import time
from flask_caching import Cache

from flask_compress import Compress

from ddtrace import patch_all

import queue
import _thread

if not Flask.debug:
    patch_all()

compress = Compress()

app = Flask(__name__, static_folder='build', static_url_path='/')
app.config.from_object(PostgresConfig)

executor = Executor(app)
cache = Cache(app, config={'CACHE_TYPE': 'SimpleCache'})

db = SQLAlchemy(app, session_options={'autocommit': False})

import logic
import stats_v3

env = os.environ.get('FLASK_ENV')

Compress(app)

CORS(app, resources={
    r"/api/*": {
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
        rarity = request.args.get('rarity', None)

        return flaskify(oto_response.Response(logic.newest_listings(collection, schema, rarity, template_id)))
    except Exception as err:
        logging.error(err)
        return flaskify(oto_response.Response('An unexpected Error occured', errors=err, status=500))


announcer = MessageAnnouncer()


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
                logging.error(err)
                return flaskify(oto_response.Response(
                    {'error': 'An unexpected Error occured: {}'.format(err)}, errors=err, status=500))
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
    verified = request.args.get('verified', 'all')
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
        term, collection, schema, limit, order_by, exact_search, offset, verified
    )

    return flaskify(oto_response.Response(search_res))


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
        user, favorites, backed, recently_sold, attributes
    )

    return flaskify(oto_response.Response(search_res))


@app.route('/api/filter-attributes/<collection>')
@catch_and_respond()
def filter_attributes(collection):
    schema = request.args.get('schema')
    templates = request.args.get('templates')

    collection = _format_collection(collection)

    search_res = logic.filter_attributes(
        collection, schema, templates
    )

    return flaskify(oto_response.Response(search_res))


@app.route('/api/collection-filters/<collection>')
@catch_and_respond()
def collection_filters(collection):
    collection = _format_collection(collection)

    search_res = logic.collection_filters(collection)

    return flaskify(oto_response.Response(search_res))


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
    favorites = request.args.get('favorites', 'false') == 'true'
    backed = request.args.get('backed', 'false') == 'true'
    contract = request.args.get('contract')
    user = request.args.get('user', '')
    order_by = request.args.get('order_by') if request.args.get('order_by') else 'date_desc'
    exact_search = request.args.get('exact_search') == 'true'
    search_type = request.args.get('search_type') if request.args.get('search_type') else ''
    attributes = request.args.get('attributes', None)
    only = request.args.get('only', None)

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
        term, owner, market, collection, schema, limit, order_by,
        exact_search, search_type, min_price, max_price, min_mint, max_mint, contract, offset, verified,
        user, favorites, backed, recently_sold, attributes, only
    )

    return flaskify(oto_response.Response(search_res))


@app.route('/api/collections-overview/<collection>')
@app.route('/api/collections-overview')
@catch_and_respond()
def get_collections_overview(collection='*'):
    collection = request.args.get('collection', collection)
    collection = _format_collection(collection)
    type = request.args.get('type')
    tag_id = request.args.get('tag_id')
    limit = request.args.get('limit', 100)
    verified = request.args.get('verified', 'verified')
    trending = request.args.get('trending', 'false') == 'true'
    return flaskify(oto_response.Response(logic.get_collections_overview(
        collection, type, tag_id, verified, trending, limit)))


@app.route('/api/collection-schemas/<collection>')
@catch_and_respond()
def get_collection_schemas(collection):
    return flaskify(oto_response.Response(logic.get_collection_schemas(collection)))


@app.route('/api/tags/<collection>')
@catch_and_respond()
def get_tags(collection):
    return flaskify(oto_response.Response(logic.get_tags(collection)))


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
    return flaskify(oto_response.Response(stats_v3.get_number_of_assets(collection)))


@app.route('/v3/num-users/<collection>')
@catch_and_respond()
def get_num_users(collection):
    return flaskify(oto_response.Response(stats_v3.get_number_of_users(collection)))


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


if __name__ == '__main__':
    compress.init_app(app)
    logging.basicConfig(filename='app.err', level=logging.ERROR)
    run_app(app)
