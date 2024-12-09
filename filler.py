import datetime
import itertools
import logging
import os
import re
import time

import _thread

from flask import Flask, json, request
from oto.adaptors.flask import flaskify
from oto import response as oto_response

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import SQLAlchemyError

import funcs
from app_runner import run_loader
from config import PostgresFillerConfig

from flask_executor import Executor

import requests
import random

app = Flask(__name__)
app.config.from_object(PostgresFillerConfig if os.getenv('env') != 'dev' else PostgresFillerConfig)

db = SQLAlchemy(app, session_options={'autocommit': False})
db_auto = SQLAlchemy(app, session_options={'autocommit': True})

executor = Executor(app)

isLoading = False
isLoadingChronicleTx = False
isLoadingUSD = False
isVacuuming = False
isUpdatingAtomicAssets = False
isUpdatingAssetsData = False
isLoadingPFPAttributes = False
isUpdatingRWAXAssets = False
isUpdatingRecentlySold = False
isUpdatingFloorPrices = False
isUpdatingTemplateStats = False
isUpdatingBigVolumes = False
isUpdatingSmallVolumes = False
isUpdatingDrops = False
isUpdatingCollectionUserStats = False
isUpdatingSmallViews = False


action_measure_god = {
    'total_time': 0,
    'total_count': 0,
    'commit_time': 0,
    'update_last_time': 0,
    'update_time': 0,
    'parse_time': 0,
    'transaction_time': 0
}

isStopped = True
isForked = True

last_wax_stash_sync = 0

hyperions = [
    {
        'url': 'https://wax.hivebp.io',
        'status': 200,
        'blocks_behind': 0,
        'limit': 1000,
    }
]

apis = [
    {
        'url': 'https://api.hivebp.io',
        'status': 200,
        'blocks_behind': 0,
        'limit': 1000,
    },
    {
        'url': 'https://api2.hivebp.io',
        'status': 200,
        'blocks_behind': 0,
        'limit': 1000,
    },
    {
        'url': 'https://api3.hivebp.io',
        'status': 200,
        'blocks_behind': 0,
        'limit': 1000,
    }
]


def log_error(err):
    funcs.log_error(err)


def create_session():
    return db.session


def get_hyperions():
    global hyperions

    urls = []

    for hyperion in hyperions:
        urls.append(hyperion['url'])

    random.shuffle(urls)

    return urls


def get_url(pos):
    urls = get_hyperions()

    url = urls[pos]

    return url


def load_wax_usd_rate(session, action):
    try:
        median = action['median']

        timestamp = datetime.datetime.strptime(re.sub(r'\.\d+Z', 'Z', action['timestamp']),
                                               '%Y-%m-%dT%H:%M:%S.%f')
        usd = float(median)/10000.0

        session.execute('INSERT INTO usd_prices VALUES (:timestamp, :usd)', {
            'timestamp': timestamp, 'usd': usd
        })
    except SQLAlchemyError as e:
        log_error('load_wax_usd_rate: {}'.format(e))
        raise e
    except Exception as err:
        log_error('load_wax_usd_rate: {}'.format(err))
        raise err


@app.route('/loader/vacuum')
def vacuum():
    global isVacuuming
    if isVacuuming:
        return flaskify(oto_response.Response('Already processing request', status=102))
    isVacuuming = True
    session = create_session()
    total_start_time = time.time()
    try:

        session.connection().connection.set_isolation_level(0)
        start_time = time.time()
        session.execute('VACUUM listing_prices_new_mv')
        end_time = time.time()
        print('VACUUM VIEW 1: {}'.format(end_time - start_time))

        start_time = time.time()
        session.execute('VACUUM cheapest_new_mv')
        end_time = time.time()
        print('VACUUM VIEW 2: {}'.format(end_time - start_time))

        start_time = time.time()
        session.execute('VACUUM collection_users_mw')
        end_time = time.time()
        print('VACUUM VIEW 5: {}'.format(end_time - start_time))

        start_time = time.time()
        session.execute('VACUUM users_mv')
        end_time = time.time()
        print('VACUUM VIEW 6: {}'.format(end_time - start_time))

        start_time = time.time()
        session.execute('VACUUM price_limits_mv')
        end_time = time.time()
        print('VACUUM VIEW 7: {}'.format(end_time - start_time))

        session.connection().connection.set_isolation_level(1)
    except SQLAlchemyError as err:
        session.rollback()
        log_error('refresh_cheapest: {}'.format(err))
    except Exception as err:
        log_error('refresh_cheapest: {}'.format(err))
    finally:
        isVacuuming = False
        session.remove()
    total_end_time = time.time()
    return flaskify(oto_response.Response('Refreshed Cheapest {}'.format(total_end_time - total_start_time)))


@app.route('/loader/reboot-database')
def reboot_database():
    return "Dangerous, enable only when you intend to erase all data and reset the tables"

    start_time = time.time()
    session = create_session()
    try:
        block_num_tables = session.execute(
            'SELECT t1.table_name '
            'FROM tables_with_block_num t1 '
        )

        for tables in block_num_tables:
            print(
                'TRUNCATE {table_name}'.format(
                    table_name=tables['table_name']
                )
            )
            session.execute(
                'TRUNCATE {table_name}'.format(
                    table_name=tables['table_name']
                )
            )

        session.execute(
            'TRUNCATE transfers'
        )
        session.execute(
            'TRUNCATE simpleassets_offers'
        )
        session.execute(
            'TRUNCATE simpleassets_updates'
        )
        session.execute(
            'TRUNCATE simpleassets_burns'
        )
        session.execute(
            'TRUNCATE collections'
        )
        session.execute(
            'TRUNCATE schemas'
        )
        session.execute(
            'TRUNCATE templates'
        )
        session.execute(
            'TRUNCATE assets'
        )
        session.execute(
            'TRUNCATE attributes'
        )
        session.execute(
            'ALTER SEQUENCE attributes_attribute_id_seq RESTART WITH 1'
        )
        session.execute(
            'TRUNCATE data'
        )
        session.execute(
            'ALTER SEQUENCE data_data_id_seq RESTART WITH 1'
        )
        session.execute(
            'TRUNCATE images'
        )
        session.execute(
            'ALTER SEQUENCE listings_sale_id_seq RESTART WITH 1'
        )
        session.execute(
            'ALTER SEQUENCE images_image_id_seq RESTART WITH 1'
        )
        session.execute(
            'TRUNCATE videos'
        )
        session.execute(
            'ALTER SEQUENCE videos_video_id_seq RESTART WITH 1'
        )
        session.execute(
            'TRUNCATE names'
        )
        session.execute(
            'ALTER SEQUENCE names_name_id_seq RESTART WITH 1'
        )
        session.execute(
            'TRUNCATE transactions'
        )
        session.execute(
            'ALTER SEQUENCE transactions_id_seq RESTART WITH 1'
        )
        session.execute(
            'INSERT INTO handle_fork VALUES (false, 0)'
        )
        session.commit()
    except SQLAlchemyError as err:
        log_error('insert_atomic_template {}'.format(err))
        session.rollback()
    except Exception as err:
        raise err
    end_time = time.time()
    return flaskify(oto_response.Response({'total_time': end_time - start_time}))


def verify_account(session, account):
    session.execute(
        'UPDATE collections SET verified = TRUE WHERE collection = :collection', {'collection': account}
    )


def verify_accounts(session, accounts):
    res = session.execute('SELECT distinct collection FROM collections WHERE verified')
    already_verified = []
    for collection in res:
        already_verified.append(collection['collection'])

    to_verify = [i for i in accounts if i not in already_verified]

    for account in to_verify:
        if account not in already_verified:
            verify_account(session, account)


def unverify_account(session, account):
    session.execute(
        'UPDATE collections SET verified = FALSE WHERE collection = :collection', {'collection': account}
    )


def unverify_accounts(session, accounts):
    res = session.execute('SELECT distinct collection FROM collections WHERE NOT verified')
    already_unverified = []
    for collection in res:
        already_unverified.append(collection['collection'])

    to_unverify = [i for i in accounts if i not in already_unverified]

    for account in to_unverify:
        if account not in already_unverified:
            unverify_account(session, account)


def blacklist_account(session, account):
    session.execute('INSERT INTO blacklisted_collections VALUES (:collection)', {'collection': account})
    session.execute('UPDATE collections SET blacklisted = TRUE WHERE collection = :collection', {'collection': account})


def blacklist_accounts(session, accounts):
    res = session.execute('SELECT distinct collection FROM blacklisted_collections')
    already_blacklisted = []
    for collection in res:
        already_blacklisted.append(collection['collection'])

    for account in accounts:
        if account not in already_blacklisted:
            blacklist_account(session, account)
    session.commit()


def unblacklist_account(session, account):
    session.execute('DELETE FROM blacklisted_collections WHERE collection = :collection', {'collection': account})
    session.execute(
        'UPDATE collections SET blacklisted = FALSE WHERE collection = :collection', {'collection': account}
    )


def all_combinations(array):
    # Convert each row of the 2D array into a list, if not already
    rows = [row for row in array]
    # Use itertools.product to generate all possible combinations
    # *rows unpacks the list of rows into separate arguments for product
    return list(itertools.product(*rows))


