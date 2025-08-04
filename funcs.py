import datetime
import json
import re
import logging
import time

import pytz
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from functools import wraps


def log_exception(e):
    logging.exception(e)


def log_error(e):
    logging.error(e)


def setup_logger(name, log_file, level=logging.INFO):
    handler = logging.FileHandler(log_file)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)

    return logger


measure_god = {}


def add_measure_god(elapsed, name):
    global measure_god
    if name in measure_god:
        measure_god[name]['totalTime'] += elapsed
        measure_god[name]['calls'] += 1
        measure_god[name]['average'] = measure_god[name]['totalTime'] / measure_god[name]['calls']
    else:
        measure_god[name] = {
            'totalTime': elapsed,
            'calls': 1,
            'average': elapsed
        }


def measure_godding():
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            start = time.time()
            rv = f(*args, **kwargs)
            end = time.time()
            add_measure_god(end - start, f.__name__)
            return rv
        return decorated_function
    return decorator


def catch_and_log():
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                return f(*args, **kwargs)
            except SQLAlchemyError as err:
                log_error('{}: {}'.format(f.__name__, err))
                log_exception(err)
                raise err
            except Exception as err:
                log_error('{}: {}'.format(f.__name__, err))
                log_exception(err)
                raise err
        return decorated_function
    return decorator


def load_transaction_basics(transaction):
    new_transaction = {}
    new_transaction['transaction_id'] = transaction['trx_id']
    new_transaction['seq'] = transaction['global_sequence']
    new_transaction['block_num'] = transaction['block_num']
    new_transaction['timestamp'] = datetime.datetime.strptime(
        re.sub(r'\.\d+Z', 'Z', transaction['@timestamp']), '%Y-%m-%dT%H:%M:%S.%f'
    ) if '@timestamp' in transaction else (transaction['timestamp'])
    new_transaction['action_name'] = transaction['act']['name']
    return new_transaction


def session_execute_logged(session, sql, args={}):
    global measure_god

    start = time.time()

    res = session.execute(text(sql), args)

    end = time.time()

    elapsed = end - start
    if sql in measure_god:
        measure_god[sql]['totalTime'] += elapsed
        measure_god[sql]['calls'] += 1
        measure_god[sql]['average'] = measure_god[sql]['totalTime'] / measure_god[sql]['calls']
    else:
        measure_god[sql] = {
            'totalTime': elapsed,
            'calls': 1,
            'average': elapsed
        }

    return res.mappings()


def parse_attributes(session, collection, schema, data):
    attribute_ids = []
    for key in data.keys():
        if key.lower() in ['name', 'img', 'title', 'video', 'unique', 'generic', 'description']:
            continue
        if len(key) > 64 or not key:
            continue
        value = data[key]
        int_value = None
        float_value = None
        bool_value = None
        if isinstance(value, bool):
            bool_value = value
            value = None
        elif isinstance(value, int):
            int_value = value
            value = None
            if int_value > 9223372036854775807 or int_value < -9223372036854775808:
                value = str(value)
                int_value = None
        elif isinstance(value, float):
            float_value = value
            value = None
        else:
            value = str(value)
            if len(value) > 64 or not value:
                continue
        res = session_execute_logged(
            session,
            'WITH insert_result AS (INSERT INTO attributes '
            '(collection, schema, attribute_name, string_value, int_value, float_value, bool_value) '
            'SELECT :collection, :schema, :key, :strvalue, :numvalue, :floatvalue, :boolvalue '
            'WHERE NOT EXISTS ('
            '   SELECT attribute_name '
            '   FROM attributes '
            '   WHERE collection = :collection AND schema = :schema '
            '   AND attribute_name = :key AND {attribute_clause} '
            ') RETURNING attribute_id) '
            'SELECT attribute_id FROM attributes '
            'WHERE collection = :collection AND schema = :schema '
            'AND attribute_name = :key AND {attribute_clause} '
            'UNION SELECT attribute_id FROM insert_result'.format(
                attribute_clause='int_value = :numvalue' if int_value or int_value == 0 else (
                    'float_value = :floatvalue') if float_value or float_value == 0 else (
                    'bool_value = :boolvalue' if bool_value or bool_value == False else 'string_value = :strvalue'
                )
            ),
            {
                'collection': collection, 'schema': schema, 'key': key,
                'strvalue': value, 'numvalue': int_value, 'floatvalue': float_value,
                'boolvalue': bool_value
            }
        ).first()
        if res:
            attribute_ids.append(res['attribute_id'])

    return attribute_ids


def parse_simple_attributes(session, collection, schema, data):
    attribute_ids = []
    for key in data.keys():
        if collection == 'ilovekolobok' and key in ['bdate', 'genome', 'cd', 'p1', 'p2', 'prize_date']:
            continue
        if key.lower() in ['name', 'img', 'title', 'video', 'unique', 'generic', 'description']:
            continue
        if len(key) > 64 or not key:
            continue
        value = data[key]
        int_value = None
        float_value = None
        bool_value = None
        if isinstance(value, bool):
            bool_value = value
            value = None
        elif isinstance(value, int):
            int_value = value
            value = None
            if int_value > 9223372036854775807 or int_value < -9223372036854775808:
                value = str(value)
                int_value = None
        elif isinstance(value, float):
            float_value = value
            value = None
        else:
            value = str(value)
            if len(value) > 64 or not value:
                continue
        res = session_execute_logged(
            session,
            'WITH insert_result AS (INSERT INTO attributes '
            '(collection, schema, attribute_name, string_value, int_value, float_value, bool_value) '
            'SELECT :collection, :schema, :key, :strvalue, :numvalue, :floatvalue, :boolvalue '
            'WHERE NOT EXISTS ('
            '   SELECT attribute_name '
            '   FROM attributes '
            '   WHERE collection = :collection AND schema = :schema '
            '   AND attribute_name = :key AND {attribute_clause} '
            ') RETURNING attribute_id) '
            'SELECT attribute_id FROM attributes '
            'WHERE collection = :collection AND schema = :schema '
            'AND attribute_name = :key AND {attribute_clause} '
            'UNION SELECT attribute_id FROM insert_result'.format(
                attribute_clause='int_value = :numvalue' if int_value or int_value == 0 else (
                    'float_value = :floatvalue') if float_value or float_value == 0 else (
                    'bool_value = :boolvalue' if bool_value or bool_value == False else 'string_value = :strvalue'
                )
            ),
            {
                'collection': collection, 'schema': schema, 'key': key,
                'strvalue': value, 'numvalue': int_value, 'floatvalue': float_value,
                'boolvalue': bool_value
            }
        ).first()
        if res:
            attribute_ids.append(res['attribute_id'])

    return attribute_ids


def parse_data(data):
    data_items = {}
    for item in data:
        if 'int' in item['value'][0]:
            data_items[item['key']] = int(item['value'][1])
        elif 'float' in item['value'][0]:
            data_items[item['key']] = float(item['value'][1])
        elif 'string' in item['value'][0]:
            data_items[item['key']] = item['value'][1].replace("\\u0000", "").replace('\x00', '')
        else:
            data_items[item['key']] = str(item['value'][1])

    return data_items


def construct_memo_clause(transaction):
    if 'memo' in transaction and transaction['memo']:
        return (
            'WITH insert_result AS (INSERT INTO memos (memo) SELECT :memo WHERE NOT EXISTS ('
            'SELECT memo FROM memos WHERE md5(memo) = md5(:memo)) RETURNING memo_id) '
        )
    return ''


def construct_with_clause(asset):
    with_clause = ''
    with_clauses = []
    if 'image' in asset and asset['image']:
        with_clauses.append(
            'image_insert_result AS (INSERT INTO images (image) SELECT :image WHERE NOT EXISTS ('
            'SELECT image FROM images WHERE image = :image) RETURNING image_id)'
        )
    if 'video' in asset and asset['video']:
        with_clauses.append(
            'video_insert_result AS (INSERT INTO videos (video) SELECT :video WHERE NOT EXISTS ('
            'SELECT video FROM videos WHERE video = :video) RETURNING video_id)'
        )
    if 'name' in asset and asset['name']:
        with_clauses.append(
            'name_insert_result AS (INSERT INTO names (name) SELECT :name WHERE NOT EXISTS ('
            'SELECT name FROM names WHERE name = :name) RETURNING name_id)'
        )
    if 'idata' in asset and asset['idata'] and asset['idata'] != '{}':
        with_clauses.append(
            'idata_insert_result AS (INSERT INTO data (data) SELECT :idata WHERE NOT EXISTS ('
            'SELECT data FROM data WHERE md5(data) = md5(:idata)) RETURNING data_id)'
        )
    if 'mdata' in asset and asset['mdata'] and asset['mdata'] != '{}' and (
            'idata' not in asset or asset['mdata'] != asset['idata']):
        with_clauses.append(
            'mdata_insert_result AS (INSERT INTO data (data) SELECT :mdata WHERE NOT EXISTS ('
            'SELECT data FROM data WHERE md5(data) = md5(:mdata)) RETURNING data_id)'
        )
    if len(with_clauses) > 0:
        with_clause = 'WITH ' + ', '.join(with_clauses)

    return with_clause


def construct_mdata_column(asset):
    if asset['mdata'] and asset['mdata'] != '{}' and (
            'idata' not in asset or asset['mdata'] != asset['idata']
    ):
        return (
            '(SELECT data_id FROM data WHERE md5(data) = md5(:mdata) UNION SELECT data_id FROM mdata_insert_result)'
        )
    elif 'idata' in asset and asset['idata'] and asset['idata'] != '{}' and asset['mdata'] == asset['idata']:
        return (
            '(SELECT data_id FROM data WHERE md5(data) = md5(:mdata) UNION SELECT data_id FROM idata_insert_result)'
        )
    else:
        return 'NULL'


def _parse_mdata(asset):
    try:
        return json.loads(asset['mdata'].replace('\\', '').replace('\"{', '{').replace('}\"', '}').replace('""', '","').replace('”', '"')) if asset['mdata'] else None
    except ValueError:
        return {'mdata': asset['mdata']}


def _parse_idata(asset):
    try:
        return json.loads(asset['idata'].replace('\\', '').replace('\"{', '{').replace('}\"', '}').replace('""', '","').replace('”', '"')) if asset['idata'] else None
    except ValueError:
        return {'idata': asset['idata']}


def _get_data(trx):
    act = trx['act']
    return json.loads(act['data']) if isinstance(act['data'], str) else act['data']


def _get_name(asset):
    mdata = _parse_mdata(asset)
    idata = _parse_idata(asset)
    name = None
    title = None
    if mdata and isinstance(mdata, dict) and 'name' in mdata.keys():
        name = mdata['name']
    if mdata and isinstance(mdata, dict) and 'title' in mdata.keys():
        title = mdata['title']
    if idata and isinstance(idata, dict) and 'name' in idata.keys():
        name = idata['name']

    if name and title:
        return '{} - {}'.format(name, title)
    if name:
        return name
    if title:
        return title

    return None


def _get_image(asset):
    mdata = _parse_mdata(asset)
    idata = _parse_idata(asset)
    img = mdata['img'] if mdata and isinstance(mdata, dict) and 'img' in mdata.keys() else None
    if not img:
        img = idata['img'] if idata and isinstance(idata, dict) and 'img' in idata.keys() else None

    return img


def _get_video(asset):
    mdata = _parse_mdata(asset)
    idata = _parse_idata(asset)
    img = mdata['video'] if mdata and isinstance(mdata, dict) and 'video' in mdata.keys() else None
    if not img:
        img = idata['video'] if idata and isinstance(idata, dict) and 'video' in idata.keys() else None

    return img


def _insert_transfer(session, transaction):
    with_clause = construct_memo_clause(transaction)
    session_execute_logged(
        session,
        '{with_clause} '
        'INSERT INTO transfers '
        '(asset_ids, seq, block_num, timestamp, sender, receiver, memo_id) '
        'SELECT :asset_ids, :seq, :block_num, :timestamp, :sender, :receiver, '
        '{memo_column} '
        'WHERE NOT EXISTS (SELECT seq FROM transfers WHERE seq = :seq)'.format(
            with_clause=with_clause,
            memo_column=(
                '(SELECT memo_id FROM memos WHERE md5(memo) = md5(:memo) UNION SELECT memo_id FROM insert_result)'
            ) if 'memo' in transaction and transaction['memo'] else 'NULL'
        ),
        transaction
    )

    if len(transaction['asset_ids']) == 0:
        return

    for asset_id in transaction['asset_ids']:
        session_execute_logged(
            session,
            'UPDATE assets SET owner = :receiver, transferred = :timestamp WHERE asset_id = :asset_id ', {
                'receiver': transaction['receiver'],
                'timestamp': transaction['timestamp'],
                'asset_id': asset_id,
                'seq': transaction['seq']
            }
        )

    if transaction['receiver'] in ['waxdaofarmer', 'pepperstake']:
        try:
            for asset_id in transaction['asset_ids']:
                transaction['asset_id'] = asset_id
                session_execute_logged(
                    session,
                    'INSERT INTO stakes ('
                    '   asset_id, stake_contract, staker, memo, seq, block_num, timestamp '
                    ') '
                    'SELECT :asset_id, :receiver, :sender, :memo, :seq, :block_num, :timestamp ',
                    transaction
                )
        except SQLAlchemyError as err:
            log_error('_insert_transfer: {}'.format(err))
            raise err
        except Exception as err:
            log_error('_insert_transfer: {}'.format(err))
            raise err
    elif transaction['sender'] in ['waxdaofarmer', 'pepperstake']:
        for asset_id in transaction['asset_ids']:
            transaction['asset_id'] = asset_id
            session_execute_logged(
                session,
                'INSERT INTO removed_stakes ('
                '   asset_id, stake_contract, staker, memo, seq, block_num, timestamp, removed_seq, removed_block_num '
                ') '
                'SELECT asset_id, stake_contract, staker, memo, seq, block_num, timestamp, :seq, :block_num '
                'FROM stakes WHERE asset_id = :asset_id ',
                transaction
            )
            session_execute_logged(
                session,
                'DELETE FROM stakes '
                'WHERE asset_id = :asset_id ',
                transaction
            )
    if transaction['receiver'] == 'simplemarket':
        try:
            try:
                memo_dict = json.loads(transaction['memo'])
            except Exception as err:
                return
            if 'price' not in memo_dict:
                return
            price_tag = memo_dict['price']
            price = float(price_tag.split(' ')[0])
            currency = price_tag.split(' ')[1]
            transaction['price'] = price
            transaction['currency'] = currency

            session_execute_logged(
                session,
                'INSERT INTO listings ('
                '   asset_ids, collection, seller, market, maker, price, currency, listing_id, seq, block_num, '
                '   timestamp, estimated_wax_price '
                ') '
                'SELECT array_agg(asset_id) AS asset_ids, collection, :sender, :receiver, NULL, :price, :currency, '
                'asset_id, :seq, :block_num, :timestamp, CASE WHEN :currency = \'WAX\' THEN :price '
                'ELSE :price * (SELECT usd FROM usd_prices ORDER BY timestamp DESC LIMIT 1) END '
                'FROM ('
                '   SELECT unnest(:asset_ids) AS asset_id '
                ') t LEFT JOIN assets a USING(asset_id) '
                'GROUP BY asset_id, collection ',
                transaction
            )
        except SQLAlchemyError as err:
            log_error('_insert_transfer: {}'.format(err))
            raise err
        except Exception as err:
            log_error('_insert_transfer: {}'.format(err))
            raise err
    elif transaction['sender'] == 'simplemarket' and transaction['seq'] < 429078747:
        try:
            for asset_id in transaction['asset_ids']:
                transaction['asset_id'] = asset_id
                session_execute_logged(
                    session,
                    'INSERT INTO removed_simplemarket_listings '
                    'SELECT l.*, :seq, :block_num FROM listings l '
                    'WHERE market = \'simplemarket\' AND l.listing_id = :asset_id '
                    'AND NOT EXISTS (SELECT sale_id FROM removed_simplemarket_listings WHERE sale_id = l.sale_id)',
                    transaction
                )
                session.commit()

                session_execute_logged(
                    session,
                    'INSERT INTO sales '
                    'SELECT l.asset_ids, a.collection, seller, :receiver, '
                    'CASE WHEN currency = \'WAX\' THEN price ELSE price / ('
                    '   SELECT usd FROM usd_prices WHERE timestamp < :timestamp ORDER BY timestamp DESC LIMIT 1'
                    ') END, CASE WHEN currency = \'USD\' THEN price ELSE price * ('
                    '   SELECT usd FROM usd_prices WHERE timestamp < :timestamp ORDER BY timestamp DESC LIMIT 1'
                    ') END, currency, :asset_id, l.market, NULL, NULL, :seq, :block_num, :timestamp '
                    'FROM listings l LEFT JOIN assets a ON asset_id = asset_ids[1] '
                    'WHERE market = \'simplemarket\' AND :asset_id = l.listing_id ',
                    transaction
                )
                session.commit()

            session_execute_logged(
                session,
                'DELETE FROM listings l WHERE sale_id IN ('
                '   SELECT sale_id FROM removed_simplemarket_listings WHERE removed_seq = :seq'
                ')',
                transaction
            )
        except SQLAlchemyError as err:
            log_error('_insert_transfer: {}'.format(err))
            raise err
        except Exception as err:
            log_error('_insert_transfer: {}'.format(err))
            raise err


@catch_and_log()
def load_drop(session, update, contract):
    new_drop = load_transaction_basics(update)
    data = _get_data(update)
    if 'drop_id' not in data or ('assets_to_mint' not in data and 'templates_to_mint' not in data and 'attributes' not in data):
        return
    new_drop['drop_id'] = data['drop_id']
    new_drop['collection'] = data['collection_name']
    new_drop['collection_name'] = data['collection_name']
    new_drop['display_data'] = data['display_data'] if 'display_data' in data else None
    new_drop['fee_rate'] = data['fee_rate'] if 'fee_rate' in data else 0
    new_drop['account_limit'] = data['account_limit'] if 'account_limit' in data else 0
    new_drop['account_limit_cooldown'] = data['account_limit_cooldown'] if 'account_limit_cooldown' in data else 0
    new_drop['max_claimable'] = data['max_claimable']
    new_drop['start_time'] = datetime.datetime.fromtimestamp(data['start_time']) if 'start_time' in data and data[
        'start_time'] else None
    new_drop['end_time'] = datetime.datetime.fromtimestamp(data['end_time']) if 'end_time' in data and data[
        'end_time'] else None
    new_drop['num_claimed'] = 0
    new_drop['auth_required'] = data['auth_required'] if 'auth_required' in data else False
    new_drop['is_hidden'] = data['is_hidden'] if 'is_hidden' in data else False
    new_drop['contract'] = contract
    new_drop['templates_to_mint'] = []
    new_drop['benefit_id'] = data['benefit_id'] if 'benefit_id' in data else None
    new_drop['game_id'] = data['game_id'] if 'game_id' in data else None
    if 'attributes' in data:
        new_drop['attributes'] = data['attributes']
    new_drop['blacklist'] = data['attributes'] if 'attributes' in data else None
    new_drop['name_pattern'] = data['name_pattern'] if 'name_pattern' in data else None
    new_drop['template_id'] = data['template_id'] if 'template_id' in data else None

    if 'assets_to_mint' in data:
        for asset in data['assets_to_mint']:
            new_drop['templates_to_mint'].append(asset['template_id'])
    elif 'templates_to_mint' in data:
        for template in data['templates_to_mint']:
            new_drop['templates_to_mint'].append(template)
    elif 'template_id' in data:
        new_drop['templates_to_mint'].append(data['template_id'])

    new_drop['price'] = None
    new_drop['currency'] = None
    if 'settlement_symbol' not in data or '0,NULL' == data['settlement_symbol']:
        new_drop['price'] = 0
        new_drop['currency'] = None
    else:
        lp = data['listing_price'].split(' ')
        new_drop['price'] = float(lp[0])
        new_drop['currency'] = lp[1]

    if 'attributes' in new_drop:
        attributes = {'attributes': new_drop['attributes']}
        if new_drop['blacklist']:
            new_drop['blacklist'] = json.dumps({'blacklist': new_drop['blacklist']})

        new_drop['attributes'] = json.dumps(attributes)
        session_execute_logged(
            session,
            'INSERT INTO pfp_drop_data (drop_id, contract, attributes, name_pattern) '
            'SELECT :drop_id, :contract, :attributes, :name_pattern '
            'WHERE NOT EXISTS ('
            '   SELECT drop_id, contract FROM pfp_drop_data WHERE drop_id = :drop_id AND contract = :contract'
            ') ',
            new_drop
        )

    if 'alternative_prices' in data:
        prices = [{
            'price': new_drop['price'],
            'currency': new_drop['currency']
        }]
        currencies = [new_drop['currency']]
        for price in data['alternative_prices']:
            prices.append({
                'price': float(price.split(' ')[0]),
                'currency': price.split(' ')[1]
            })
            currencies.append(price.split(' ')[1])

        new_drop['prices'] = json.dumps(prices)
        new_drop['currencies'] = currencies

        session_execute_logged(
            session,
           'INSERT INTO drop_log_prices ('
           '    drop_id, contract, prices, currencies, seq, block_num, timestamp'
           ') '
           'SELECT :drop_id, :contract, :prices, :currencies, :seq, :block_num, :timestamp '
           'WHERE NOT EXISTS (SELECT seq FROM drop_log_prices WHERE seq = :seq) ', new_drop
        )

    session_execute_logged(
        session,
        'INSERT INTO drops (drop_id, collection, price, currency, fee, display_data, '
        'start_time, end_time, max_claimable, num_claimed, contract, posted, seq, block_num,'
        'templates_to_mint, auth_required, is_hidden, timestamp, account_limit, account_limit_cooldown) '
        'SELECT :drop_id, :collection, :price, :currency, :fee_rate, :display_data, :start_time, :end_time, '
        ':max_claimable, :num_claimed, :contract, FALSE, :seq, :block_num, :templates_to_mint, '
        ':auth_required, :is_hidden, :timestamp, :account_limit, :account_limit_cooldown '
        'WHERE NOT EXISTS (SELECT seq FROM drops WHERE seq = :seq) ',
        new_drop
    )

    if new_drop['benefit_id'] and new_drop['game_id']:
        session_execute_logged(
            session,
            'INSERT INTO twitch_drops (drop_id, contract, seq, block_num, benefit_id, game_id) '
            'SELECT :drop_id, :contract, :seq, :block_num, :benefit_id, :game_id '
            'WHERE NOT EXISTS (SELECT seq FROM twitch_drops WHERE seq = :seq) ',
            new_drop
        )

    session.commit()


@catch_and_log()
def load_drop_update(session, update, contract):
    data = _get_data(update)

    drop = load_transaction_basics(update)

    drop['display_data'] = data['display_data']
    drop['drop_id'] = data['drop_id']
    drop['contract'] = contract

    session_execute_logged(
        session,
        'INSERT INTO drop_display_updates '
        '(seq, timestamp, block_num, contract, drop_id, new_display_data, old_display_data) '
        'SELECT :seq, :timestamp, :block_num, :contract, :drop_id, :display_data, (SELECT display_data '
        'FROM drops WHERE drop_id = :drop_id AND contract = :contract) '
        'WHERE NOT EXISTS (SELECT seq FROM drop_display_updates WHERE seq = :seq) ',
        drop
    )

    session.commit()

    session_execute_logged(
        session,
        'UPDATE drops d SET display_data = dd.new_display_data '
        'FROM drop_display_updates dd '
        'WHERE dd.seq = :seq AND d.drop_id = dd.drop_id AND d.contract = dd.contract',
        drop
    )


