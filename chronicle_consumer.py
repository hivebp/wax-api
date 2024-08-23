import asyncio
import json
import logging
import time

import websockets

from websockets import WebSocketServerProtocol
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import scoped_session, sessionmaker
from eventemitter import EventEmitter

import funcs
import config
from config import PostgresConsumerConfig

logging.basicConfig(filename='consumer.err', level=logging.ERROR)

engine = create_engine(PostgresConsumerConfig.SQLALCHEMY_DATABASE_URI)


def create_session():
    return scoped_session(sessionmaker(bind=engine))


def log_error(e):
    print(e)
    logging.error(e)


def handle_atomicassets_burns_reversed(session, block_num):
    reverse_trxs = session.execute(
        'SELECT * FROM atomicassets_burns_reversed WHERE block_num >= :block_num ORDER BY seq ASC',
        {'block_num': block_num}
    )

    for trx in reverse_trxs:
        session.execute(
            'UPDATE assets SET burned = FALSE, owner = :burner WHERE asset_id = :asset_id',
            {'asset_id': trx['asset_id'], 'burner': trx['burner']}
        )


def handle_atomicassets_updates_reversed(session, block_num):
    reverse_trxs = session.execute(
        'SELECT * FROM atomicassets_updates_reversed WHERE block_num >= :block_num ORDER BY seq ASC',
        {'block_num': block_num}
    )

    for trx in reverse_trxs:
        try:
            update = session.execute(
                'SELECT a.collection, a.schema, a.asset_id, d1.data AS mdata, d2.data AS idata, d3.data AS tdata, '
                'u.seq, old_mdata_id '
                'FROM atomicassets_updates_reversed u '
                'INNER JOIN assets a USING(asset_id) '
                'LEFT JOIN templates t USING (template_id) '
                'LEFT JOIN data d1 ON (old_mdata_id = d1.data_id) '
                'LEFT JOIN data d2 ON (a.immutable_data_id = d2.data_id) '
                'LEFT JOIN data d3 ON (t.immutable_data_id = d3.data_id) '
                'WHERE u.seq = :seq '
                'ORDER BY u.asset_id ASC ', {'seq': trx['seq']}
            ).first()

            try:
                data = funcs.parse_data(
                    json.loads(update['tdata'])
                ) if 'tdata' in update.keys() and update['tdata'] else {}
                if 'idata' in update.keys() and update['idata']:
                    data.update(funcs.parse_data(json.loads(update['idata'])))
                if 'mdata' in update.keys() and update['mdata']:
                    data.update(funcs.parse_data(json.loads(update['mdata'])))

                new_asset = {}

                new_asset['name'] = data['name'].strip()[0:255] if 'name' in data.keys() else None
                new_asset['image'] = str(data['img']).strip()[0:255] if 'img' in data.keys() else None
                new_asset['video'] = str(data['video']).strip()[0:255] if 'video' in data.keys() else None
                new_asset['seq'] = update['seq']
                new_asset['old_mdata_id'] = update['old_mdata_id']
                new_asset['asset_id'] = update['asset_id']

                new_asset['attribute_ids'] = funcs.parse_attributes(
                    session, update['collection'], update['schema'], data)

                session.execute(
                   'UPDATE assets SET attribute_ids = :attribute_ids, mutable_data_id = :old_mdata_id '
                   '{name_clause} {image_clause} {video_clause} '
                   'WHERE asset_id = :asset_id '.format(
                       name_clause=(
                           ', name_id = (SELECT name_id FROM names WHERE name = :name)'
                       ) if new_asset['name'] else ', name_id = NULL',
                       image_clause=(
                           ', image_id = (SELECT image_id FROM images WHERE image = :image)'
                       ) if new_asset['image'] else ', image_id = NULL',
                       video_clause=(
                           ', video_id = (SELECT video_id FROM videos WHERE video = :video)'
                       ) if new_asset['video'] else ', video_id = NULL',
                   ), new_asset
                )
            except Exception as err:
                log_error('handle_atomicassets_updates_reversed: {}'.format(err))
                raise err
        except SQLAlchemyError as err:
            log_error('handle_atomicassets_updates_reversed: {}'.format(err))
            raise err
        except Exception as err:
            log_error('handle_atomicassets_updates_reversed: {}'.format(err))
            raise err