@app.route('/loader/add-sets')
def add_sets():
    attribute_names = request.args.get('attribute_names', '')
    collection = request.args.get('collection', '')
    schema = request.args.get('schema', '')
    use_name = request.args.get('use_name', 'false') == 'true'

    session = create_session()

    attribute_ids = []
    for attribute_name in attribute_names.split(','):
        res = session.execute(
            'SELECT attribute_id '
            'FROM attributes '
            'WHERE collection = :collection '
            'AND schema = :schema '
            'AND attribute_name = :attribute_name ',
            {'collection': collection, 'schema': schema, 'attribute_name': attribute_name}
        )
        ids = []
        for attribute in res:
            ids.append(int(attribute['attribute_id']))

        attribute_ids.append(ids)

    combinations = all_combinations(attribute_ids)

    cnt = 0

    if use_name:
        names = session.execute(
            'SELECT DISTINCT name_id FROM assets WHERE collection = :collection AND schema = :schema',
            {'collection': collection, 'schema': schema}
        )
        for name in names:
            for combination in combinations:
                res = session.execute(
                    'INSERT INTO sets '
                    'SELECT :collection, :schema, :attribute_ids, NULL, :name_id '
                    'WHERE EXISTS ('
                    '   SELECT asset_id FROM assets WHERE collection = :collection AND schema = :schema '
                    '   AND name_id = :name_id AND :attribute_ids <@ attribute_ids'
                    ') AND NOT EXISTS ('
                    '   SELECT set_id '
                    '   FROM sets '
                    '   WHERE attribute_ids = :attribute_ids '
                    '   AND name_id = :name_id '
                    '   AND collection = :collection '
                    '   AND schema = :schema'
                    ')',
                    {
                        'collection': collection,
                        'schema': schema,
                        'attribute_ids': list(combination),
                        'name_id': name['name_id']
                    }
                )

                cnt += res.rowcount
                session.commit()
    else:
        for combination in combinations:
            res = session.execute(
                'INSERT INTO sets '
                'SELECT :collection, :schema, :attribute_ids '
                'WHERE EXISTS ('
                '   SELECT asset_id '
                '   FROM assets '
                '   WHERE collection = :collection '
                '   AND schema = :schema '
                '   AND :attribute_ids <@ attribute_ids'
                ') AND NOT EXISTS ('
                '   SELECT set_id '
                '   FROM sets '
                '   WHERE attribute_ids = :attribute_ids '
                '   AND name_id IS NULL '
                '   AND collection = :collection '
                '   AND schema = :schema'
                ')',
                {'collection': collection, 'schema': schema, 'attribute_ids': list(combination)}
            )
            cnt += res.rowcount
            session.commit()

    return flaskify(oto_response.Response('Added {} Sets'.format(cnt)))


@app.route('/loader/update-rwax-assets')
def update_rwax_assets():
    global isUpdatingRWAXAssets

    if isUpdatingRWAXAssets:
        return flaskify(oto_response.Response('Already processing request', status=102))
    isUpdatingRWAXAssets = True

    session = create_session()

    try:
        session.execute(
            'INSERT INTO rwax_assets '
            'SELECT asset_id, collection, schema, template_id '
            'FROM rwax_templates '
            'LEFT JOIN assets a USING (collection, template_id) '
            'WHERE NOT EXISTS ('
            '   SELECT asset_id FROM rwax_assets WHERE asset_id = a.asset_id'
            ')'
        )

        session.execute(
            'DELETE FROM rwax_assets '
            'WHERE asset_id IN (SELECT asset_id FROM rwax_assets ra LEFT JOIN assets a USING (asset_id) '
            'WHERE a.template_id NOT IN (SELECT template_id FROM rwax_templates WHERE template_id = a.template_id))'
        )

        session.commit()

        return flaskify(oto_response.Response('Updated RWAX Assets'))
    except SQLAlchemyError as err:
        log_error('update_rwax_assets: {}'.format(err))
        session.rollback()
        return flaskify(oto_response.Response('An unexpected Error occured', errors=err, status=500))
    except Exception as err:
        log_error('update_rwax_assets: {}'.format(err))
        return flaskify(oto_response.Response('An unexpected Error occured', errors=err, status=500))
    finally:
        session.remove()
        isUpdatingRWAXAssets = False


@app.route('/loader/update-pfp-attributes')
def update_pfp_attributes():
    global isLoadingPFPAttributes

    if isLoadingPFPAttributes:
        return flaskify(oto_response.Response('Already processing request', status=102))
    isLoadingPFPAttributes = True

    session = create_session()

    try:
        session.commit()

        session.execute(
            'INSERT INTO pfp_templates '
            'SELECT collection, schema, template_id '
            'FROM ('
            '   SELECT unnest(templates_to_mint) AS template_id '
            '   FROM drops WHERE (drop_id, contract) IN (SELECT drop_id, contract FROM pfp_drop_data )'
            ') a '
            'INNER JOIN templates t USING (template_id) '
            'WHERE NOT EXISTS ('
            '   SELECT collection, schema, template_id FROM pfp_templates '
            '   WHERE collection = t.collection AND schema = t.schema AND template_id = t.template_id '
            ') '
            'GROUP BY 1, 2, 3'
        )
        session.commit()

        session.execute(
            'INSERT INTO pfp_schemas '
            'SELECT collection, schema '
            'FROM pfp_templates '
            'WHERE (collection, schema) NOT IN (SELECT collection, schema FROM pfp_schemas)'
        )
        session.commit()

        session.execute(
            'INSERT INTO pfp_assets '
            'SELECT a.asset_id, a.collection, a.schema, a.template_id, array_agg(attribute_id) '
            'FROM ('
            '   SELECT asset_id, t.collection, t.schema, template_id, a.attribute_ids '
            '   FROM templates t '
            '   INNER JOIN assets a USING(template_id) '
            '   WHERE (t.collection, t.schema) IN (SELECT collection, schema FROM pfp_schemas) '
            '   AND NOT EXISTS (SELECT asset_id FROM pfp_assets WHERE asset_id = a.asset_id)) a '
            'LEFT JOIN attributes att ON att.attribute_id = ANY(a.attribute_ids) '
            'WHERE NOT EXISTS ('
            '   SELECT attribute_name FROM pfp_attribute_blacklist WHERE attribute_name = att.attribute_name'
            ') GROUP BY 1, 2, 3, 4 '
        )
        session.commit()

        collections = session.execute('SELECT DISTINCT collection FROM pfp_schemas')
        for collection in collections:
            session.execute(
                'UPDATE pfp_assets a SET num_traits = ('
                '   SELECT COUNT(attribute_id) '
                '   FROM ('
                '      SELECT attribute_id '
                '      FROM pfp_assets '
                '      LEFT JOIN attributes ON attribute_id = ANY(attribute_ids) '
                '      WHERE attribute_name != \'num_traits\' AND string_value NOT IN (\'none\', \'None\') '
                '      AND asset_id = a.asset_id'
                '   ) a'
                ') '
                'WHERE num_traits IS NULL AND attribute_ids IS NOT NULL AND a.collection = :collection ',
                {'collection': collection['collection']}
            )

            session.execute(
                'DELETE FROM pfp_assets WHERE asset_id IN ('
                '   SELECT asset_id '
                '   FROM pfp_assets p '
                '   INNER JOIN assets a USING(asset_id) '
                '   WHERE p.collection = :collection '
                '   AND (a.collection, a.schema) NOT IN ('
                '       SELECT collection, schema FROM pfp_schemas'
                '   )'
                ')', {'collection': collection['collection']}
            )

        session.commit()

        session.execute(
            'INSERT INTO attribute_stats '
            'SELECT collection, schema, attribute_id '
            'FROM attributes a '
            'WHERE EXISTS ('
            '   SELECT collection, schema '
            '   FROM pfp_schemas '
            '   WHERE collection = a.collection '
            '   AND schema = a.schema'
            ') '
            'AND EXISTS ('
            '   SELECT asset_id '
            '   FROM pfp_assets '
            '   WHERE collection = a.collection AND schema = a.schema '
            '   AND attribute_id = ANY(attribute_ids) '
            ')'
            'AND NOT EXISTS (SELECT attribute_id FROM attribute_stats WHERE attribute_id = a.attribute_id)'
        )

        session.commit()

        session.execute(
            'WITH attribute_totals AS ('
            '   SELECT attribute_id, COUNT(1) AS total '
            '   FROM attributes '
            '   LEFT JOIN pfp_assets aa ON attribute_id = ANY(attribute_ids) '
            '   LEFT JOIN assets a USING(asset_id) '
            '   WHERE NOT burned GROUP BY 1'
            ') '
            'UPDATE attribute_stats atu SET total = att.total FROM attribute_totals att WHERE att.attribute_id = '
            'atu.attribute_id '
        )

        session.execute(
            'WITH template_totals AS ('
            '   SELECT a.collection, a.schema, COUNT(1) AS total_schema '
            '   FROM pfp_assets a '
            '   LEFT JOIN assets USING(asset_id) '
            '   WHERE NOT burned GROUP BY 1, 2'
            ') '
            'UPDATE attribute_stats asu SET total_schema = tt.total_schema '
            'FROM template_totals tt WHERE asu.collection = tt.collection AND asu.schema = tt.schema '
        )

        session.execute(
            'UPDATE attribute_stats SET rarity_score = 1 / (total / CAST(total_schema AS float)) '
            'WHERE total IS NOT NULL AND total_schema > 0'
        )
        session.commit()

        collections = session.execute(
            'SELECT DISTINCT collection FROM pfp_schemas'
        )

        session.remove()

        session = create_session()
        for collection in collections:
            session.execute(
                'UPDATE pfp_assets aa SET rarity_score = asu.rarity_score FROM ('
                '   SELECT aa.asset_id, SUM(asu.rarity_score) AS rarity_score '
                '   FROM attribute_stats asu '
                '   LEFT JOIN pfp_assets aa ON asu.attribute_id = ANY(attribute_ids) '
                '   AND asu.collection = aa.collection '
                '   AND asu.schema = aa.schema '
                '   INNER JOIN assets a USING (asset_id) '
                '   WHERE asu.collection = :collection AND NOT burned '
                '   GROUP BY 1'
                ') asu WHERE asu.asset_id = aa.asset_id ', {'collection': collection['collection']}
            )

            session.execute(
                'UPDATE pfp_assets asu SET rank = NULL, rarity_score = NULL '
                'FROM assets a '
                'WHERE asu.asset_id = a.asset_id AND a.burned AND rank IS NOT NULL AND rarity_score IS NOT NULL '
                'AND asu.collection = :collection', {'collection': collection['collection']}
            )

            session.execute(
                'UPDATE pfp_assets asu SET rank = ats.rank FROM ('
                '   SELECT asset_id, '
                '   RANK() OVER(PARTITION BY asu.collection, asu.schema ORDER BY rarity_score DESC NULLS LAST) AS rank,'
                '   burned FROM pfp_assets asu INNER JOIN assets USING (asset_id) '
                '   WHERE NOT burned AND asu.collection = :collection'
                ') ats '
                'WHERE ats.asset_id = asu.asset_id AND NOT ats.burned', {'collection': collection['collection']}
            )

            session.execute(
                'UPDATE attribute_stats atu SET floor_wax = tp.floor_wax '
                'FROM attribute_floors_mv tp '
                'WHERE tp.attribute_id = atu.attribute_id AND collection = :collection',
                {'collection': collection['collection']}
            )
            session.commit()

        return flaskify(oto_response.Response('Updated PFP Attributes'))
    except SQLAlchemyError as err:
        log_error('load_pfp_attributes: {}'.format(err))
        session.rollback()
        return flaskify(oto_response.Response('An unexpected Error occured', errors=err, status=500))
    except Exception as err:
        log_error('load_pfp_attributes: {}'.format(err))
        return flaskify(oto_response.Response('An unexpected Error occured', errors=err, status=500))
    finally:
        session.remove()
        isLoadingPFPAttributes = False