@catch_and_log()
def load_drop_limit_update(session, update, contract):
    data = _get_data(update)

    drop = load_transaction_basics(update)

    drop['account_limit'] = data['account_limit']
    drop['account_limit_cooldown'] = int(data['account_limit_cooldown'])
    drop['drop_id'] = data['drop_id']
    drop['contract'] = contract

    session_execute_logged(
        session,
        'INSERT INTO drop_limit_updates ('
        '   seq, timestamp, block_num, contract, drop_id, new_account_limit, new_account_limit_cooldown, '
        '   old_account_limit, old_account_limit_cooldown'
        ') '
        'SELECT :seq, :timestamp, :block_num, :contract, :drop_id, :account_limit, '
        ':account_limit_cooldown, '
        '(SELECT account_limit FROM drops WHERE drop_id = :drop_id AND contract = :contract), '
        '(SELECT account_limit_cooldown FROM drops WHERE drop_id = :drop_id AND contract = :contract) '
        'WHERE NOT EXISTS (SELECT seq FROM drop_limit_updates WHERE seq = :seq) ',
        drop
    )

    session.commit()

    session_execute_logged(
        session,
        'UPDATE drops d '
        'SET account_limit = new_account_limit, '
        'account_limit_cooldown = new_account_limit_cooldown '
        'FROM drop_limit_updates dl '
        'WHERE dl.seq = :seq AND d.drop_id = dl.drop_id AND d.contract = dl.contract ',
        drop
    )


@catch_and_log()
def load_drop_max_update(session, update, contract):
    data = _get_data(update)

    drop = load_transaction_basics(update)

    drop['max_claimable'] = data['new_max_claimable']
    drop['drop_id'] = data['drop_id']
    drop['contract'] = contract
    if len(drop['max_claimable']) > 19 and int(drop['max_claimable']) > 9223372036854775807:
        drop['max_claimable'] = 9223372036854775807

    session_execute_logged(
        session,
        'INSERT INTO drop_max_updates '
        '(seq, timestamp, block_num, contract, drop_id, new_max_claimable, old_max_claimable) '
        'SELECT :seq, :timestamp, :block_num, :contract, :drop_id, :max_claimable, '
        '(SELECT max_claimable FROM drops WHERE drop_id = :drop_id AND contract = :contract) '
        'WHERE NOT EXISTS (SELECT seq FROM drop_max_updates WHERE seq = :seq) ',
        drop
    )

    session.commit()

    session_execute_logged(
        session,
        'UPDATE drops d SET max_claimable = du.new_max_claimable '
        'FROM drop_max_updates du '
        'WHERE du.seq = :seq AND d.drop_id = du.drop_id AND d.contract = du.contract',
        drop
    )


@catch_and_log()
def load_drop_price_update(session, update, contract):
    data = _get_data(update)

    drop = load_transaction_basics(update)

    drop['drop_id'] = data['drop_id']
    drop['contract'] = contract

    listing_price_key = 'listing_prices'

    if listing_price_key not in data:
        listing_price_key = 'listing_price'

    if '0 NULL' == data[listing_price_key]:
        drop['price'] = 0
        drop['currency'] = None
    else:
        lp = data[listing_price_key].split(' ')
        drop['price'] = float(lp[0])
        drop['currency'] = lp[1]

    if 'alternative_prices' in data:
        prices = [{
            'price': drop['price'],
            'currency': drop['currency']
        }]
        currencies = [drop['currency']]
        for price in data['alternative_prices']:
            prices.append({
                'price': float(price.split(' ')[0]),
                'currency': price.split(' ')[1]
            })
            currencies.append(price.split(' ')[1])

        drop['prices'] = json.dumps(prices)
        drop['currencies'] = currencies

        session_execute_logged(
            session,
           'INSERT INTO drop_log_prices ('
           '    drop_id, contract, prices, currencies, seq, block_num, timestamp'
           ') '
           'SELECT :drop_id, :contract, :prices, :currencies, :seq, :block_num, :timestamp '
           'WHERE NOT EXISTS (SELECT seq FROM drop_log_prices WHERE seq = :seq) ', drop)

    session_execute_logged(
        session,
        'INSERT INTO drop_price_updates '
        '(seq, timestamp, block_num, contract, drop_id, new_price, new_currency, old_price, old_currency) '
        'SELECT :seq, :timestamp, :block_num, :contract, :drop_id, :price, :currency, '
        '(SELECT price FROM drops WHERE drop_id = :drop_id AND contract = :contract), '
        '(SELECT currency FROM drops WHERE drop_id = :drop_id AND contract = :contract) '
        'WHERE NOT EXISTS (SELECT seq FROM drop_price_updates WHERE seq = :seq) ',
        drop
    )

    session.commit()

    session_execute_logged(
        session,
        'UPDATE drops d SET price = du.new_price, currency = du.new_currency '
        'FROM drop_price_updates du '
        'WHERE du.seq = :seq AND d.drop_id = du.drop_id AND d.contract = du.contract',
        drop
    )


@catch_and_log()
def load_drop_prices_update(session, update, contract='nfthivedrops'):
    data = _get_data(update)

    drop = load_transaction_basics(update)

    drop['drop_id'] = data['drop_id']
    drop['contract'] = contract

    listing_prices = data['listing_prices']
    listing_price = listing_prices[0]
    if len(listing_price) == 1:
        listing_price = listing_prices

    if '0 NULL' == listing_price:
        drop['price'] = 0
        drop['currency'] = None
    else:
        lp = listing_price.split(' ')
        drop['price'] = float(lp[0])
        drop['currency'] = lp[1]

    session_execute_logged(
        session,
        'INSERT INTO drop_price_updates '
        '(seq, timestamp, block_num, contract, drop_id, new_price, new_currency, old_price, old_currency) '
        'SELECT :seq, :timestamp, :block_num, :contract, :drop_id, :price, :currency, '
        '(SELECT price FROM drops WHERE drop_id = :drop_id AND contract = :contract), '
        '(SELECT currency FROM drops WHERE drop_id = :drop_id AND contract = :contract) '
        'WHERE NOT EXISTS (SELECT seq FROM drop_price_updates WHERE seq = :seq) ',
        drop
    )

    session.commit()

    session_execute_logged(
        session,
        'UPDATE drops d SET price = du.new_price, currency = du.new_currency '
        'FROM drop_price_updates du '
        'WHERE du.seq = :seq AND d.drop_id = du.drop_id AND d.contract = du.contract',
        drop
    )


@catch_and_log()
def load_drop_fee_rate(session, update, contract):
    data = _get_data(update)

    drop = load_transaction_basics(update)

    drop['fee_rate'] = data['fee_rate'] if 'fee_rate' in data else data['fee']
    drop['drop_id'] = data['drop_id']
    drop['contract'] = contract

    session_execute_logged(
        session,
        'INSERT INTO drop_fee_updates (seq, timestamp, block_num, contract, drop_id, new_fee_rate, old_fee_rate) '
        'SELECT :seq, :timestamp, :block_num, :contract, :drop_id, :fee_rate, '
        '(SELECT fee FROM drops WHERE drop_id = :drop_id AND contract = :contract) '
        'WHERE NOT EXISTS (SELECT seq FROM drop_fee_updates WHERE seq = :seq) ',
        drop
    )

    session.commit()

    session_execute_logged(
        session,
        'UPDATE drops d SET fee = du.new_fee_rate '
        'FROM drop_fee_updates du '
        'WHERE du.seq = :seq AND d.drop_id = du.drop_id AND d.contract = du.contract',
        drop
    )


@catch_and_log()
def load_drop_drop_auth(session, update, contract):
    data = _get_data(update)

    drop = load_transaction_basics(update)

    drop['auth_required'] = data['auth_required']
    drop['drop_id'] = data['drop_id']
    drop['contract'] = contract

    session_execute_logged(
        session,
        'INSERT INTO drop_auth_updates (seq, timestamp, block_num, contract, drop_id, new_auth_required, '
        'old_auth_required) '
        'SELECT :seq, :timestamp, :block_num, :contract, :drop_id, :auth_required, '
        '(SELECT auth_required FROM drops WHERE drop_id = :drop_id AND contract = :contract) '
        'WHERE NOT EXISTS (SELECT seq FROM drop_auth_updates WHERE seq = :seq) ',
        drop
    )

    session.commit()

    session_execute_logged(
        session,
        'UPDATE drops d SET auth_required = du.new_auth_required '
        'FROM drop_auth_updates du '
        'WHERE du.seq = :seq AND d.drop_id = du.drop_id AND d.contract = du.contract',
        drop
    )


@catch_and_log()
def load_drop_hidden(session, update, contract):
    data = _get_data(update)

    drop = load_transaction_basics(update)

    drop['is_hidden'] = data['is_hidden']
    drop['drop_id'] = data['drop_id']
    drop['contract'] = contract

    session_execute_logged(
        session,
        'INSERT INTO drop_hidden_updates '
        '(seq, timestamp, block_num, contract, drop_id, new_is_hidden, old_is_hidden) '
        'SELECT :seq, :timestamp, :block_num, :contract, :drop_id, :is_hidden, '
        '(SELECT is_hidden FROM drops WHERE drop_id = :drop_id AND contract = :contract) '
        'WHERE NOT EXISTS (SELECT seq FROM drop_hidden_updates WHERE seq = :seq) ',
        drop
    )

    session.commit()

    session_execute_logged(
        session,
        'UPDATE drops d SET is_hidden = du.new_is_hidden '
        'FROM drop_hidden_updates du '
        'WHERE du.seq = :seq AND d.drop_id = du.drop_id AND d.contract = du.contract',
        drop
    )


@catch_and_log()
def load_drop_times_update(session, update, contract):
    data = _get_data(update)

    drop = load_transaction_basics(update)

    if 'start_time' not in data or 'end_time' not in data:
        return
    drop['start_time'] = datetime.datetime.fromtimestamp(data['start_time']) if data['start_time'] else None
    drop['end_time'] = datetime.datetime.fromtimestamp(data['end_time']) if data['end_time'] else None
    drop['drop_id'] = data['drop_id']
    drop['contract'] = contract

    session_execute_logged(
        session,
        'INSERT INTO drop_times_updates '
        '(seq, timestamp, block_num, contract, drop_id, new_start_time, new_end_time, old_start_time, '
        'old_end_time) '
        'SELECT :seq, :timestamp, :block_num, :contract, :drop_id, :start_time, :end_time, '
        '(SELECT start_time FROM drops WHERE drop_id = :drop_id AND contract = :contract), '
        '(SELECT end_time FROM drops WHERE drop_id = :drop_id AND contract = :contract) '
        'WHERE NOT EXISTS (SELECT seq FROM drop_times_updates WHERE seq = :seq) ',
        drop
    )

    session.commit()

    session_execute_logged(
        session,
        'UPDATE drops d SET start_time = du.new_start_time, end_time = du.new_end_time '
        'FROM drop_times_updates du '
        'WHERE du.seq = :seq AND d.drop_id = du.drop_id AND d.contract = du.contract',
        drop
    )


@catch_and_log()
def load_claim_drop(session, transfer, contract):
    try:
        data = _get_data(transfer)
        if 'drop_id' not in data:
            return
        new_transfer = load_transaction_basics(transfer)
        new_transfer['claimer'] = data['claimer']
        new_transfer['drop_id'] = data['drop_id']
        new_transfer['amount'] = data['claim_amount'] if 'claim_amount' in data else data['amount'] if 'amount' in data else 1
        new_transfer['wax_usd'] = int(data['intended_delphi_median']) * 0.0001 if 'intended_delphi_median' in data else 0
        new_transfer['contract'] = contract
        new_transfer['country'] = data['country'][0:11] if 'country' in data else None
        new_transfer['referrer'] = data['referrer'][0:11] if 'referrer' in data else None
        new_transfer['currency'] = data['currency'][0:11].replace("\x00", "") if 'currency' in data and data['currency'] else None

        new_transfer['benefit_id'] = data['benefit_id'] if 'benefit_id' in data else None
        new_transfer['reward_id'] = data['reward_id'] if 'reward_id' in data else None
        new_transfer['reward_string'] = data['reward_string'] if 'reward_string' in data else None

        session_execute_logged(
            session,
            'INSERT INTO drop_claims ('
            '   drop_id, contract, claimer, country, referrer, amount, currency, seq, block_num, timestamp'
            ') '
            'SELECT :drop_id, :contract, :claimer, :country, :referrer, :amount, :currency, :seq, :block_num, :timestamp '
            'WHERE NOT EXISTS (SELECT seq FROM drop_claims WHERE seq = :seq)',
            new_transfer
        )

        if new_transfer['benefit_id']:
            session_execute_logged(
                session,
                'INSERT INTO twitch_claims ('
                '   seq, timestamp, block_num, drop_id, claimer, contract, benefit_id, reward_id, reward_string'
                ') '
                'SELECT :seq, :timestamp, :block_num, :drop_id, :claimer, :contract, :benefit_id, '
                ':reward_id, :reward_string '
                'WHERE NOT EXISTS (SELECT seq FROM twitch_claims WHERE seq = :seq)',
                new_transfer
            )
    except SQLAlchemyError as err:
        log_error('{}'.format(err))
        log_exception(err)
        raise err
    except Exception as err:
        log_error('{}'.format(err))
        log_exception(err)
        raise err


@catch_and_log()
def load_erase_drop(session, transfer, contract):
    data = _get_data(transfer)
    new_transfer = load_transaction_basics(transfer)
    new_transfer['drop_id'] = data['drop_id']
    new_transfer['contract'] = contract

    session_execute_logged(
        session,
        'INSERT INTO drop_erase_updates (seq, timestamp, block_num, drop_id, erased, contract) '
        'SELECT :seq, :timestamp, :block_num, :drop_id, true, :contract '
        'WHERE NOT EXISTS (SELECT seq FROM drop_erase_updates WHERE seq = :seq)',
        new_transfer
    )

    session.commit()

    session_execute_logged(
        session,
        'UPDATE drops d SET erased = TRUE '
        'FROM drop_erase_updates du '
        'WHERE du.seq = :seq AND d.drop_id = du.drop_id AND d.contract = du.contract',
        new_transfer
    )


@catch_and_log()
def load_addconftoken(session, transaction):
    data = _get_data(transaction)

    new_token = load_transaction_basics(transaction)

    new_token['contract'] = data['token_contract']
    new_token['symbol'] = data['token_symbol'].split(',')[1]
    new_token['decimals'] = data['token_symbol'].split(',')[0]

    session_execute_logged(
        session,
        'INSERT INTO drop_token_actions (seq, timestamp, block_num, contract, symbol, decimals, action) '
        'SELECT :seq, :timestamp, :block_num, :contract, :symbol, :decimals, :action_name '
        'WHERE NOT EXISTS (SELECT seq FROM drop_token_actions WHERE seq = :seq) ',
        new_token
    )


@catch_and_log()
def load_remconftoken(session, transaction):
    data = _get_data(transaction)

    new_token = load_transaction_basics(transaction)

    new_token['contract'] = data['token_contract']
    new_token['symbol'] = data['token_symbol'].split(',')[1]
    new_token['decimals'] = data['token_symbol'].split(',')[0]

    session_execute_logged(
        session,
        'INSERT INTO drop_token_actions (seq, timestamp, block_num, contract, symbol, decimals, action) '
        'SELECT :seq, :timestamp, :block_num, :contract, :symbol, :decimals, :action_name '
        'WHERE NOT EXISTS (SELECT seq FROM drop_token_actions WHERE seq = :seq) ',
        new_token
    )


@catch_and_log()
def add_pfp_result(session, transfer):
    data = _get_data(transfer)
    new_transfer = load_transaction_basics(transfer)
    if 'result_id' not in data or 'drop_id' not in data:
        return

    new_transfer['claimer'] = data['claimer']
    new_transfer['drop_id'] = data['drop_id']
    new_transfer['results'] = json.dumps(data['results'])
    new_transfer['result_id'] = data['result_id']

    session_execute_logged(
        session,
        'INSERT INTO pfp_results (drop_id, claimer, results, result_id, seq, block_num, timestamp, name) '
        'SELECT :drop_id, :claimer, :results, :result_id, :seq, :block_num, :timestamp, NULL '
        'WHERE NOT EXISTS (SELECT seq FROM pfp_results WHERE seq = :seq) ',
        new_transfer
    )

    session.commit()


@catch_and_log()
def load_add_reward(session, transfer):
    data = _get_data(transfer)
    new_transfer = load_transaction_basics(transfer)
    new_transfer['id'] = data['reward_string']

    session_execute_logged(
        session,
        'UPDATE twitch_benefits SET pushed = TRUE WHERE id = :id',
        new_transfer
    )


@catch_and_log()
def load_mint_pfp(session, mint):
    data = _get_data(mint)
    result_id = data['result_id']

    transaction = load_transaction_basics(mint)
    transaction['result_id'] = result_id
    transaction['drop_id'] = data['drop_id']
    transaction['owner'] = data['owner']

    session_execute_logged(
        session,
        'INSERT INTO pfp_mints SELECT :result_id, :drop_id, :owner, :seq, :block_num, :timestamp '
        'WHERE NOT EXISTS (SELECT seq FROM pfp_mints WHERE seq = :seq)',
        transaction
    )


@catch_and_log()
def add_swap_pfp(session, transfer):
    data = _get_data(transfer)
    new_transfer = load_transaction_basics(transfer)
    new_transfer['claimer'] = data['owner']
    new_transfer['asset_id'] = data['asset_id']
    new_transfer['result_id'] = data['result_id']

    session_execute_logged(
        session,
        'INSERT INTO pfp_swap_results (drop_id, claimer, results, result_id, seq, block_num, timestamp) '
        'SELECT drop_id, :claimer, results, :result_id, :seq, :block_num, :timestamp '
        'FROM pfp_results p '
        'WHERE NOT EXISTS (SELECT seq FROM pfp_swap_results WHERE seq = :seq) AND p.result_id = :result_id ',
        new_transfer
    )


@catch_and_log()
def load_remint_pfp(session, mint):
    data = _get_data(mint)
    transaction = load_transaction_basics(mint)
    transaction['result_id'] = data['result_id']
    transaction['drop_id'] = data['drop_id']
    transaction['asset_id'] = data['asset_id']
    transaction['owner'] = data['owner']
    transaction['hash'] = data['hash']

    session_execute_logged(
        session,
        'INSERT INTO pfp_swap_mints SELECT :result_id, :drop_id, :asset_id, :owner, :hash, '
        ':seq, :block_num, :timestamp '
        'WHERE NOT EXISTS (SELECT seq FROM pfp_swap_mints WHERE seq = :seq)',
        transaction
    )


@catch_and_log()
def load_logprices(session, update, contract):
    data = _get_data(update)

    drop = load_transaction_basics(update)

    drop['drop_id'] = data['drop_id']
    drop['contract'] = contract
    prices = []
    currencies = []
    for price in data['listing_prices']:
        prices.append({
            'price': float(price.split(' ')[0]),
            'currency': price.split(' ')[1]
        })
        currencies.append(price.split(' ')[1])

    drop['prices'] = json.dumps(prices)
    drop['currencies'] = currencies

    session_execute_logged(
        session,
        'INSERT INTO drop_log_prices (drop_id, contract, prices, currencies, seq, block_num, timestamp) '
        'SELECT :drop_id, :contract, :prices, :currencies, :seq, :block_num, :timestamp '
        'WHERE NOT EXISTS (SELECT seq FROM drop_log_prices WHERE seq = :seq) ', drop)


@catch_and_log()
def load_atomic_market_buy(session, transaction):
    data = _get_data(transaction)

    new_sale = load_transaction_basics(transaction)

    new_sale['buyer'] = data['buyer']
    new_sale['sale_id'] = int(data['sale_id'])
    new_sale['taker'] = data['taker_marketplace'] if data['taker_marketplace'] else None

    session_execute_logged(
        session,
        'INSERT INTO atomicmarket_purchases (buyer, block_num, seq, timestamp, listing_id, taker) '
        'SELECT :buyer, :block_num, :seq, :timestamp, :sale_id, :taker '
        'WHERE :seq NOT IN (SELECT seq FROM atomicmarket_purchases WHERE seq = :seq) ',
        new_sale
    )

    session_execute_logged(
        session,
        'INSERT INTO sales '
        'SELECT asset_ids, a.collection, seller, :buyer, '
        'CASE WHEN currency = \'WAX\' THEN price ELSE price / ('
        '   SELECT usd FROM usd_prices WHERE timestamp < :timestamp ORDER BY timestamp DESC LIMIT 1'
        ') END, CASE WHEN currency = \'USD\' THEN price ELSE price * ('
        '   SELECT usd FROM usd_prices WHERE timestamp < :timestamp ORDER BY timestamp DESC LIMIT 1'
        ') END, currency, :sale_id, \'atomicmarket\', maker, :taker, '
        ':seq, :block_num, :timestamp '
        'FROM atomicmarket_listings l LEFT JOIN assets a ON a.asset_id = l.asset_ids[1] '
        'WHERE l.listing_id = :sale_id',
        new_sale
    )

    session_execute_logged(
        session,
        'INSERT INTO removed_atomic_listings '
        'SELECT l.*, :seq, :block_num FROM listings l '
        'WHERE market = \'atomicmarket\' AND listing_id = :sale_id ',
        new_sale
    )
    session.commit()

    session_execute_logged(
        session,
        'DELETE FROM listings l WHERE sale_id IN ('
        '   SELECT sale_id FROM removed_atomic_listings WHERE removed_seq = :seq'
        ')',
        new_sale
    )
    session.commit()


@catch_and_log()
def load_atomic_market_cancel(session, transaction):
    data = _get_data(transaction)

    new_sale = load_transaction_basics(transaction)

    new_sale['sale_id'] = int(data['sale_id'])

    session_execute_logged(
        session,
        'INSERT INTO atomicmarket_cancels (block_num, seq, timestamp, listing_id) '
        'SELECT :block_num, :seq, :timestamp, :sale_id '
        'WHERE NOT EXISTS (SELECT seq FROM atomicmarket_cancels WHERE seq = :seq) ',
        new_sale
    )
    session.commit()

    session_execute_logged(
        session,
        'INSERT INTO removed_atomic_listings '
        'SELECT l.*, :seq, :block_num FROM listings l '
        'WHERE market = \'atomicmarket\' AND listing_id = :sale_id ',
        new_sale
    )
    session.commit()

    session_execute_logged(
        session,
        'DELETE FROM listings l WHERE sale_id IN ('
        '   SELECT sale_id FROM removed_atomic_listings WHERE removed_seq = :seq'
        ')',
        new_sale
    )
    session.commit()


@catch_and_log()
def load_atomic_market_sale(session, transaction):
    data = _get_data(transaction)

    asset_ids = []
    for asset_id in data['asset_ids']:
        asset_ids.append(int(asset_id))

    new_sale = load_transaction_basics(transaction)
    new_sale['asset_ids'] = asset_ids
    new_sale['seller'] = data['seller']
    new_sale['price'] = float(data['listing_price'].split(' ')[0])
    new_sale['currency'] = data['listing_price'].split(' ')[1]
    new_sale['listing_id'] = data['sale_id']
    new_sale['maker'] = data['maker_marketplace'] if data['maker_marketplace'] else None

    session_execute_logged(
        session,
        'INSERT INTO atomicmarket_listings '
        'SELECT :asset_ids, :seller, :price, :currency, :listing_id, :maker, :seq, :block_num, :timestamp '
        'WHERE NOT EXISTS (SELECT seq FROM atomicmarket_listings WHERE seq = :seq)',
        new_sale
    )


@catch_and_log()
def load_atomic_market_cancel_auct(session, transaction):
    data = _get_data(transaction)
    new_sale = load_transaction_basics(transaction)

    new_sale['auction_id'] = int(data['auction_id'])

    session_execute_logged(
        session,
        'INSERT INTO atomicmarket_auction_cancels '
        'SELECT :auction_id, :seq, :block_num, :timestamp '
        'WHERE NOT EXISTS (SELECT seq FROM atomicmarket_auction_cancels WHERE seq = :seq)',
        new_sale
    )

    session_execute_logged(
        session,
        'INSERT INTO removed_atomicmarket_auctions '
        'SELECT au.*, :seq, :block_num FROM auctions au WHERE auction_id = :auction_id '
        'AND NOT EXISTS (SELECT seq FROM removed_atomicmarket_auctions WHERE removed_seq = :seq)',
        new_sale
    )

    session_execute_logged(
        session,
        'DELETE FROM auctions WHERE auction_id = :auction_id',
        new_sale
    )