def handle_craft_erase_updates_reversed(session, block_num):
    reverse_trxs = session.execute(
        'SELECT * FROM craft_erase_updates_reversed WHERE block_num >= :block_num ORDER BY seq ASC',
        {'block_num': block_num}
    )

    for trx in reverse_trxs:
        session.execute(
            'UPDATE crafts SET erased = FALSE WHERE craft_id = :craft_id', {'craft_id': trx['craft_id']}
        )


def handle_craft_ready_updates_reversed(session, block_num):
    reverse_trxs = session.execute(
        'SELECT * FROM craft_ready_updates_reversed WHERE block_num >= :block_num ORDER BY seq ASC',
        {'block_num': block_num}
    )

    for trx in reverse_trxs:
        session.execute(
            'UPDATE crafts SET ready = FALSE WHERE craft_id = :craft_id', {'craft_id': trx['craft_id']}
        )


def handle_craft_times_updates_reversed(session, block_num):
    reverse_trxs = session.execute(
        'SELECT * FROM craft_times_updates_reversed WHERE block_num >= :block_num ORDER BY seq ASC',
        {'block_num': block_num}
    )

    for trx in reverse_trxs:
        session.execute(
            'UPDATE crafts SET unlock_time = :old_unlock_time, end_time = :old_end_time '
            'WHERE craft_id = :craft_id',
            {
                'craft_id': trx['craft_id'],
                'old_unlock_time': trx['old_unlock_time'],
                'old_end_time': trx['old_end_time']
            }
        )


def handle_craft_total_updates_reversed(session, block_num):
    reverse_trxs = session.execute(
        'SELECT * FROM craft_total_updates_reversed WHERE block_num >= :block_num ORDER BY seq ASC',
        {'block_num': block_num}
    )

    for trx in reverse_trxs:
        session.execute(
            'UPDATE crafts SET unlock_time = :old_unlock_time, end_time = :old_end_time '
            'WHERE craft_id = :craft_id',
            {
                'craft_id': trx['craft_id'],
                'old_unlock_time': trx['old_unlock_time'],
                'old_end_time': trx['old_end_time']
            }
        )


def handle_drop_auth_updates_reversed(session, block_num):
    reverse_trxs = session.execute(
        'SELECT * FROM drop_auth_updates_reversed WHERE block_num >= :block_num ORDER BY seq ASC',
        {'block_num': block_num}
    )

    for trx in reverse_trxs:
        session.execute(
            'UPDATE drops SET auth_required = :old_auth_required '
            'WHERE drop_id = :drop_id AND contract = :contract',
            {
                'drop_id': trx['drop_id'],
                'contract': trx['contract'],
                'old_auth_required': trx['old_auth_required']
            }
        )


def handle_drop_display_updates_reversed(session, block_num):
    reverse_trxs = session.execute(
        'SELECT * FROM drop_display_updates_reversed WHERE block_num >= :block_num ORDER BY seq ASC',
        {'block_num': block_num}
    )

    for trx in reverse_trxs:
        session.execute(
            'UPDATE drops SET display_data = :old_display_data '
            'WHERE drop_id = :drop_id AND contract = :contract',
            {
                'drop_id': trx['drop_id'],
                'contract': trx['contract'],
                'old_display_data': trx['old_display_data']
            }
        )


def handle_drop_erase_updates_reversed(session, block_num):
    reverse_trxs = session.execute(
        'SELECT * FROM drop_erase_updates_reversed WHERE block_num >= :block_num ORDER BY seq ASC',
        {'block_num': block_num}
    )

    for trx in reverse_trxs:
        session.execute(
            'UPDATE drops SET erased = FALSE '
            'WHERE drop_id = :drop_id AND contract = :contract',
            {
                'drop_id': trx['drop_id'],
                'contract': trx['contract']
            }
        )


def handle_drop_fee_updates_reversed(session, block_num):
    reverse_trxs = session.execute(
        'SELECT * FROM drop_fee_updates_reversed WHERE block_num >= :block_num ORDER BY seq ASC',
        {'block_num': block_num}
    )

    for trx in reverse_trxs:
        session.execute(
            'UPDATE drops SET fee_rate = :old_fee_rate '
            'WHERE drop_id = :drop_id AND contract = :contract',
            {
                'drop_id': trx['drop_id'],
                'contract': trx['contract'],
                'old_fee_rate': trx['old_fee_rate']
            }
        )