@app.route('/loader/sync-new-collection-verifications')
def sync_new_collection_verifications():
    url = 'https://config.api.atomichub.io/v1/atomichub-config?chains=wax-mainnet'

    response = requests.request("GET", url)

    if response.status_code != 200:
        log_error('sync_new_collection_verifications {}: {}'.format(response.status_code, response.content))
        return flaskify(oto_response.Response(
            'An unexpected Error occured', errors=response.content, status=response.status_code))

    collections = json.loads(response.content)

    whitelist = []
    blacklist = []
    verified = []
    unverified = []
    nsfw = []
    badges = {}

    for collection in collections['data']['collections']:
        if collection['state'] == 'whitelisted':
            whitelist.append(collection['id'])
        elif collection['state'] == 'verified':
            verified.append(collection['id'])
        elif collection['state'] == 'blacklisted':
            blacklist.append(collection['id'])
        elif collection['state'] == 'no_status':
            unverified.append(collection['id'])
        if 'flags' in collection and collection['flags'] and 'nsfw' in collection['flags']:
            nsfw.append(collection['id'])
        if 'badges' in collection:
            for badge in collection['badges']:
                if collection['id'] not in badges:
                    badges[collection['id']] = {}
                badges[collection['id']][badge['name']] = badge

    session = create_session()

    old_badges = session.execute( 'SELECT * FROM badges')
    for old_badge in old_badges:
        if old_badge['collection'] not in badges:
            session.execute(
                'DELETE FROM badges WHERE collection = :collection',
                {'collection': old_badge['collection']}
            )
        elif old_badge['name'] not in badges[old_badge['collection']]:
            session.execute(
                'DELETE FROM badges WHERE collection = :collection AND name = :name',
                {'collection': old_badge['collection'], 'name': old_badge['name']}
            )
        else:
            badges[old_badge['collection']][old_badge['name']]['update'] = True

    for collection in badges:
        for name in badges[collection]:
            badge = badges[collection][name]
            if 'update' in badge:
                session.execute(
                    'UPDATE badges SET value = :value, level = :level, timestamp = :timestamp '
                    'WHERE collection = :collection AND name = :name',
                    {
                        'value': badge['value'],
                        'level': badge['level'],
                        'timestamp': datetime.datetime.fromtimestamp(int(badge['created_at']) / 1000),
                        'name': badge['name'],
                        'collection': collection
                    }
                )
            else:
                session.execute(
                    'INSERT INTO badges SELECT :collection, :name, :level, :value, :timestamp '
                    'WHERE NOT EXISTS ('
                    '   SELECT collection, name FROM badges WHERE collection = :collection AND name = :name'
                    ')', {
                        'value': badge['value'],
                        'level': badge['level'],
                        'timestamp': datetime.datetime.fromtimestamp(int(badge['created_at']) / 1000),
                        'name': badge['name'],
                        'collection': collection
                    }
                )

    blacklisted_collections = session.execute('SELECT distinct collection FROM blacklisted_collections')

    whitelist_overwrite = session.execute('SELECT collection FROM whitelist_overwrite')

    for collection in whitelist_overwrite:
        if collection['collection'] in unverified:
            unverified.remove(collection['collection'])

    unverify_overwrite = session.execute(
        'SELECT collection FROM unverify_overwrite'
    )

    for collection in unverify_overwrite:
        if collection['collection'] in verified:
            verified.remove(collection['collection'])

    unblacklist = []
    for collection in blacklisted_collections:
        if collection['collection'] not in blacklist:
            unblacklist.append(collection['collection'])

    blacklist_overwrite = session.execute(
        'SELECT collection FROM blacklist_overwrite'
    )

    for collection in blacklist_overwrite:
        if collection['collection'] in unblacklist:
            unblacklist.remove(collection['collection'])

    verify_accounts(session, verified)
    verify_accounts(session, whitelist)
    unverify_accounts(session, unverified)

    blacklist_accounts(session, blacklist)
    for collection in unblacklist:
        unblacklist_account(session, collection)

    session.commit()
    session.remove()

    return flaskify(oto_response.Response('Collections Synced'))