@catch_and_log()
def load_atomic_market_auct_bid(session, transaction):
    data = _get_data(transaction)

    new_sale = load_transaction_basics(transaction)

    new_sale['taker'] = data['taker_marketplace']
    new_sale['bidder'] = data['bidder']
    new_sale['auction_id'] = int(data['auction_id'])
    new_sale['bid'] = float(data['bid'].split(' ')[0])
    new_sale['currency'] = data['bid'].split(' ')[1]

    session_execute_logged(
        session,
        'INSERT INTO auction_bids '
        'SELECT :auction_id, :bidder, bidder, :bid, current_bid, :currency, currency, :taker, \'atomicmarket\', :seq, '
        ':block_num, :timestamp FROM auctions WHERE auction_id = :auction_id '
        'AND NOT EXISTS (SELECT seq FROM auction_bids WHERE seq = :seq)', new_sale
    )

    session_execute_logged(
        session,
        'UPDATE auctions SET current_bid = :bid, bidder = :bidder, currency = :currency '
        'WHERE auction_id = :auction_id AND market = \'atomicmarket\'',
        new_sale
    )


@catch_and_log()
def load_atomic_market_auct(session, transaction):
    data = _get_data(transaction)

    new_sale = load_transaction_basics(transaction)

    asset_ids = []
    for asset_id in data['asset_ids']:
        asset_ids.append(int(asset_id))
    new_sale['auction_id'] = data['auction_id']
    new_sale['asset_ids'] = asset_ids
    new_sale['seller'] = data['seller']
    new_sale['market'] = 'atomicmarket'
    new_sale['start_bid'] = float(data['starting_bid'].split(' ')[0])
    new_sale['end_time'] = datetime.datetime.fromtimestamp(data['end_time'], tz=pytz.UTC)
    new_sale['current_bid'] = new_sale['start_bid']
    new_sale['currency'] = data['starting_bid'].split(' ')[1]
    new_sale['maker'] = data['maker_marketplace'] if data['maker_marketplace'] else None
    new_sale['collection'] = data['collection_name']

    session_execute_logged(
        session,
        'INSERT INTO auction_logs '
        'SELECT :auction_id, :asset_ids, :collection, :seller, NULL, :end_time, :start_bid, :current_bid, :currency, '
        ':maker, :market, FALSE, :seq, :block_num, :timestamp '
        'WHERE NOT EXISTS (SELECT seq FROM auction_logs WHERE seq = :seq)',
        new_sale
    )

    session_execute_logged(
        session,
        'INSERT INTO auctions '
        'SELECT * FROM auction_logs WHERE seq = :seq '
        'AND NOT EXISTS (SELECT seq FROM auctions WHERE seq = :seq)',
        new_sale
    )


@catch_and_log()
def load_atomic_market_claim_auct(session, transaction):
    data = _get_data(transaction)

    new_sale = load_transaction_basics(transaction)

    new_sale['auction_id'] = int(data['auction_id'])
    new_sale['market'] = 'atomicmarket'
    new_sale['claimer'] = transaction['act']['authorization'][0]['actor']

    session_execute_logged(
        session,
        'INSERT INTO auction_claims '
        'SELECT :auction_id, :market, :claimer, :seq, :block_num, :timestamp '
        'WHERE NOT EXISTS (SELECT seq FROM auction_claims WHERE seq = :seq)',
        new_sale
    )

    session_execute_logged(
        session,
        'INSERT INTO claimed_auctions '
        'SELECT auction_id, asset_ids, seller, claimer, market, maker, taker, MAX(bid) AS final_bid, '
        'au.currency, ac.seq, ac.block_num, ac.timestamp '
        'FROM auction_claims ac '
        'LEFT JOIN auction_logs au USING (auction_id, market) '
        'LEFT JOIN auction_bids ab USING (auction_id, market) '
        'WHERE ac.seq = :seq AND NOT EXISTS (SELECT seq FROM claimed_auctions WHERE seq = :seq)'
        'GROUP BY 1, 2, 3, 4, 5, 6, 7, 9, 10, 11, 12',
        new_sale
    )

    session_execute_logged(
        session,
        'INSERT INTO removed_atomicmarket_auctions '
        'SELECT au.*, :seq, :block_num FROM auctions au LEFT JOIN auction_claims ac USING(auction_id) '
        'WHERE auction_id = ac.auction_id AND ac.seq = :seq '
        'AND NOT EXISTS (SELECT seq FROM removed_atomicmarket_auctions WHERE removed_seq = :seq)',
        new_sale
    )

    session_execute_logged(
        session,
        'DELETE FROM auctions WHERE auction_id = :auction_id',
        new_sale
    )


@catch_and_log()
def load_atomic_market_cancel_buy_offer(session, transaction):
    data = _get_data(transaction)

    new_sale = load_transaction_basics(transaction)

    new_sale['buyoffer_id'] = int(data['buyoffer_id'])

    session_execute_logged(
        session,
        'INSERT INTO atomicmarket_cancel_buy_offers '
        'SELECT :buyoffer_id, :seq, :block_num, :timestamp '
        'WHERE NOT EXISTS (SELECT seq FROM atomicmarket_cancel_buy_offers WHERE seq = :seq)',
        new_sale
    )

    session_execute_logged(
        session,
        'INSERT INTO removed_atomicmarket_buy_offers '
        'SELECT a.*, :seq, :block_num FROM atomicmarket_buy_offers a '
        'WHERE buyoffer_id = :buyoffer_id '
        'AND NOT EXISTS ('
        '   SELECT buyoffer_id FROM removed_atomicmarket_buy_offers WHERE buyoffer_id = :buyoffer_id'
        ')',
        new_sale
    )

    session_execute_logged(
        session,
        'DELETE FROM atomicmarket_buy_offers '
        'WHERE buyoffer_id = :buyoffer_id',
        new_sale
    )


@catch_and_log()
def load_atomic_market_accept_buy_offer(session, transaction):
    data = _get_data(transaction)

    new_sale = load_transaction_basics(transaction)

    new_sale['buyoffer_id'] = int(data['buyoffer_id'])
    assets = data['expected_asset_ids']
    asset_ids = []

    for asset in assets:
        asset_ids.append(int(asset))
    new_sale['expected_asset_ids'] = asset_ids

    new_sale['expected_price'] = float(data['expected_price'].split(' ')[0])
    new_sale['taker_marketplace'] = data['taker_marketplace']

    session_execute_logged(
        session,
        'INSERT INTO atomicmarket_accept_buy_offers '
        'SELECT :buyoffer_id, :expected_asset_ids, :expected_price, :taker_marketplace, :seq, :block_num, '
        ':timestamp '
        'WHERE NOT EXISTS (SELECT seq FROM atomicmarket_accept_buy_offers WHERE seq = :seq)', new_sale
    )

    session_execute_logged(
        session,
        'INSERT INTO removed_atomicmarket_buy_offers '
        'SELECT * FROM atomicmarket_buy_offers '
        'WHERE buyoffer_id = :buyoffer_id '
        'AND NOT EXISTS ('
        '   SELECT buyoffer_id FROM removed_atomicmarket_buy_offers WHERE buyoffer_id = :buyoffer_id'
        ')',
        new_sale
    )

    session_execute_logged(
        session,
        'DELETE FROM atomicmarket_buy_offers '
        'WHERE buyoffer_id = :buyoffer_id',
        new_sale
    )


@catch_and_log()
def load_atomic_market_decline_buy_offer(session, transaction):
    data = _get_data(transaction)

    new_sale = load_transaction_basics(transaction)

    new_sale['buyoffer_id'] = int(data['buyoffer_id'])
    new_sale['market'] = 'atomicmarket'
    new_sale['claimer'] = transaction['act']['authorization'][0]['actor']
    new_sale['memo'] = data['decline_memo'][0:255]

    with_clause = ''
    if new_sale['memo']:
        with_clause = (
            'WITH insert_result AS (INSERT INTO memos (memo) SELECT :memo WHERE NOT EXISTS ('
            'SELECT memo FROM memos WHERE md5(memo) = md5(:memo)) RETURNING memo_id) '
        )

    session_execute_logged(
        session,
        '{with_clause} '
        'INSERT INTO atomicmarket_decline_buy_offers '
        'SELECT :buyoffer_id, {memo_column}, :seq, :block_num, :timestamp '
        'WHERE NOT EXISTS ('
        '   SELECT buyoffer_id FROM atomicmarket_decline_buy_offers WHERE buyoffer_id = :buyoffer_id'
        ')'.format(
            with_clause=with_clause,
            memo_column=(
                '(SELECT memo_id FROM memos WHERE md5(memo) = md5(:memo) UNION SELECT memo_id FROM insert_result)'
            ) if 'memo' in new_sale and new_sale['memo'] else 'NULL'
        ), new_sale
    )

    session_execute_logged(
        session,
        'INSERT INTO removed_atomicmarket_buy_offers '
        'SELECT * FROM atomicmarket_buy_offers '
        'WHERE buyoffer_id = :buyoffer_id '
        'AND NOT EXISTS ('
        '   SELECT buyoffer_id FROM removed_atomicmarket_buy_offers WHERE buyoffer_id = :buyoffer_id'
        ')',
        new_sale
    )

    session_execute_logged(
        session,
        'DELETE FROM atomicmarket_buy_offers '
        'WHERE buyoffer_id = :buyoffer_id',
        new_sale
    )


@catch_and_log()
def load_atomic_market_log_new_buy_offer(session, transaction):
    data = _get_data(transaction)

    new_sale = load_transaction_basics(transaction)

    new_sale['buyoffer_id'] = int(data['buyoffer_id'])
    new_sale['buyer'] = data['buyer']
    new_sale['recipient'] = data['recipient']
    new_sale['price'] = float(data['price'].split(' ')[0])
    new_sale['currency'] = data['price'].split(' ')[1]
    assets = data['asset_ids']
    asset_ids = []
    for asset in assets:
        asset_ids.append(int(asset))
    new_sale['asset_ids'] = asset_ids

    new_sale['memo'] = data['memo'][0:255]

    with_clause = construct_memo_clause(data)

    new_sale['maker_marketplace'] = data['maker_marketplace']
    new_sale['collection_name'] = data['collection_name']

    new_sale['collection_fee'] = float(data['collection_fee'])

    session_execute_logged(
        session,
        '{with_clause} '
        'INSERT INTO atomicmarket_buy_offers_listings '
        'SELECT :buyoffer_id, :buyer, :recipient, :price, :currency, :asset_ids, {memo_column}, '
        ':maker_marketplace, :collection_name, :collection_fee, :seq, :block_num, :timestamp '
        'WHERE NOT EXISTS ('
        '   SELECT buyoffer_id FROM atomicmarket_buy_offers_listings WHERE buyoffer_id = :buyoffer_id'
        ') '
        'AND NOT EXISTS ('
        '   SELECT buyoffer_id FROM removed_atomicmarket_buy_offers WHERE buyoffer_id = :buyoffer_id'
        ')'.format(
            with_clause=with_clause,
            memo_column=(
                '(SELECT memo_id FROM memos WHERE md5(memo) = md5(:memo) UNION SELECT memo_id FROM insert_result)'
            ) if 'memo' in new_sale and new_sale['memo'] else 'NULL'
        ), new_sale
    )

    session.commit()

    session_execute_logged(
        session,
        'INSERT INTO atomicmarket_buy_offers '
        'SELECT * FROM atomicmarket_buy_offers_listings WHERE seq = :seq '
        'AND NOT EXISTS ('
        '   SELECT buyoffer_id FROM atomicmarket_buy_offers WHERE buyoffer_id = :buyoffer_id'
        ') '
        'AND NOT EXISTS ('
        '   SELECT buyoffer_id FROM removed_atomicmarket_buy_offers WHERE buyoffer_id = :buyoffer_id'
        ')',
        new_sale
    )


@catch_and_log()
def load_atomic_market_sale_start(session, transaction):
    data = _get_data(transaction)

    new_sale = load_transaction_basics(transaction)

    new_sale['listing_id'] = int(data['sale_id'])
    new_sale['offer_id'] = int(data['offer_id'])

    session_execute_logged(
        session,
        'INSERT INTO atomicmarket_sale_starts '
        'SELECT :listing_id, :offer_id, :seq, :block_num, :timestamp '
        'WHERE NOT EXISTS (SELECT seq FROM atomicmarket_sale_starts WHERE seq = :seq)', new_sale
    )
    session_execute_logged(
        session,
        'INSERT INTO listings ('
        '   asset_ids, collection, seller, market, maker, price, currency, listing_id, seq, block_num, timestamp, '
        '   estimated_wax_price '
        ') '
        'SELECT asset_ids[\:99], collection, seller, \'atomicmarket\', maker, price, currency, listing_id, s.seq, '
        's.block_num, s.timestamp, CASE WHEN currency = \'WAX\' THEN price ELSE '
        '(price / (SELECT usd FROM usd_prices ORDER BY timestamp DESC LIMIT 1)) END '
        'FROM atomicmarket_sale_starts s '
        'INNER JOIN atomicmarket_listings l USING(listing_id) '
        'INNER JOIN assets a ON a.asset_id = ANY(asset_ids) '
        'WHERE s.seq = :seq GROUP BY 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11 ',
        new_sale
    )
    session.commit()


@catch_and_log()
def load_atomic_market_cancel_template_buyo(session, transaction):
    data = _get_data(transaction)

    new_sale = load_transaction_basics(transaction)

    new_sale['buyoffer_id'] = int(data['buyoffer_id'])

    session_execute_logged(
        session,
        'INSERT INTO atomicmarket_cancel_template_buy_offers '
        'SELECT :buyoffer_id, :seq, :block_num, :timestamp '
        'WHERE NOT EXISTS (SELECT seq FROM atomicmarket_cancel_template_buy_offers WHERE seq = :seq)',
        new_sale
    )

    session_execute_logged(
        session,
        'INSERT INTO removed_atomicmarket_template_buy_offers '
        'SELECT a.*, :seq, :block_num FROM atomicmarket_template_buy_offers a '
        'WHERE buyoffer_id = :buyoffer_id '
        'AND NOT EXISTS ('
        '   SELECT buyoffer_id FROM removed_atomicmarket_template_buy_offers WHERE buyoffer_id = :buyoffer_id'
        ')',
        new_sale
    )

    session_execute_logged(
        session,
        'DELETE FROM atomicmarket_template_buy_offers '
        'WHERE buyoffer_id = :buyoffer_id',
        new_sale
    )


@catch_and_log()
def load_atomic_market_fulfill_template_buyo(session, transaction):
    data = _get_data(transaction)

    new_sale = load_transaction_basics(transaction)

    new_sale['buyoffer_id'] = int(data['buyoffer_id'])

    new_sale['expected_price'] = float(data['expected_price'].split(' ')[0])
    new_sale['currency'] = data['expected_price'].split(' ')[1]
    new_sale['seller'] = data['seller']
    new_sale['asset_id'] = data['asset_id']
    new_sale['taker_marketplace'] = data['taker_marketplace']

    session_execute_logged(
        session,
        'INSERT INTO atomicmarket_fulfill_template_buy_offers '
        'SELECT :buyoffer_id, :asset_id, :seller, :expected_price, :currency, :taker_marketplace, '
        ':seq, :block_num, :timestamp '
        'WHERE NOT EXISTS ('
        '   SELECT seq FROM atomicmarket_fulfill_template_buy_offers WHERE seq = :seq'
        ')',
        new_sale
    )
    session.commit()

    session_execute_logged(
        session,
        'INSERT INTO removed_atomicmarket_template_buy_offers '
        'SELECT * FROM atomicmarket_template_buy_offers '
        'WHERE buyoffer_id = :buyoffer_id '
        'AND NOT EXISTS ('
        '   SELECT buyoffer_id FROM removed_atomicmarket_template_buy_offers WHERE buyoffer_id = :buyoffer_id'
        ')',
        new_sale
    )

    session_execute_logged(
        session,
        'INSERT INTO sold_atomicmarket_template_buy_offers '
        'SELECT buyoffer_id, buyer, price, currency, template_id, maker, :taker_marketplace, collection, '
        'collection_fee, seq, block_num, timestamp '
        'FROM atomicmarket_template_buy_offers '
        'WHERE buyoffer_id = :buyoffer_id '
        'AND NOT EXISTS ('
        '   SELECT buyoffer_id FROM sold_atomicmarket_template_buy_offers WHERE buyoffer_id = :buyoffer_id'
        ')',
        new_sale
    )

    session_execute_logged(
        session,
        'DELETE FROM atomicmarket_template_buy_offers '
        'WHERE buyoffer_id = :buyoffer_id',
        new_sale
    )


@catch_and_log()
def load_atomic_market_lognew_template_buyo(session, transaction):
    data = _get_data(transaction)

    new_sale = load_transaction_basics(transaction)

    new_sale['buyoffer_id'] = int(data['buyoffer_id'])
    new_sale['buyer'] = data['buyer']
    new_sale['price'] = float(data['price'].split(' ')[0])
    new_sale['currency'] = data['price'].split(' ')[1]
    new_sale['template_id'] = data['template_id']

    new_sale['maker_marketplace'] = data['maker_marketplace']
    new_sale['collection_name'] = data['collection_name']

    new_sale['collection_fee'] = float(data['collection_fee'])

    session_execute_logged(
        session,
        'INSERT INTO atomicmarket_template_buy_offer_listings '
        'SELECT :buyoffer_id, :buyer, :price, :currency, :template_id, :maker_marketplace,'
        ':collection_name, :collection_fee, :seq, :block_num, :timestamp '
        'WHERE NOT EXISTS ('
        '   SELECT buyoffer_id FROM atomicmarket_template_buy_offer_listings WHERE buyoffer_id = :buyoffer_id'
        ')'
        'AND NOT EXISTS ('
        '   SELECT buyoffer_id FROM removed_atomicmarket_template_buy_offers WHERE buyoffer_id = :buyoffer_id'
        ')',
        new_sale
    )

    session_execute_logged(
        session,
        'INSERT INTO atomicmarket_template_buy_offers '
        'SELECT * FROM atomicmarket_template_buy_offer_listings '
        'WHERE seq = :seq '
        'AND NOT EXISTS (SELECT buyoffer_id FROM atomicmarket_template_buy_offers WHERE buyoffer_id = :buyoffer_id) '
        'AND NOT EXISTS (SELECT buyoffer_id FROM removed_atomicmarket_template_buy_offers WHERE buyoffer_id = :buyoffer_id) ',
        new_sale
    )


@catch_and_log()
def insert_atomic_asset(session, action):
    asset = _get_data(action)
    new_asset = load_transaction_basics(action)

    asset_id = asset['asset_id']
    new_asset['contract'] = 'atomicassets'
    new_asset['template_id'] = asset['template_id'] if 'template_id' in asset.keys() else None
    new_asset['burnable'] = True
    new_asset['transferable'] = True
    new_asset['asset_id'] = asset_id

    if 'collection_name' not in asset:
        return

    new_asset['owner'] = asset['new_asset_owner'] if 'new_asset_owner' in asset else asset['new_owner']
    data = parse_data(
        asset['immutable_template_data']
    ) if 'immutable_template_data' in asset else {}
    if 'immutable_data' in asset:
        data.update(parse_data(asset['immutable_data']))
    if 'mutable_data' in asset:
        data.update(parse_data(asset['mutable_data']))

    new_asset['name'] = data['name'].strip()[0:255] if 'name' in data.keys() else None
    new_asset['collection'] = asset['collection_name'] if 'collection_name' in asset else None

    if 'schema_name' not in asset:
        return
    new_asset['schema'] = asset['schema_name']

    new_asset['image'] = data['img'] if 'img' in data.keys() else None

    new_asset['video'] = data['video'] if 'video' in data.keys() else None

    new_asset['image'] = str(new_asset['image']).strip()[0:255] if new_asset['image'] else None

    new_asset['video'] = str(new_asset['video']).strip()[0:255] if new_asset['video'] else None

    new_asset['attribute_ids'] = parse_attributes(session, new_asset['collection'], new_asset['schema'], data)

    new_asset['idata'] = json.dumps(asset['immutable_data'])
    new_asset['mdata'] = json.dumps(asset['mutable_data'])

    with_clause = construct_with_clause(new_asset)

    mdata_column = construct_mdata_column(new_asset)

    session_execute_logged(
        session,
        '{with_clause} '
        'INSERT INTO assets '
        '(asset_id, contract, collection, schema, owner, template_id, name_id, image_id, video_id, '
        'block_num, seq, timestamp, burnable, transferable, attribute_ids, immutable_data_id, mutable_data_id) '
        'SELECT :asset_id, :contract, :collection, :schema, :owner, :template_id, '
        '{name_column}, '
        '{image_column}, '
        '{video_column}, '
        ':block_num, :seq, :timestamp, :burnable, :transferable, :attribute_ids, '
        '{idata_column}, '
        '{mdata_column} '
        'WHERE NOT EXISTS (SELECT asset_id FROM assets WHERE asset_id = :asset_id) '.format(
            with_clause=with_clause,
            name_column=(
                '(SELECT name_id FROM names WHERE name = :name UNION SELECT name_id FROM name_insert_result)'
            ) if new_asset['name'] else 'NULL',
            image_column=(
                '(SELECT image_id FROM images WHERE image = :image UNION SELECT image_id FROM image_insert_result)'
            ) if new_asset['image'] else 'NULL',
            video_column=(
                '(SELECT video_id FROM videos WHERE video = :video UNION SELECT video_id FROM video_insert_result)'
            ) if new_asset['video'] else 'NULL',
            idata_column=(
                '(SELECT data_id FROM data WHERE md5(data) = md5(:idata) '
                'UNION SELECT data_id FROM idata_insert_result)'
            ) if new_asset['idata'] and new_asset['idata'] != '{}' else 'NULL',
            mdata_column=mdata_column,
        ),
        new_asset
    )


@catch_and_log()
def insert_back_action(session, action):
    back = load_transaction_basics(action)
    data = _get_data(action)

    backed_token = data['backed_token'].split(' ') if 'backed_token' in data else data['back_quantity'].split(' ')

    back['backer'] = data['asset_owner'] if 'asset_owner' in data else data['owner']
    back['currency'] = backed_token[1]
    back['amount'] = float(backed_token[0])
    back['asset_id'] = data['asset_id']

    session_execute_logged(
        session,
        'INSERT INTO backed_assets '
        'SELECT :asset_id, :amount, :currency, :backer, :seq, :block_num, :timestamp '
        'WHERE NOT EXISTS (SELECT seq FROM backed_assets WHERE seq = :seq)',
        back
    )


@catch_and_log()
def load_atomic_transfer(session, transfer):
    data = _get_data(transfer)

    new_transfer = load_transaction_basics(transfer)

    assets = data['assetids'] if 'assetids' in data else data['asset_ids']

    new_transfer['memo'] = data['memo'][0:255]
    new_transfer['sender'] = data['from']
    new_transfer['receiver'] = data['to']

    asset_ids = []
    for asset_id in assets:
        asset_ids.append(int(asset_id))

    new_transfer['asset_ids'] = asset_ids

    _insert_transfer(session, new_transfer)


@catch_and_log()
def load_atomic_burn(session, action):
    data = _get_data(action)
    tx = load_transaction_basics(action)

    tx['asset_id'] = data['asset_id']
    tx['burner'] = data['asset_owner']
    session_execute_logged(
        session,
        'INSERT INTO atomicassets_burns SELECT :asset_id, :burner, :seq, :block_num, :timestamp '
        'WHERE NOT EXISTS (SELECT seq FROM atomicassets_burns WHERE seq = :seq)',
        tx
    )

    session_execute_logged(
        session,
        'UPDATE assets SET burned = TRUE, owner = NULL WHERE asset_id = :asset_id ',
        tx
    )


@catch_and_log()
def load_atomic_offer(session, action):
    data = _get_data(action)

    recipient = data['recipient']

    new_offer = load_transaction_basics(action)

    sender_asset_ids = []
    recipient_asset_ids = []
    new_offer['sender'] = data['sender']
    new_offer['recipient'] = recipient
    new_offer['memo'] = data['memo'][0:255]
    new_offer['offer_id'] = data['offer_id']
    new_offer['status'] = 'new'

    for asset_id in data['sender_asset_ids']:
        sender_asset_ids.append(int(asset_id))
    for asset_id in data['recipient_asset_ids']:
        recipient_asset_ids.append(int(asset_id))

    new_offer['recipient_asset_ids'] = recipient_asset_ids
    new_offer['sender_asset_ids'] = sender_asset_ids

    with_clause = construct_memo_clause(new_offer)

    session_execute_logged(
        session,
        '{with_clause} '
        'INSERT INTO atomicassets_offer_logs '
        '(offer_id, sender, recipient, sender_asset_ids, recipient_asset_ids, status, memo_id, seq, block_num, '
        'timestamp) '
        'SELECT :offer_id, :sender, :recipient, :sender_asset_ids, :recipient_asset_ids, :status, '
        '{memo_column}, :seq, :block_num, :timestamp '
        'WHERE NOT EXISTS (SELECT seq FROM atomicassets_offer_logs WHERE seq = :seq)'.format(
            with_clause=with_clause,
            memo_column=(
                '(SELECT memo_id FROM memos WHERE md5(memo) = md5(:memo) UNION SELECT memo_id FROM insert_result)'
            ) if 'memo' in action and action['memo'] else 'NULL'
        ), new_offer
    )

    if new_offer['recipient'] != 'atomicmarket':
        session_execute_logged(
            session,
            'INSERT INTO atomicassets_offers SELECT * FROM atomicassets_offer_logs '
            'WHERE seq = :seq AND NOT EXISTS (SELECT seq FROM atomicassets_offers WHERE seq = :seq)',
            new_offer
        )


