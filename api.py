import os
from functools import wraps
from random import random, randint

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

env = os.environ.get('FLASK_ENV')

Compress(app)

CORS(app, resources={
    r"/api/*": {
        "origins": [
            "*",
        ]
    }
})

import logic


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
    limit = request.args.get('limit', 40)
    offset = request.args.get('offset', 0)
    min_mint = request.args.get('min_mint')
    max_mint = request.args.get('max_mint')
    min_average = request.args.get('min_average')
    max_average = request.args.get('max_average')
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


@app.route('/api/listings')
@catch_and_respond()
def listings():
    term = request.args.get('term')
    owner = request.args.get('seller')
    market = request.args.get('market')
    collection = request.args.get('collection')
    schema = request.args.get('schema')
    limit = request.args.get('limit', 40)
    offset = request.args.get('offset', 0)
    min_mint = request.args.get('min_mint')
    max_mint = request.args.get('max_mint')
    min_price = request.args.get('min_price')
    max_price = request.args.get('max_price')
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
    pfps_only = request.args.get('pfps_only', 'false') == 'true'

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
        user, favorites, backed, recently_sold, attributes, pfps_only
    )

    return flaskify(oto_response.Response(search_res))


if __name__ == '__main__':
    compress.init_app(app)
    logging.basicConfig(filename='app.err', level=logging.ERROR)
    run_app(app)