def parse_action(session, action):
    global action_measure_god
    act = action['act'] if action and 'act' in action.keys() else None
    name = act['name'] if act and 'name' in act.keys() else None
    account = act['account'] if act and 'account' in act.keys() else None
    if account not in action_measure_god:
        action_measure_god[account] = {}
    start_time = time.time()
    try:
        if account in ['atomicdropsx', 'neftyblocksd', 'nfthivedrops', 'twitchreward']:
            if name == 'lognewdrop':
                funcs.load_drop(session, action, account)
            elif name == 'setdropdata':
                funcs.load_drop_update(session, action, account)
            elif name == 'setdroplimit':
                funcs.load_drop_limit_update(session, action, account)
            elif name == 'setdropmax':
                funcs.load_drop_max_update(session, action, account)
            elif name == 'setdropprice':
                funcs.load_drop_price_update(session, action, account)
            elif name == 'setdprices':
                funcs.load_drop_prices_update(session, action, account)
            elif name == 'setfeerate':
                funcs.load_drop_fee_rate(session, action, account)
            elif name == 'setdropauth':
                funcs.load_drop_drop_auth(session, action, account)
            elif name == 'setdrophiddn':
                funcs.load_drop_hidden(session, action, account)
            elif name == 'setdroptimes':
                funcs.load_drop_times_update(session, action, account)
            elif name == 'claimdrop' or name == 'claimdropkey' or name == 'claimdropwl' or name == 'claimwproof':
                funcs.load_claim_drop(session, action, account)
            elif name == 'erasedrop':
                funcs.load_erase_drop(session, action, account)
            elif name == 'addconftoken' and account == 'nfthivedrops':
                funcs.load_addconftoken(session, action)
            elif name == 'remconftoken' and account == 'nfthivedrops':
                funcs.load_remconftoken(session, action)
            elif name == 'addpfpresult' and account == 'nfthivedrops':
                funcs.add_pfp_result(session, action)
            elif name == 'lognewpfp':
                funcs.load_drop(session, action, account)
            elif name == 'setpfpdata':
                funcs.load_drop_update(session, action, account)
            elif name == 'setpfplimit':
                funcs.load_drop_limit_update(session, action, account)
            elif name == 'setpfpmax':
                funcs.load_drop_max_update(session, action, account)
            elif name == 'setpfpprice':
                funcs.load_drop_prices_update(session, action, account)
            elif name == 'setpfpprices':
                funcs.load_drop_prices_update(session, action, account)
            elif name == 'setpfpfee':
                funcs.load_drop_fee_rate(session, action, account)
            elif name == 'setpfpauth':
                funcs.load_drop_drop_auth(session, action, account)
            elif name == 'setdroptimes':
                funcs.load_drop_times_update(session, action, account)
            elif name == 'setdroptimes':
                funcs.load_drop_times_update(session, action, account)
            elif name == 'claimpfpdrop' or name == 'claimpfpwl' or name == 'claimpfproof':
                funcs.load_claim_drop(session, action, account)
            elif name == 'erasepfp':
                funcs.load_erase_drop(session, action, account)
            elif name == 'addreward':
                funcs.load_add_reward(session, action)
            elif name == 'mintpfp':
                funcs.load_mint_pfp(session, action)
            elif name == 'swappfp':
                funcs.add_swap_pfp(session, action)
            elif name == 'remintpfp':
                funcs.load_remint_pfp(session, action)
            elif name == 'logprices' and account == 'nfthivedrops':
                funcs.load_logprices(session, action, account)
        elif account == 'atomicmarket':
            if name == 'purchasesale':
                funcs.load_atomic_market_buy(session, action)
            elif name == 'cancelsale':
                funcs.load_atomic_market_cancel(session, action)
            elif name == 'lognewsale':
                funcs.load_atomic_market_sale(session, action)
            elif name == 'cancelauct':
                funcs.load_atomic_market_cancel_auct(session, action)
            elif name == 'auctionbid':
                funcs.load_atomic_market_auct_bid(session, action)
            elif name == 'lognewauct':
                funcs.load_atomic_market_auct(session, action)
            elif name == 'auctclaimbuy':
                funcs.load_atomic_market_claim_auct(session, action)
            elif name == 'cancelbuyo':
                funcs.load_atomic_market_cancel_buy_offer(session, action)
            elif name == 'acceptbuyo':
                funcs.load_atomic_market_accept_buy_offer(session, action)
            elif name == 'declinebuyo':
                funcs.load_atomic_market_decline_buy_offer(session, action)
            elif name == 'lognewbuyo':
                funcs.load_atomic_market_log_new_buy_offer(session, action)
            elif name == 'logsalestart':
                funcs.load_atomic_market_sale_start(session, action)
            elif name == 'canceltbuyo':
                funcs.load_atomic_market_cancel_template_buyo(session, action)
            elif name == 'fulfilltbuyo':
                funcs.load_atomic_market_fulfill_template_buyo(session, action)
            elif name == 'lognewtbuyo':
                funcs.load_atomic_market_lognew_template_buyo(session, action)
        elif account == 'atomicassets':
            if name == 'logmint':
                funcs.insert_atomic_asset(session, action)
            elif name == 'logbackasset':
                funcs.insert_back_action(session, action)
            elif name == 'logtransfer':
                funcs.load_atomic_transfer(session, action)
            elif name == 'burnasset':
                funcs.load_atomic_burn(session, action)
            elif name == 'lognewoffer':
                funcs.load_atomic_offer(session, action)
            elif name == 'acceptoffer':
                funcs.load_accept_offer(session, action)
            elif name == 'canceloffer':
                funcs.load_cancel_offer(session, action)
            elif name == 'declineoffer':
                funcs.load_decline_offer(session, action)
            elif name == 'setassetdata':
                funcs.load_atomic_update(session, action)
            elif name == 'setcoldata':
                funcs.load_collection_update(session, action)
            elif name == 'setmarketfee':
                funcs.load_collection_fee_update(session, action)
            elif name == 'addcolauth':
                funcs.add_collection_author(session, action)
            elif name == 'remcolauth':
                funcs.remove_collection_author(session, action)
            elif name == 'lognewtempl':
                funcs.insert_atomic_template(session, action)
            elif name == 'createschema':
                funcs.insert_schema(session, action)
            elif name == 'createcol':
                funcs.insert_collection(session, action)
        elif account == 'nft.hive':
            if name == 'lognewsale':
                funcs.load_nft_hive_ft_lists(session, action)
            elif name == 'logbuy':
                funcs.load_nft_hive_ft_buys(session, action)
            elif name == 'cancelsale':
                funcs.load_nft_hive_ft_cancels(session, action)
            elif name == 'execute':
                funcs.load_nft_hive_execute(session, action)
        elif account == 'simpleassets':
            if name == 'createlog':
                funcs.load_asset(session, action)
            elif name == 'transfer':
                funcs.load_transaction(session, action)
            elif name == 'offer':
                funcs.load_offer(session, action)
            elif name == 'claim':
                funcs.load_claim(session, action)
            elif name == 'burn':
                funcs.load_asset_burn(session, action)
            elif name == 'update':
                funcs.load_asset_update(session, action)
        elif account == 'waxplorercom':
            if name == 'logbuy':
                funcs.load_waxplorercom_buy(session, action)
            elif name == 'lognewsale':
                funcs.load_waxplorercom_list(session, action)
            elif name == 'cancelsale':
                funcs.load_waxplorercom_unlist(session, action)
        elif account == 'market.myth':
            if name == 'logsale':
                funcs.load_market_myth_buy(session, action)
        elif account == 'simplemarket':
            if name == 'updateprice':
                funcs.load_simplemarket_update(session, action)
            elif name == 'buylog':
                funcs.load_simplemarket_buy(session, action)
            elif name == 'cancel':
                funcs.load_simplemarket_cancel(session, action)
        elif account == 'wax.gg':
            if name == 'updatephoto':
                funcs.load_user_picture(session, action)
        elif account == 'neftyblocksp':
            if name == 'createpack':
                funcs.load_createpack(session, action, 'neftyblocksp')
            elif name == 'createspack':
                funcs.load_createpack(session, action, 'neftyblocksp')
            elif name == 'lognewpack':
                funcs.load_neftyblocksp_lognewpack(session, action)
            elif name == 'setpackdata':
                funcs.load_setpackdata(session, action, 'neftyblocksp')
        elif account == 'nfthivepacks':
            if name == 'lognewpack':
                funcs.load_nfthivepacks_lognewpack(session, action)
            elif name == 'setdisplay':
                funcs.load_setpackdata(session, action, 'nfthivepacks')
            elif name == 'delpack':
                funcs.load_delpack(session, action, 'nfthivepacks')
            elif name == 'delrelease':
                funcs.load_delrelease(session, action)
            elif name == 'setpacktime':
                funcs.load_setpacktime(session, action, 'nfthivepacks')
            elif name == 'delpool':
                funcs.load_delpool(session, action)
            elif name == 'lognewpool':
                funcs.addpool(session, action, account)
            elif name == 'addassets':
                funcs.addassets(session, action, 'nfthivepacks')
            elif name == 'remassets':
                funcs.remassets(session, action, 'nfthivepacks')
            elif name == 'logresult':
                funcs.log_pack_result(session, action, 'nfthivepacks')
        elif account == 'atomicpacksx':
            if name == 'announcepack':
                funcs.load_announcepack(session, action, 'atomicpacksx')
            elif name == 'lognewpack':
                funcs.load_atomicpacksx_lognewpack(session, action)
            elif name == 'completepack':
                funcs.load_completepack(session, action, 'atomicpacksx')
            elif name == 'setpackdata':
                funcs.load_setpackdata(session, action, 'atomicpacksx')
            elif name == 'setpacktime':
                funcs.load_setpacktime(session, action, 'atomicpacksx')
        elif account == 'waxbuyoffers':
            if name == 'lognewoffer':
                funcs.load_lognewoffer(session, action)
            elif name == 'logbalance':
                funcs.load_logbalance(session, action)
            elif name == 'logerase':
                funcs.load_logerase(session, action)
            elif name == 'logsale':
                funcs.load_logsale(session, action)
        elif account == 'clltncattool':
            if name == 'settag':
                funcs.load_settag(session, action)
            elif name == 'addtag':
                funcs.load_addtag(session, action)
            elif name == 'settagcol':
                funcs.load_settag(session, action)
            elif name == 'suggesttag':
                funcs.load_suggesttag(session, action)
            elif name == 'addfilter':
                funcs.load_tag_filter(session, action)
            elif name == 'remfilter':
                funcs.load_tag_filter(session, action)
        elif account == 'atomhubtools':
            if name == 'addaccvalues':
                funcs.load_account_values(session, action)
            elif name == 'remaccvalues':
                funcs.load_account_values(session, action)
            elif name == 'addblacklist':
                funcs.load_verifications(session, action)
            elif name == 'addscam':
                funcs.load_verifications(session, action)
            elif name == 'addverify':
                funcs.load_verifications(session, action)
            elif name == 'remverify':
                funcs.load_verifications(session, action)
            elif name == 'addwhitelist':
                funcs.load_verifications(session, action)
            elif name == 'remwhitelist':
                funcs.load_verifications(session, action)
        elif account == 'neftyblocksa':
            if name == 'addtolist':
                funcs.load_nefty_account_values(session, action)
            elif name == 'delfromlist':
                funcs.load_nefty_account_values(session, action)
        elif account == 'verifystatus':
            if name == 'addtolist':
                funcs.load_status_addtolist(session, action)
            elif name == 'remfromlist':
                funcs.load_status_remfromlist(session, action)
            elif name == 'setlist':
                funcs.load_status_setlist(session, action)
            elif name == 'logvotes':
                funcs.load_status_logvotes(session, action)
        elif account == 'redeemprtcol':
            if name == 'redeem':
                funcs.load_redeem(session, action)
            elif name == 'accept':
                funcs.load_accept_redemption(session, action)
            elif name == 'reject':
                funcs.load_reject_redemption(session, action)
            elif name == 'release':
                funcs.load_release_redemption(session, action)
        elif account == 'wufclaimtool':
            if name == 'lognewdrop':
                funcs.load_airdrop(session, action)
            elif name == 'addclaimers':
                funcs.load_addclaimers(session, action)
            elif name == 'delairdrop':
                funcs.load_delairdrop(session, action)
            elif name == 'claim':
                funcs.load_claim_airdrop(session, action)
            elif name == 'setready':
                funcs.load_wuf_setready(session, action)
        elif account == 'nfthivecraft':
            if name == 'lognewcraft':
                funcs.load_craft(session, action, 'nfthivecraft')
            elif name == 'setcrafttime':
                funcs.load_craft_times_update(session, action)
            elif name == 'setdisplay':
                funcs.load_craft_update(session, action)
            elif name == 'setready':
                funcs.load_craft_set_ready(session, action)
            elif name == 'logresult':
                funcs.load_craft_result(session, action)
            elif name == 'delcraft':
                funcs.load_erase_craft(session, action)
            elif name == 'craft':
                funcs.load_claim_craft(session, action)
            elif name == 'mint':
                funcs.load_mint_craft(session, action)
            elif name == 'settotal':
                funcs.load_craft_total_update(session, action)
            elif name == 'lognewmirror':
                funcs.load_craft(session, action, 'nfthivecraft')
            elif name == 'mirrorcraft':
                funcs.load_claim_craft(session, action)
            elif name == 'logmresult':
                funcs.load_mirror_craft_result(session, action)
            elif name == 'delmirror':
                funcs.load_erase_craft(session, action)
            elif name == 'setmdisplay':
                funcs.load_craft_update(session, action)
            elif name == 'setmirrortime':
                funcs.load_craft_times_update(session, action)
            elif name == 'mintmirror':
                funcs.load_mint_mirror(session, action)
            elif name == 'swappfp':
                funcs.add_swap_mirror(session, action)
            elif name == 'remintmirror':
                funcs.load_remint_mirror(session, action)
        elif account == 'rwax':
            if name == 'createtoken':
                funcs.load_create_token(session, action)
            elif name == 'logtokenize':
                funcs.load_log_tokenize(session, action)
            elif name == 'redeem':
                funcs.load_rwax_redeem(session, action)
            elif name == 'erasetoken':
                funcs.load_rwax_erasetoken(session, action)
        elif account == 'waxtokenbase':
            if name == 'addtoken':
                funcs.load_addtoken(session, action)
            elif name == 'updatetoken':
                funcs.load_updatetoken(session, action)
        elif account == 'waxdaobacker':
            if name == 'logbackasset':
                funcs.insert_waxdao_back_action(session, action)
    except SQLAlchemyError as err:
        log_error('parse_action {}: {}'.format(name, err))
        session.rollback()
        raise err
    end_time = time.time()
    if name not in action_measure_god[account]:
        count = action_measure_god['total_count'] + 1
        total = action_measure_god['total_time'] + end_time - start_time
        action_measure_god['total_count'] = count
        action_measure_god['total_time'] = total
        action_measure_god[account][name] = {
            'count': 1,
            'total': end_time - start_time,
            'average': end_time - start_time
        }
    else:
        name_total = action_measure_god[account][name]['total'] + end_time - start_time
        name_count = action_measure_god[account][name]['count'] + 1
        count = action_measure_god['total_count'] + 1
        action_measure_god['total_count'] = count
        action_measure_god[account][name]['count'] = name_count
        action_measure_god[account][name]['total'] = name_total
        action_measure_god[account][name]['average'] = float(name_total) / float(name_count)
    return end_time - start_time