@catch_and_log()
def load_accept_offer(session, action):
    data = _get_data(action)

    offer = load_transaction_basics(action)
    offer['status'] = 'accepted'
    offer['offer_id'] = data['offer_id']
    session_execute_logged(
        session,
        'INSERT INTO atomicassets_offer_updates (offer_id, status, seq, timestamp) '
        'SELECT  :offer_id, :status, :seq, :timestamp '
        'WHERE NOT EXISTS (SELECT seq FROM atomicassets_offer_updates WHERE seq = :seq)',
        offer
    )
    session.commit()
    session_execute_logged(
        session,
        'INSERT INTO removed_atomicassets_offers '
        'SELECT * FROM atomicassets_offers WHERE offer_id = :offer_id '
        'AND NOT EXISTS (SELECT offer_id FROM removed_atomicassets_offers WHERE offer_id = :offer_id)',
        offer
    )
    session.commit()
    session_execute_logged(
        session,
        'DELETE FROM atomicassets_offers '
        'WHERE offer_id = :offer_id ',
        offer
    )
    session.commit()


@catch_and_log()
def load_cancel_offer(session, action):
    data = _get_data(action)

    offer = load_transaction_basics(action)
    offer['status'] = 'canceled'
    offer['offer_id'] = data['offer_id']
    session_execute_logged(
        session,
        'INSERT INTO atomicassets_offer_updates (offer_id, status, seq, timestamp) '
        'SELECT  :offer_id, :status, :seq, :timestamp '
        'WHERE NOT EXISTS (SELECT seq FROM atomicassets_offer_updates WHERE seq = :seq)',
        offer
    )
    session.commit()
    session_execute_logged(
        session,
        'INSERT INTO removed_atomicassets_offers '
        'SELECT * FROM atomicassets_offers WHERE offer_id = :offer_id '
        'AND NOT EXISTS (SELECT offer_id FROM removed_atomicassets_offers WHERE offer_id = :offer_id)',
        offer
    )
    session.commit()
    session_execute_logged(
        session,
        'DELETE FROM atomicassets_offers '
        'WHERE offer_id = :offer_id ',
        offer
    )
    session.commit()


@catch_and_log()
def load_decline_offer(session, action):
    data = _get_data(action)

    offer = load_transaction_basics(action)
    offer['status'] = 'declined'
    offer['offer_id'] = data['offer_id']
    session_execute_logged(
        session,
        'INSERT INTO atomicassets_offer_updates (offer_id, status, seq, timestamp) '
        'SELECT  :offer_id, :status, :seq, :timestamp '
        'WHERE NOT EXISTS (SELECT seq FROM atomicassets_offer_updates WHERE seq = :seq)', offer
    )
    session.commit()
    session_execute_logged(
        session,
        'INSERT INTO removed_atomicassets_offers '
        'SELECT * FROM atomicassets_offers WHERE offer_id = :offer_id '
        'AND NOT EXISTS (SELECT offer_id FROM removed_atomicassets_offers WHERE offer_id = :offer_id)', offer
    )
    session.commit()
    session_execute_logged(
        session,
        'DELETE FROM atomicassets_offers '
        'WHERE offer_id = :offer_id ', offer
    )
    session.commit()


@catch_and_log()
def update_sales_summary(session):
    session_execute_logged(
        session,
        'INSERT INTO sales_summary SELECT collection, \'sales\', wax_price, usd_price, 1, buyer, seller, market, '
        'taker, maker, listing_id, timestamp, seq, block_num FROM sales WHERE seq > (SELECT COALESCE(MAX(seq), 0) '
        'FROM sales_summary WHERE type = \'sales\')'
    )

    session_execute_logged(
        session,
        'INSERT INTO sales_summary SELECT collection, \'drops\', '
        'CASE WHEN currency = \'WAX\' THEN price WHEN currency = \'USD\' THEN price / ('
        '   SELECT usd FROM usd_prices WHERE timestamp < dt.timestamp ORDER BY timestamp DESC LIMIT 1'
        ') ELSE 0 END, '
        'CASE WHEN currency = \'USD\' THEN price WHEN currency = \'WAX\' THEN price * ('
        '   SELECT usd FROM usd_prices WHERE timestamp < dt.timestamp ORDER BY timestamp DESC LIMIT 1'
        ') ELSE 0 END, num_items, buyer, seller, market, NULL, NULL, drop_id, timestamp, seq, block_num '
        'FROM ('
        '    SELECT collection, '
        '    CASE WHEN du.new_price IS NULL AND d2.old_price IS NULL THEN d.price '
        '    WHEN du.new_price IS NULL THEN d2.old_price '
        '    ELSE du.new_price END AS price, '
        '    CASE WHEN du.new_currency IS NULL AND d2.old_currency IS NULL THEN d.currency '
        '    WHEN du.new_currency IS NULL THEN d2.old_currency ELSE du.new_currency END AS currency, ' 
        '    amount AS num_items, claimer AS buyer, collection AS seller, dc.contract as market, NULL, NULL, '
        '    dc.drop_id, dc.timestamp, dc.seq, dc.block_num '
        '    FROM drop_claims dc '
        '    INNER JOIN drops d USING (drop_id, contract) '
        '    LEFT JOIN drop_price_updates du ON du.drop_id = dc.drop_id AND du.contract = dc.contract AND du.seq = ('
        '      SELECT MAX(seq)'
        '      FROM drop_price_updates'
        '      WHERE contract = dc.contract AND drop_id = dc.drop_id AND seq < dc.seq'
        '    )'
        '    LEFT JOIN drop_price_updates d2 ON d2.drop_id = dc.drop_id AND d2.contract = dc.contract AND d2.seq = ('
        '      SELECT MIN(seq)'
        '      FROM drop_price_updates'
        '      WHERE contract = dc.contract AND drop_id = dc.drop_id AND seq > dc.seq'
        '    ) '
        '   WHERE dc.seq > (SELECT COALESCE(MAX(seq), 0) FROM sales_summary WHERE type = \'drops\')'
        ') dt'
    )

    session.commit()


def apply_atomic_updates(session):
    try:
        updates = session_execute_logged(
            session,
            'SELECT a.collection, a.schema, u.asset_id, d1.data AS mdata, d2.data AS idata, u.seq, new_mdata_id, '
            'u.block_num '
            'FROM atomicassets_updates u '
            'INNER JOIN assets a USING(asset_id) '
            'LEFT JOIN data d1 ON (new_mdata_id = d1.data_id) '
            'LEFT JOIN data d2 ON (a.immutable_data_id = d2.data_id) '
            'WHERE NOT applied AND u.timestamp < NOW() AT time zone \'UTC\' - INTERVAL \'3 minutes\' '
            'ORDER BY u.seq ASC '
            'LIMIT 100 '
        )

        for update in updates:
            forked = session.execute('SELECT * FROM handle_fork').first()
            if forked['forked'] and forked['block_num'] <= update['block_num']:
                raise RuntimeError('Fork')
            try:
                data = json.loads(update['idata']) if 'idata' in update.keys() and update['idata'] else {}
                if 'mdata' in update.keys() and update['mdata']:
                    data.update(json.loads(update['mdata']))
            except Exception as err:
                continue

            new_asset = {}

            new_asset['name'] = data['name'].strip()[0:255] if 'name' in data.keys() else None
            new_asset['image'] = str(data['img']).strip()[0:255] if 'img' in data.keys() else None
            new_asset['video'] = str(data['video']).strip()[0:255] if 'video' in data.keys() else None
            new_asset['seq'] = update['seq']
            new_asset['new_mdata_id'] = update['new_mdata_id']
            new_asset['asset_id'] = update['asset_id']

            new_asset['attribute_ids'] = parse_simple_attributes(session, update['collection'], update['schema'], data)

            with_clause = construct_with_clause(new_asset)

            session_execute_logged(
                session,
                '{with_clause} '
                'UPDATE assets SET attribute_ids = :attribute_ids, mutable_data_id = :new_mdata_id '
                '{name_clause} {image_clause} {video_clause} '
                'WHERE asset_id = :asset_id' .format(
                    with_clause=with_clause,
                    name_clause=(
                        ', name_id = (SELECT name_id FROM names WHERE name = :name '
                        'UNION SELECT name_id FROM name_insert_result)'
                    ) if new_asset['name'] else ', name_id = NULL',
                    image_clause=(
                        ', image_id = (SELECT image_id FROM images WHERE image = :image '
                        'UNION SELECT image_id FROM image_insert_result)'
                    ) if new_asset['image'] else ', image_id = NULL',
                    video_clause=(
                        ', video_id = (SELECT video_id FROM videos WHERE video = :video '
                        'UNION SELECT video_id FROM video_insert_result)'
                    ) if new_asset['video'] else ', video_id = NULL',
                ), new_asset)
            session_execute_logged(
                session,
                'UPDATE atomicassets_updates SET applied = TRUE WHERE seq = :seq',
                new_asset
            )
        session.commit()
    except SQLAlchemyError as err:
        log_error('apply_simple_updates: {}'.format(err))
        raise err
    except RuntimeError as err:
        time.sleep(30)
        log_error('apply_simple_updates: {}'.format(err))
        raise err
    except Exception as err:
        log_error('apply_simple_updates: {}'.format(err))
        raise err


def apply_simple_updates(session):
    try:
        updates = session_execute_logged(
            session,
            'SELECT a.collection, a.schema, u.asset_id, d1.data AS mdata, d2.data AS idata, u.seq, new_mdata_id, '
            'u.block_num '
            'FROM simpleassets_updates u '
            'INNER JOIN assets a USING(asset_id) '
            'LEFT JOIN data d1 ON (new_mdata_id = d1.data_id) '
            'LEFT JOIN data d2 ON (a.immutable_data_id = d2.data_id) '
            'WHERE NOT applied AND u.timestamp < NOW() AT time zone \'UTC\' - INTERVAL \'3 minutes\' '
            'ORDER BY u.seq ASC '
            'LIMIT 100 '
        )

        for update in updates:
            forked = session.execute('SELECT * FROM handle_fork').first()
            if forked['forked'] and forked['block_num'] <= update['block_num']:
                raise RuntimeError('Fork')
            try:
                data = json.loads(update['idata']) if 'idata' in update.keys() and update['idata'] else {}
                if 'mdata' in update.keys() and update['mdata']:
                    data.update(json.loads(update['mdata']))
            except Exception as err:
                continue

            new_asset = {}

            new_asset['name'] = data['name'].strip()[0:255] if 'name' in data.keys() else None
            new_asset['image'] = str(data['img']).strip()[0:255] if 'img' in data.keys() else None
            new_asset['video'] = str(data['video']).strip()[0:255] if 'video' in data.keys() else None
            new_asset['seq'] = update['seq']
            new_asset['new_mdata_id'] = update['new_mdata_id']
            new_asset['asset_id'] = update['asset_id']

            new_asset['attribute_ids'] = parse_simple_attributes(session, update['collection'], update['schema'], data)

            with_clause = construct_with_clause(new_asset)

            session_execute_logged(
                session,
                '{with_clause} '
                'UPDATE assets SET attribute_ids = :attribute_ids, mutable_data_id = :new_mdata_id '
                '{name_clause} {image_clause} {video_clause} '
                'WHERE asset_id = :asset_id' .format(
                    with_clause=with_clause,
                    name_clause=(
                        ', name_id = (SELECT name_id FROM names WHERE name = :name '
                        'UNION SELECT name_id FROM name_insert_result)'
                    ) if new_asset['name'] else ', name_id = NULL',
                    image_clause=(
                        ', image_id = (SELECT image_id FROM images WHERE image = :image '
                        'UNION SELECT image_id FROM image_insert_result)'
                    ) if new_asset['image'] else ', image_id = NULL',
                    video_clause=(
                        ', video_id = (SELECT video_id FROM videos WHERE video = :video '
                        'UNION SELECT video_id FROM video_insert_result)'
                    ) if new_asset['video'] else ', video_id = NULL',
                ), new_asset)
            session_execute_logged(
                session,
                'UPDATE simpleassets_updates SET applied = TRUE WHERE seq = :seq',
                new_asset
            )
        session.commit()
    except SQLAlchemyError as err:
        log_error('apply_simple_updates: {}'.format(err))
        raise err
    except RuntimeError as err:
        time.sleep(30)
        log_error('apply_simple_updates: {}'.format(err))
        raise err
    except Exception as err:
        log_error('apply_simple_updates: {}'.format(err))
        raise err


@catch_and_log()
def calc_atomic_mints(session):
    forked = session.execute('SELECT * FROM handle_fork').first()
    if forked['forked'] and forked['block_num']:
        raise RuntimeError('Fork')

    res = session_execute_logged(
        session,
        'SELECT * FROM atomicassets_updates WHERE NOT applied ORDER BY seq ASC'
    )

    session.commit()

    forked = session.execute('SELECT * FROM handle_fork').first()
    if forked['forked'] and forked['block_num']:
        raise RuntimeError('Fork')

    res = session_execute_logged(
        session,
        'UPDATE assets a SET mint = am.mint '
        'FROM ('
        '   SELECT asset_id, m.mint '
        '   FROM asset_mints m '
        '   INNER JOIN assets a2 USING(asset_id) '
        '   WHERE a2.mint IS NULL LIMIT 10000'
        ') am '
        'WHERE a.asset_id = am.asset_id'
    )

    session.commit()

    return res.rowcount


@catch_and_log()
def calc_atomic_mints(session):
    forked = session.execute('SELECT * FROM handle_fork').first()
    if forked['forked'] and forked['block_num']:
        raise RuntimeError('Fork')

    session_execute_logged(
        session,
        'INSERT INTO asset_mints '
        'SELECT asset_id, template_id, '
        'COALESCE((SELECT MAX(mint) FROM asset_mints WHERE template_id = a.template_id), 0) + 1 '
        'FROM assets a '
        'WHERE template_id > 0 '
        'AND asset_id > (SELECT MAX(asset_id) FROM asset_mints) '
        'AND timestamp < NOW() AT time zone \'utc\' - INTERVAL \'10 minutes\'  ORDER BY asset_id ASC LIMIT 1'
    )

    session.commit()

    res = session_execute_logged(
        session,
        'UPDATE assets a SET mint = am.mint '
        'FROM ('
        '   SELECT asset_id, m.mint '
        '   FROM asset_mints m '
        '   INNER JOIN assets a2 USING(asset_id) '
        '   WHERE a2.mint IS NULL LIMIT 10000'
        ') am '
        'WHERE a.asset_id = am.asset_id'
    )

    session.commit()

    return res.rowcount


@catch_and_log()
def _apply_atomic_update(session, transaction):
    update = session_execute_logged(
        session,
        'SELECT a.collection, a.schema, a.asset_id, d1.data AS mdata, d2.data AS idata, d3.data AS tdata, u.seq, '
        'new_mdata_id '
        'FROM atomicassets_updates u '
        'INNER JOIN assets a USING(asset_id) '
        'LEFT JOIN templates t USING (template_id) '
        'LEFT JOIN data d1 ON (new_mdata_id = d1.data_id) '
        'LEFT JOIN data d2 ON (a.immutable_data_id = d2.data_id) '
        'LEFT JOIN data d3 ON (t.immutable_data_id = d3.data_id) '
        'WHERE u.seq = :seq '
        'ORDER BY u.asset_id ASC ',
        transaction
    ).first()

    try:
        data = parse_data(
            json.loads(update['tdata'])
        ) if 'tdata' in update.keys() and update['tdata'] else {}
        if 'idata' in update.keys() and update['idata']:
            data.update(parse_data(json.loads(update['idata'])))
        if 'mdata' in update.keys() and update['mdata']:
            data.update(parse_data(json.loads(update['mdata'])))

        new_asset = {}

        new_asset['name'] = data['name'].strip()[0:255] if 'name' in data.keys() else None
        new_asset['image'] = str(data['img']).strip()[0:255] if 'img' in data.keys() else None
        new_asset['video'] = str(data['video']).strip()[0:255] if 'video' in data.keys() else None
        new_asset['seq'] = update['seq']
        new_asset['new_mdata_id'] = update['new_mdata_id']
        new_asset['asset_id'] = update['asset_id']

        new_asset['attribute_ids'] = parse_attributes(session, update['collection'], update['schema'], data)

        with_clause = construct_with_clause(new_asset)

        session_execute_logged(
            session,
            '{with_clause} '
            'UPDATE assets SET attribute_ids = :attribute_ids, mutable_data_id = :new_mdata_id '
            '{name_clause} {image_clause} {video_clause} '
            'WHERE asset_id = :asset_id '.format(
                with_clause=with_clause,
                name_clause=(
                    ', name_id = ('
                    '   SELECT name_id FROM names WHERE name = :name UNION SELECT name_id FROM name_insert_result'
                    ')'
                ) if new_asset['name'] else ', name_id = NULL',
                image_clause=(
                    ', image_id = ('
                    '   SELECT image_id FROM images WHERE image = :image UNION SELECT image_id FROM image_insert_result'
                    ')'
                ) if new_asset['image'] else ', image_id = NULL',
                video_clause=(
                    ', video_id = ('
                    '   SELECT video_id FROM videos WHERE video = :video UNION SELECT video_id FROM video_insert_result'
                    ')'
                ) if new_asset['video'] else ', video_id = NULL',
            ),
            new_asset
        )
        session_execute_logged(
            session,
            'UPDATE atomicassets_updates SET applied = TRUE WHERE seq = :seq',
            new_asset
        )
        session.commit()
    except Exception as err:
        log_error('apply_atomic_update: {}'.format(err))
        raise err


@catch_and_log()
def load_atomic_update(session, asset_update):
    data = _get_data(asset_update)

    asset = load_transaction_basics(asset_update)

    asset['asset_id'] = data['assetid'] if 'assetid' in data.keys() else data['asset_id']
    asset['mdata'] = json.dumps(data['new_mutable_data']) if 'new_mutable_data' in data.keys() else None

    with_clause = construct_with_clause(asset)

    session_execute_logged(
        session,
        '{with_clause} '
        'INSERT INTO atomicassets_updates (seq, asset_id, timestamp, block_num, new_mdata_id, old_mdata_id) '
        'SELECT :seq, :asset_id, :timestamp, :block_num, {mdata_column}, '
        '(SELECT mutable_data_id FROM assets WHERE asset_id = :asset_id) '
        'WHERE NOT EXISTS (SELECT seq FROM atomicassets_updates WHERE seq = :seq) '.format(
            with_clause=with_clause,
            mdata_column=(
                '(SELECT data_id FROM data WHERE md5(data) = md5(:mdata) '
                'UNION SELECT data_id FROM mdata_insert_result)'
            ) if asset['mdata'] and asset['mdata'] != '{}' else 'NULL',
        ), asset
    )
    session.commit()


@catch_and_log()
def load_collection_update(session, update):
    data = _get_data(update)
    update_data = data['data']

    collection = load_transaction_basics(update)

    collection['collection'] = data['collection_name']
    collection['name'] = None
    collection['description'] = None
    collection['url'] = None
    collection['img'] = None
    collection['image'] = None
    collection['socials'] = None
    collection['creator_info'] = None
    collection['images'] = None
    collection['market_fee'] = None

    for item in update_data:
        collection[item['key']] = item['value'][1]

    if collection['url'] and len(collection['url']) > 255:
        collection['url'] = collection['url'][0:255]

    if collection['name'] and len(collection['name']) > 255:
        collection['name'] = collection['name'][0:255]

    if collection['img']:
        collection['image'] = collection['img'][0:255]

    with_clause = construct_with_clause(collection)
    if with_clause:
        with_clause += (
            ', old_collection AS (SELECT name_id, description, url, image_id, socials, creator_info, images '
            'FROM collections WHERE collection = :collection) '
        )
    else:
        with_clause = (
            'WITH old_collection AS (SELECT name_id, description, url, image_id, socials, creator_info, images '
            'FROM collections WHERE collection = :collection)'
        )

    session_execute_logged(
        session,
        '{with_clause} '
        'INSERT INTO collection_updates (collection, new_name_id, old_name_id, new_description, old_description, '
        'new_url, old_url, new_image_id, old_image_id, new_socials, old_socials, new_creator_info, '
        'old_creator_info, new_images, old_images, seq, block_num, timestamp) '
        'SELECT :collection, {name_column}, c.name_id, :description, c.description, :url, c.url, '
        '{image_column}, c.image_id, :socials, c.socials, :creator_info, c.creator_info, :images, c.images, '
        ':seq, :block_num, :timestamp FROM old_collection c '
        'WHERE NOT EXISTS (SELECT seq FROM collection_updates WHERE seq = :seq) '.format(
            with_clause=with_clause,
            name_column=(
                '(SELECT name_id FROM names WHERE name = :name UNION SELECT name_id FROM name_insert_result)'
            ) if collection['name'] else 'NULL',
            image_column=(
                '(SELECT image_id FROM images WHERE image = :image UNION SELECT image_id FROM image_insert_result)'
            ) if collection['image'] else 'NULL',
        ), collection)

    session_execute_logged(
        session,
        'UPDATE collections c SET '
        'name_id = CASE WHEN u.new_name_id IS NOT NULL THEN u.new_name_id ELSE name_id END, '
        'description = CASE WHEN u.new_description IS NOT NULL THEN u.new_description ELSE description END, '
        'url = CASE WHEN u.new_url IS NOT NULL THEN u.new_url ELSE url END, '
        'image_id = CASE WHEN u.new_image_id IS NOT NULL THEN u.new_image_id ELSE image_id END, '
        'socials = CASE WHEN u.new_socials IS NOT NULL THEN u.new_socials ELSE socials END, '
        'creator_info = CASE WHEN u.new_creator_info IS NOT NULL THEN u.new_creator_info ELSE creator_info END, '
        'images = CASE WHEN u.new_images IS NOT NULL THEN u.new_images ELSE images END '
        'FROM collection_updates u WHERE u.seq = :seq AND u.collection = c.collection', collection
    )

    session.commit()


@catch_and_log()
def load_collection_fee_update(session, update):
    data = _get_data(update)

    collection = load_transaction_basics(update)

    collection['collection'] = data['collection_name']
    collection['new_market_fee'] = float(data['market_fee'])

    session_execute_logged(
        session,
        'INSERT INTO collection_fee_updates (collection, new_market_fee, old_market_fee, block_num, seq, timestamp)'
        'SELECT :collection, :new_market_fee, '
        '(SELECT market_fee FROM collections WHERE collection = :collection), '
        ':block_num, :seq, :timestamp '
        'WHERE NOT EXISTS (SELECT seq FROM collection_fee_updates WHERE seq = :seq) ',
        collection
    )

    session_execute_logged(
        session,
        'UPDATE collections set market_fee = :new_market_fee WHERE collection = :collection',
        collection
    )


@catch_and_log()
def add_collection_author(session, update):
    data = _get_data(update)

    collection = load_transaction_basics(update)

    collection['collection'] = data['collection_name']
    collection['account_to_add'] = data['account_to_add']

    session_execute_logged(
        session,
        'INSERT INTO collection_account_updates (collection, account_to_add, seq, block_num, timestamp) '
        'SELECT :collection, :account_to_add, :seq, :block_num, :timestamp '
        'WHERE NOT EXISTS (SELECT seq FROM collection_account_updates WHERE seq = :seq) ',
        collection
    )

    session_execute_logged(
        session,
        'UPDATE collections SET authorized = array_append(authorized, :account_to_add) '
        'WHERE collection = :collection ',
        collection
    )