def handle_drop_hidden_updates_reversed(session, block_num):
    reverse_trxs = session.execute(
        'SELECT * FROM drop_hidden_updates_reversed WHERE block_num >= :block_num ORDER BY seq ASC',
        {'block_num': block_num}
    )

    for trx in reverse_trxs:
        session.execute(
            'UPDATE drops SET is_hidden = :old_is_hidden '
            'WHERE drop_id = :drop_id AND contract = :contract',
            {
                'drop_id': trx['drop_id'],
                'contract': trx['contract'],
                'old_is_hidden': trx['old_is_hidden']
            }
        )


def handle_drop_limit_updates_reversed(session, block_num):
    reverse_trxs = session.execute(
        'SELECT * FROM drop_limit_updates_reversed WHERE block_num >= :block_num ORDER BY seq ASC',
        {'block_num': block_num}
    )

    for trx in reverse_trxs:
        session.execute(
            'UPDATE drops SET account_limit = :old_account_limit, account_limit_cooldown = :old_account_limit_cooldown '
            'WHERE drop_id = :drop_id AND contract = :contract',
            {
                'drop_id': trx['drop_id'],
                'contract': trx['contract'],
                'old_account_limit': trx['old_account_limit'],
                'old_account_limit_cooldown': trx['old_account_limit_cooldown']
            }
        )


def handle_drop_max_updates_reversed(session, block_num):
    reverse_trxs = session.execute(
        'SELECT * FROM drop_max_updates_reversed WHERE block_num >= :block_num ORDER BY seq ASC',
        {'block_num': block_num}
    )

    for trx in reverse_trxs:
        session.execute(
            'UPDATE drops SET max_claimable = :old_max_claimable '
            'WHERE drop_id = :drop_id AND contract = :contract',
            {
                'drop_id': trx['drop_id'],
                'contract': trx['contract'],
                'old_max_claimable': trx['old_max_claimable']
            }
        )


def handle_drop_price_updates_reversed(session, block_num):
    reverse_trxs = session.execute(
        'SELECT * FROM drop_price_updates_reversed WHERE block_num >= :block_num ORDER BY seq ASC',
        {'block_num': block_num}
    )

    for trx in reverse_trxs:
        session.execute(
            'UPDATE drops SET price = :old_price, currency = :old_currency '
            'WHERE drop_id = :drop_id AND contract = :contract',
            {
                'drop_id': trx['drop_id'],
                'contract': trx['contract'],
                'old_price': trx['old_price'],
                'old_currency': trx['old_currency']
            }
        )


def handle_drop_times_updates_reversed(session, block_num):
    reverse_trxs = session.execute(
        'SELECT * FROM drop_times_updates_reversed WHERE block_num >= :block_num ORDER BY seq ASC',
        {'block_num': block_num}
    )

    for trx in reverse_trxs:
        session.execute(
            'UPDATE drops SET start_time = :old_start_time, end_time = :old_end_time '
            'WHERE drop_id = :drop_id AND contract = :contract',
            {
                'drop_id': trx['drop_id'],
                'contract': trx['contract'],
                'old_start_time': trx['old_start_time'],
                'old_end_time': trx['old_end_time']
            }
        )


def handle_simpleassets_burns_reversed(session, block_num):
    reverse_trxs = session.execute(
        'SELECT * FROM simpleassets_burns_reversed WHERE block_num >= :block_num ORDER BY seq ASC',
        {'block_num': block_num}
    )

    for trx in reverse_trxs:
        session.execute(
            'UPDATE assets SET burned = FALSE, owner = burner '
            'FROM simpleassets_burns_reversed s WHERE asset_id = ANY(asset_ids) AND s.seq = :seq', {'seq': trx['seq']}
        )