@app.route('/loader/update-estimated-wax-price')
def update_estimated_wax_price():
    session = create_session()

    try:
        session.execute(
            'WITH current_usd_price AS (SELECT usd FROM usd_prices ORDER BY timestamp DESC LIMIT 1) '
            'UPDATE listings SET estimated_wax_price = price / (SELECT usd FROM current_usd_price) '
            'WHERE currency = \'USD\''
        )

        session.commit()

        return flaskify(oto_response.Response('Estimated WAX Prices Updated'))
    except SQLAlchemyError as err:
        log_error('update_estimated_wax_price: {}'.format(err))
        session.rollback()
        return flaskify(oto_response.Response('An unexpected Error occured', errors=err, status=500))
    finally:
        session.remove()


@app.route('/loader/update-small-views')
def update_small_views():
    global isUpdatingSmallViews

    if isUpdatingSmallViews:
        return flaskify(oto_response.Response('Already processing request', status=102))

    isUpdatingSmallViews = True

    session = create_session()

    try:
        session.execute('REFRESH MATERIALIZED VIEW CONCURRENTLY tags_mv')
        session.commit()
        session.execute('REFRESH MATERIALIZED VIEW CONCURRENTLY user_pictures_mv')
        session.commit()
        session.execute('REFRESH MATERIALIZED VIEW CONCURRENTLY tag_filters_mv')
        session.commit()
        session.execute('REFRESH MATERIALIZED VIEW CONCURRENTLY personal_blacklist_actions_mv')
        session.commit()
        session.execute('REFRESH MATERIALIZED VIEW CONCURRENTLY personal_blacklist_mv')
        session.commit()
        session.execute('REFRESH MATERIALIZED VIEW CONCURRENTLY drop_prices_mv')
        session.commit()

        return flaskify(oto_response.Response('Small Views Updated'))
    except SQLAlchemyError as err:
        log_error('update_small_views: {}'.format(err))
        session.rollback()
        return flaskify(oto_response.Response('An unexpected Error occured', errors=err, status=500))
    finally:
        isUpdatingSmallViews = False
        session.remove()


@app.route('/loader/update-floor-prices')
def update_floor_prices():
    global isUpdatingFloorPrices

    if isUpdatingFloorPrices:
        return flaskify(oto_response.Response('Already processing request', status=102))

    isUpdatingFloorPrices = True

    session = create_session()

    try:
        session.execute('REFRESH MATERIALIZED VIEW CONCURRENTLY listings_floor_breakdown_mv')
        session.commit()
        session.execute('REFRESH MATERIALIZED VIEW CONCURRENTLY template_floor_prices_mv')
        session.commit()
        session.execute('REFRESH MATERIALIZED VIEW CONCURRENTLY attribute_floors_mv')
        session.commit()
        session.execute('REFRESH MATERIALIZED VIEW CONCURRENTLY listings_helper_mv')
        session.commit()

        return flaskify(oto_response.Response('Floor Prices Updated'))
    except SQLAlchemyError as err:
        log_error('update_floor_prices: {}'.format(err))
        session.rollback()
        return flaskify(oto_response.Response('An unexpected Error occured', errors=err, status=500))
    finally:
        isUpdatingFloorPrices = False
        session.remove()


@app.route('/loader/clean-up')
def clean_up():
    session = create_session()
    try:
        res = session.execute(
            'SELECT transaction_id, listing_id, seq, seller '
            'FROM duplicate_atomic_listings '
            'LEFT JOIN chronicle_transactions USING (seq) '
            'ORDER BY listing_id DESC'
        )

        for trx in res:
            trx_id = trx['transaction_id']

            url = 'https://wax.hivebp.io/v2/history/get_transaction?id=' + trx_id

            response = requests.request("GET", url)

            content = json.loads(response.content)
            if not content['executed']:
                session.execute(
                    'INSERT INTO deleted_chronicle_transactions '
                    'SELECT * FROM chronicle_transactions WHERE seq = :seq AND transaction_id = :transaction_id',
                    {'seq': trx['seq'], 'transaction_id': trx_id}
                )
                session.commit()
    except SQLAlchemyError as err:
        log_error('clean_up: {}'.format(err))
        session.rollback()
        return flaskify(oto_response.Response('An unexpected Error occured', errors=err, status=500))
    except Exception as err:
        print(err)
    finally:
        session.remove()


@app.route('/loader/update-template-stats')
def update_template_stats():
    global isUpdatingTemplateStats

    if isUpdatingTemplateStats:
        return flaskify(oto_response.Response('Already processing request', status=102))

    isUpdatingTemplateStats = True

    session = create_session()
    try:
        session.execute(
            'INSERT INTO template_sales '
            'SELECT template_id, a.schema, a.collection, wax_price, usd_price, s.seq, s.block_num, s.timestamp '
            'FROM sales s '
            'INNER JOIN assets a ON a.asset_id = s.asset_ids[1] '
            'WHERE s.seq > (SELECT MAX(seq) FROM template_sales) '
            'AND template_id > 0 AND ARRAY_LENGTH(asset_ids, 1) = 1'
        )
        session.commit()

        session.execute('REFRESH MATERIALIZED VIEW CONCURRENTLY template_stats_mv')
        session.commit()

        session.execute('REFRESH MATERIALIZED VIEW CONCURRENTLY schema_stats_mv')
        session.commit()

        session.execute('REFRESH MATERIALIZED VIEW CONCURRENTLY templates_minted_mv')
        session.commit()

        return flaskify(oto_response.Response('Template Stats Updated'))
    except SQLAlchemyError as err:
        log_error('update_template_stats: {}'.format(err))
        session.rollback()
        return flaskify(oto_response.Response('An unexpected Error occured', errors=err, status=500))
    finally:
        isUpdatingTemplateStats = False
        session.remove()


@app.route('/loader/create-volume-day-views')
def create_volume_day_views():
    session = create_session()

    for table in [
        'collection_seller', 'seller'
    ]:
        columns = ''
        table_columns = table.split('_')
        if 'collection' in table_columns:
            columns += 'collection, '
        if 'seller' in table_columns:
            columns += 'seller, '

        for day in [
            '365_days', '180_days', '90_days', '60_days', '30_days', '15_days', '14_days', '7_days', '3_days', '2_days',
            '1_days'
        ]:
            print(
                'volume_{table}_{day}_mv'.format(
                    table=table, day=day
                )
            )

            session.execute(
                'DROP MATERIALIZED VIEW IF EXISTS volume_{table}_{day}_mv CASCADE'.format(
                    table=table, day=day
                )
            )

            where_clause = ''

            aggregates = 'SUM(wax_volume) AS wax_volume, SUM(usd_volume) AS usd_volume, SUM(sales) AS sales'

            sources = {
                'collection_seller': 'volume_collection_market_user_{day}_mv t'.format(day=day),
                'seller': 'volume_collection_market_user_{day}_mv t'.format(day=day),
            }

            source = sources[table]

            if source == 'sales_summary':
                where_clause = 'WHERE timestamp > NOW() AT TIME ZONE \'UTC\' - INTERVAL \'{interval}\''.format(
                    interval=day.replace('_', ' ')
                )
                aggregates = 'sum(wax_price) AS wax_volume, sum(usd_price) AS usd_volume, COUNT(1) AS sales'

            if 'user' not in table_columns and 'buyer' not in table_columns and 'seller' not in table_columns:
                aggregates += ', COUNT(DISTINCT seller) AS sellers, COUNT(DISTINCT buyer) AS buyers'

            sql = (
                'CREATE MATERIALIZED VIEW IF NOT EXISTS volume_{table}_{day}_mv AS '
                'SELECT {columns}type, '
                '{aggregates} '
                'FROM {source} '
                '{where_clause} '
                'GROUP BY {columns}type '.format(
                    day=day, table=table, source=source, columns=columns, aggregates=aggregates,
                    where_clause=where_clause
                )
            )

            print(sql)

            start = time.time()
            session.execute(sql)
            end = time.time()

            print(end - start)

            session.execute(
                'CREATE UNIQUE INDEX ON volume_{table}_{day}_mv ({columns}type) '.format(
                    table=table, columns=columns, day=day
                )
            )

            session.commit()
    return flaskify(oto_response.Response('Volumes Created'))