@catch_and_log()
def remove_collection_author(session, update):
    data = _get_data(update)

    collection = load_transaction_basics(update)

    collection['collection'] = data['collection_name']
    collection['account_to_remove'] = data['account_to_remove']

    session_execute_logged(
        session,
        'INSERT INTO collection_account_updates (collection, account_to_remove, seq, block_num, timestamp) '
        'SELECT :collection, :account_to_remove, :seq, :block_num, :timestamp '
        'WHERE NOT EXISTS (SELECT seq FROM collection_account_updates WHERE seq = :seq) ',
        collection
    )

    session_execute_logged(
        session,
        'UPDATE collections SET authorized = array_remove(authorized, :account_to_remove) '
        'WHERE collection = :collection ',
        collection
    )


@catch_and_log()
def insert_atomic_template(session, action):
    template = _get_data(action)
    new_template = load_transaction_basics(action)
    template_id = template['template_id']
    new_template['template_id'] = template_id
    new_template['burnable'] = template['burnable']
    new_template['transferable'] = template['transferable']
    new_template['max_supply'] = template['max_supply']
    new_template['collection'] = template['collection_name']
    new_template['schema'] = template['schema_name']
    data = parse_data(template['immutable_data'])
    new_template['name'] = str(data['name']).strip()[0:255] if 'name' in data else None
    new_template['image'] = str(data['img']).strip()[0:255] if 'img' in data else None
    new_template['video'] = str(data['video']).strip()[0:255] if 'video' in data else None
    new_template['idata'] = json.dumps(template['immutable_data'])

    new_template['attribute_ids'] = parse_attributes(
        session, new_template['collection'], new_template['schema'], data)

    with_clause = construct_with_clause(new_template)

    session_execute_logged(
        session,
        '{with_clause} '
        'INSERT INTO templates (template_id, collection, schema, seq, block_num, timestamp, name_id, image_id, '
        'video_id, max_supply, burnable, transferable, num_assets, attribute_ids, immutable_data_id) '
        'SELECT :template_id, :collection, :schema, :seq, :block_num, :timestamp, '
        '{name_column}, '
        '{image_column}, '
        '{video_column}, '
        ':max_supply, :burnable, :transferable, 0, :attribute_ids, '
        '{idata_column} '
        'WHERE NOT EXISTS (SELECT seq FROM templates WHERE seq = :seq) '.format(
            with_clause=with_clause,
            name_column=(
                '(SELECT name_id FROM names WHERE name = :name UNION SELECT name_id FROM name_insert_result)'
            ) if new_template['name'] else 'NULL',
            image_column=(
                '(SELECT image_id FROM images WHERE image = :image UNION SELECT image_id FROM image_insert_result)'
            ) if new_template['image'] else 'NULL',
            video_column=(
                '(SELECT video_id FROM videos WHERE video = :video UNION SELECT video_id FROM video_insert_result)'
            ) if new_template['video'] else 'NULL',
            idata_column=(
                '(SELECT data_id FROM data WHERE md5(data) = md5(:idata) '
                'UNION SELECT data_id FROM idata_insert_result)'
            ) if new_template['idata'] and new_template['idata'] != '{}' else 'NULL',
        ),
        new_template
    )
    session.commit()

    if new_template['attribute_ids'] and len(new_template['attribute_ids']) > 0:
        session_execute_logged(
            session,
            'INSERT INTO template_attributes_mapping '
            'SELECT :collection, :schema, :template_id, unnest(:attribute_ids), :seq, :block_num '
            'WHERE NOT EXISTS (SELECT seq FROM template_attributes_mapping WHERE seq = :seq)',
            new_template
        )


@catch_and_log()
def insert_schema(session, action):
    schema = _get_data(action)
    new_schema = load_transaction_basics(action)
    if 'collection_name' not in schema:
        return
    new_schema['collection'] = schema['collection_name']
    new_schema['schema'] = schema['schema_name']
    new_schema['format'] = json.dumps(schema['schema_format'])

    session_execute_logged(
        session,
        'INSERT INTO schemas (schema, collection, seq, block_num, timestamp, schema_format) '
        'SELECT :schema, :collection, :seq, :block_num, :timestamp, :format '
        'WHERE NOT EXISTS (SELECT schema, collection FROM schemas '
        'WHERE schema = :schema AND collection = :collection)',
        new_schema
    )


@catch_and_log()
def insert_collection(session, action):
    collection = _get_data(action)
    new_collection = load_transaction_basics(action)
    if 'collection_name' not in collection:
        return
    new_collection['collection'] = collection['collection_name']
    data = parse_data(collection['data']) if 'data' in collection.keys() else json.loads(collection['json_data'])
    new_collection['image'] = data['img'][0:255] if 'img' in data else None
    new_collection['name'] = data['name'][0:255] if 'name' in data else None
    new_collection['url'] = data['url'][0:255] if 'url' in data else None
    new_collection['description'] = data['description'] if 'description' in data else None
    new_collection['socials'] = data['socials'] if 'socials' in data else None
    new_collection['creator_info'] = data['creator_info'] if 'creator_info' in data else None
    new_collection['images'] = data['images'] if 'images' in data else None

    new_collection['authorized'] = collection['authorized_accounts']
    new_collection['author'] = collection['author']
    new_collection['market_fee'] = collection['market_fee'] if 'market_fee' in collection else 0

    with_clause = construct_with_clause(new_collection)

    session_execute_logged(
        session,
        '{with_clause} '
        'INSERT INTO collections ('
        '   collection, seq, block_num, timestamp, name_id, image_id, author, url, description, market_fee, '
        '   authorized, socials, creator_info, images'
        ') '
        'SELECT :collection, :seq, :block_num, :timestamp, '
        '{name_column}, '
        '{image_column}, '
        ':author, :url, :description, :market_fee, :authorized, :socials, :creator_info, :images '
        'WHERE NOT EXISTS (SELECT collection FROM collections WHERE collection = :collection)'.format(
            with_clause=with_clause,
            name_column=(
                '(SELECT name_id FROM names WHERE name = :name UNION SELECT name_id FROM name_insert_result)'
            ) if new_collection['name'] else 'NULL',
            image_column=(
                '(SELECT image_id FROM images WHERE image = :image UNION SELECT image_id FROM image_insert_result)'
            ) if new_collection['image'] else 'NULL',
        ),
        new_collection)
    session.commit()


@catch_and_log()
def load_nft_hive_ft_lists(session, action):
    data = _get_data(action)
    order_id = data['sale_id']
    quantity = data['quantity'].split(' ')
    symbol = quantity[1]
    quantity = int(float(quantity[0]))
    sell = load_transaction_basics(action)
    sell['seller'] = data['seller']

    if 'WAX' in data['listing_price']:
        sell['price'] = float(data['listing_price'].replace(' WAX', ''))
        sell['currency'] = 'WAX'
    else:
        return []

    sell['market'] = 'nft.hive'
    sell['symbol'] = symbol
    sell['order_id'] = order_id

    for i in range(quantity):
        session_execute_logged(
            session,
            'INSERT INTO ft_listings '
            '(symbol, contract, order_id, market, price, currency, amount, seller, seq, block_num, timestamp, '
            'active) '
            'SELECT :symbol, NULL, :order_id, :market, :price, '
            ':currency, 1, :seller, :seq, :block_num, :timestamp, TRUE '
            'WHERE NOT EXISTS (SELECT seq FROM ft_listings WHERE seq = :seq)',
            sell
        )
    session.commit()


@catch_and_log()
def load_nft_hive_ft_buys(session, action):
    data = _get_data(action)
    order_id = data['sale_id']

    tx = load_transaction_basics(action)
    tx['order_id'] = order_id
    tx['buyer'] = data['buyer']

    session_execute_logged(
        session,
        'INSERT INTO nft_hive_actions '
        'SELECT :buyer, :seq, :timestamp, :order_id, :action_name '
        'WHERE NOT EXISTS (SELECT seq FROM nft_hive_actions WHERE seq = :seq)', tx)

    session_execute_logged(
        session,
        'UPDATE ft_listings SET active = false WHERE market = \'nft.hive\' AND order_id = :order_id', tx
    )

    session.commit()


@catch_and_log()
def load_nft_hive_ft_cancels(session, action):
    data = _get_data(action)
    authorization = action['act']['authorization']
    actor = authorization[0]['actor']
    order_id = data['sale_id']

    tx = load_transaction_basics(action)
    tx['order_id'] = order_id
    tx['account'] = actor

    session_execute_logged(
        session,
        'INSERT INTO nft_hive_actions '
        'SELECT :account, :seq, :timestamp, :order_id, :action_name '
        'WHERE NOT EXISTS (SELECT seq FROM nft_hive_actions WHERE seq = :seq)',
        tx
    )

    session_execute_logged(
        session,
        'UPDATE ft_listings SET active = false WHERE market = \'nft.hive\' AND order_id = :order_id',
        tx
    )

    session.commit()


@catch_and_log()
def load_nft_hive_execute(session, transaction):
    data = _get_data(transaction)
    signer = data['signer']
    trx = load_transaction_basics(transaction)
    try:
        action = json.loads(data['action'])
    except Exception as err:
        return
    if 'action' in data and 'name' in action:
        name = action['name']
        data = action['data']
        trx['user'] = signer
        if name == 'create-banner' and signer in ['frcqu.wam', 't1.5c.wam', 'tgz5k.wam', 'scfay.wam', 'nonoswax.gm']:
            if not 'startTime' in data:
                data['startTime'] = datetime.datetime.utcnow()
            else:
                data['startTime'] = datetime.datetime.fromtimestamp(int(data['startTime']), tz=pytz.UTC)
            if 'startTime' in data and 'endTime' in data and 'market' in data and 'ipfs' in data and 'url' in data:
                trx['url'] = data['url']
                trx['ipfs'] = data['ipfs']
                trx['start_date'] = data['startTime']
                trx['end_date'] = datetime.datetime.fromtimestamp(int(data['endTime']), tz=pytz.UTC)
                trx['market'] = data['market']
                session_execute_logged(
                    session,
                    'INSERT INTO banners '
                    'SELECT :ipfs, :url, :start_date, :end_date, :market, :seq, :block_num, :timestamp '
                    'WHERE NOT EXISTS (SELECT image, url, end_date FROM banners '
                    'WHERE image = :ipfs AND url = :url AND end_date = :end_date)',
                    trx
                )
        elif name == 'favorite-asset':
            if 'id' in data:
                trx['asset_id'] = data['id']
                session_execute_logged(
                    session,
                    'INSERT INTO favorites '
                    'SELECT :user, asset_id, template_id, :seq, :block_num, :timestamp '
                    'FROM assets a WHERE asset_id = :asset_id AND template_id NOT IN ('
                    '   SELECT template_id FROM favorites WHERE user_name = :user'
                    ') AND NOT EXISTS ('
                    '   SELECT asset_id FROM favorites WHERE user_name = :user AND asset_id = :asset_id'
                    ')',
                    trx
                )
        elif name == 'unfavorite-asset':
            if 'id' in data:
                trx['asset_id'] = data['id']
                session_execute_logged(
                    session,
                    'INSERT INTO removed_favorites '
                    'SELECT f.*, :seq, :block_num '
                    'FROM favorites f '
                    'WHERE user_name = :user AND ('
                    '   template_id = ('
                    '       SELECT template_id FROM assets WHERE asset_id = :asset_id AND template_id > 0'
                    '   ) OR asset_id = :asset_id'
                    ')',
                    trx
                )
                session_execute_logged(
                    session,
                    'DELETE FROM favorites '
                    'WHERE user_name = :user AND ('
                    '   template_id = ('
                    '       SELECT template_id FROM assets WHERE asset_id = :asset_id AND template_id > 0'
                    '   ) OR asset_id = :asset_id'
                    ')',
                    trx
                )

        elif name == 'favorite-template':
            if 'id' in data:
                trx['template_id'] = data['id']
                session_execute_logged(
                    session,
                    'INSERT INTO favorites '
                    'SELECT :user, asset_id, :template_id, :seq, :block_num, :timestamp '
                    'FROM assets a WHERE template_id = :template_id AND NOT EXISTS ('
                    '   SELECT template_id FROM favorites WHERE user_name = :user AND template_id = :template_id'
                    ') ORDER BY asset_id ASC LIMIT 1',
                    trx
                )
        elif name == 'unfavorite-template':
            if 'id' in data:
                trx['template_id'] = data['id']
                session_execute_logged(
                    session,
                    'INSERT INTO removed_favorites '
                    'SELECT f.*, :seq, :block_num '
                    'FROM favorites f '
                    'WHERE user_name = :user AND template_id = :template_id',
                    trx
                )
                session_execute_logged(
                    session,
                    'DELETE FROM favorites '
                    'WHERE user_name = :user AND template_id = :template_id',
                    trx
                )
        elif name == 'follow':
            if 'collection' in data:
                trx['collection'] = data['collection']
                session_execute_logged(
                    session,
                    'INSERT INTO follows '
                    'SELECT :user, :collection, :seq, :block_num, :timestamp '
                    'FROM collections a WHERE collection = :collection AND NOT EXISTS ('
                    '   SELECT collection FROM follows WHERE user_name = :user AND collection = :collection'
                    ')',
                    trx
                )
        elif name == 'unfollow':
            if 'collection' in data:
                trx['collection'] = data['collection']
                session_execute_logged(
                    session,
                    'INSERT INTO removed_follows '
                    'SELECT f.*, :seq, :block_num FROM follows f WHERE user_name = :user AND collection = :collection',
                    trx
                )
                session_execute_logged(
                    session,
                    'DELETE FROM follows WHERE user_name = :user AND collection = :collection',
                    trx
                )
        elif name == 'toggle-notifications':
            if 'enable' in data:
                if not data['enable']:
                    session_execute_logged(
                        session,
                        'INSERT INTO removed_notification_users '
                        'SELECT n.*, :seq, :block_num FROM notification_users n WHERE user = :user',
                        trx
                    )
                    session_execute_logged(
                        session,
                        'DELETE FROM notification_users WHERE user_name = :user',
                        trx
                    )
                else:
                    session_execute_logged(
                        session,
                        'INSERT INTO notification_users SELECT :user, :seq, :block_num, :timestamp '
                        'WHERE NOT EXISTS (SELECT user_name FROM notification_users WHERE user_name = :user)',
                        trx
                    )
        session.commit()


@catch_and_log()
def load_asset(session, asset):
    data = _get_data(asset)

    asset_id = data['assetid']
    if not isinstance(asset_id, int) and (not isinstance(asset_id, str) or not asset_id.isnumeric()):
        log_error('Tried loading assetId {}. Asset: {}'.format(asset_id, asset))
        return
    new_asset = load_transaction_basics(asset)
    new_asset['asset_id'] = asset_id
    new_asset['contract'] = 'simpleassets'
    new_asset['collection'] = data['author']
    new_asset['schema'] = data['category'].strip()[0:15]
    new_asset['owner'] = data['owner']
    new_asset['mdata'] = data['mdata']
    new_asset['idata'] = data['idata']
    new_asset['name'] = _get_name(new_asset)
    new_asset['image'] = _get_image(new_asset)
    new_asset['video'] = _get_video(new_asset)

    asset_data = {}
    try:
        if 'idata' in data and data['idata']:
            asset_data.update(json.loads(data['idata']))
    except Exception as err:
        log_error('load_asset idata: {}'.format(err))
    try:
        if 'mdata' in data and data['mdata']:
            asset_data.update(json.loads(data['mdata']))
    except Exception as err:
        log_error('load_asset mdata: {}'.format(err))

    new_asset['attribute_ids'] = parse_simple_attributes(
        session, new_asset['collection'], new_asset['schema'], asset_data)

    tx = load_transaction_basics(asset)
    tx['asset_id'] = asset_id
    tx['receiver'] = data['owner']

    with_clause = construct_with_clause(new_asset)

    mdata_column = construct_mdata_column(new_asset)

    session_execute_logged(
        session,
        '{with_clause} '
        'INSERT INTO assets '
        '(asset_id, contract, collection, schema, owner, template_id, name_id, image_id, video_id, '
        'block_num, seq, timestamp, burnable, transferable, attribute_ids, immutable_data_id, mutable_data_id) '
        'SELECT :asset_id, :contract, :collection, :schema, :owner, NULL, '
        '{name_column}, '
        '{image_column}, '
        '{video_column}, '
        ':block_num, :seq, :timestamp, TRUE, TRUE, :attribute_ids, '
        '{idata_column}, '
        '{mdata_column} '
        'WHERE NOT EXISTS (SELECT asset_id FROM assets WHERE asset_id = :asset_id) '.format(
            with_clause=with_clause,
            name_column=(
                '(SELECT name_id FROM names WHERE name = :name UNION SELECT name_id FROM name_insert_result)'
            ) if new_asset['name'] else 'NULL',
            image_column=(
                '(SELECT image_id FROM images WHERE image = :image UNION SELECT image_id FROM image_insert_result)'
            ) if new_asset['image'] else 'NULL',
            video_column=(
                '(SELECT video_id FROM videos WHERE video = :video UNION SELECT video_id FROM video_insert_result)'
            ) if new_asset['video'] else 'NULL',
            idata_column=(
                '(SELECT data_id FROM data WHERE md5(data) = md5(:idata) '
                'UNION SELECT data_id FROM idata_insert_result)'
            ) if new_asset['idata'] and new_asset['idata'] != '{}' else 'NULL',
            mdata_column=mdata_column,
        ), new_asset
    )


@catch_and_log()
def load_transaction(session, transaction):
    data = _get_data(transaction)

    asset_ids = []
    for asset_id in data['assetids']:
        asset_ids.append(int(asset_id))

    new_transaction = load_transaction_basics(transaction)

    new_transaction['memo'] = data['memo'][0:255]
    new_transaction['sender'] = data['from']
    new_transaction['receiver'] = data['to']

    new_transaction['asset_ids'] = asset_ids

    _insert_transfer(session, new_transaction)


@catch_and_log()
def load_offer(session, offer):
    data = _get_data(offer)

    asset_ids = []
    for asset_id in data['assetids']:
        asset_ids.append(int(asset_id))

    transaction = load_transaction_basics(offer)
    transaction['asset_ids'] = asset_ids
    transaction['owner'] = data['owner']
    transaction['newowner'] = data['newowner']
    transaction['memo'] = data['memo'][0:255]

    with_clause = construct_memo_clause(transaction)
    session_execute_logged(
        session,
        '{with_clause} '
        'INSERT INTO simpleassets_offers '
        '(asset_ids, owner, newowner, seq, block_num, timestamp, memo_id) '
        'SELECT :asset_ids, :owner, :newowner, :seq, :block_num, :timestamp, '
        '{memo_column} '
        'WHERE NOT EXISTS (SELECT seq FROM simpleassets_offers WHERE seq = :seq)'.format(
            with_clause=with_clause,
            memo_column=(
                '(SELECT memo_id FROM memos WHERE md5(memo) = md5(:memo) UNION SELECT memo_id FROM insert_result)'
            ) if 'memo' in transaction and transaction['memo'] else 'NULL'
        ),
        transaction
    )

    if transaction['owner'] == 'simplemarket' and transaction['seq'] < 429078747:
        for asset_id in transaction['asset_ids']:
            transaction['asset_id'] = asset_id
            session_execute_logged(
                session,
                'INSERT INTO removed_simplemarket_listings '
                'SELECT l.*, :seq, :block_num FROM listings l '
                'WHERE market = \'simplemarket\' AND :asset_id = l.listing_id '
                'AND NOT EXISTS (SELECT sale_id FROM removed_simplemarket_listings WHERE sale_id = l.sale_id)',
                transaction
            )
            session.commit()

            session_execute_logged(
                session,
                'INSERT INTO sales '
                'SELECT l.asset_ids, l.collection, seller, :newowner, '
                'CASE WHEN currency = \'WAX\' THEN price ELSE price / ('
                '   SELECT usd FROM usd_prices WHERE timestamp < :timestamp ORDER BY timestamp DESC LIMIT 1'
                ') END, CASE WHEN currency = \'USD\' THEN price ELSE price * ('
                '   SELECT usd FROM usd_prices WHERE timestamp < :timestamp ORDER BY timestamp DESC LIMIT 1'
                ') END, currency, :asset_id, l.market, NULL, NULL, :seq, :block_num, :timestamp '
                'FROM listings l '
                'WHERE market = \'simplemarket\' AND :asset_id = l.listing_id ',
                transaction
            )
            session.commit()

        session_execute_logged(
            session,
            'DELETE FROM listings l WHERE sale_id IN ('
            '   SELECT sale_id FROM removed_simplemarket_listings WHERE removed_seq = :seq'
            ')', transaction
        )


@catch_and_log()
def load_claim(session, claim):
    data = _get_data(claim)

    asset_ids = []
    new_transaction = load_transaction_basics(claim)

    for asset_id in data['assetids']:
        asset_ids.append(int(asset_id))

        new_transaction['asset_id'] = asset_id
        new_transaction['claimer'] = data['claimer']

        session.execute(
            'INSERT INTO simpleassets_claims '
            '(asset_id, claimer, old_owner, seq, block_num, timestamp) '
            'SELECT asset_id, :claimer, owner, :seq, :block_num, :timestamp '
            'FROM assets '
            'WHERE asset_id = :asset_id '
            'AND NOT EXISTS ('
            '   SELECT asset_id, seq '
            '   FROM simpleassets_claims WHERE seq = :seq AND asset_id = :asset_id'
            ')',
            new_transaction
        )

        session.execute(
            'UPDATE assets SET  owner = :claimer '
            'WHERE asset_id = :asset_id ',
            new_transaction
        )


@catch_and_log()
def load_asset_burn(session, asset):
    data = _get_data(asset)
    tx = load_transaction_basics(asset)

    asset_ids = []
    for asset_id in data['assetids']:
        asset_ids.append(int(asset_id))
        session_execute_logged(
            session,
            'UPDATE assets SET burned = TRUE, owner = NULL WHERE asset_id = :asset_id',
            {'asset_id': asset_id}
        )

    tx['asset_ids'] = asset_ids
    tx['burner'] = data['owner']
    session_execute_logged(
        session,
        'INSERT INTO simpleassets_burns SELECT :asset_ids, :burner, :seq, :block_num, :timestamp '
        'WHERE NOT EXISTS (SELECT seq FROM simpleassets_burns WHERE seq = :seq)',
        tx
    )


def _apply_simpleassets_update(session, asset):
    try:
        update = session_execute_logged(
            session,
            'SELECT a.collection, a.schema, a.asset_id, d1.data AS mdata, d2.data AS idata, u.seq, new_mdata_id '
            'FROM simpleassets_updates u '
            'INNER JOIN assets a USING(asset_id) '
            'LEFT JOIN data d1 ON (new_mdata_id = d1.data_id) '
            'LEFT JOIN data d2 ON (a.immutable_data_id = d2.data_id) '
            'WHERE u.seq = :seq ',
            asset
        ).first()

        try:
            data = json.loads(update['idata']) if 'idata' in update.keys() and update['idata'] else {}
            if 'mdata' in update.keys() and update['mdata']:
                data.update(json.loads(update['mdata']))
        except Exception as err:
            return

        new_asset = {}

        new_asset['name'] = data['name'].strip()[0:255] if 'name' in data.keys() else None
        new_asset['image'] = str(data['img']).strip()[0:255] if 'img' in data.keys() else None
        new_asset['video'] = str(data['video']).strip()[0:255] if 'video' in data.keys() else None
        new_asset['seq'] = update['seq']
        new_asset['new_mdata_id'] = update['new_mdata_id']
        new_asset['asset_id'] = update['asset_id']

        new_asset['attribute_ids'] = parse_simple_attributes(session, update['collection'], update['schema'], data)

        with_clause = construct_with_clause(new_asset)

        session_execute_logged(
            session,
            '{with_clause} '
            'UPDATE assets SET attribute_ids = :attribute_ids, mutable_data_id = :new_mdata_id '
            '{name_clause} {image_clause} {video_clause} '
            'WHERE asset_id = :asset_id' .format(
                with_clause=with_clause,
                name_clause=(
                    ', name_id = (SELECT name_id FROM names WHERE name = :name UNION SELECT name_id FROM name_insert_result)'
                ) if new_asset['name'] else ', name_id = NULL',
                image_clause=(
                    ', image_id = (SELECT image_id FROM images WHERE image = :image UNION SELECT image_id FROM image_insert_result)'
                ) if new_asset['image'] else ', image_id = NULL',
                video_clause=(
                    ', video_id = (SELECT video_id FROM videos WHERE video = :video UNION SELECT video_id FROM video_insert_result)'
                ) if new_asset['video'] else ', video_id = NULL',
            ),
            new_asset
        )
        session_execute_logged(
            session,
            'UPDATE simpleassets_updates SET applied = TRUE WHERE asset_id = :asset_id',
            new_asset
        )
        session.commit()
    except SQLAlchemyError as err:
        log_error('_apply_simpleassets_update: {}'.format(err))
        raise err
    except RuntimeError as err:
        time.sleep(30)
        log_error('_apply_simpleassets_update: {}'.format(err))
        raise err
    except Exception as err:
        log_error('_apply_simpleassets_update: {}'.format(err))
        raise err