def handle_simpleassets_updates_reversed(session, block_num):
    reverse_trxs = session.execute(
        'SELECT * FROM simpleassets_updates_reversed WHERE block_num >= :block_num ORDER BY seq ASC',
        {'block_num': block_num}
    )

    for trx in reverse_trxs:
        try:
            update = session.execute(
                'SELECT a.collection, a.schema, a.asset_id, d1.data AS mdata, d2.data AS idata, '
                'u.seq, old_mdata_id '
                'FROM simpleassets_updates_reversed u '
                'INNER JOIN assets a USING(asset_id) '
                'LEFT JOIN data d1 ON (old_mdata_id = d1.data_id) '
                'LEFT JOIN data d2 ON (a.immutable_data_id = d2.data_id) '
                'WHERE u.seq = :seq '
                'ORDER BY u.asset_id ASC ', {'seq': trx['seq']}
            ).first()

            try:
                data = funcs.parse_data(
                    json.loads(update['idata'])
                ) if 'idata' in update.keys() and update['idata'] else {}
                if 'mdata' in update.keys() and update['mdata']:
                    data.update(funcs.parse_data(json.loads(update['mdata'])))

                new_asset = {}

                new_asset['name'] = data['name'].strip()[0:255] if 'name' in data.keys() else None
                new_asset['image'] = str(data['img']).strip()[0:255] if 'img' in data.keys() else None
                new_asset['video'] = str(data['video']).strip()[0:255] if 'video' in data.keys() else None
                new_asset['seq'] = update['seq']
                new_asset['old_mdata_id'] = update['old_mdata_id']
                new_asset['asset_id'] = update['asset_id']

                new_asset['attribute_ids'] = funcs.parse_attributes(
                    session, update['collection'], update['schema'], data)

                session.execute(
                   'UPDATE assets SET attribute_ids = :attribute_ids, mutable_data_id = :old_mdata_id '
                   '{name_clause} {image_clause} {video_clause} '
                   'WHERE asset_id = :asset_id '.format(
                       name_clause=(
                           ', name_id = (SELECT name_id FROM names WHERE name = :name)'
                       ) if new_asset['name'] else ', name_id = NULL',
                       image_clause=(
                           ', image_id = (SELECT image_id FROM images WHERE image = :image)'
                       ) if new_asset['image'] else ', image_id = NULL',
                       video_clause=(
                           ', video_id = (SELECT video_id FROM videos WHERE video = :video)'
                       ) if new_asset['video'] else ', video_id = NULL',
                   ), new_asset
                )
            except Exception as err:
                log_error('handle_simpleassets_updates_reversed: {}'.format(err))
                raise err
        except SQLAlchemyError as err:
            log_error('handle_simpleassets_updates_reversed: {}'.format(err))
            raise err
        except Exception as err:
            log_error('handle_simpleassets_updates_reversed: {}'.format(err))
            raise err


def handle_transfers_reversed(session, block_num):
    reverse_trxs = session.execute(
        'SELECT * FROM transfers_reversed WHERE block_num >= :block_num ORDER BY seq ASC',
        {'block_num': block_num}
    )

    for trx in reverse_trxs:
        session.execute(
            'UPDATE assets SET owner = :sender '
            'FROM transfers_reversed s WHERE asset_id = ANY(asset_ids) AND s.seq = :seq', {'seq': trx['seq']}
        )


def handle_fork(block_num, unconfirmed_block, confirmed_block, session):
    try:
        fork = {
            'block_num': block_num,
            'unconfirmed_block': unconfirmed_block,
            'confirmed_block': confirmed_block
        }

        session.execute('UPDATE handle_fork SET forked = TRUE, block_num = :block_num ', fork)
        session.execute('INSERT INTO forks '
                        'VALUES(:block_num, :unconfirmed_block, :confirmed_block, NOW() AT TIME ZONE \'utc\')', fork)

        session.commit()
        block_num_tables_reversed = session.execute(
            'SELECT t1.table_name, t2.table_name AS reverse_table_name '
            'FROM tables_with_block_num t1 '
            'LEFT JOIN tables_with_block_num t2 ON (t2.table_name = CONCAT(t1.table_name, \'_reversed\')) '
            'WHERE t1.table_name NOT LIKE \'%_reversed\' AND t1.table_name NOT LIKE \'removed_%\' '
            'AND t1.table_name NOT IN (\'forks\', \'handle_fork\') '
            'AND t2.table_name IS NOT NULL'
        )

        for tables in block_num_tables_reversed:
            if tables['reverse_table_name']:
                session.execute(
                    'INSERT INTO {reverse_table_name} '
                    'SELECT * FROM {table_name} WHERE block_num >= :block_num'.format(
                        reverse_table_name=tables['reverse_table_name'],
                        table_name=tables['table_name']
                    ), {'block_num': block_num}
                )
        session.commit()

        block_num_tables = session.execute(
            'SELECT t1.table_name, t2.table_name AS reverse_table_name '
            'FROM tables_with_block_num t1 '
            'LEFT JOIN tables_with_block_num t2 ON (t2.table_name = CONCAT(t1.table_name, \'_reversed\')) '
            'WHERE t1.table_name NOT LIKE \'%_reversed\' AND t1.table_name NOT LIKE \'removed_%\' '
            'AND t1.table_name NOT IN (\'forks\', \'handle_fork\')'
        )

        for tables in block_num_tables:
            session.execute(
                'DELETE FROM {table_name} WHERE block_num >= :block_num'.format(
                    table_name=tables['table_name']
                ), {'block_num': block_num}
            )

        session.commit()

        handle_atomicassets_burns_reversed(session, block_num)
        handle_atomicassets_updates_reversed(session, block_num)
        handle_craft_erase_updates_reversed(session, block_num)
        handle_craft_ready_updates_reversed(session, block_num)
        handle_craft_times_updates_reversed(session, block_num)
        handle_craft_total_updates_reversed(session, block_num)
        handle_drop_auth_updates_reversed(session, block_num)
        handle_drop_display_updates_reversed(session, block_num)
        handle_drop_erase_updates_reversed(session, block_num)
        handle_drop_fee_updates_reversed(session, block_num)
        handle_drop_hidden_updates_reversed(session, block_num)
        handle_drop_limit_updates_reversed(session, block_num)
        handle_drop_max_updates_reversed(session, block_num)
        handle_drop_price_updates_reversed(session, block_num)
        handle_drop_times_updates_reversed(session, block_num)
        handle_simpleassets_burns_reversed(session, block_num)
        handle_simpleassets_updates_reversed(session, block_num)
        handle_transfers_reversed(session, block_num)

        session.commit()

        session.execute('UPDATE handle_fork SET forked = FALSE')

        session.commit()
    except SQLAlchemyError as err:
        log_error('handle_fork {}: {}'.format(block_num, err))
        session.rollback()
        raise err
    except Exception as err:
        log_error('handle_fork {}: {}'.format(block_num, err))
        raise err