@app.route('/loader/create-volume-views')
def create_volumes_views():
    session = create_session()

    for table in [
        #'collection_market_user', 'collection_seller', 'collection_buyer',
        #'template_user'
    ]:
        for year in ['before_2024', 'from_2024']:
            sources = {
                'collection_market_user': 'sales_summary t ',
                'collection_seller': 'volume_collection_market_user_{year}_mv t'.format(year=year),
                'collection_buyer': 'volume_collection_market_user_{year}_mv t'.format(year=year),
                'template_user': 'template_sales t LEFT JOIN sales_summary s USING (seq) '
            }

            columns = ''

            table_columns = table.split('_')
            if 'collection' in table_columns:
                columns += 'collection, '
            if 'template' in table_columns:
                columns += 'template_id, schema, t.collection, '
            if 'market' in table_columns:
                columns += 'market, maker, taker, '
            if 'user' in table_columns:
                columns += 'buyer, seller, '
            if 'buyer' in table_columns:
                columns += 'buyer, '
            if 'seller' in table_columns:
                columns += 'seller, '

            source = sources[table]

            aggregates = 'SUM(wax_volume) AS wax_volume, SUM(usd_volume) AS usd_volume, SUM(sales) AS sales'

            where_clause = ''

            if 'sales_summary' in source:
                if year == 'from_2024':
                    where_clause = 'WHERE s.timestamp >= \'2024-01-01\''
                else:
                    where_clause = 'WHERE s.timestamp < \'2024-01-01\''
                aggregates = 'sum(s.wax_price) AS wax_volume, sum(s.usd_price) AS usd_volume, COUNT(1) AS sales'

            if 'user' not in table_columns and 'buyer' not in table_columns and 'seller' not in table_columns:
                aggregates += ',COUNT(DISTINCT seller) AS sellers, COUNT(DISTINCT buyer) AS buyers'

            print(
                'volume_{table}_{year}_mv'.format(
                    table=table, year=year
                )
            )

            session.execute(
                'DROP MATERIALIZED VIEW IF EXISTS volume_{table}_{year}_mv CASCADE'.format(
                    table=table, year=year
                )
            )

            session.execute(
                'CREATE MATERIALIZED VIEW IF NOT EXISTS volume_{table}_{year}_mv AS ' 
                'SELECT {columns}type, '
                '{aggregates} ' 
                'FROM {source} {where_clause}'
                'GROUP BY {columns}type '.format(
                    table=table, year=year, columns=columns, source=source, aggregates=aggregates,
                    where_clause=where_clause
                )
            )

            session.execute(
                'CREATE UNIQUE INDEX ON volume_{table}_{year}_mv ({columns}type) '.format(
                    table=table, columns=columns.replace('t.', ''), year=year
                )
            )

            session.commit()
    for table in [
        #'collection_market_user', 'collection_market', 'collection', 'market',
        #'collection_seller', 'collection_buyer', 'seller', 'buyer',
        #'template_user', 'template'
    ]:
        columns = ''
        table_columns = table.split('_')
        if 'collection' in table_columns:
            columns += 'collection, '
        if 'market' in table_columns:
            columns += 'market, maker, taker, '
        if 'template' in table_columns:
            columns += 'template_id, schema, collection, '
        if 'user' in table_columns:
            columns += 'buyer, seller, '
        if 'buyer' in table_columns:
            columns += 'buyer, '
        if 'seller' in table_columns:
            columns += 'seller, '

        aggregates = 'SUM(wax_volume) AS wax_volume, SUM(usd_volume) AS usd_volume, SUM(sales) AS sales'

        if 'user' not in table_columns and 'buyer' not in table_columns and 'seller' not in table_columns:
            aggregates += ', COUNT(DISTINCT seller) AS sellers, COUNT(DISTINCT buyer) AS buyers'

        print(
            'volume_{table}_all_time_mv'.format(
                table=table
            )
        )

        session.execute(
            'DROP MATERIALIZED VIEW IF EXISTS volume_{table}_all_time_mv CASCADE'.format(
                table=table
            )
        )

        sources = {
            'collection_market_user': (
                '('
                '   SELECT * FROM '
                '   volume_collection_market_user_from_2024_mv '
                '   UNION ALL'
                '   SELECT * FROM '
                '   volume_collection_market_user_before_2024_mv '
                ') t'
            ),
            'collection_market': 'volume_collection_market_user_all_time_mv t',
            'collection': 'volume_collection_market_user_all_time_mv t',
            'market': 'volume_collection_market_user_all_time_mv t',
            'collection_seller': (
                '('
                '   SELECT * FROM '
                '   volume_collection_seller_from_2024_mv'
                '   UNION ALL'
                '   SELECT * FROM '
                '   volume_collection_seller_before_2024_mv'
                ') t'
            ),
            'collection_buyer': (
                '('
                '   SELECT * FROM '
                '   volume_collection_buyer_from_2024_mv'
                '   UNION ALL'
                '   SELECT * FROM '
                '   volume_collection_buyer_before_2024_mv'
                ') t'
            ),
            'seller': 'volume_collection_seller_all_time_mv t',
            'buyer': 'volume_collection_buyer_all_time_mv t',
            'template_user': (
                '('
                '   SELECT * FROM '
                '   volume_template_user_from_2024_mv'
                '   UNION ALL'
                '   SELECT * FROM '
                '   volume_template_user_before_2024_mv'
                ') t'
            ),
            'template': 'volume_template_user_all_time_mv t'
        }

        source = sources[table]

        sql = (
            'CREATE MATERIALIZED VIEW IF NOT EXISTS volume_{table}_all_time_mv AS '
            'SELECT {columns}type, '
            '{aggregates} '
            'FROM {source} '
            'GROUP BY {columns}type '.format(
                table=table, source=source, columns=columns, aggregates=aggregates
            )
        )

        print(sql)

        start = time.time()
        session.execute(sql)
        end = time.time()

        print(end - start)

        session.execute(
            'CREATE UNIQUE INDEX ON volume_{table}_all_time_mv ({columns}type) '.format(
                table=table, columns=columns
            )
        )

        session.commit()

    for table in [
        'collection_market_user', 'collection_market', 'collection', 'market',
        'collection_seller', 'collection_buyer', 'seller', 'buyer',
        'template_user', 'template'
    ]:
        columns = ''
        table_columns = table.split('_')
        if 'collection' in table_columns:
            columns += 'collection, '
        if 'market' in table_columns:
            columns += 'market, maker, taker, '
        if 'template' in table_columns:
            columns += 'template_id, schema, t.collection, '
        if 'user' in table_columns:
            columns += 'buyer, seller, '
        if 'buyer' in table_columns:
            columns += 'buyer, '
        if 'seller' in table_columns:
            columns += 'seller, '

        for day in [
            '1_day'
        ]:
            session.execute(
                'DROP MATERIALIZED VIEW IF EXISTS volume_{table}_{day}_mv CASCADE'.format(
                    table=table, day=day
                )
            )

        for day in [
            '365_days', '180_days', '90_days', '60_days', '30_days', '15_days', '14_days', '7_days', '3_days', '2_days',
            '1_days'
        ]:
            print(
                'volume_{table}_{day}_mv'.format(
                    table=table, day=day
                )
            )

            session.execute(
                'DROP MATERIALIZED VIEW IF EXISTS volume_{table}_{day}_mv CASCADE'.format(
                    table=table, day=day
                )
            )

            where_clause = ''

            aggregates = 'SUM(wax_volume) AS wax_volume, SUM(usd_volume) AS usd_volume, SUM(sales) AS sales'

            sources = {
                'collection_market_user': 'sales_summary t ',
                'collection_market': 'volume_collection_market_user_{day}_mv t'.format(day=day),
                'collection': 'volume_collection_market_user_{day}_mv t'.format(day=day),
                'market': 'volume_collection_market_user_{day}_mv t'.format(day=day),
                'collection_seller': 'volume_collection_market_user_{day}_mv t'.format(day=day),
                'collection_buyer': 'volume_collection_market_user_{day}_mv t'.format(day=day),
                'seller': 'volume_collection_market_user_{day}_mv t'.format(day=day),
                'buyer': 'volume_collection_market_user_{day}_mv t'.format(day=day),
                'template_user': 'template_sales t INNER JOIN sales_summary s USING(seq) ',
                'template': 'volume_template_user_{day}_mv t'.format(day=day),
            }

            source = sources[table]

            if 'sales_summary' in source:
                where_clause = 'WHERE t.timestamp > NOW() AT TIME ZONE \'UTC\' - INTERVAL \'{interval}\''.format(
                    interval=day.replace('_', ' ')
                )
                aggregates = 'sum(t.wax_price) AS wax_volume, sum(t.usd_price) AS usd_volume, COUNT(1) AS sales'

            if 'user' not in table_columns and 'buyer' not in table_columns and 'seller' not in table_columns:
                aggregates += ', COUNT(DISTINCT seller) AS sellers, COUNT(DISTINCT buyer) AS buyers'

            sql = (
                'CREATE MATERIALIZED VIEW IF NOT EXISTS volume_{table}_{day}_mv AS '
                'SELECT {columns}type, '
                '{aggregates} '
                'FROM {source} '
                '{where_clause} '
                'GROUP BY {columns}type '.format(
                    day=day, table=table, source=source, columns=columns, aggregates=aggregates,
                    where_clause=where_clause
                )
            )

            print(sql)

            start = time.time()
            session.execute(sql)
            end = time.time()

            print(end - start)

            session.execute(
                'CREATE UNIQUE INDEX ON volume_{table}_{day}_mv ({columns}type) '.format(
                    table=table, columns=columns.replace('t.', ''), day=day
                )
            )

            session.commit()
    return flaskify(oto_response.Response('Volumes Created'))