@catch_and_log()
def load_asset_update(session, asset_update):
    data = _get_data(asset_update)
    asset_id = data['assetid']
    if not isinstance(asset_id, int) and (not isinstance(asset_id, str) or not asset_id.isnumeric()):
        log_error('Tried loading assetId {}. Asset: {}'.format(asset_id, asset_update))
        return False
    asset = load_transaction_basics(asset_update)

    asset['asset_id'] = data['assetid']
    asset['mdata'] = data['mdata']

    with_clause = construct_with_clause(asset)

    session_execute_logged(
        session,
        '{with_clause} '
        'INSERT INTO simpleassets_updates ('
        '   seq, asset_id, timestamp, block_num, new_mdata_id, old_mdata_id, applied'
        ') '
        'SELECT :seq, :asset_id, :timestamp, :block_num, {mdata_column}, '
        '(SELECT mutable_data_id FROM assets WHERE asset_id = :asset_id), :block_num < 258510531 '
        'WHERE NOT EXISTS (SELECT seq FROM simpleassets_updates WHERE seq = :seq) '.format(
            with_clause=with_clause,
            mdata_column=(
                '(SELECT data_id FROM data WHERE md5(data) = md5(:mdata) '
                'UNION SELECT data_id FROM mdata_insert_result)'
            ) if asset['mdata'] and asset['mdata'] != '{}' else 'NULL',
        ),
        asset
    )

    _apply_simpleassets_update(session, asset)


@catch_and_log()
def load_waxplorercom_buy(session, action):
    data = _get_data(action)
    buy = load_transaction_basics(action)
    buy['sale_id'] = data['sale_id']
    buy['market'] = 'waxplorercom'
    buy['buyer'] = data['buyer']

    session.execute(
        'INSERT INTO market_actions '
        'SELECT :sale_id, :market, :buyer, \'buy\', :seq, :block_num, :timestamp '
        'WHERE NOT EXISTS (SELECT seq FROM market_actions WHERE seq = :seq)',
        buy
    )

    session.execute(
        'INSERT INTO removed_waxplorercom_listings '
        'SELECT l.*, :seq, :block_num FROM listings l '
        'WHERE market = :market AND :sale_id = l.listing_id ',
        buy
    )
    session.commit()

    session.execute(
        'INSERT INTO sales '
        'SELECT l.asset_ids, a.collection, seller, :buyer, '
        'CASE WHEN currency = \'WAX\' THEN price ELSE price / ('
        '   SELECT usd FROM usd_prices WHERE timestamp < :timestamp ORDER BY timestamp DESC LIMIT 1'
        ') END, CASE WHEN currency = \'USD\' THEN price ELSE price * ('
        '   SELECT usd FROM usd_prices WHERE timestamp < :timestamp ORDER BY timestamp DESC LIMIT 1'
        ') END, currency, listing_id, market, maker, NULL, '
        ':seq, :block_num, :timestamp '
        'FROM listings l LEFT JOIN assets a ON a.asset_id = l.asset_ids[1] '
        'WHERE market = \'waxplorercom\' AND :sale_id = l.listing_id ',
        buy
    )
    session.commit()

    session.execute(
        'DELETE FROM listings l WHERE sale_id IN ('
        '   SELECT sale_id FROM removed_waxplorercom_listings WHERE removed_seq = :seq'
        ')', buy
    )
    session.commit()


@catch_and_log()
def load_waxplorercom_list(session, action):
    data = _get_data(action)

    new_transaction = load_transaction_basics(action)
    asset_ids = []
    for asset_id in data['asset_ids']:
        asset_ids.append(int(asset_id))
    new_transaction['sale_id'] = data['sale_id']
    new_transaction['market'] = 'waxplorercom'
    new_transaction['asset_ids'] = asset_ids

    new_transaction['price'] = data['listing_price'].replace(' WAX', '')
    new_transaction['currency'] = 'WAX'
    new_transaction['seller'] = data['seller']

    session.execute(
        'INSERT INTO listings ('
        '   asset_ids, collection, seller, market, price, currency, listing_id, seq, block_num, '
        '   timestamp, estimated_wax_price '
        ') '
        'SELECT array_agg(asset_id) AS asset_ids, collection, :seller, :market, :price, :currency, '
        'asset_id, :seq, :block_num, :timestamp, CASE WHEN :currency = \'WAX\' THEN :price '
        'ELSE :price * (SELECT usd FROM usd_prices ORDER BY timestamp DESC LIMIT 1) END '
        'FROM ('
        '   SELECT unnest(:asset_ids) AS asset_id '
        ') t LEFT JOIN assets a USING(asset_id) '
        'GROUP BY asset_id, collection ', new_transaction
    )


@catch_and_log()
def load_waxplorercom_unlist(session, action):
    data = _get_data(action)
    authorization = action['act']['authorization']
    buy = load_transaction_basics(action)
    buy['actor'] = authorization[0]['actor']
    buy['sale_id'] = data['sale_id']
    buy['market'] = 'waxplorercom'

    session.execute(
        'INSERT INTO market_actions '
        'SELECT :sale_id, :market, :actor, \'cancel\', :seq, :block_num, :timestamp '
        'WHERE NOT EXISTS (SELECT seq FROM market_actions WHERE seq = :seq)',
        buy
    )

    session.execute(
        'INSERT INTO removed_waxplorercom_listings '
        'SELECT l.*, :seq, :block_num FROM listings l '
        'WHERE market = :market AND :sale_id = l.listing_id ',
        buy
    )
    session.commit()

    session.execute(
        'DELETE FROM listings l WHERE sale_id IN ('
        '   SELECT sale_id FROM removed_waxplorercom_listings WHERE removed_seq = :seq'
        ')',
        buy
    )
    session.commit()


@catch_and_log()
def load_market_myth_buy(session, action):
    data = _get_data(action)
    asset_id = data['assetid']

    buy = load_transaction_basics(action)
    buy['market'] = 'market.myth'
    buy['buyer'] = data['buyer']
    buy['seller'] = data['seller']
    buy['asset_ids'] = [int(asset_id)]
    buy['asset_id'] = asset_id
    buy['price'] = float(data['price'].split(' ')[0])
    buy['currency'] = data['price'].split(' ')[1]
    buy['referral'] = data['referral'] if 'referral' in data and data['referral'] == 'waxplorerref' else None

    session.execute(
        'INSERT INTO market_myth_sales '
        'SELECT :asset_ids, :seller, :buyer, :price, :currency, :asset_id, :market, NULL, :referral, '
        ':seq, :block_num, :timestamp '
        'WHERE NOT EXISTS (SELECT seq FROM market_myth_sales WHERE seq = :seq) ',
        buy
    )
    session.commit()


@catch_and_log()
def load_simplemarket_update(session, action):
    data = _get_data(action)
    sale_id = data['saleid']
    new_price = float(data['newprice'].split(' ')[0])
    currency = data['newprice'].split(' ')[1]
    offer_price = float(data['offerprice'].split(' ')[0]) if 'offerprice' in data else None
    offer_currency = data['offerprice'].split(' ')[1] if 'offerprice' in data else None
    offer_time = datetime.datetime.fromtimestamp(int(data['offertime'])) if 'offertime' in data.keys() and int(data['offertime']) < 3000000000 else None

    transaction = load_transaction_basics(action)
    transaction['sale_id'] = sale_id
    transaction['new_price'] = new_price
    transaction['currency'] = currency
    transaction['offer_time'] = offer_time
    transaction['offer_price'] = offer_price
    transaction['offer_currency'] = offer_currency

    session.execute(
        'INSERT INTO simplemarket_updates '
        'SELECT :sale_id, :seq, :block_num, :timestamp, :new_price, :currency, :offer_price, :offer_currency, '
        ':offer_time, price, currency '
        'FROM listings l '
        'WHERE market = \'simplemarket\' AND :sale_id = listing_id '
        'AND NOT EXISTS (SELECT seq FROM simplemarket_updates WHERE seq = :seq)',
        transaction
    )
    session.commit()

    session.execute(
        'UPDATE listings SET price = new_price, currency = u.currency, '
        'estimated_wax_price = CASE WHEN  u.currency = \'WAX\' '
        'THEN new_price ELSE new_price / (SELECT usd FROM usd_prices ORDER BY timestamp DESC LIMIT 1) END '
        'FROM simplemarket_updates u '
        'WHERE u.seq = :seq AND market = \'simplemarket\' '
        'AND :sale_id = listing_id ',
        transaction
    )


@catch_and_log()
def load_simplemarket_buy(session, action):
    data = _get_data(action)

    transaction = load_transaction_basics(action)
    transaction['buyer'] = data['from']
    transaction['price'] = float(data['quantity'].split(' ')[0])
    transaction['currency'] = data['quantity'].split(' ')[1]
    sell_data = json.loads(data['assets_seller'])
    for key in sell_data.keys():
        if 'seller' not in transaction:
            transaction['seller'] = key
            transaction['asset_id'] = sell_data[key][0][0]

    session_execute_logged(
        session,
        'INSERT INTO simplemarket_purchases '
        'SELECT :asset_id, :seller, :buyer, :seq, :block_num, :timestamp, :price, :currency '
        'WHERE NOT EXISTS (SELECT seq FROM simplemarket_purchases WHERE seq = :seq)',
        transaction
    )
    session.commit()

    session_execute_logged(
        session,
        'INSERT INTO sales '
        'SELECT l.asset_ids, a.collection, seller, :buyer, '
        'CASE WHEN currency = \'WAX\' THEN price ELSE price / ('
        '   SELECT usd FROM usd_prices WHERE timestamp < :timestamp ORDER BY timestamp DESC LIMIT 1'
        ') END, CASE WHEN currency = \'USD\' THEN price ELSE price * ('
        '   SELECT usd FROM usd_prices WHERE timestamp < :timestamp ORDER BY timestamp DESC LIMIT 1'
        ') END, currency, :asset_id, l.market, NULL, NULL, :seq, :block_num, :timestamp '
        'FROM listings l LEFT JOIN assets a ON a.asset_id = l.asset_ids[1] '
        'WHERE market = \'simplemarket\' AND :asset_id = l.listing_id AND seller = :seller',
        transaction
    )
    session.commit()

    session_execute_logged(
        session,
        'INSERT INTO removed_simplemarket_listings '
        'SELECT l.*, :seq, :block_num '
        'FROM listings l '
        'WHERE market = \'simplemarket\' AND '
        ':asset_id = l.listing_id AND seller = :seller',
        transaction
    )
    session.commit()

    session_execute_logged(
        session,
        'DELETE FROM listings l WHERE sale_id IN ('
        '   SELECT sale_id FROM removed_simplemarket_listings WHERE removed_seq = :seq'
        ')',
        transaction
    )
    session.commit()


@catch_and_log()
def load_simplemarket_cancel(session, action):
    data = _get_data(action)

    transaction = load_transaction_basics(action)
    transaction['owner'] = data['owner']
    transaction['asset_ids'] = []
    for asset_id in data['assetids']:
        transaction['asset_ids'].append(int(asset_id))

    session_execute_logged(
        session,
        'INSERT INTO simplemarket_cancels '
        'SELECT :asset_ids, :owner, :seq, :block_num, :timestamp '
        'WHERE NOT EXISTS (SELECT seq FROM simplemarket_cancels WHERE seq = :seq)',
        transaction
    )
    session.commit()

    for asset_id in transaction['asset_ids']:
        transaction['asset_id'] = asset_id
        session_execute_logged(
            session,
            'INSERT INTO removed_simplemarket_listings '
            'SELECT l.*, :seq, :block_num '
            'FROM listings l '
            'WHERE market = \'simplemarket\' '
            'AND :asset_id = l.listing_id ',
            transaction
        )
        session.commit()

    session_execute_logged(
        session,
        'DELETE FROM listings l WHERE sale_id IN ('
        '   SELECT sale_id FROM removed_simplemarket_listings WHERE removed_seq = :seq'
        ')',
        transaction
    )
    session.commit()


@catch_and_log()
def load_user_picture(session, action):
    data = _get_data(action)
    tx = load_transaction_basics(action)
    tx['account'] = data['account'] if 'account' in data else data['user']
    tx['image'] = data['photo_hash'][0:255]

    with_clause = construct_with_clause(tx)

    session_execute_logged(
        session,
        '{with_clause} '
        'INSERT INTO user_picture_updates '
        'SELECT :account, {image_column}, :seq, :block_num, :timestamp '
        'WHERE NOT EXISTS (SELECT seq FROM user_picture_updates WHERE seq = :seq)'.format(
            with_clause=with_clause,
            image_column=(
                '(SELECT image_id FROM images WHERE image = :image UNION SELECT image_id FROM image_insert_result)'
            ) if tx['image'] else 'NULL',
        ),
        tx
    )


@catch_and_log()
def load_createpack(session, action, contract):
    new_pack = load_transaction_basics(action)
    data = _get_data(action)

    new_pack['contract'] = contract
    new_pack['collection'] = data['collection_name']
    new_pack['template_id'] = data['pack_template_id']
    new_pack['unlock_time'] = datetime.datetime.fromtimestamp(int(data['unlock_time'])) if int(
        data['unlock_time']) > 0 else None
    new_pack['display_data'] = data['display_data']

    session_execute_logged(
        session,
        'INSERT INTO pack_creations ('
        '   contract, collection, unlock_time, display_data, template_id, seq, block_num, timestamp'
        ') '
        'SELECT :contract, :collection, :unlock_time, :display_data, :template_id, :seq, :block_num, :timestamp '
        'WHERE NOT EXISTS ('
        '   SELECT seq FROM pack_creations WHERE seq = :seq'
        ')',
        new_pack
    )


@catch_and_log()
def load_neftyblocksp_lognewpack(session, action):
    new_pack = load_transaction_basics(action)
    data = _get_data(action)

    new_pack['pack_id'] = data['pack_id']
    new_pack['collection'] = data['collection_name'] if 'collection_name' in data else None
    new_pack['contract'] = 'neftyblocksp'

    session_execute_logged(
        session,
        'INSERT INTO packs ('
        '   pack_id, contract, collection, unlock_time, display_data, '
        '   template_id, unpack_url, seq, block_num, timestamp '
        ') '
        'SELECT :pack_id, :contract, :collection, unlock_time, display_data, template_id, '
        'CONCAT(\'/unpack?author=\', :collection), :seq, :block_num, :timestamp '
        'FROM pack_creations c WHERE c.seq = :seq - 1 '
        'AND NOT EXISTS (SELECT seq FROM packs WHERE seq = :seq) ',
        new_pack
    )


@catch_and_log()
def load_setpackdata(session, action, contract):
    new_pack_data = load_transaction_basics(action)
    data = _get_data(action)

    new_pack_data['pack_id'] = data['pack_id']
    new_pack_data['display_data'] = data['display_data']
    new_pack_data['contract'] = contract

    session_execute_logged(
        session,
        'INSERT INTO pack_display_updates ('
        '   pack_id, contract, new_display_data, old_display_data, seq, block_num, timestamp '
        ') '
        'SELECT :pack_id, :contract, :display_data, '
        '(SELECT display_data FROM packs WHERE pack_id = :pack_id AND contract = :contract), '
        ':seq, :block_num, :timestamp '
        'WHERE NOT EXISTS (SELECT seq FROM pack_display_updates WHERE seq = :seq) ',
        new_pack_data
    )

    session_execute_logged(
        session,
        'UPDATE packs SET display_data = :display_data WHERE pack_id = :pack_id AND contract = :contract ',
        new_pack_data
    )


@catch_and_log()
def load_nfthivepacks_lognewpack(session, action):
    new_pack = load_transaction_basics(action)
    data = _get_data(action)

    new_pack['pack_id'] = data['pack_id']
    new_pack['release_id'] = data['release_id'] if 'release_id' in data else None
    new_pack['collection'] = data['collection_name'] if 'collection_name' in data else None
    new_pack['template_id'] = data['template_id'] if 'template_id' in data else None
    new_pack['display_data'] = data['display_data'] if 'display_data' in data else None
    new_pack['contract'] = 'nfthivepacks'

    session_execute_logged(
        session,
        'INSERT INTO packs ('
        '   pack_id, contract, collection, unlock_time, seq, timestamp, display_data, '
        '   template_id, block_num, release_id, unpack_url '
        ') '
        'SELECT :pack_id, :contract, :collection, NULL, :seq, :timestamp, :display_data, :template_id, :block_num, '
        ':release_id, CONCAT(\'/unpack?author=\', :collection) '
        'WHERE NOT EXISTS (SELECT seq FROM packs WHERE seq = :seq) ',
        new_pack
    )


@catch_and_log()
def load_delpack(session, action, contract):
    new_pack_data = load_transaction_basics(action)
    data = _get_data(action)

    new_pack_data['pack_id'] = data['pack_id']
    new_pack_data['contract'] = contract

    session_execute_logged(
        session,
        'INSERT INTO removed_packs SELECT p.*, :seq, :block_num FROM packs p '
        'WHERE pack_id = :pack_id AND contract = :contract ',
        new_pack_data
    )

    session_execute_logged(
        session,
        'DELETE FROM packs WHERE pack_id = :pack_id AND contract = :contract ',
        new_pack_data
    )


@catch_and_log()
def load_delrelease(session, action):
    new_pack_data = load_transaction_basics(action)
    data = _get_data(action)

    new_pack_data['release_id'] = data['release_id']

    session_execute_logged(
        session,
        'INSERT INTO removed_packs SELECT p.*, :seq, :block_num FROM packs p '
        'WHERE release_id = :release_id AND contract = \'nfthivepacks\' ',
        new_pack_data
    )

    session_execute_logged(
        session,
        'DELETE FROM packs WHERE release_id = :release_id AND contract = \'nfthivepacks\' ',
        new_pack_data
    )


@catch_and_log()
def load_setpacktime(session, action, contract):
    new_pack_data = load_transaction_basics(action)
    data = _get_data(action)

    new_pack_data['pack_id'] = data['pack_id']
    new_pack_data['unlock_time'] = datetime.datetime.fromtimestamp(
        int(data['new_unlock_time'])) if 'new_unlock_time' in data and int(
        data['new_unlock_time']) > 0 else datetime.datetime.fromtimestamp(
        int(data['unlock_time'])) if 'unlock_time' in data and int(
        data['unlock_time']) > 0 else None
    new_pack_data['contract'] = contract

    session_execute_logged(
        session,
        'INSERT INTO pack_time_updates ('
        '   pack_id, contract, new_unlock_time, old_unlock_time, seq, block_num, timestamp'
        ') '
        'SELECT :pack_id, :contract, :unlock_time, '
        '(SELECT unlock_time FROM packs WHERE pack_id = :pack_id AND contract = :contract), '
        ':seq, :block_num, :timestamp '
        'WHERE NOT EXISTS (SELECT seq FROM pack_time_updates WHERE seq = :seq) ',
        new_pack_data
    )

    session_execute_logged(
        session,
        'UPDATE packs SET unlock_time = :unlock_time WHERE pack_id = :pack_id AND contract = :contract ',
        new_pack_data
    )


@catch_and_log()
def load_delpool(session, action):
    new_pack_data = load_transaction_basics(action)
    data = _get_data(action)

    new_pack_data['pool_id'] = data['pool_id']

    session_execute_logged(
        session,
        'INSERT INTO removed_pool_assets '
        'SELECT a.*, :seq, :block_num FROM pool_assets a '
        'WHERE pool_id = :pool_id AND contract = \'nfthivepacks\' ',
        new_pack_data
    )

    session_execute_logged(
        session,
        'DELETE FROM pool_assets WHERE pool_id = :pool_id AND contract = \'nfthivepacks\' ',
        new_pack_data
    )

    session_execute_logged(
        session,
        'INSERT INTO removed_pools '
        'SELECT p.*, :seq, :block_num '
        'FROM pools p '
        'WHERE pool_id = :pool_id AND contract = \'nfthivepacks\' ',
        new_pack_data
    )

    session_execute_logged(
        session,
        'DELETE FROM pools WHERE pool_id = :pool_id AND contract = \'nfthivepacks\' ',
        new_pack_data
    )


@catch_and_log()
def addpool(session, action, contract):
    new_pack_data = load_transaction_basics(action)
    data = _get_data(action)

    new_pack_data['pool_id'] = data['pool_id']
    new_pack_data['release_id'] = data['release_id']
    new_pack_data['contract'] = contract

    session_execute_logged(
        session,
        'INSERT INTO pools '
        'SELECT :pool_id, :contract, :release_id, :seq, :block_num, :timestamp '
        'WHERE (:pool_id, :contract, :release_id) NOT IN ('
        '   SELECT pool_id, contract, release_id FROM pools WHERE release_id = :release_id'
        ') ',
        new_pack_data
    )


@catch_and_log()
def addassets(session, action, contract):
    new_pack_data = load_transaction_basics(action)
    data = _get_data(action)

    new_pack_data['pool_id'] = data['pool_id']
    new_pack_data['contract'] = contract

    if len(data['asset_ids']) == 1:
        new_pack_data['asset_id'] = data['asset_ids'][0]
        session_execute_logged(
            session,
            'INSERT INTO pool_assets '
            'SELECT :pool_id, :contract, :asset_id, :seq, :block_num, :timestamp '
            'WHERE (:pool_id, :contract, :asset_id) NOT IN ('
            '   SELECT pool_id, contract, asset_id FROM pool_assets WHERE asset_id = :asset_id'
            ') ',
            new_pack_data
        )
    elif len(data['asset_ids']) > 1:
        new_pack_data['asset_ids'] = data['asset_ids']
        session_execute_logged(
            session,
            'INSERT INTO pool_assets '
            'SELECT * FROM (SELECT :pool_id AS pool_id, :contract AS contract, '
            'CAST(UNNEST(:asset_ids) AS bigint) AS a_id, :seq AS seq, :block_num AS block_num, '
            'CAST(:timestamp AS timestamp) AS timestamp) a '
            'WHERE (pool_id, contract, a_id) NOT IN ('
            '   SELECT pool_id, contract, asset_id FROM pool_assets WHERE asset_id = a_id'
            ') ',
            new_pack_data
        )


@catch_and_log()
def remassets(session, action, contract):
    new_pack_data = load_transaction_basics(action)
    data = _get_data(action)

    new_pack_data['pool_id'] = data['pool_id']
    new_pack_data['contract'] = contract

    for asset_id in data['asset_ids']:
        new_pack_data['asset_id'] = asset_id
        session_execute_logged(
            session,
            'INSERT INTO pool_deletions '
            'SELECT :pool_id, :contract, :asset_id, :seq, :block_num, :timestamp '
            'WHERE (:pool_id, :contract, :asset_id) NOT IN ('
            '   SELECT pool_id, contract, asset_id FROM pool_assets WHERE asset_id = :asset_id'
            ') ',
            new_pack_data
        )


@catch_and_log()
def log_pack_result(session, action, contract):
    new_pack_data = load_transaction_basics(action)
    data = _get_data(action)

    new_pack_data['contract'] = contract

    if len(data['result_asset_ids']) == 1:
        new_pack_data['asset_id'] = data['result_asset_ids'][0]
        session_execute_logged(
            session,
            'DELETE FROM pool_assets '
            'WHERE contract = :contract AND asset_id = :asset_id',
            new_pack_data
        )

        session_execute_logged(
            session,
            'INSERT INTO removed_pool_assets '
            'SELECT a.*, :seq, :block_num FROM pool_assets a '
            'WHERE contract = :contract AND asset_id = :asset_id ',
            new_pack_data
        )
    elif len(data['result_asset_ids']) > 1:
        new_pack_data['asset_ids'] = tuple(data['result_asset_ids'])
        session_execute_logged(
            session,
            'DELETE FROM pool_assets '
            'WHERE contract = :contract AND asset_id IN :asset_ids',
            new_pack_data
        )

        session_execute_logged(
            session,
            'INSERT INTO removed_pool_assets '
            'SELECT a.*, :seq, :block_num FROM pool_assets a '
            'WHERE contract = :contract AND asset_id IN :asset_ids ',
            new_pack_data
        )