def handle_transaction(action, block_num, timestamp, session):
    if not action or 'trace' not in action.keys():
        return
    try:
        traces = action['trace']
        trx_id = traces['id']
        for trace in traces['action_traces']:
            try:
                if not trace['receipt'] or trace['receipt']['receiver'] != trace['act']['account'] or trace['act'][
                    'account'
                ] not in config.contracts:
                    continue
                trace['seq'] = trace['receipt']['global_sequence']
                trace['transaction_id'] = trx_id
                trace['block_num'] = block_num
                trace['timestamp'] = timestamp

                account = trace['act']['account']
                name = trace['act']['name']
                actor = trace['act']['authorization'][0]['actor'] if trace['act']['authorization'] and len(
                    trace['act']['authorization']) > 0 else None
                trace['actor'] = actor
                trace['account'] = account
                trace['name'] = name

                insert_transaction = (account == 'atomicassets' and name in [
                    'logmint',
                    'logtransfer',
                    'burnasset',
                    'lognewoffer',
                    'acceptoffer',
                    'canceloffer',
                    'declineoffer',
                    'setcoldata',
                    'setmarketfee',
                    'addcolauth',
                    'remcolauth',
                    'lognewtempl',
                    'createcol',
                    'logbackasset',
                    'createschema',
                    'extendschema',
                    'setassetdata'
                ]) or (account == 'atomicmarket' and name in [
                    'purchasesale',
                    'cancelsale',
                    'lognewsale',
                    'cancelauct',
                    'auctionbid',
                    'lognewauct',
                    'auctclaimbuy',
                    'cancelbuyo',
                    'acceptbuyo',
                    'declinebuyo',
                    'lognewbuyo',
                    'logsalestart',
                    'canceltbuyo',
                    'fulfilltbuyo',
                    'lognewtbuyo'
                ]) or (account == 'simpleassets' and name in [
                    'createlog',
                    'transfer',
                    'offer',
                    'burn',
                    'update',
                    'claim',
                ]) or (account in ['atomicdropsx', 'neftyblocksd', 'nfthivedrops'] and name in [
                    'lognewdrop',
                    'setdropdata',
                    'setdroplimit',
                    'setdropmax',
                    'setdropprice',
                    'setdprices',
                    'setfeerate',
                    'setdropauth',
                    'setdrophiddn',
                    'setdroptimes',
                    'claimdrop',
                    'claimdropkey',
                    'claimdropwl',
                    'claimwproof',
                    'erasedrop',
                    'lognewpfp',
                    'setpfpdata',
                    'setpfplimit',
                    'setpfpmax',
                    'setpfpprice',
                    'setpfpprices',
                    'setpfpfee',
                    'setpfpauth',
                    'setpfptimes',
                    'claimpfpdrop',
                    'claimpfpwl',
                    'claimpfproof',
                    'erasepfp',
                    'mintpfp',
                    'addpfpresult',
                    'logprices',
                    'swappfp',
                    'remintpfp'
                ]) or (account == 'nfthivedrops' and name in [
                    'addconftoken',
                    'remconftoken'
                ]) or (account == 'waxarena3dk1' and name == 'createbid') or (account == 'wax.stash' and name in [
                    'editlisting',
                    'cancellistin'
                ]) or (account == 'gpk.myth' and name in [
                    'loglist',
                    'delist',
                    'logsale'
                ]) or (account == 'nft.hive' and name in [
                    'lognewsale',
                    'logbuy',
                    'cancelsale',
                    'execute'
                ]) or (account == 'ws.myth' and name in [
                    'loglist',
                    'delist',
                    'logsale'
                ]) or (account == 'waxstashsale' and name in [
                    'cancelpacks',
                    'cancelpack'
                ]) or (account == 'waxplorercom' and name in [
                    'logbuy',
                    'lognewsale',
                    'cancelsale',
                ]) or (account == 'market.myth' and name in [
                    'logsale',
                    'loglisting',
                    'dropsale'
                ]) or (account == 'simplemarket' and name in [
                    'updateprice',
                    'buylog',
                    'cancel'
                ]) or (account == 'market.place' and name in [
                    'list',
                    'unlist',
                    'bid',
                    'buy',
                    'claimauction',
                    'logindex',
                    'updlisting'
                ]) or (account == 'wax.gg' and name == 'updatephoto') or (account in [
                    'packs.topps', 'packs.ws', 'pack.worlds'
                ] and name == 'transfer') or (account == 'sales.nft' and name in [
                    'logsale',
                    'shopsetitem'
                ]) or (account == 'atomicpacksx' and name in [
                    'announcepack',
                    'lognewpack',
                    'completepack',
                    'setpackdata',
                    'setpacktime'
                ]) or (account == 'nfthivepacks' and name in [
                    'lognewpack',
                    'setdisplay',
                    'delpack',
                    'setpacktime',
                    'delrelease',
                    'addassets',
                    'createpool',
                    'remassets',
                    'logresult'
                ]) or (account == 'neftyblocksp' and name in [
                    'createpack',
                    'createspack',
                    'lognewpack',
                    'setpackdata'
                ]) or (account == 'waxbuyoffers' and name in [
                    'logsale',
                    'lognewoffer',
                    'logerase',
                    'logbalance'
                ]) or (account == 'clltncattool' or name in [
                    'setcategory',
                    'setcatcol',
                    'settag',
                    'settagcol',
                    'suggestcat',
                    'suggesttag',
                    'addfilter',
                    'remfilter'
                ]) or (account == 'atomhubtools' and name in [
                    'addaccvalues',
                    'remaccvalues',
                    'addblacklist',
                    'addscam',
                    'addaccvalues',
                    'remscam',
                    'addverify',
                    'remverify',
                    'addwhitelist',
                    'remwhitelist'
                ]) or (account == 'neftyblocksa' and name in [
                    'addtolist',
                    'delfromlist'
                ]) or (account == 'verifystatus' and name in [
                    'addtolist',
                    'remfromlist',
                    'setlist',
                    'addmarket',
                    'remmarket',
                    'logvotes'
                ]) or (account == 'nfthivecraft' and name in [
                    'lognewcraft',
                    'setcrafttime',
                    'setdisplay',
                    'setready',
                    'logresult',
                    'delcraft',
                    'craft',
                    'mint',
                    'lognewmirror',
                    'mirrorcraft',
                    'logmresult',
                    'delmirror',
                    'setmdisplay',
                    'setmirrortime',
                    'mintmirror',
                    'settotal',
                    'swappfp',
                    'remintmirror'
                ]) or (account == 'twitchreward' and name in [
                    'lognewdrop',
                    'setdropmax',
                    'setdropdata',
                    'claimdrop',
                    'erasedrop',
                    'addreward'
                ]) or (account == 'redeemprtcol' and name in [
                    'redeem', 'accept', 'reject', 'release'
                ]) or (account == 'wufclaimtool' and name in [
                    'lognewdrop', 'addclaimers', 'delairdrop', 'claim', 'setready'
                ]) or (account == 'wufclaimtool' and name in [
                    'lognewdrop', 'addclaimers', 'delairdrop', 'claim', 'setready'
                ]) or (account == 'rwax' and name in [
                    'createtoken', 'logtokenize', 'redeem'
                ])

                if insert_transaction:
                    trace['data'] = json.dumps(trace['act']['data'])
                    session.execute(
                        'INSERT INTO chronicle_transactions SELECT :transaction_id, :seq, :timestamp, :block_num, '
                        ':account, :name, :data, FALSE, :actor '
                        'WHERE NOT EXISTS (SELECT seq FROM chronicle_transactions WHERE seq = :seq)'
                        , trace
                    )
            except SQLAlchemyError as err:
                session.rollback()
                session.remove()
                log_error('handle_transaction sql {}: {}'.format(trace, err))
                raise err
            except Exception as err:
                logging.error('handle_transaction in {}: {}'.format(trace, err))
                raise err
    except Exception as err:
        logging.error('handle_transaction out {}: {}'.format(action, err))
        raise err