@app.route('/loader/update-big-volumes')
def update_big_volumes():
    global isUpdatingBigVolumes

    if isUpdatingBigVolumes:
        return flaskify(oto_response.Response('Already processing request', status=102))

    isUpdatingBigVolumes = True

    session = create_session()

    try:
        session.execute('REFRESH MATERIALIZED VIEW volume_collection_market_user_from_2024_mv')
        session.commit()
        session.execute('REFRESH MATERIALIZED VIEW volume_collection_seller_from_2024_mv')
        session.commit()
        session.execute('REFRESH MATERIALIZED VIEW volume_collection_buyer_from_2024_mv')
        session.commit()
        session.execute('REFRESH MATERIALIZED VIEW collection_sales_by_date_from_2024_mv')
        session.commit()
        session.execute('REFRESH MATERIALIZED VIEW template_collection_sales_by_date_from_2024_mv')
        session.commit()
        session.execute('REFRESH MATERIALIZED VIEW volume_collection_market_user_all_time_mv')
        session.execute('REFRESH MATERIALIZED VIEW volume_collection_market_user_365_days_mv')
        session.execute('REFRESH MATERIALIZED VIEW volume_collection_market_user_180_days_mv')
        session.execute('REFRESH MATERIALIZED VIEW volume_collection_market_user_90_days_mv')
        session.execute('REFRESH MATERIALIZED VIEW volume_collection_market_user_60_days_mv')
        session.execute('REFRESH MATERIALIZED VIEW volume_collection_market_user_30_days_mv')
        session.commit()
        session.execute('REFRESH MATERIALIZED VIEW volume_template_user_from_2024_mv')
        session.commit()
        session.execute('REFRESH MATERIALIZED VIEW volume_template_user_all_time_mv')
        session.commit()
        session.execute('REFRESH MATERIALIZED VIEW monthly_collection_volume_mv')
        session.commit()
        session.execute('REFRESH MATERIALIZED VIEW CONCURRENTLY collection_sales_by_date_mv')
        session.commit()
        session.execute('REFRESH MATERIALIZED VIEW CONCURRENTLY template_collection_sales_by_date_mv')
        session.commit()

        for days in ['all_time', '365_days', '180_days', '90_days', '60_days', '30_days']:
            session.execute(
                'REFRESH MATERIALIZED VIEW CONCURRENTLY volume_collection_market_{days}_mv'.format(days=days)
            )
            session.commit()
            session.execute(
                'REFRESH MATERIALIZED VIEW CONCURRENTLY volume_collection_{days}_mv'.format(days=days)
            )
            session.commit()
            session.execute(
                'REFRESH MATERIALIZED VIEW CONCURRENTLY volume_market_{days}_mv'.format(days=days)
            )
            session.commit()
            session.execute(
                'REFRESH MATERIALIZED VIEW CONCURRENTLY volume_collection_seller_{days}_mv'.format(days=days)
            )
            session.commit()
            session.execute(
                'REFRESH MATERIALIZED VIEW CONCURRENTLY volume_seller_{days}_mv'.format(days=days)
            )
            session.commit()
            session.execute(
                'REFRESH MATERIALIZED VIEW CONCURRENTLY volume_collection_buyer_{days}_mv'.format(days=days)
            )
            session.commit()
            session.execute(
                'REFRESH MATERIALIZED VIEW CONCURRENTLY volume_buyer_{days}_mv'.format(days=days)
            )
            session.commit()
            session.execute(
                'REFRESH MATERIALIZED VIEW CONCURRENTLY volume_drop_{days}_mv'.format(days=days)
            )
            session.commit()
            session.execute(
                'REFRESH MATERIALIZED VIEW CONCURRENTLY volume_template_user_{days}_mv'.format(days=days)
            )
            session.commit()
            session.execute(
                'REFRESH MATERIALIZED VIEW CONCURRENTLY volume_template_{days}_mv'.format(days=days)
            )
            session.commit()

        return flaskify(oto_response.Response('Big Volumes Updated'))
    except SQLAlchemyError as err:
        log_error('update_big_volumes: {}'.format(err))
        session.rollback()
        return flaskify(oto_response.Response('An unexpected Error occured', errors=err, status=500))
    finally:
        isUpdatingBigVolumes = False
        session.remove()


@app.route('/loader/update-small-volumes')
def update_small_volumes():
    global isUpdatingSmallVolumes

    if isUpdatingSmallVolumes:
        return flaskify(oto_response.Response('Already processing request', status=102))

    isUpdatingSmallVolumes = True

    session = create_session()

    try:
        funcs.update_sales_summary(session)

        session.execute('REFRESH MATERIALIZED VIEW volume_collection_market_user_15_days_mv')
        session.execute('REFRESH MATERIALIZED VIEW volume_collection_market_user_14_days_mv')
        session.execute('REFRESH MATERIALIZED VIEW volume_collection_market_user_7_days_mv')
        session.execute('REFRESH MATERIALIZED VIEW volume_collection_market_user_3_days_mv')
        session.execute('REFRESH MATERIALIZED VIEW volume_collection_market_user_2_days_mv')
        session.execute('REFRESH MATERIALIZED VIEW volume_collection_market_user_1_days_mv')
        session.commit()

        session.execute(
            'REFRESH MATERIALIZED VIEW CONCURRENTLY sales_seven_day_chart_mv'
        )
        session.commit()

        for days in ['15_days', '14_days', '7_days', '3_days', '2_days', '1_days']:
            session.execute(
                'REFRESH MATERIALIZED VIEW CONCURRENTLY volume_collection_market_{days}_mv'.format(days=days)
            )
            session.commit()
            session.execute(
                'REFRESH MATERIALIZED VIEW CONCURRENTLY volume_collection_{days}_mv'.format(days=days)
            )
            session.commit()
            session.execute(
                'REFRESH MATERIALIZED VIEW CONCURRENTLY volume_market_{days}_mv'.format(days=days)
            )
            session.commit()
            session.execute(
                'REFRESH MATERIALIZED VIEW CONCURRENTLY volume_collection_seller_{days}_mv'.format(days=days)
            )
            session.commit()
            session.execute(
                'REFRESH MATERIALIZED VIEW CONCURRENTLY volume_seller_{days}_mv'.format(days=days)
            )
            session.commit()
            session.execute(
                'REFRESH MATERIALIZED VIEW CONCURRENTLY volume_collection_buyer_{days}_mv'.format(days=days)
            )
            session.commit()
            session.execute(
                'REFRESH MATERIALIZED VIEW CONCURRENTLY volume_buyer_{days}_mv'.format(days=days)
            )
            session.commit()
            session.execute(
                'REFRESH MATERIALIZED VIEW CONCURRENTLY volume_drop_{days}_mv'.format(days=days)
            )
            session.commit()
            session.execute(
                'REFRESH MATERIALIZED VIEW CONCURRENTLY volume_template_{days}_mv'.format(days=days)
            )
            session.commit()

        return flaskify(oto_response.Response('Small Volumes Updated'))
    except SQLAlchemyError as err:
        log_error('update_small_volumes: {}'.format(err))
        session.rollback()
        return flaskify(oto_response.Response('An unexpected Error occured', errors=err, status=500))
    finally:
        isUpdatingSmallVolumes = False
        session.remove()


@app.route('/loader/update-collection-user-stats')
def update_collection_user_stats():
    global isUpdatingCollectionUserStats

    if isUpdatingCollectionUserStats:
        return flaskify(oto_response.Response('Already processing request', status=102))

    isUpdatingCollectionUserStats = True

    session = create_session()

    try:
        session.execute('REFRESH MATERIALIZED VIEW CONCURRENTLY collection_users_mv')
        session.commit()

        session.execute('REFRESH MATERIALIZED VIEW CONCURRENTLY collection_user_count_mv')
        session.commit()

        session.execute('REFRESH MATERIALIZED VIEW CONCURRENTLY users_mv')
        session.commit()

        return flaskify(oto_response.Response('Collection User Stats Updated'))
    except SQLAlchemyError as err:
        log_error('update_volumes: {}'.format(err))
        session.rollback()
        return flaskify(oto_response.Response('An unexpected Error occured', errors=err, status=500))
    finally:
        isUpdatingCollectionUserStats = False
        session.remove()


def get_delphi_oracle_actions():
    hyperions = get_hyperions()
    for hyperion in hyperions:
        try:
            body = {
                'code': 'delphioracle',
                'index_position': 'primary',
                'json': 'true',
                'key_type': 'i64',
                'limit': 1,
                'lower_bound': '',
                'reverse': 'true',
                'scope': 'waxpusd',
                'show_payer': 'false',
                'table': 'datapoints',
                'table_key': '',
                'upper_bound': ''
            }

            url = '{}/v1/chain/get_table_rows'.format(hyperion)
            print('{}/{}'.format(url, 'delphioracle'))
            response = requests.request("POST", url, json=body)

            return json.loads(response.content)
        except Exception as err:
            log_error('get_delphi_oracle_actions: {}'.format(err))
            continue

    return {'rows': []}