@catch_and_log()
def load_announcepack(session, action, contract):
    new_pack_data = load_transaction_basics(action)
    data = _get_data(action)

    new_pack_data['display_data'] = data['display_data'] if 'display_data' in data.keys() else None
    new_pack_data['contract'] = contract
    new_pack_data['collection'] = data['collection_name']
    new_pack_data['unlock_time'] = datetime.datetime.fromtimestamp(int(data['unlock_time'])) if int(
        data['unlock_time']) > 0 else None

    session_execute_logged(
        session,
        'INSERT INTO pack_announcements ('
        '   contract, collection, display_data, unlock_time, seq, block_num, timestamp '
        ') '
        'SELECT :contract, :collection, :display_data, :unlock_time, :seq, :block_num, :timestamp '
        'WHERE NOT EXISTS (SELECT seq FROM pack_announcements WHERE seq = :seq) ',
        new_pack_data
    )


@catch_and_log()
def load_atomicpacksx_lognewpack(session, action):
    new_pack = load_transaction_basics(action)
    data = _get_data(action)

    new_pack['pack_id'] = data['pack_id']
    new_pack['collection'] = data['collection_name'] if 'collection_name' in data else None
    new_pack['contract'] = 'atomicpacksx'

    session_execute_logged(
        session,
        'INSERT INTO packs ('
        '   pack_id, contract, collection, unlock_time, display_data, '
        '   unpack_url, seq, block_num, timestamp '
        ') '
        'SELECT :pack_id, :contract, :collection, unlock_time, display_data, '
        'CONCAT(\'/unpack?author=\', :collection), :seq, :block_num, :timestamp '
        'FROM pack_announcements c WHERE c.seq = :seq - 1 '
        'AND NOT EXISTS (SELECT seq FROM packs WHERE seq = :seq) ',
        new_pack
    )


@catch_and_log()
def load_completepack(session, action, contract):
    new_pack_data = load_transaction_basics(action)
    data = _get_data(action)

    new_pack_data['pack_id'] = data['pack_id']
    new_pack_data['pack_template_id'] = data['pack_template_id'] if 'pack_template_id' in data.keys() else data[
        'template_id']
    new_pack_data['contract'] = contract

    session_execute_logged(
        session,
        'INSERT INTO pack_template_updates ('
        '   pack_id, contract, new_template_id, old_template_id, seq, block_num, timestamp'
        ') '
        'SELECT :pack_id, :contract, :pack_template_id, '
        '(SELECT template_id FROM packs WHERE pack_id = :pack_id AND contract = :contract), :seq, :block_num, '
        ':timestamp '
        'WHERE NOT EXISTS (SELECT seq FROM pack_template_updates WHERE seq = :seq) ',
        new_pack_data
    )

    session_execute_logged(
        session,
        'UPDATE packs SET template_id = :pack_template_id WHERE contract = :contract AND pack_id = :pack_id ',
        new_pack_data
    )


@catch_and_log()
def load_lognewoffer(session, action):
    new_buy_offer_data = load_transaction_basics(action)
    data = _get_data(action)
    new_buy_offer_data['price'] = float(data['offer'].split(' ')[0])
    new_buy_offer_data['currency'] = data['offer'].split(' ')[1]

    new_buy_offer_data['offer_id'] = data['offer_id']
    new_buy_offer_data['buyer'] = data['buyer']
    new_buy_offer_data['template_id'] = data['template_id']
    new_buy_offer_data['collection'] = data['collection_name']
    new_buy_offer_data['name'] = data['asset_name']
    new_buy_offer_data['image'] = data['image'] if 'image' in data else ''
    new_buy_offer_data['video'] = data['video'] if 'video' in data else ''

    with_clause = construct_with_clause(new_buy_offer_data)
    session_execute_logged(
        session,
        '{with_clause} '
        'INSERT INTO buyoffers ('
        '   offer_id, price, currency, buyer, template_id, collection, name_id, image_id, video_id, active, seq, '
        '   block_num, timestamp'
        ') '
        'SELECT :offer_id, :price, :currency, :buyer, :template_id, :collection, {name_column}, {image_column}, '
        '{video_column}, TRUE, :seq, :block_num, :timestamp '
        'WHERE NOT EXISTS (SELECT seq FROM buyoffers WHERE seq = :seq) '.format(
            with_clause=with_clause,
            name_column=(
                '(SELECT name_id FROM names WHERE name = :name UNION SELECT name_id FROM name_insert_result)'
            ) if new_buy_offer_data['name'] else 'NULL',
            image_column=(
                '(SELECT image_id FROM images WHERE image = :image UNION SELECT image_id FROM image_insert_result)'
            ) if new_buy_offer_data['image'] else 'NULL',
            video_column=(
                '(SELECT video_id FROM videos WHERE video = :video UNION SELECT video_id FROM video_insert_result)'
            ) if new_buy_offer_data['video'] else 'NULL',
        ),
        new_buy_offer_data
    )


@catch_and_log()
def load_logbalance(session, action):
    log_balance_data = load_transaction_basics(action)
    data = _get_data(action)

    log_balance_data['balance'] = float(data['balance'].replace(' WAX', ''))
    log_balance_data['buyer'] = data['buyer']

    session_execute_logged(
        session,
        'INSERT INTO buyoffer_balance_updates ('
        '   buyer, balance, seq, block_num, timestamp '
        ') '
        'SELECT :buyer, :balance, :seq, :block_num, :timestamp '
        'WHERE NOT EXISTS (SELECT seq FROM buyoffer_balance_updates WHERE seq = :seq) ',
        log_balance_data
    )


@catch_and_log()
def load_logerase(session, action):
    erase_data = load_transaction_basics(action)
    data = _get_data(action)
    erase_data['offer_id'] = data['offer_id']

    session_execute_logged(
        session,
        'INSERT INTO buyoffer_cancels ('
        '   offer_id, seq, block_num, timestamp '
        ') '
        'SELECT :offer_id, :seq, :block_num, :timestamp '
        'WHERE NOT EXISTS (SELECT seq FROM buyoffer_cancels WHERE seq = :seq) ',
        erase_data
    )


@catch_and_log()
def load_logsale(session, action):
    sale_data = load_transaction_basics(action)
    data = _get_data(action)
    sale_data['offer_id'] = data['offer_id'] if 'offer_id' in data else 0
    sale_data['asset_id'] = data['asset_id']
    sale_data['taker'] = data['taker'] if 'taker' in data else 'nft.hive'
    sale_data['seller'] = data['seller'] if 'seller' in data else ''
    sale_data['price'] = data['amount'].replace(' WAX', '')

    session_execute_logged(
        session,
        'INSERT INTO buyoffer_purchases ('
        '   offer_id, asset_id, price, taker, seller, seq, block_num, timestamp '
        ') '
        'SELECT :offer_id, :asset_id, :price, :taker, :seller, :seq, :block_num, :timestamp '
        'WHERE NOT EXISTS (SELECT seq FROM buyoffer_purchases WHERE seq = :seq) ',
        sale_data
    )


@catch_and_log()
def load_addtag(session, action):
    set_data = load_transaction_basics(action)
    data = _get_data(action)

    set_data['tag_name'] = data['tag_name']

    session_execute_logged(
        session,
        'INSERT INTO tags (tag_name, seq, block_num, timestamp) '
        'SELECT :tag_name, :seq, :block_num, :timestamp  '
        'WHERE NOT EXISTS (SELECT seq FROM tags WHERE seq = :seq) ',
        set_data
    )


@catch_and_log()
def load_settag(session, action):
    set_data = load_transaction_basics(action)
    data = _get_data(action)

    set_data['tag_id'] = data['tag_id']
    set_data['collection'] = data['collection_name']

    session_execute_logged(
        session,
        'INSERT INTO tag_updates SELECT :tag_id, :collection, :seq, :block_num, :timestamp  '
        'WHERE NOT EXISTS (SELECT seq FROM tag_updates WHERE seq = :seq) ',
        set_data
    )


@catch_and_log()
def load_suggesttag(session, action):
    data = _get_data(action)

    new_suggestion = load_transaction_basics(action)

    new_suggestion['suggester'] = action['act']['authorization'][0]['actor']
    new_suggestion['tag_id'] = data['tag_id']
    new_suggestion['collection'] = data['collection_name']

    session_execute_logged(
        session,
        'INSERT INTO tag_suggestions '
        'SELECT :suggester, :tag_id, :collection, :seq, :block_num, :timestamp  '
        'WHERE NOT EXISTS (SELECT seq FROM tag_suggestions WHERE seq = :seq AND tag_id = :tag_id) ',
        new_suggestion
    )


@catch_and_log()
def load_account_values(session, action):
    data = _get_data(action)

    if data['list_name'] == 'templ.link':
        return
    new_action = load_transaction_basics(action)

    new_action['account'] = data['account']
    new_action['list_name'] = data['list_name']
    new_action['values'] = data['values_to_add'] if action['act']['name'] == 'addaccvalues' else data[
        'values_to_remove']

    for value in new_action['values']:
        if len(value) > 13:
            return

    if len(new_action['account']) > 13:
        return

    session_execute_logged(
        session,
        'INSERT INTO account_value_actions '
        '(account, action_name, list_name, values, seq, block_num, timestamp) '
        'SELECT :account, :action_name, :list_name, :values, :seq, :block_num, :timestamp '
        'WHERE NOT EXISTS (SELECT seq FROM account_value_actions WHERE seq = :seq) ',
        new_action
    )


@catch_and_log()
def load_verifications(session, transaction):
    data = _get_data(transaction)

    new_action = load_transaction_basics(transaction)

    new_action['account'] = data['authorized_account']
    new_action['collection'] = data['collection_name']

    if len(new_action['collection']) > 12:
        return

    session_execute_logged(
        session,
        'INSERT INTO verification_actions '
        '(collection, action_name, account, seq, block_num, timestamp) '
        'SELECT :collection, :action_name, :account, :seq, :block_num, :timestamp '
        'WHERE NOT EXISTS (SELECT seq FROM verification_actions WHERE seq = :seq) ',
        new_action
    )


@catch_and_log()
def load_nefty_account_values(session, action):
    data = _get_data(action)

    new_action = load_transaction_basics(action)

    new_action['account'] = action['act']['account']
    new_action['list_name'] = data['list']
    new_action['values'] = data['collections']

    for value in new_action['values']:
        if len(value) > 12:
            return

    if len(new_action['account']) > 12:
        return

    if len(new_action['list_name']) > 12:
        return

    session_execute_logged(
        session,
        'INSERT INTO account_value_actions '
        '(account, action_name, list_name, values, seq, block_num, timestamp) '
        'SELECT :account, :action_name, :list_name, :values, :seq, :block_num, :timestamp '
        'WHERE NOT EXISTS (SELECT seq FROM account_value_actions WHERE seq = :seq) ',
        new_action
    )


@catch_and_log()
def load_status_addtolist(session, action):
    data = _get_data(action)

    new_action = load_transaction_basics(action)

    new_action['market'] = data['market']
    new_action['list_name'] = data['label']

    for collection in data['collections']:
        new_action['collection'] = collection
        if len(new_action['collection']) > 12:
            continue
        session_execute_logged(
            session,
            'INSERT INTO market_statuses '
            '(market, list_name, collection, seq, block_num, timestamp) '
            'SELECT :market, :list_name, :collection, :seq, :block_num, :timestamp '
            'WHERE (:market, :list_name, :collection) NOT IN ('
            'SELECT market, list_name, collection FROM market_statuses '
            'WHERE market = :market AND list_name = :list_name AND collection = :collection) ',
            new_action
        )


@catch_and_log()
def load_status_remfromlist(session, action):
    data = _get_data(action)

    new_action = load_transaction_basics(action)

    new_action['market'] = data['market']
    new_action['list_name'] = data['label']

    for collection in data['collections']:
        new_action['collection'] = collection
        if len(new_action['collection']) > 12:
            continue
        session_execute_logged(
            session,
            'DELETE FROM market_statuses '
            'WHERE market = :market AND list_name = :list_name AND collection = :collection ',
            new_action
        )


@catch_and_log()
def load_status_setlist(session, action):
    data = _get_data(action)

    new_action = load_transaction_basics(action)

    new_action['market'] = data['market']
    new_action['list_name'] = data['label']

    session_execute_logged(
        session,
        'DELETE FROM market_statuses '
        'WHERE market = :market AND list_name = :list_name ',
        new_action
    )

    for collection in data['collections']:
        new_action['collection'] = collection
        if len(new_action['collection']) > 12:
            continue
        session_execute_logged(
            session,
            'INSERT INTO market_statuses '
            '(market, list_name, collection, seq, block_num, timestamp) '
            'SELECT :market, :list_name, :collection, :seq, :block_num, :timestamp '
            'WHERE (:market, :list_name, :collection) NOT IN ('
            'SELECT market, list_name, collection FROM market_statuses '
            'WHERE market = :market AND list_name = :list_name AND collection = :collection) ',
            new_action
        )


@catch_and_log()
def load_status_logvotes(session, action):
    data = _get_data(action)

    new_action = load_transaction_basics(action)

    new_action['voter'] = data['voter']

    session_execute_logged(
        session,
        'DELETE FROM collection_votes '
        'WHERE voter = :voter ',
        new_action
    )

    for collection in data['upvotes']:
        new_action['collection'] = collection
        new_action['amount'] = float(data['vote_power'].replace(' WAX', ''))
        session_execute_logged(
            session,
            'INSERT INTO collection_votes '
            '(voter, collection, amount, seq, block_num, timestamp) '
            'SELECT :voter, :collection, :amount, :seq, :block_num, :timestamp '
            'WHERE (:voter, :collection) NOT IN (SELECT voter, collection FROM collection_votes '
            'WHERE voter = :voter AND collection = :collection) ',
            new_action
        )
    for collection in data['downvotes']:
        new_action['collection'] = collection
        new_action['amount'] = -float(data['vote_power'].replace(' WAX', ''))
        session_execute_logged(
            session,
            'INSERT INTO collection_votes '
            '(voter, collection, amount, seq, block_num, timestamp) '
            'SELECT :voter, :collection, :amount, :seq, :block_num, :timestamp '
            'WHERE (:voter, :collection) NOT IN (SELECT voter, collection FROM collection_votes '
            'WHERE voter = :voter AND collection = :collection) ',
            new_action
        )


@catch_and_log()
def load_redeem(session, transaction):
    data = _get_data(transaction)

    new_action = load_transaction_basics(transaction)

    new_action['asset_owner'] = data['asset_owner']
    new_action['asset_id'] = data['asset_id']

    session_execute_logged(
        session,
        'INSERT INTO redeem_actions (asset_owner, asset_id, action, seq, block_num, timestamp) '
        'SELECT :asset_owner, :asset_id, :action_name, :seq, :block_num, :timestamp '
        'WHERE NOT EXISTS (SELECT seq FROM redeem_actions WHERE seq = :seq) ',
        new_action
    )


@catch_and_log()
def load_accept_redemption(session, transaction):
    data = _get_data(transaction)

    new_action = load_transaction_basics(transaction)

    new_action['authorized_account'] = data['authorized_account']
    new_action['asset_id'] = data['asset_id']

    session_execute_logged(
        session,
        'INSERT INTO redeem_actions '
        '(authorized_account, asset_id, action, seq, block_num, timestamp) '
        'SELECT :authorized_account, :asset_id, :action_name, :seq, :block_num, :timestamp '
        'WHERE NOT EXISTS (SELECT seq FROM redeem_actions WHERE seq = :seq) '
        , new_action
    )


@catch_and_log()
def load_reject_redemption(session, transaction):
    data = _get_data(transaction)

    new_action = load_transaction_basics(transaction)

    new_action['authorized_account'] = data['authorized_account']
    new_action['asset_id'] = data['asset_id']

    with_clause = construct_memo_clause(new_action)

    session_execute_logged(
        session,
        '{with_clause} '
        'INSERT INTO redeem_actions '
        '(authorized_account, asset_id, action, memo_id, seq, block_num, timestamp) '
        'SELECT :authorized_account, :asset_id, :action_name, {memo_column}, :seq, :block_num, :timestamp '
        'WHERE NOT EXISTS (SELECT seq FROM redeem_actions WHERE seq = :seq) '.format(
            with_clause=with_clause,
            memo_column=(
                '(SELECT memo_id FROM memos WHERE md5(memo) = md5(:memo) UNION SELECT memo_id FROM insert_result)'
            ) if 'memo' in new_action and new_action['memo'] else 'NULL'
        ),
        new_action
    )


@catch_and_log()
def load_release_redemption(session, transaction):
    data = _get_data(transaction)

    new_action = load_transaction_basics(transaction)

    new_action['authorized_account'] = data['authorized_account']
    new_action['asset_id'] = data['asset_id']

    session_execute_logged(
        session,
        'INSERT INTO redeem_actions '
        '(authorized_account, asset_id, action, seq, block_num, timestamp) '
        'SELECT :authorized_account, :asset_id, :action_name, :seq, :block_num, :timestamp '
        'WHERE NOT EXISTS (SELECT seq FROM redeem_actions WHERE seq = :seq) '
        , new_action
    )


@catch_and_log()
def load_airdrop(session, transaction):
    data = _get_data(transaction)

    new_action = load_transaction_basics(transaction)

    new_action['airdrop_id'] = data['airdrop_id']
    new_action['token'] = data['token']
    new_action['contract'] = data['contract']
    new_action['creator'] = data['creator']
    if 'holder_contract' not in data:
        return
    new_action['holder_contract'] = data['holder_contract']
    new_action['min_amount'] = data['min_amount']
    new_action['max_amount'] = data['max_amount']
    new_action['snapshot_time'] = datetime.datetime.fromtimestamp(data['snapshot_time'])
    new_action['display_data'] = data['display_data']
    new_action['ready'] = data['ready']

    session_execute_logged(
        session,
        'INSERT INTO wuffi_airdrops '
        '(airdrop_id, token, contract, creator, holder_contract, min_amount, max_amount, snapshot_time, '
        'display_data, ready, seq, block_num, timestamp) '
        'SELECT :airdrop_id, :token, :contract, :creator, :holder_contract, :min_amount, :max_amount, '
        ':snapshot_time, :display_data, :ready, :seq, :block_num, :timestamp '
        'WHERE NOT EXISTS (SELECT seq FROM wuffi_airdrops WHERE seq = :seq) ',
        new_action
    )


@catch_and_log()
def load_addclaimers(session, transaction):
    data = _get_data(transaction)

    new_action = load_transaction_basics(transaction)

    new_action['airdrop_id'] = data['airdrop_id']
    claimers = data['claimers']

    for claimer in claimers:
        new_action['claimer'] = claimer['claimer']
        new_action['tokens'] = claimer['amount']

        session_execute_logged(
            session,
            'INSERT INTO wuffi_airdrop_claimers (airdrop_id, claimer, tokens, seq, block_num, timestamp) '
            'SELECT :airdrop_id, :claimer, :tokens, :seq, :block_num, :timestamp '
            'WHERE NOT EXISTS (SELECT seq FROM wuffi_airdrop_claimers WHERE seq = :seq AND claimer = :claimer) ',
            new_action
        )


@catch_and_log()
def load_delairdrop(session, transaction):
    data = _get_data(transaction)

    new_action = load_transaction_basics(transaction)

    new_action['airdrop_id'] = data['airdrop_id']

    session_execute_logged(
        session,
        'INSERT INTO removed_wuffi_airdrops '
        'SELECT *, :seq, :block_num FROM wuffi_airdrops '
        'WHERE airdrop_id = :airdrop_id AND NOT EXISTS ('
        '   SELECT seq FROM removed_wuffi_airdrops WHERE removed_seq = :seq'
        ') ',
        new_action
    )

    session.commit()

    session_execute_logged(
        session,
        'DELETE FROM wuffi_airdrops '
        'WHERE airdrop_id = :airdrop_id ',
        new_action
    )


@catch_and_log()
def load_claim_airdrop(session, transaction):
    data = _get_data(transaction)

    new_action = load_transaction_basics(transaction)

    new_action['airdrop_id'] = data['airdrop_id']
    new_action['account'] = data['account']

    session_execute_logged(
        session,
        'INSERT INTO wuffi_airdrop_claims (airdrop_id, account, seq, block_num, timestamp) '
        'SELECT :airdrop_id, :account, :seq, :block_num, :timestamp '
        'WHERE NOT EXISTS (SELECT seq FROM wuffi_airdrop_claims WHERE seq = :seq) ',
        new_action
    )


@catch_and_log()
def load_wuf_setready(session, transaction):
    data = _get_data(transaction)

    new_action = load_transaction_basics(transaction)

    new_action['airdrop_id'] = data['airdrop_id']
    new_action['ready'] = data['ready']

    session_execute_logged(
        session,
        'INSERT INTO wuffi_airdrop_ready_updates (airdrop_id, ready, old_ready, seq, block_num, timestamp) '
        'SELECT :airdrop_id, :ready, (SELECT ready FROM wuffi_airdrops WHERE airdrop_id = :airdrop_id), '
        ':seq, :block_num, :timestamp '
        'WHERE NOT EXISTS (SELECT seq FROM wuffi_airdrop_ready_updates WHERE seq = :seq) ',
        new_action
    )

    session_execute_logged(
        session,
        'UPDATE wuffi_airdrops '
        'SET ready = :ready '
        'WHERE airdrop_id = :airdrop_id ',
        new_action
    )


@catch_and_log()
def load_craft(session, update, contract):
    new_drop = load_transaction_basics(update)
    data = _get_data(update)
    if 'craft_id' not in data:
        return
    new_drop['craft_id'] = data['craft_id']
    new_drop['collection'] = data['collection_name']
    new_drop['collection_name'] = data['collection_name']
    new_drop['display_data'] = data['display_data'] if 'display_data' in data else None

    new_drop['unlock_time'] = datetime.datetime.fromtimestamp(data['unlock_time']) if 'unlock_time' in data and data['unlock_time'] else None
    new_drop['num_crafted'] = 0
    new_drop['contract'] = contract

    new_drop['recipe'] = json.dumps(data['recipe']) if 'recipe' in data else None
    new_drop['outcomes'] = json.dumps(data['outcomes']) if 'outcomes' in data else json.dumps({
        "outcomes": [{"template_id": data['outcome_template_id'], "pool_id": 0, "odds": 1, "guaranteed": True}],
        "token_outcomes": [], "min_random_outcomes": 0, "max_random_outcomes": 0, "min_random_token_outcomes": 0,
        "max_random_token_outcomes": 0
    }) if 'outcome_template_id' in data else None

    new_drop['total'] = data['total'] if 'total' in data else 0

    session_execute_logged(
        session,
        'INSERT INTO crafts (craft_id, collection, display_data, unlock_time, num_crafted, erased, contract, '
        'ready, recipe, outcomes, total, seq, block_num, timestamp) '
        'SELECT :craft_id, :collection, :display_data, :unlock_time, 0, FALSE, :contract, '
        'TRUE, :recipe, :outcomes, :total, :seq, :block_num, :timestamp '
        'WHERE NOT EXISTS (SELECT seq FROM crafts WHERE seq = :seq) ', new_drop
    )
    session.commit()


@catch_and_log()
def load_craft_times_update(session, update):
    data = _get_data(update)

    craft = load_transaction_basics(update)

    if 'unlock_time' not in data:
        return

    craft['unlock_time'] = datetime.datetime.fromtimestamp(data['unlock_time']) if data['unlock_time'] else None
    craft['end_time'] = datetime.datetime.fromtimestamp(data['end_time']) if 'end_time' in data and data[
        'end_time'] else None
    craft['craft_id'] = data['craft_id']

    session_execute_logged(
        session,
        'INSERT INTO craft_times_updates (craft_id, new_unlock_time, old_unlock_time, seq, block_num, timestamp, '
        'new_end_time, old_end_time) '
        'SELECT :craft_id, :unlock_time, (SELECT unlock_time FROM crafts WHERE craft_id = :craft_id), '
        ':seq, :block_num, :timestamp, :end_time, (SELECT end_time FROM crafts WHERE craft_id = :craft_id) '
        'WHERE NOT EXISTS (SELECT seq FROM craft_times_updates WHERE seq = :seq)',
        craft
    )

    session_execute_logged(
        session,
        'UPDATE crafts SET unlock_time = :unlock_time, end_time = :end_time WHERE craft_id = :craft_id ',
        craft
    )