class Server:
    clients = set()
    emitter = EventEmitter()

    confirmed_block = 0
    unconfirmed_block = 0

    async def register(self, ws: WebSocketServerProtocol) -> None:
        self.clients.add(ws)
        self.emitter.emit('connected', {
            'remoteAddress': config.chronicle_settings['host'],
            'remoteFamily': 'IPv4',
            'remotePort': config.chronicle_settings['port']
        })

    async def unregister(self, ws: WebSocketServerProtocol) -> None:
        self.emitter.emit('disconnected', {
            'remoteAddress': config.chronicle_settings['host'],
            'remoteFamily': 'IPv4',
            'remotePort': config.chronicle_settings['port']
        })
        if ws in self.clients:
            self.clients.remove(ws)

    async def send_to_clients(self, ws: WebSocketServerProtocol) -> None:
        self.clients.remove(ws)

    async def ws_handler(self, ws: WebSocketServerProtocol, uri: str):
        await self.register(ws)
        try:
            await self.distribute(ws)
        finally:
            await self.unregister(ws)

    async def distribute(self, ws: WebSocketServerProtocol):
        if not ws:
            logging.error('No Socket')
        try:
            session = create_session()
            try:
                async for msg in ws:
                    try:
                        msg_type = int.from_bytes(msg[0:3], byteorder='little')

                        do_ack = False

                        if msg_type == 1003:
                            message = json.loads(msg[8:].decode())
                            block_num = int(message['block_num'])
                            timestamp = message['block_timestamp']
                            handle_transaction(message, block_num, timestamp, session)
                        elif msg_type == 1001:
                            message = json.loads(msg[8:].decode())
                            block_num = int(message['block_num'])
                            handle_fork(block_num, self.unconfirmed_block, self.confirmed_block, session)
                            self.confirmed_block = block_num - 1
                            self.unconfirmed_block = block_num - 1
                            do_ack = True
                        elif msg_type == 1009:
                            if self.unconfirmed_block > self.confirmed_block:
                                self.confirmed_block = self.unconfirmed_block
                                do_ack = True
                        elif msg_type == 1010:
                            message = json.loads(msg[8:].decode())
                            block_num = int(message['block_num'])
                            self.unconfirmed_block = block_num
                            if self.unconfirmed_block - self.confirmed_block >= 100:
                                self.confirmed_block = self.unconfirmed_block
                                do_ack = True
                        if do_ack:
                            self.emitter.emit('ackBlock', self.confirmed_block)
                            session.commit()
                            await ws.send('{}'.format(self.confirmed_block))
                    except SQLAlchemyError as err:
                        log_error('distribute SQLAlchemyError: {}'.format(err))
                        time.sleep(30)
                        raise err
            except SQLAlchemyError as err:
                log_error('distribute SQLAlchemyError: {}'.format(err))
                raise err
            finally:
                session.commit()
                session.remove()
        except Exception as err:
            logging.error('distribute: {}'.format(err))
            self.emitter.emit('error', {
                'remoteAddress': config.chronicle_settings['host'],
                'remoteFamily': 'IPv4',
                'remotePort': config.chronicle_settings['port']
            })


server = Server()
start_server = websockets.serve(server.ws_handler, "0.0.0.0", 8800, max_size=12000000)

loop = asyncio.get_event_loop()
loop.run_until_complete(start_server)
loop.run_forever()