@app.route('/loader/refresh-drops-views')
def refresh_drops_views():
    global isUpdatingDrops

    if isUpdatingDrops:
        return flaskify(oto_response.Response('Already processing request', status=102))

    isUpdatingDrops = True

    start_time = time.time()
    session = create_session()
    try:
        session.execute('REFRESH MATERIALIZED VIEW CONCURRENTLY drop_claim_counts_mv')
        session.commit()
    except SQLAlchemyError as err:
        log_error('refresh_drops_views: {}'.format(err))
        session.rollback()
    except Exception as err:
        log_error('refresh_drops_views: {}'.format(err))
    finally:
        isUpdatingDrops = False
        session.remove()
    end_time = time.time()

    return flaskify(oto_response.Response('Refreshed Drop Claim Counts {}'.format(end_time - start_time)))


@app.route('/loader/refresh-recently-sold')
def refresh_recently_sold():
    global isUpdatingRecentlySold

    if isUpdatingRecentlySold:
        return flaskify(oto_response.Response('Already processing request', status=102))

    isUpdatingRecentlySold = True
    start_time = time.time()
    session = create_session()
    try:
        session.execute('REFRESH MATERIALIZED VIEW CONCURRENTLY recently_sold_hour_mv')
        session.execute('REFRESH MATERIALIZED VIEW CONCURRENTLY recently_sold_day_mv')
        session.execute('REFRESH MATERIALIZED VIEW CONCURRENTLY recently_sold_week_mv')
        session.execute('REFRESH MATERIALIZED VIEW CONCURRENTLY recently_sold_month_mv')
        session.commit()
    except SQLAlchemyError as err:
        log_error('refresh_recently_sold: {}'.format(err))
        session.rollback()
    except Exception as err:
        log_error('refresh_recently_sold: {}'.format(err))
    finally:
        isUpdatingRecentlySold = False
        session.remove()
    end_time = time.time()

    return flaskify(oto_response.Response('Refreshed Recently Sold {}'.format(end_time - start_time)))


@app.route('/loader/load-chronicle-transactions')
def load_chronicle_transactions():
    global isStopped
    isStopped = False
    global isLoadingChronicleTx
    global isForked
    global action_measure_god
    action_measure_god['total_time'] = 0
    action_measure_god['fork_time'] = 0
    action_measure_god['actual_fork_handling'] = 0
    isLoadingChronicleTx = True
    while not isStopped:
        max_seq = 0
        min_seq = 0
        session = create_session()
        try:
            start_full_time = time.time()
            start = time.time()

            txs = session.execute(
                'SELECT * FROM chronicle_transactions '
                'WHERE NOT ingested AND NOT EXISTS (SELECT * FROM handle_fork WHERE forked) '
                'ORDER BY seq ASC LIMIT 10000 '
            )

            end = time.time()

            if txs.rowcount == 0:
                time.sleep(2)

            transaction_time = end - start

            for tx in txs:
                if min_seq == 0:
                    min_seq = tx['seq']
                max_seq = tx['seq']
                start = time.time()
                forked = session.execute('SELECT * FROM handle_fork').first()

                if isForked:
                    isForked = forked['forked']

                if isForked:
                    return

                if forked['forked'] and forked['block_num'] <= tx['block_num']:
                    raise RuntimeError('Fork')
                end = time.time()
                action_measure_god['fork_time'] += end - start
                action = {
                    'act': {
                        'account': tx['account'],
                        'name': tx['action_name'],
                        'data': tx['data'],
                        'authorization': [{'actor': tx['actor']}]
                    },
                    'trx_id': tx['transaction_id'],
                    'global_sequence': tx['seq'],
                    'block_num': tx['block_num'],
                    'timestamp': tx['timestamp']
                }

                parse_time = parse_action(session, action)

                action_measure_god['parse_time'] = action_measure_god['parse_time'] + parse_time
                session.execute(
                    'UPDATE chronicle_transactions SET ingested = TRUE WHERE seq = :max_seq', {'max_seq': max_seq}
                )

            session.commit()
            action_measure_god['transaction_time'] = action_measure_god['transaction_time'] + transaction_time

            end_full_time = time.time()

            action_measure_god['total_time'] = action_measure_god['total_time'] + end_full_time - start_full_time
        except RuntimeError as err:
            start = time.time()
            log_error('Fork handled: {}'.format(err))
            session.commit()
            isForked = True
            time.sleep(30)
            end = time.time()
            action_measure_god['actual_fork_handling'] += end - start
        except SQLAlchemyError as err:
            log_error('SQLAlchemyError load_chronicle_transactions: {}'.format(err))
            session.rollback()
            isStopped = True
        except Exception as err:
            log_error('load_chronicle_transactions: {}'.format(err))
            session.execute(
                'INSERT INTO error_transactions SELECT * FROM chronicle_transactions WHERE seq = :seq',
                {'seq': max_seq}
            )
            session.commit()
            isStopped = True
        finally:
            session.remove()
    isLoadingChronicleTx = False


def load_usd_rate_till_stopped():
    global isStopped
    global isLoadingUSD
    try:
        isLoadingUSD = True
        while not isStopped:
            load_usd_rate()
            time.sleep(30)
    except Exception as err:
        log_error('load_usd_rate_till_stopped: {}'.format(err))
        return flaskify(oto_response.Response('An unexpected Error occured', errors=err, status=500))
    finally:
        isLoadingUSD = False


@app.route('/loader/status')
def status():
    global isUpdatingAtomicAssets
    global isLoadingUSD
    global isStopped
    global action_measure_god

    return flaskify(oto_response.Response({
        'stopped': isStopped,
        'loading': isLoading,
        'isUpdatingAtomicAssets': isUpdatingAtomicAssets,
        'isLoadingUSD': isLoadingUSD,
        'measureGod': action_measure_god
    }))


@app.route('/loader/load-usd-rate')
def load_usd_rate():
    try:
        start_time = time.time()
        delphi_actions = get_delphi_oracle_actions()

        if 'rows' in delphi_actions.keys():
            session = create_session()
            try:
                for delphi_action in delphi_actions['rows']:
                    load_wax_usd_rate(session, delphi_action)
                session.commit()
            except SQLAlchemyError as err:
                log_error('load_usd_rate: {}'.format(err))
                session.rollback()
            finally:
                session.remove()
        end_time = time.time()
        print('load_usd_rate {}'.format(end_time - start_time))
    except Exception as err:
        log_error('load_usd_rate: {}'.format(err))
    return flaskify(oto_response.Response('USD prices loaded'))


def keep_updating_assets():
    global isStopped
    global isUpdatingAssetsData
    isStopped = False
    try:
        isUpdatingAssetsData = True
        while not isStopped:
            session = create_session()
            try:
                funcs.apply_atomic_updates(session)
                funcs.apply_simple_updates(session)
            except SQLAlchemyError as err:
                log_error('keep_updating_assets: {}'.format(err))
                session.rollback()
            except RuntimeError as err:
                log_error('keep_updating_assets: {}'.format(err))
                session.rollback()
                time.sleep(30)
            finally:
                session.remove()
    except Exception as err:
        log_error('keep_updating_assets: {}'.format(err))
        return flaskify(oto_response.Response('An unexpected Error occured', errors=err, status=500))
    finally:
        isUpdatingAssetsData = False


@app.route('/loader/update-atomic-mints')
def keep_updating_atomic_mints():
    global isStopped
    global isUpdatingAtomicAssets
    isStopped = False
    try:
        isUpdatingAtomicAssets = True
        while not isStopped:
            session = create_session()
            try:
                rowcnt = funcs.calc_atomic_mints(session)
                if rowcnt < 1:
                    time.sleep(5)
            except SQLAlchemyError as err:
                log_error('keep_updating_atomic_mints: {}'.format(err))
                session.rollback()
            except RuntimeError as err:
                log_error('keep_updating_atomic_mints: {}'.format(err))
                session.rollback()
                time.sleep(30)
            finally:
                session.remove()
    except Exception as err:
        log_error('keep_updating_atomic_mints: {}'.format(err))
        return flaskify(oto_response.Response('An unexpected Error occured', errors=err, status=500))
    finally:
        isUpdatingAtomicAssets = False


@app.route('/loader/start/')
def start():
    global isUpdatingAtomicAssets
    global isLoadingChronicleTx
    global isLoadingUSD
    global isStopped
    if not isStopped or isLoadingChronicleTx or isUpdatingAtomicAssets or isLoadingUSD:
        return flaskify(oto_response.Response('Already processing request', status=102))
    try:
        isStopped = False
        _thread.start_new_thread(load_chronicle_transactions, ())
        _thread.start_new_thread(keep_updating_atomic_mints, ())
        _thread.start_new_thread(load_usd_rate_till_stopped, ())
        _thread.start_new_thread(keep_updating_assets, ())
        return flaskify(oto_response.Response({'Started'}))
    except Exception as err:
        log_error('start: {}'.format(err))
        return flaskify(oto_response.Response('An unexpected Error occured', errors=err, status=500))


@app.route('/loader/stop/')
def stop():
    global isStopped
    isStopped = True
    return flaskify(oto_response.Response('Stopping after next iteration'))


if __name__ == '__main__':
    logging.basicConfig(filename='loader.err', level=logging.ERROR)
    run_loader(app)