@catch_and_log()
def load_craft_update(session, update):
    data = _get_data(update)

    craft = load_transaction_basics(update)

    craft['display_data'] = data['display_data']
    craft['craft_id'] = data['craft_id']

    session_execute_logged(
        session,
        'INSERT INTO craft_updates (craft_id, new_display_data, old_display_data, seq, block_num, timestamp) '
        'SELECT :craft_id, :display_data, (SELECT display_data FROM crafts WHERE craft_id = :craft_id), :seq, '
        ':block_num, :timestamp '
        'WHERE NOT EXISTS (SELECT seq FROM craft_updates WHERE seq = :seq) ', craft)

    session_execute_logged(
        session,
        'UPDATE crafts SET display_data = :display_data WHERE craft_id = :craft_id ', craft
    )

    session.commit()


@catch_and_log()
def load_craft_set_ready(session, update):
    data = _get_data(update)

    craft = load_transaction_basics(update)
    craft['craft_id'] = data['craft_id']

    session_execute_logged(
        session,
        'INSERT INTO craft_ready_updates (craft_id, ready, seq, block_num, timestamp) '
        'SELECT :craft_id, TRUE, :seq, :block_num, :timestamp '
        'WHERE NOT EXISTS (SELECT seq FROM craft_ready_updates WHERE seq = :seq) ', craft)

    session_execute_logged(
        session,
        'UPDATE crafts SET ready = TRUE WHERE craft_id = :craft_id ', craft
    )

    session.commit()


@catch_and_log()
def load_craft_result(session, update):
    data = _get_data(update)

    craft = load_transaction_basics(update)
    craft['crafter'] = data['crafter'] if 'crafter' in data else None
    craft['craft_id'] = data['craft_id'] if 'craft_id' in data else None
    craft['result_id'] = data['result_id'] if 'result_id' in data else None
    result_asset_ids = data['result_asset_ids'] if 'result_asset_ids' in data else []
    minted_templates = data['minted_templates'] if 'minted_templates' in data else []
    craft['token_results'] = data['token_results'] if 'token_results' in data else []
    craft['layer_ingredients'] = json.dumps(data['layer_ingredients']) if 'layer_ingredients' in data else None
    craft['lockups'] = None
    if 'lock_ups' in data:
        craft['lockups'] = []
        for lockup in data['lock_ups']:
            craft['lockups'].append(int(lockup))

    asset_ids = []
    for asset_id in result_asset_ids:
        asset_ids.append(int(asset_id))

    craft['result_asset_ids'] = asset_ids

    template_ids = []
    for template_id in minted_templates:
        template_ids.append(int(template_id))

    craft['minted_templates'] = template_ids

    session_execute_logged(
        session,
        'INSERT INTO craft_results '
        'SELECT :craft_id, :result_id, :crafter, :result_asset_ids, :minted_templates, :token_results, :seq, '
        ':block_num, :timestamp '
        'WHERE NOT EXISTS (SELECT seq FROM craft_results WHERE seq = :seq)',
        craft
    )

    if craft['layer_ingredients'] and len(craft['layer_ingredients']) > 0 and craft['layer_ingredients'] != '[]':
        session_execute_logged(
            session,
            'INSERT INTO craft_minting '
            'SELECT :craft_id, :result_id, :crafter, :layer_ingredients, :lockups, NULL, FALSE, :seq, :block_num, '
            ':timestamp '
            'WHERE NOT EXISTS (SELECT seq FROM craft_minting WHERE seq = :seq)',
            craft
        )


@catch_and_log()
def load_erase_craft(session, transfer):
    data = _get_data(transfer)
    new_transfer = load_transaction_basics(transfer)
    new_transfer['craft_id'] = data['craft_id']

    session_execute_logged(
        session,
        'INSERT INTO craft_erase_updates (craft_id, erased, seq, block_num, timestamp) '
        'SELECT :craft_id, TRUE, :seq, :block_num, :timestamp '
        'WHERE NOT EXISTS (SELECT seq FROM craft_erase_updates WHERE seq = :seq)',
        new_transfer
    )

    session_execute_logged(
        session,
        'UPDATE crafts SET erased = TRUE WHERE craft_id = :craft_id ',
        new_transfer
    )

    session.commit()
    return new_transfer['craft_id']


@catch_and_log()
def load_claim_craft(session, transfer):
    data = _get_data(transfer)
    new_transfer = load_transaction_basics(transfer)
    new_transfer['crafter'] = data['user_name']
    new_transfer['craft_id'] = data['craft_id']

    session_execute_logged(
        session,
        'INSERT INTO craft_actions ('
        '   craft_id, crafter, action, seq, block_num, timestamp '
        ') '
        'SELECT :craft_id, :crafter, \'craft\', :seq, :block_num, :timestamp '
        'WHERE NOT EXISTS (SELECT seq FROM craft_actions WHERE seq = :seq)',
        new_transfer
    )


@catch_and_log()
def load_mint_craft(session, mint):
    data = _get_data(mint)
    result_id = data['result_id']

    session_execute_logged(
        session,
        'UPDATE craft_minting SET minted = TRUE WHERE result_id = :result_id',
        {'result_id': result_id}
    )

    session.commit()


@catch_and_log()
def load_craft_total_update(session, update):
    data = _get_data(update)

    craft = load_transaction_basics(update)

    craft['total'] = data['total']
    craft['craft_id'] = data['craft_id']

    session_execute_logged(
        session,
        'INSERT INTO craft_total_updates (craft_id, new_total, old_total, seq, block_num, timestamp) '
        'SELECT :craft_id, :total, (SELECT total FROM crafts WHERE craft_id = :craft_id), :seq, '
        ':block_num, :timestamp '
        'WHERE NOT EXISTS (SELECT seq FROM craft_total_updates WHERE seq = :seq) ', craft)

    session_execute_logged(
        session,
        'UPDATE crafts SET total = :total WHERE craft_id = :craft_id ', craft
    )

    session.commit()


@catch_and_log()
def load_mirror_craft_result(session, update):
    data = _get_data(update)

    craft = load_transaction_basics(update)
    craft['crafter'] = data['crafter'] if 'crafter' in data else None
    craft['craft_id'] = data['craft_id'] if 'craft_id' in data else None
    craft['result_id'] = data['result_id'] if 'result_id' in data else None
    craft['minted_template'] = data['minted_template'] if 'minted_templates' in data else None
    craft['mirror_result'] = json.dumps(data['mirror_result']) if 'mirror_result' in data else None
    craft['lockups'] = None
    if 'lock_ups' in data:
        craft['lockups'] = []
        for lockup in data['lock_ups']:
            craft['lockups'].append(int(lockup))

    session_execute_logged(
        session,
        'INSERT INTO mirror_results '
        'SELECT :craft_id, :result_id, :crafter, :minted_template, :mirror_result, FALSE, NULL, FALSE, :seq, '
        ':block_num, :timestamp '
        'WHERE NOT EXISTS (SELECT seq FROM mirror_results WHERE seq = :seq)',
        craft
    )


@catch_and_log()
def load_mint_mirror(session, mint):
    data = _get_data(mint)
    transaction = load_transaction_basics(mint)
    transaction['result_id'] = data['result_id']
    transaction['ipfs'] = data['ipfs']

    session_execute_logged(
        session,
        'INSERT INTO mirror_mints '
        'SELECT :result_id, :ipfs, :seq, :block_num, :timestamp '
        'WHERE NOT EXISTS (SELECT seq FROM mirror_mints WHERE seq = :seq)',
        transaction
    )

    session_execute_logged(
        session,
        'UPDATE mirror_results '
        'SET minted = TRUE '
        'WHERE result_id = :result_id AND ipfs = :ipfs',
        transaction
    )


@catch_and_log()
def add_swap_mirror(session, transfer):
    data = _get_data(transfer)
    new_transfer = load_transaction_basics(transfer)
    new_transfer['claimer'] = data['owner']
    new_transfer['asset_id'] = data['asset_id']
    new_transfer['result_id'] = data['result_id']

    session_execute_logged(
        session,
        'INSERT INTO mirror_swap_results (craft_id, claimer, results, result_id, seq, block_num, timestamp) '
        'SELECT craft_id, :claimer, mirror_result, :result_id, :seq, :block_num, :timestamp '
        'FROM mirror_results p '
        'WHERE NOT EXISTS (SELECT seq FROM mirror_swap_results WHERE seq = :seq) AND p.result_id = :result_id ',
        new_transfer
    )


@catch_and_log()
def load_remint_mirror(session, mint):
    data = _get_data(mint)
    result_id = data['result_id']

    transaction = load_transaction_basics(mint)
    transaction['result_id'] = result_id

    session_execute_logged(
        session,
        'INSERT INTO mirror_swap_mints '
        'SELECT :result_id, :seq, :block_num, :timestamp '
        'WHERE NOT EXISTS (SELECT seq FROM mirror_swap_mints WHERE seq = :seq)',
        transaction
    )

    session_execute_logged(
        session,
        'UPDATE mirror_swap_results SET minted = TRUE WHERE result_id = :result_id',
        {'result_id': result_id}
    )


@catch_and_log()
def load_create_token(session, token):
    data = _get_data(token)
    new_token = load_transaction_basics(token)
    new_token['authorized_account'] = data['authorized_account']
    new_token['collection'] = data['collection_name']
    new_token['symbol'] = data['maximum_supply'].split(' ')[1]
    new_token['maximum_supply'] = float(data['maximum_supply'].split(' ')[0])
    new_token['decimals'] = len(data['maximum_supply'].split(' ')[0].split('.')[1]) if len(
        data['maximum_supply'].split(' ')[0].split('.')) > 1 else 0
    new_token['contract'] = data['contract']
    new_token['max_assets'] = data['max_assets_to_tokenize'] if 'max_assets_to_tokenize' in data else 0

    new_token['trait_factors'] = json.dumps(data['trait_factors'])
    new_token['token_name'] = data['token_name']
    new_token['token_logo'] = data['token_logo']
    new_token['token_logo_lg'] = data['token_logo_lg']

    if 'templates' in data:
        new_token['template_id'] = data['templates'][0]['template_id']
        max_assets_to_tokenize = 0
        for template in data['templates']:
            max_assets_to_tokenize += template['max_assets_to_tokenize']

        new_token['max_assets'] = max_assets_to_tokenize
        session_execute_logged(
            session,
            'INSERT INTO rwax_tokens ('
            '   collection, schema, symbol, contract, decimals, max_assets, maximum_supply, trait_factors, '
            '   token_name, token_logo, token_logo_lg, timestamp, seq, block_num'
            ') '
            'SELECT :collection, (SELECT schema FROM templates WHERE template_id = :template_id), :symbol, :contract, '
            ':decimals, :max_assets, :maximum_supply, :trait_factors, :token_name, :token_logo, :token_logo_lg, '
            ':timestamp, :seq, :block_num '
            'WHERE NOT EXISTS (SELECT seq FROM rwax_tokens WHERE seq = :seq)',
            new_token
        )
    else:
        new_token['schema_name'] = data['schema_name']
        session_execute_logged(
            session,
            'INSERT INTO rwax_tokens ('
            '   collection, schema, symbol, contract, decimals, max_assets, maximum_supply, trait_factors, '
            '   token_name, token_logo, token_logo_lg, timestamp, seq, block_num'
            ') '
            'SELECT :collection, :schema_name, :symbol, :contract, :decimals, :max_assets, :maximum_supply, '
            ':trait_factors, :token_name, :token_logo, :token_logo_lg, :timestamp, :seq, :block_num '
            'WHERE NOT EXISTS (SELECT seq FROM rwax_tokens WHERE seq = :seq)',
            new_token
        )


@catch_and_log()
def load_set_max_assets(session, token):
    data = _get_data(token)
    new_token = load_transaction_basics(token)
    new_token['authorized_account'] = data['authorized_account']
    new_token['collection'] = data['collection_name']
    new_token['symbol'] = data['maximum_supply'].split(' ')[1]
    new_token['maximum_supply'] = float(data['maximum_supply'].split(' ')[0])
    new_token['decimals'] = len(data['maximum_supply'].split(' ')[0].split('.')[1]) if len(
        data['maximum_supply'].split(' ')[0].split('.')) > 1 else 0
    new_token['contract'] = data['contract']
    new_token['max_assets'] = data['max_assets_to_tokenize']

    session_execute_logged(
        session,
        'INSERT INTO rwax_max_assets_updates ('
        '   collection, symbol, contract, decimals, new_max_assets, '
        '   old_max_assets, timestamp, seq, block_num'
        ') '
        'SELECT :collection, :symbol, :contract, :decimals, :max_assets, '
        '('
        '  SELECT max_assets FROM rwax_tokens WHERE contract = :contract AND symbol = :symbol'
        '), :timestamp, :seq, :block_num '
        'WHERE NOT EXISTS (SELECT seq FROM rwax_max_assets_updates WHERE seq = :seq)',
        new_token
    )

    session_execute_logged(
        session,
        'UPDATE rwax_tokens SET max_assets = :max_assets '
        'WHERE contract = :contract AND symbol = :symbol ',
        new_token
    )


@catch_and_log()
def load_set_factors(session, token):
    data = _get_data(token)
    new_token = load_transaction_basics(token)
    new_token['authorized_account'] = data['authorized_account']
    new_token['collection'] = data['collection_name']
    new_token['symbol'] = data['maximum_supply'].split(' ')[1]
    new_token['maximum_supply'] = float(data['maximum_supply'].split(' ')[0])
    new_token['decimals'] = len(data['maximum_supply'].split(' ')[0].split('.')[1]) if len(
        data['maximum_supply'].split(' ')[0].split('.')) > 1 else 0
    new_token['contract'] = data['contract']
    new_token['trait_factors'] = json.dumps(data['trait_factors'])

    session_execute_logged(
        session,
        'INSERT INTO rwax_traitfactor_updates ('
        '   collection, symbol, contract, decimals, maximum_supply, new_trait_factors, '
        '   old_trait_factors, timestamp, seq, block_num'
        ') '
        'SELECT :collection, :symbol, :contract, :decimals, :maximum_supply, '
        ':trait_factors, (SELECT trait_factors FROM rwax_tokens WHERE contract = :contract AND symbol = :symbol), '
        ':timestamp, :seq, :block_num '
        'WHERE NOT EXISTS (SELECT seq FROM rwax_traitfactor_updates WHERE seq = :seq)',
        new_token
    )

    session_execute_logged(
        session,
        'UPDATE rwax_tokens SET trait_factors = :trait_factors '
        'WHERE contract = :contract AND symbol = :symbol ',
        new_token
    )


@catch_and_log()
def load_rwax_erasetoken(session, erase):
    data = _get_data(erase)
    erased_token = load_transaction_basics(erase)
    erased_token['authorized_account'] = data['authorized_account']
    if 'token' in data:
        contract = data['token']['contract']
        quantity = data['token']['quantity']
        symbol = quantity.split(' ')[1]
        decimals = len(quantity.split(' ')[0].split('.')[1])
    else:
        contract = data['contract']
        symbol = data['token_symbol'].split(',')[1]
        decimals = int(data['token_symbol'].split(',')[0])

    erased_token['contract'] = contract
    erased_token['symbol'] = symbol
    erased_token['decimals'] = decimals

    session_execute_logged(
        session,
        'INSERT INTO rwax_erase_tokens ('
        '   contract, decimals, symbol, timestamp, seq, block_num'
        ') '
        'SELECT :contract, :decimals, :symbol, :timestamp, :seq, :block_num '
        'WHERE NOT EXISTS (SELECT seq FROM rwax_erase_tokens WHERE seq = :seq)',
        erased_token
    )

    session_execute_logged(
        session,
        'INSERT INTO removed_rwax_tokens '
        'SELECT r.*, :seq, :block_num FROM rwax_tokens r '
        'WHERE contract = :contract AND symbol = :symbol',
        erased_token
    )

    session_execute_logged(
        session,
        'DELETE FROM rwax_tokens '
        'WHERE contract = :contract AND symbol = :symbol',
        erased_token
    )

    session_execute_logged(
        session,
        'INSERT INTO removed_rwax_templates '
        'SELECT r.*, :seq, :block_num FROM rwax_templates r '
        'WHERE contract = :contract AND symbol = :symbol',
        erased_token
    )

    session_execute_logged(
        session,
        'DELETE FROM rwax_templates '
        'WHERE contract = :contract AND symbol = :symbol',
        erased_token
    )

    session_execute_logged(
        session,
        'INSERT INTO removed_rwax_redeemables '
        'SELECT r.*, :seq, :block_num FROM rwax_redeemables r '
        'WHERE contract = :contract AND symbol = :symbol',
        erased_token
    )

    session_execute_logged(
        session,
        'DELETE FROM rwax_redeemables '
        'WHERE contract = :contract AND symbol = :symbol ',
        erased_token
    )


@catch_and_log()
def load_tag_filter(session, action):
    act = action['act']

    data = _get_data(action)

    action_name = act['name']

    new_filter = load_transaction_basics(action)
    new_filter['tag_id'] = data['tag_id']
    new_filter['user_name'] = data['user_name']
    new_filter['action_name'] = action_name

    session_execute_logged(
        session,
        'INSERT INTO tag_filter_actions '
        'SELECT :user_name, :tag_id, :action_name, :seq, :block_num, :timestamp '
        'WHERE NOT EXISTS (SELECT seq FROM tag_filter_actions WHERE seq = :seq) ', new_filter
    )


@catch_and_log()
def load_log_tokenize(session, tokenize):
    data = _get_data(tokenize)
    new_token = load_transaction_basics(tokenize)
    new_token['asset_id'] = data['asset_id']
    new_token['tokenizer'] = data['tokenizer'] if 'tokenizer' in data else 'anotherhiver'
    new_token['symbol'] = data['issued_tokens'].split(' ')[1]
    new_token['amount'] = float(data['issued_tokens'].split(' ')[0])
    new_token['contract'] = data['contract'] if 'contract' in data else 'token.rwax'

    session_execute_logged(
        session,
        'INSERT INTO rwax_tokenizations ('
        '   asset_id, tokenizer, symbol, contract, amount, timestamp, seq, block_num'
        ') '
        'SELECT :asset_id, :tokenizer, :symbol, :contract, :amount, :timestamp, :seq, :block_num '
        'WHERE NOT EXISTS (SELECT seq FROM rwax_tokenizations WHERE seq = :seq)',
        new_token
    )

    session_execute_logged(
        session,
        'INSERT INTO rwax_redeemables ('
        '   asset_id, tokenizer, contract, symbol, amount, timestamp, seq, block_num'
        ') '
        'SELECT :asset_id, :tokenizer, :contract, :symbol, :amount, :timestamp, :seq, :block_num '
        'WHERE NOT EXISTS (SELECT seq FROM rwax_redemptions WHERE seq = :seq)',
        new_token
   )


@catch_and_log()
def insert_waxdao_back_action(session, action):
    back = load_transaction_basics(action)
    data = _get_data(action)

    back['backer'] = data['backer']
    for token in data['tokens_to_back']:
        backed_token = token['quantity'].split(' ')
        back['currency'] = backed_token[1]
        back['amount'] = float(backed_token[0])
        back['asset_id'] = data['asset_id']

        session_execute_logged(
            session,
            'INSERT INTO backed_assets '
            'SELECT :asset_id, :amount, :currency, :backer, :seq, :block_num, :timestamp '
            'WHERE NOT EXISTS (SELECT seq FROM backed_assets WHERE seq = :seq AND currency = :currency)',
            back
        )


@catch_and_log()
def load_rwax_redeem(session, redeem):
    data = _get_data(redeem)
    new_token = load_transaction_basics(redeem)
    new_token['asset_id'] = data['asset_id'] if 'asset_id' in data else 0
    new_token['redeemer'] = data['redeemer'] if 'redeemer' in data else 'anotherhiver'

    if 'contract' in data:
        new_token['contract'] = data['contract']
        new_token['symbol'] = data['quantity'].split(' ')[1]
        new_token['amount'] = float(data['quantity'].split(' ')[0])
    else:
        new_token['symbol'] = data['amount']['quantity'].split(' ')[1]
        new_token['amount'] = float(data['amount']['quantity'].split(' ')[0])
        new_token['contract'] = data['amount']['contract']

    session_execute_logged(
        session,
        'INSERT INTO rwax_redemptions ('
        '   asset_id, redeemer, contract, symbol, amount, timestamp, seq, block_num'
        ') '
        'SELECT :asset_id, :redeemer, :contract, :symbol, :amount, :timestamp, :seq, :block_num '
        'WHERE NOT EXISTS (SELECT seq FROM rwax_redemptions WHERE seq = :seq)',
        new_token
    )

    session_execute_logged(
        session,
        'INSERT INTO removed_rwax_redeemables '
        'SELECT r.*, :seq, :block_num '
        'FROM rwax_redeemables r WHERE asset_id = :asset_id',
        new_token
    )

    session_execute_logged(
        session,
        'DELETE FROM rwax_redeemables '
        'WHERE asset_id = :asset_id',
        new_token
    )


@catch_and_log()
def load_addtoken(session, token):
    data = _get_data(token)
    new_token = load_transaction_basics(token)
    new_token['contract'] = data['contract']
    new_token['symbol'] = data['maximum_supply'].split(' ')[1]
    new_token['maximum_supply'] = float(data['maximum_supply'].split(' ')[0])
    new_token['decimals'] = len(data['maximum_supply'].split(' ')[0].split('.')[1]) if len(
        data['maximum_supply'].split(' ')[0].split('.')) > 1 else 0
    new_token['token_name'] = data['token_name']
    new_token['token_logo'] = data['token_logo']
    new_token['token_logo_lg'] = data['token_logo_lg']

    session_execute_logged(
        session,
        'INSERT INTO tokens ('
        '   contract, symbol, decimals, maximum_supply, token_name, token_logo, token_logo_lg, seq, '
        '   block_num, timestamp'
        ') '
        'SELECT :contract, :symbol, :decimals, :maximum_supply, :token_name, :token_logo, :token_logo_lg, '
        ':seq, :block_num, :timestamp '
        'WHERE NOT EXISTS (SELECT seq FROM tokens WHERE seq = :seq)',
        new_token
    )


@catch_and_log()
def load_updatetoken(session, token):
    data = _get_data(token)
    new_token = load_transaction_basics(token)
    new_token['contract'] = data['contract']
    new_token['symbol'] = data['maximum_supply'].split(' ')[1]
    new_token['maximum_supply'] = float(data['maximum_supply'].split(' ')[0])
    new_token['decimals'] = len(data['maximum_supply'].split(' ')[0].split('.')[1]) if len(
        data['maximum_supply'].split(' ')[0].split('.')) > 1 else 0
    new_token['token_name'] = data['token_name']
    new_token['token_logo'] = data['token_logo']
    new_token['token_logo_lg'] = data['token_logo_lg']

    session_execute_logged(
        session,
        'INSERT INTO token_updates ('
        '   contract, symbol, decimals, old_decimals, maximum_supply, old_maximum_supply, token_name, '
        '   old_token_name, token_logo, old_token_logo, token_logo_lg, old_token_logo_lg, seq, block_num, timestamp'
        ') '
        'SELECT :contract, :symbol, :decimals, decimals :maximum_supply, maximum_supply, :token_name, '
        'token_name, :token_logo, token_logo, :token_logo_lg, token_logo_lg, :seq, :block_num, :timestamp '
        'FROM tokens WHERE contract = :contract AND symbol = :symbol'
        'WHERE NOT EXISTS (SELECT seq FROM token_updates WHERE seq = :seq)',
        new_token
    )

    session_execute_logged(
        session,
        'UPDATE tokens SET decimals = :decimals, maximum_supply = :maximum_supply, token_name = :token_name, '
        'token_logo = :token_logo, token_logo_lg = :token_logo_lg '
        'WHERE contract = :contract AND symbol = :symbol',
        new_token
    )
