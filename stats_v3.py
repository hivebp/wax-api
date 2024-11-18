import json
import time

from sqlalchemy.exc import SQLAlchemyError

from api import cache, logging, db

import datetime


def create_session():
    return db.session


def _format_assets(assets):
    asset_list = []
    for asset in assets:
        asset_list.append({
            'assetId': asset['asset_id'],
            'name': asset['name'],
            'mint': asset['mint'],
            'image': asset['image'],
            'templateId': asset['template_id']
        })
    return asset_list


def _create_date_list(days):
    dates = range(days)
    items = []
    for date in dates:
        d = datetime.datetime.today() - datetime.timedelta(days=(days - (date + 1)))
        items.append(d.strftime("%Y-%m-%d"))
    return items


def _create_empty_chart(key, days, key2=None, key3=None):
    dates = range(days)
    items = []
    for date in dates:
        d = datetime.datetime.today() - datetime.timedelta(days=(days - (date + 1)))
        if key3:
            items.append({
                key: 0,
                key2: 0,
                key3: 0,
                'date': d.strftime("%Y-%m-%d")
            })
        elif key2:
            items.append({
                key: 0,
                key2: 0,
                'date': d.strftime("%Y-%m-%d")
            })
        else:
            items.append({
                key: 0,
                'date': d.strftime("%Y-%m-%d")
            })
    return items


def add_trend(res):
    dates = _create_empty_chart('waxVolume', 7)
    dates[0]['waxVolume'] = res['wax_volume_day_1'] if 'wax_volume_day_1' in res.keys() else 0
    dates[1]['waxVolume'] = res['wax_volume_day_2'] if 'wax_volume_day_2' in res.keys() else 0
    dates[2]['waxVolume'] = res['wax_volume_day_3'] if 'wax_volume_day_3' in res.keys() else 0
    dates[3]['waxVolume'] = res['wax_volume_day_4'] if 'wax_volume_day_4' in res.keys() else 0
    dates[4]['waxVolume'] = res['wax_volume_day_5'] if 'wax_volume_day_5' in res.keys() else 0
    dates[5]['waxVolume'] = res['wax_volume_day_6'] if 'wax_volume_day_6' in res.keys() else 0
    dates[6]['waxVolume'] = res['wax_volume_day_7'] if 'wax_volume_day_7' in res.keys() else 0
    return dates


@cache.memoize(timeout=300)
def user_stats(user):
    session = create_session()
    try:
        res = session.execute(
            'SELECT owner as user_name, wax_value, usd_value, num_assets, image, '
            'SUM(s.wax_volume_all_time + b.wax_volume_all_time) AS wax_volume_all_time, '
            'SUM(s.usd_volume_all_time + b.usd_volume_all_time) AS usd_volume_all_time, '
            'SUM(s.wax_volume_all_time) AS wax_sell_volume_all_time, '
            'SUM(s.usd_volume_all_time) AS usd_sell_volume_all_time, '
            'SUM(b.wax_volume_all_time) AS wax_buy_volume_all_time, '
            'SUM(b.usd_volume_all_time) AS usd_buy_volume_all_time, '
            'SUM(b.purchases_all_time) AS purchases_all_time, '
            'SUM(s.purchases_all_time) AS sales_all_time '
            'FROM users_mv '
            'LEFT JOIN seller_volumes_mv s ON owner = s.user_name '
            'LEFT JOIN buyer_volumes_mv b ON owner = b.user_name '
            'LEFT JOIN user_pictures_mv up ON owner = up.user_name '
            'WHERE owner = :owner GROUP BY 1, 2, 3, 4, 5 ',
            {'owner': user}
        ).first()

        if not res:
            return {
                'numUsers': 'Error',
                'waxValue': 'Error',
                'usdValue': 'Error',
                'numAssets': 'Error'
            }

        return {
            'name': res.user_name,
            'image': res.image,
            'waxValue': float(res.wax_value if res.wax_value else 0),
            'usdValue': float(res.usd_value if res.usd_value else 0),
            'numAssets': int(res.num_assets if res.num_assets else 0),
            'waxVolumeAllTime': float(res.wax_volume_all_time if res.wax_volume_all_time else 0),
            'usdVolumeAllTime': float(res.usd_volume_all_time if res.usd_volume_all_time else 0),
            'waxBuyVolumeAllTime': float(res.wax_buy_volume_all_time if res.wax_buy_volume_all_time else 0),
            'usdBuyVolumeAllTime': float(res.usd_buy_volume_all_time if res.usd_buy_volume_all_time else 0),
            'waxSellVolumeAllTime': float(res.wax_sell_volume_all_time if res.wax_sell_volume_all_time else 0),
            'usdSellVolumeAllTime': float(res.usd_sell_volume_all_time if res.usd_sell_volume_all_time else 0),
            'purchasesAllTime': float(res.purchases_all_time if res.purchases_all_time else 0),
            'salesAllTime': float(res.sales_all_time if res.sales_all_time else 0),
        }
    except SQLAlchemyError as e:
        logging.error(e)
        session.rollback()
        raise e
    finally:
        session.remove()


@cache.memoize(timeout=300)
def collection_stats(collection):
    session = create_session()
    try:
        res = session.execute(
            'SELECT num_users, wax_value, usd_value, num_assets  '
            'FROM collection_user_count_mv '
            'WHERE collection = :collection',
            {'collection': collection}
        ).first()

        if not res:
            return {
                'numUsers': 0,
                'usdMarketCap': 0,
                'waxMarketCap': 0,
                'numAssets': 0,
            }

        return {
            'numUsers': res.num_users,
            'usdMarketCap': float(res.usd_value if res.usd_value else 0),
            'waxMarketCap': float(res.wax_value if res.wax_value else 0),
            'numAssets': int(res.num_assets if res.num_assets else 0),
        }
    except SQLAlchemyError as e:
        logging.error(e)
        session.rollback()
        raise e
    finally:
        session.remove()


@cache.memoize(timeout=300)
def get_user_info(user):
    session = create_session()
    try:
        res = session.execute(
            'SELECT owner as user_name, wax_value, usd_value, num_assets, image '
            'FROM users_mv '
            'LEFT JOIN user_pictures_mv up ON owner = user_name '
            'WHERE owner = :owner ',
            {'owner': user}
        ).first()

        if not res:
            return {
                'name': 'Error',
                'image': 'Error',
                'waxValue': 'Error',
                'usdValue': 'Error',
                'numAssets': 'Error'
            }

        return {
            'name': res.user_name,
            'image': res.image,
            'waxValue': float(res.wax_value if res.wax_value else 0),
            'usdValue': float(res.usd_value if res.usd_value else 0),
            'numAssets': int(res.num_assets if res.num_assets else 0)
        }
    except SQLAlchemyError as e:
        logging.error(e)
        session.rollback()
        raise e
    finally:
        session.remove()


@cache.memoize(timeout=300)
def get_monthly_volume(collection, days, type):
    session = create_session()

    try:
        res = session.execute(
            'SELECT to_date, SUM(wax_volume) AS wax_volume, SUM(usd_volume) AS usd_volume '
            'FROM monthly_collection_volume_mv WHERE TRUE {type_clause} {date_clause} {collection_clause} '
            'GROUP BY 1 ORDER BY 1 ASC'.format(
                collection_clause=' AND collection = :collection ' if collection and collection != '*' else '',
                type_clause=' AND type = :type ' if type and type != 'all' else '',
                date_clause=' AND to_date >= NOW() AT TIME ZONE \'utc\' - INTERVAL :interval' if days and int(
                    days) > 0 else '',
            ), {'type': type, 'collection': collection, 'interval': '{} days'.format(days)},
        )

        volumes = []

        for item in res:
            volumes.append({
                'date': item['to_date'].strftime("%Y-%m-%d"),
                'waxVolume': item['wax_volume'],
                'usdVolume': item['usd_volume']
            })

        return volumes
    except SQLAlchemyError as e:
        logging.error(e)
        session.rollback()
        raise e
    finally:
        session.remove()


@cache.memoize(timeout=300)
def get_users_table(days, collection, actor, type, term):
    session = create_session()
    try:
        table = 'volume_'

        if collection:
            table += 'collection_'

        if actor == 'buyer':
            table += 'buyer_'
        else:
            table += 'seller_'

        if days and days != '0':
            table += days + '_days_mv'
        else:
            table += 'all_time_mv'

        search_clause = ''

        if term:
            search_clause = ' HAVING user_name ilike :term '

        users = []

        if actor == 'all':
            total_result = session.execute(
                'SELECT MAX(actors) AS total_results '
                'FROM ('
                'SELECT COUNT(DISTINCT seller) AS actors '
                'FROM {seller_table} '
                'WHERE TRUE {collection_clause} {type_clause} '
                'UNION ALL '
                'SELECT COUNT(DISTINCT buyer) AS actors '
                'FROM {buyer_table} '
                'WHERE TRUE {collection_clause} {type_clause}) f'
                ' '.format(
                    seller_table=table,
                    buyer_table=table.replace('_seller_', '_buyer_'),
                    collection_clause=' AND tb.collection = :collection ' if collection and collection != '*' else '',
                    type_clause=' AND type = :type ' if type and type != 'all' else ''
                ), {
                    'actor': actor, 'type': type, 'collection': collection
                }
            ).first()

            sql = (
                'SELECT * FROM (SELECT '
                'SUM(wax_volume) AS wax_volume, '
                'SUM(usd_volume) AS usd_volume, '
                'SUM(CASE WHEN actor = \'buyer\' THEN wax_volume ELSE 0 END) AS wax_buy_volume, '
                'SUM(CASE WHEN actor = \'buyer\' THEN usd_volume ELSE 0 END) AS usd_buy_volume, '
                'SUM(CASE WHEN actor = \'seller\' AND type = \'sales\' THEN wax_volume ELSE 0 END) AS wax_sell_volume, '
                'SUM(CASE WHEN actor = \'seller\' AND type = \'sales\' THEN usd_volume ELSE 0 END) AS usd_sell_volume, '
                'SUM(CASE WHEN actor = \'buyer\' THEN sales ELSE 0 END) AS purchases, '
                'SUM(CASE WHEN actor = \'seller\' AND type = \'sales\' THEN sales ELSE 0 END) AS sales, '
                'user_name, image, ROW_NUMBER() OVER ('
                'ORDER BY SUM(CASE WHEN actor = \'seller\' AND type != \'sales\' THEN 0 ELSE usd_volume END) DESC'
                ') AS rank '
                'FROM ('
                '   SELECT seller AS user_name, '
                '   \'seller\' AS actor, type, '
                '   SUM(wax_volume) AS wax_volume, '
                '   SUM(usd_volume) AS usd_volume, '
                '   SUM(sales) AS sales'
                '   FROM {seller_table} '
                '   WHERE TRUE {collection_clause} {type_clause} AND type = \'sales\''
                '   GROUP BY 1, 2, 3 '
                'UNION ALL '
                '   SELECT buyer AS user_name, '
                '   \'buyer\' AS actor, type, '
                '   SUM(wax_volume) AS wax_volume, '
                '   SUM(usd_volume) AS usd_volume, '
                '   SUM(sales) AS sales'
                '   FROM {buyer_table} '
                '   WHERE TRUE {collection_clause} {type_clause} '
                '   GROUP BY 1, 2, 3 '
                ') tb LEFT JOIN user_pictures_mv up USING (user_name) '
                'GROUP BY user_name, image) f '
                'GROUP BY 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11 {search_clause} '
                'ORDER BY 2 DESC '.format(
                    seller_table=table,
                    buyer_table=table.replace('_seller_', '_buyer_'),
                    collection_clause=' AND tb.collection = :collection ' if collection and collection != '*' else '',
                    type_clause=' AND type = :type ' if type and type != 'all' else '',
                    search_clause=search_clause,
                )
            )

            user_results = session.execute(
                sql, {
                    'interval': '{} days'.format(days), 'collection': collection, 'term': term, 'actor': actor,
                    'type': type
                }
            )

            for user in user_results:
                users.append(
                    {
                        'userName': user.user_name,
                        'image': user.image,
                        'total': total_result['total_results'],
                        'stats': {
                            'days': days,
                            'waxVolume': float(user.wax_volume if user.wax_volume else 0),
                            'usdVolume': float(user.usd_volume if user.usd_volume else 0),
                            'waxBuyVolume': float(user.wax_buy_volume if user.wax_buy_volume else 0),
                            'usdBuyVolume': float(user.usd_buy_volume if user.usd_buy_volume else 0),
                            'waxSellVolume': float(user.wax_sell_volume if user.wax_sell_volume else 0),
                            'usdSellVolume': float(user.usd_sell_volume if user.usd_sell_volume else 0),
                            'purchases': float(user.purchases if user.purchases else 0),
                            'sales': float(user.sales if user.sales else 0),
                            'rank': int(user.rank)
                        }
                    }
                )
        else:
            total_result = session.execute(
                'SELECT COUNT(1) AS total_results '
                'FROM {table} tb '
                'WHERE TRUE {collection_clause} {type_clause} '.format(
                    table=table,
                    collection_clause=' AND tb.collection = :collection ' if collection and collection != '*' else '',
                    type_clause=' AND type = :type ' if type and type != 'all' else ''
                ), {
                    'actor': actor, 'type': type, 'collection': collection
                }
            ).first()

            sql = (
                'SELECT {actor} AS user_name, image, '
                'SUM(wax_volume) AS wax_volume, '
                'SUM(usd_volume) AS usd_volume, '
                'SUM(sales) AS sales, '
                'ROW_NUMBER() OVER ('
                '   ORDER BY SUM(usd_volume) DESC'
                ') AS rank '
                'FROM {table} tb LEFT JOIN user_pictures_mv up ON ({actor} = user_name) '
                'WHERE TRUE {collection_clause} {type_clause} {sales_clause} GROUP BY 1, 2 {search_clause} '
                'ORDER BY 4 DESC '.format(
                  table=table, actor=actor,
                  collection_clause=' AND tb.collection = :collection ' if collection and collection != '*' else '',
                  type_clause=' AND type = :type ' if type and type != 'all' else '',
                  sales_clause=' AND type = \'sales\'' if actor == 'seller' else '',
                  search_clause=search_clause,
                )
            )

            user_results = session.execute(
                sql, {
                    'interval': '{} days'.format(days), 'collection': collection, 'term': term, 'actor': actor,
                    'type': type
                }
            )

            for user in user_results:
                users.append(
                    {
                        'userName': user.user_name,
                        'image': user.image,
                        'total': total_result['total_results'],
                        'stats': {
                            'days': days,
                            'waxVolume': float(user.wax_volume if user.wax_volume else 0),
                            'usdVolume': float(user.usd_volume if user.usd_volume else 0),
                            'sales': float(user.sales if user.sales else 0),
                            'rank': int(user.rank)
                        }
                    }
                )

        return users
    except SQLAlchemyError as e:
        logging.error(e)
        session.rollback()
    finally:
        session.remove()


@cache.memoize(timeout=300)
def get_sales_volume_graph(days=60, template_id=None, collection=None, type='all'):
    session = create_session()
    try:
        sales_volume = session.execute(
            'SELECT date, SUM(price) AS volume, SUM(usd_price) AS usdVolume, SUM(sales) AS sales '
            'FROM {template}sales_by_date t '
            'WHERE TRUE {date_clause}{collection_clause}{type_clause}{template_clause}'
            'GROUP BY 1 ORDER BY 1 DESC'.format(
                template='template_' if template_id else '',
                date_clause=' AND date >= NOW() AT TIME ZONE \'utc\' - INTERVAL :interval ' if days and int(days) > 0 else '',
                type_clause=' AND type = :type ' if type and type != 'all' else '',
                template_clause=' AND template_id = :template_id ' if template_id else '',
                collection_clause=' AND collection = :collection ' if collection else ''
            ), {
                'interval': '{} days'.format(days),
                'collection': collection,
                'template_id': template_id,
                'type': type
            }
        )

        dates = _create_empty_chart('waxVolume', int(days), 'usdVolume', 'sales')
        for item in sales_volume:
            date = item['date'].strftime("%Y-%m-%d")
            for date_item in dates:
                if date_item['date'] == date:
                    date_item['waxVolume'] = float(item['waxVolume'])
                    date_item['usdVolume'] = float(item['usd_volume'])
                    date_item['sales'] = int(item['sales'])

        return dates
    except SQLAlchemyError as e:
        logging.error(e)
        session.rollback()
        raise e
    except Exception as e:
        logging.error(e)
        raise e
    finally:
        session.remove()


@cache.memoize(timeout=300)
def get_sales_volume_graph(days=60, template_id=None, collection=None, type='all'):
    session = create_session()
    try:
        sql = (
            'SELECT to_date, SUM(wax_volume) AS wax_volume, SUM(usd_volume) AS usd_volume, SUM(sales) AS sales '
            'FROM {template}collection_sales_by_date_mv t '
            'WHERE TRUE {date_clause}{collection_clause}{type_clause}{template_clause}'
            'GROUP BY 1 ORDER BY 1 DESC'.format(
                template='template_' if template_id else '',
                date_clause=' AND to_date >= NOW() AT TIME ZONE \'utc\' - INTERVAL :interval ' if days and int(
                    days) > 0 else '',
                type_clause=' AND t.type = :type ' if type and type != 'all' else '',
                template_clause=' AND template_id = :template_id ' if template_id else '',
                collection_clause=' AND collection = :collection ' if collection and collection != '*' else ''
            )
        )

        sales_volume = session.execute(
            sql, {
                'interval': '{} days'.format(days),
                'collection': collection,
                'template_id': template_id,
                'type': type
            }
        )

        dates = _create_empty_chart('waxVolume', int(days), 'sales', 'usdVolume')
        for item in sales_volume:
            date = item['to_date'].strftime("%Y-%m-%d")
            for date_item in dates:
                if date_item['date'] == date:
                    date_item['waxVolume'] = float(item['wax_volume'])
                    date_item['usdVolume'] = float(item['usd_volume'])
                    date_item['sales'] = int(item['sales'])

        return dates
    except SQLAlchemyError as e:
        logging.error(e)
        session.rollback()
        raise e
    except Exception as e:
        logging.error(e)
        raise e
    finally:
        session.remove()


@cache.memoize(timeout=300)
def get_drops_table(days, limit, offset):
    session = create_session()
    try:
        table = 'volume_drop_all_time_mv'

        if days and days != '0':
            table = 'volume_drop_{days}_days_mv'.format(days=days)

        total_result = session.execute(
            'SELECT COUNT(1) AS total_results '
            'FROM {table} tb '.format(
                table=table
            )
        ).first()

        drops_result = session.execute(
            'SELECT dv.drop_id, dv.market, d.display_data, d.collection, cn.name AS display_name, '
            'ci.image AS collection_image, wax_volume, usd_volume, buyers, sales AS claims, '
            'json_agg(json_build_object(\'template_id\', t.template_id, \'data\', td.data)) AS template_data, '
            'COUNT(1) AS total_amount, ROW_NUMBER() OVER (ORDER BY wax_volume DESC) AS rank '
            'FROM {table} dv '
            'LEFT JOIN drops d ON d.drop_id = dv.drop_id AND d.contract = dv.market '
            'LEFT JOIN templates t ON t.template_id = ANY(templates_to_mint) '
            'LEFT JOIN data td ON t.immutable_data_id = td.data_id '
            'LEFT JOIN collections c ON c.collection = d.collection '
            'LEFT JOIN images ci ON c.image_id = ci.image_id '
            'LEFT JOIN names cn ON c.name_id = cn.name_id '
            'GROUP BY 1,2,3,4,5,6,7,8,9,10 ORDER BY wax_volume DESC '
            'LIMIT :limit OFFSET :offset'.format(
                table=table
            ), {'limit': limit, 'offset': offset}
        )

        drops = []

        for drop in drops_result:
            templates_data = drop['template_data']
            templates = []
            for template_data in templates_data:
                template = {}
                template['templateId'] = template_data['template_id']
                template['data'] = json.loads(template_data['data'])
                templates.append(template)
            try:
                drop_data = json.loads(drop['display_data'])
            except Exception as err:
                drop_data = {}
                print(err)
            if isinstance(drop_data, str):
                display_data = drop_data
                drop_data = {'displayData': display_data}
            drop_data['dropId'] = drop['drop_id']
            drop_data['market'] = drop['market']
            drops.append(
                {
                    'templates': templates,
                    'drop': drop_data,
                    'total': total_result['total_results'],
                    'collection': {
                        'name': drop.collection,
                        'displayName': drop.display_name,
                        'image': drop.collection_image,
                    },
                    'stats': {
                        'days': days,
                        'waxVolume': float(drop.wax_volume if drop.wax_volume else 0),
                        'usdVolume': float(drop.usd_volume if drop.usd_volume else 0),
                        'buyers': int(drop.buyers),
                        'claims': int(drop.claims),
                        'rank': int(drop.rank)
                    }
                }
            )

        return drops
    except SQLAlchemyError as e:
        logging.error(e)
        session.rollback()
    finally:
        session.remove()


def _parse_data_object(data):
    result = {}

    for item in data:
        result[item['key']] = item['value'][1]

    return result


@cache.memoize(timeout=300)
def get_template_table(days, collection, limit, offset):
    session = create_session()
    try:
        table = 'volume_template_all_time_mv'

        if days and days != '0' and int(days) == 1:
            table = 'volume_template_{days}_days_mv'.format(days=days)

        total_result = session.execute(
            'SELECT COUNT(1) AS total_results '
            'FROM {table} tb '
            'WHERE TRUE {collection_clause} AND tb.collection NOT IN ('
            'SELECT collection FROM collections ba WHERE blacklisted) '.format(
                table=table,
                collection_clause=' AND tb.collection = :collection ' if collection and collection != '*' else ''
            ), {
                'collection': collection
            }
        ).first()

        template_results = session.execute(
            'SELECT wax_volume, usd_volume, '
            '(SELECT wax_volume FROM volume_template_1_days_mv WHERE template_id = t.template_id) AS volume_1_day, '
            '(SELECT wax_volume FROM volume_template_2_days_mv WHERE template_id = t.template_id) AS volume_2_days, '
            'buyers, sellers, sales, '
            'tb.collection, cn.name, ci.image, t.template_id, t.schema, td.data AS idata, '
            '(SELECT floor_price FROM template_floor_prices_mv WHERE template_id = t.template_id) as floor_price, '
            'ROW_NUMBER() OVER (ORDER BY 1 DESC) AS rank '
            'FROM {table} tb '
            'INNER JOIN collections c USING (collection) '
            'INNER JOIN templates t USING(template_id) '
            'LEFT JOIN images ci ON c.image_id = ci.image_id '
            'LEFT JOIN names cn ON c.name_id = cn.name_id '
            'LEFT JOIN data td ON td.data_id = t.immutable_data_id '
            'WHERE TRUE {collection_clause} AND NOT blacklisted '
            'ORDER BY 1 DESC '
            'LIMIT :limit OFFSET :offset '.format(
                table=table,
                collection_clause=' AND tb.collection = :collection ' if collection and collection != '*' else '',
            ), {
                'collection': collection,
                'limit': limit,
                'offset': offset
            }
        )

        collections = []

        for template in template_results:
            template_data = _parse_data_object(json.loads(template['idata']))
            template_data['template_id'] = template['template_id']
            template_data['schema'] = template['schema']
            collections.append(
                {
                    'template': template_data,
                    'total': total_result['total_results'],
                    'collection': {
                        'name': template.collection,
                        'displayName': template.name,
                        'image': template.image,
                    },
                    'stats': {
                        'days': days,
                        'waxVolume': float(template.wax_volume if template.wax_volume else 0),
                        'usdVolume': float(template.usd_volume if template.usd_volume else 0),
                        'waxFloor': float(template.floor_price if template.floor_price else 0),
                        'change': float(
                            ((template.volume_1_day - (template.volume_2_days - template.volume_1_day)) / (
                                    template.volume_2_days - template.volume_1_day))
                            if template.volume_1_day and template.volume_2_days - template.volume_1_day else 0),
                        'buyers': int(template.buyers),
                        'sellers': int(template.sellers),
                        'sales': int(template.sales),
                        'rank': int(template.rank)
                    }
                }
            )

        return collections
    except SQLAlchemyError as e:
        logging.error(e)
        session.rollback()
    finally:
        session.remove()


@cache.memoize(timeout=300)
def get_top_sales_table(days, collection, template_id, limit, offset):
    session = create_session()
    try:
        res = session.execute(
            'SELECT wax_price, usd_price, buyer, seller, ct.transaction_id AS buy_transaction_id, t.collection, '
            'cn.name, ci.image as collection_image, CASE WHEN taker IS NULL THEN market ELSE taker END AS market, '
            'ROW_NUMBER() OVER (ORDER BY usd_price DESC) AS rank, '
            'json_agg(json_build_object('
            '    \'asset_id\', asset_id, \'name\', an.name, \'mint\', mint, \'image\', ai.image, '
            '    \'template_id\', template_id'
            ')) as assets '
            'FROM sales t '
            'LEFT JOIN collections c USING (collection) '
            'LEFT JOIN assets a ON a.asset_id = t.asset_ids[1] '
            'LEFT JOIN names an ON a.name_id = an.name_id '
            'LEFT JOIN names cn ON c.name_id = cn.name_id '
            'LEFT JOIN images ai ON a.image_id = ai.name_id '
            'LEFT JOIN images ci ON c.image_id = ci.name_id '
            'WHERE TRUE {time_clause} {collection_clause} {template_clause} '
            'AND NOT c.blacklisted '
            'GROUP BY 1, 2, 3, 4, 5, 6, 7, 8, 9 '
            'ORDER BY usd_price DESC LIMIT :limit OFFSET :offset '.format(
                time_clause=' AND t.timestamp > (NOW() - INTERVAL :interval) at time zone \'utc\''
                if days and int(days) > 0 else '',
                template_clause=' AND template_id = :template_id ' if template_id else '',
                collection_clause=' AND t.collection = :collection ' if collection else ''
            ), {
                'interval': '{} days'.format(days), 'collection': collection, 'limit': limit, 'offset': offset,
                'template_id': template_id
            }
        )

        sales = []

        for row in res:
            sales.append(
                {
                    'collection': {
                        'name': row.author,
                        'displayName': row.name,
                        'image': row.collection_image,
                    },
                    'assets': _format_assets(row.assets),
                    'days': days,
                    'price': row.price,
                    'usdPrice': row.usd_price,
                    'buyer': row.buyer,
                    'seller': row.seller,
                    'tx': row.buy_transaction_id,
                    'rank': row.rank
                }
            )

        return sales
    except SQLAlchemyError as e:
        logging.error(e)
        session.rollback()
        raise e
    finally:
        session.remove()


@cache.memoize(timeout=60)
def get_attribute_asset_analytics_schema(asset_id, collection, schema):
    session = create_session()
    try:
        res = session.execute(
            'SELECT asu.total, asu.total_schema, af.*, att.*, t.idata, c.name AS display_name, a.rank, a.rarity_score, '
            'c.image AS collection_image, t.template_id, t.category '
            'FROM attribute_assets a '
            'LEFT JOIN templates t USING (template_id) '
            'LEFT JOIN collections c ON t.author = c.collection_name '
            'INNER JOIN attribute_summaries asu ON attribute_id = ANY(a.attribute_ids) '
            'LEFT JOIN attribute_floors_mv af USING(attribute_id) '
            'LEFT JOIN attributes att USING(attribute_id) '
            'WHERE a.author = :collection AND a.schema = :schema {asset_clause}'.format(
                asset_clause=' AND a.asset_id = :asset_id' if asset_id else ' AND a.asset_id = (SELECT asset_id FROM attribute_assets WHERE author = :collection AND schema = :schema AND rank = 1 LIMIT 1) '
            ), {'collection': collection, 'schema': schema, 'asset_id': asset_id}
        )

        template = None
        collection = None
        attributes = []
        if res and res.rowcount > 0:
            for attribute in res:
                if not template:
                    template = json.loads(attribute['idata']) if attribute['idata'] else {}
                    template['template_id'] = attribute['template_id']
                    template['schema'] = attribute['category']
                    template['rarityScore'] = attribute['rarity_score']
                    template['rank'] = attribute['rank']
                    collection = {
                        'name': attribute.author,
                        'displayName': attribute.display_name,
                        'image': attribute.collection_image,
                    }
                attributes.append({
                    'name': attribute['attribute_name'],
                    'value': attribute['string_value'] if attribute['string_value']
                    else attribute['int_value'] if attribute['int_value'] or attribute['int_value'] == 0
                    else float(attribute['float_value']) if attribute['float_value'] or attribute['float_value'] == 0
                    else attribute['bool_value'],
                    'total': attribute['total'],
                    'percentage': attribute['total'] / attribute['total_schema'] if attribute['total_schema'] and attribute['total'] else 0,
                    'waxFloor': attribute['floor'],
                    'usdFloor': attribute['usd_floor'],
                })

            return {
                'template': template,
                'attributes': attributes,
                'collection': collection
            }
        else:
            return None
    except SQLAlchemyError as e:
        logging.error(e)
        session.rollback()
        raise e
    finally:
        session.remove()


@cache.memoize(timeout=60)
def get_pfp_asset_analytics(asset_id, template_id):
    session = create_session()
    if not asset_id and not template_id:
        return None
    try:
        res = session.execute(
            'SELECT ast.total, ast.total_schema, af.*, att.*, td.data, cn.name AS display_name, a.rank, a.rarity_score,'
            'ci.image AS collection_image, t.template_id, t.schema '
            'FROM pfp_assets a '
            'LEFT JOIN templates t USING (template_id) '
            'LEFT JOIN data td ON t.immutable_data_id = td.data_id '
            'LEFT JOIN collections c ON a.collection = c.collection '
            'LEFT JOIN names cn ON c.name_id = cn.name_id '
            'LEFT JOIN images ci ON c.image_id = ci.image_id '
            'INNER JOIN attribute_stats ast ON attribute_id = ANY(a.attribute_ids) '
            'LEFT JOIN attribute_floors_mv af USING(attribute_id) '
            'LEFT JOIN attributes att USING(attribute_id) '
            'WHERE TRUE {template_clause} {asset_clause}'.format(
                template_clause=' AND template_id = :template_id ' if template_id else '',
                asset_clause=' AND a.asset_id = :asset_id' if asset_id else (
                    ' AND a.asset_id = (SELECT asset_id FROM pfp_assets '
                    'WHERE template_id = :template_id AND rank = 1 LIMIT 1) '
                )
            ), {'template_id': template_id, 'asset_id': asset_id}
        )

        template = None
        collection = None
        attributes = []
        if res and res.rowcount > 0:
            for attribute in res:
                if not template:
                    template = _parse_data_object(json.loads(attribute['data'])) if attribute['data'] else {}
                    template['template_id'] = attribute['template_id']
                    template['schema'] = attribute['schema']
                    template['rarityScore'] = attribute['rarity_score']
                    template['rank'] = attribute['rank']
                    collection = {
                        'name': attribute.collection,
                        'displayName': attribute.display_name,
                        'image': attribute.collection_image,
                    }
                attributes.append({
                    'name': attribute['attribute_name'],
                    'value': attribute['string_value'] if attribute['string_value']
                    else attribute['int_value'] if attribute['int_value'] or attribute['int_value'] == 0
                    else float(attribute['float_value']) if attribute['float_value'] or attribute['float_value'] == 0
                    else attribute['bool_value'],
                    'total': attribute['total'],
                    'percentage': attribute['total'] / attribute['total_schema'] if attribute['total_schema'] else 0,
                    'waxFloor': attribute['floor_wax'],
                    'usdFloor': attribute['floor_usd'],
                })

            return {
                'template': template,
                'attributes': attributes,
                'collection': collection
            }
        else:
            return None
    except SQLAlchemyError as e:
        logging.error(e)
        session.rollback()
        raise e
    finally:
        session.remove()


@cache.memoize(timeout=300)
def get_similar_collections(collection):
    session = create_session()
    try:
        sql = (
            'SELECT d.collection, ci.image, cn.name, rank_val '
            'FROM (SELECT collection, SUM(1 - (rank/10)) AS rank_val '                                                                                                                                                   
            'FROM ('
            '       SELECT owner, collection, num_assets, wax_value, rank() OVER ('
            '           PARTITION BY owner ORDER BY wax_value DESC NULLS LAST'
            '       )'
            '       FROM collection_users_mv '
            '       WHERE owner IN ('
            '              SELECT owner FROM collection_users_mv '
            '              WHERE collection = :collection '
            '              AND wax_value > (SELECT AVG(wax_value) '
            '               FROM collection_users_mv WHERE collection = :collection)'
            '       ORDER BY wax_value DESC NULLS LAST LIMIT 1000) '
            '       AND collection != :collection AND wax_value > 50) b '
            'WHERE rank < 10 GROUP BY 1 ORDER BY 2 DESC NULLS LAST) d '
            'LEFT JOIN collections c USING (collection) '
            'LEFT JOIN names cn ON c.name_id = cn.name_id '
            'LEFT JOIN images ci ON c.image_id = ci.image_id '
            'ORDER BY 4 DESC LIMIT 9'
        )

        res = session.execute(
            sql, {
                'collection': collection
            }
        )

        collections = []

        for collection in res:
            collections.append({
                'collection': collection['collection'],
                'name': collection['name'],
                'image': collection['image']
            })

        return collections
    except SQLAlchemyError as e:
        logging.error(e)
        session.rollback()
        raise e
    finally:
        session.remove()


@cache.memoize(timeout=60)
def get_attribute_analytics(template_id):
    session = create_session()
    try:
        res = session.execute(
            'SELECT asu.total, asu.total_schema, af.*, a.*, t.*, c.name AS display_name, c.image AS collection_image '
            'FROM templates t '
            'LEFT JOIN collections c ON t.author = c.collection_name '
            'INNER JOIN attribute_summaries asu ON attribute_id = ANY(attribute_ids) '
            'LEFT JOIN attribute_floors_mv af USING(attribute_id) '
            'LEFT JOIN attributes a USING(attribute_id) '
            'WHERE template_id =  :template_id',
            {'template_id': template_id}
        )

        template = None
        collection = None
        attributes = []
        if res and res.rowcount > 0:
            for attribute in res:
                if not template:
                    template = json.loads(attribute['idata'])
                    template['template_id'] = attribute['template_id']
                    template['schema'] = attribute['category']
                    collection = {
                        'name': attribute.author,
                        'displayName': attribute.display_name,
                        'image': attribute.collection_image,
                    }
                attributes.append({
                    'name': attribute['attribute_name'],
                    'value': attribute['string_value'] if attribute['string_value']
                    else attribute['int_value'] if attribute['int_value'] or attribute['int_value'] == 0
                    else float(attribute['float_value']) if attribute['float_value'] or attribute['float_value'] == 0
                    else attribute['bool_value'],
                    'total': attribute['total'],
                    'percentage': attribute['total'] / attribute['total_schema'] if attribute['total_schema'] > 0 else 0,
                    'waxFloor': attribute['floor'],
                    'usdFloor': attribute['usd_floor']
                })
        else:
            return None

        return {
            'template': template,
            'attributes': attributes,
            'collection': collection
        }
    except SQLAlchemyError as e:
        logging.error(e)
        session.rollback()
        raise e
    finally:
        session.remove()


@cache.memoize(timeout=60)
def get_floor(template_id):
    session = create_session()
    try:
        total_res = session.execute(
            'SELECT COUNT(1) AS total, td.data, t.attribute_ids '
            'FROM templates t '
            'LEFT JOIN data td ON t.immutable_data_id = td.data_id '
            'WHERE t.template_id = :template_id GROUP BY 2, 3',
            {'template_id': template_id}
        ).first()

        template_data = _parse_data_object(json.loads(total_res['data']))

        template = session.execute(
            'SELECT td.data, template_id, t.schema, tb.collection, cn.name, ci.image, floor_price '
            'FROM template_floor_prices_mv tb '
            'INNER JOIN collections c USING (collection) '
            'LEFT JOIN names cn ON c.name_id = cn.name_id '
            'LEFT JOIN images ci ON c.image_id = ci.image_id '
            'INNER JOIN templates t USING(template_id) '
            'LEFT JOIN data td ON t.immutable_data_id = td.data_id '
            'WHERE template_id = :template_id',
            {'template_id': template_id}
        ).first()

        if template is None:
            return []

        template_data['template_id'] = template['template_id']
        template_data['schema'] = template['schema']

        return {
            'template': template_data,
            'waxFloor': template.floor_price,
            'collection': {
                'name': template.collection,
                'displayName': template.name,
                'image': template.image,
            }
        }
    except SQLAlchemyError as e:
        logging.error(e)
        session.rollback()
        raise e
    finally:
        session.remove()


@cache.memoize(timeout=300)
def get_volume(collection=None, days=1, type=None):
    session = create_session()

    table = 'volume_collection_all_time_mv'
    volume_column = 'wax_volume'

    if days and days != '0':
        table = 'volume_collection_{}_days_mv'.format(days)

    try:
        result = session.execute(
            'SELECT SUM(wax_volume) AS wax_volume, SUM(usd_volume) AS usd_volume '
            'FROM ('
            '   SELECT wax_volume, usd_volume '
            '   FROM {table} '
            '   WHERE TRUE {type_clause}{collection_clause} '
            ') t '.format(
                table=table,
                volume_column=volume_column,
                collection_clause=' AND collection = :collection ' if collection and collection != '*' else '',
                type_clause=' AND type = :type ' if type and type != 'all' else '',
            ), {
                'collection': collection,
                'type': type,
            }
        ).first()

        return {
            'waxVolume': float(result.wax_volume if result.wax_volume else 0),
            'usdVolume': float(result.usd_volume if result.usd_volume else 0),
        }
    except SQLAlchemyError as e:
        logging.error(e)
        session.rollback()
        raise e
    finally:
        session.remove()


@cache.memoize(timeout=300)
def get_buy_volume(user, days=1, type=None):
    session = create_session()

    table = 'volume_buyer_all_time_mv'
    volume_column = 'wax_volume'

    if days and days != '0':
        table = 'volume_buyer_{}_days_mv'.format(days)

    try:
        result = session.execute(
            'SELECT SUM(wax_volume) AS wax_volume, SUM(usd_volume) AS usd_volume, SUM(sales) AS sales '
            'FROM {table} '
            'WHERE TRUE {type_clause}{collection_clause} '.format(
                table=table,
                volume_column=volume_column,
                collection_clause=' AND buyer = :user ' if user and user != '*' else '',
                type_clause=' AND type = :type ' if type and type != 'all' else '',
            ), {
                'user': user,
                'type': type,
            }
        ).first()

        return {
            'waxVolume': float(result.wax_volume if result.wax_volume else 0),
            'usdVolume': float(result.usd_volume if result.usd_volume else 0),
            'buys': int(result.sales if result.sales else 0)
        }
    except SQLAlchemyError as e:
        logging.error(e)
        session.rollback()
        raise e
    finally:
        session.remove()


@cache.memoize(timeout=300)
def get_sell_volume(user, days=1, type=None):
    session = create_session()

    table = 'volume_seller_all_time_mv'
    volume_column = 'wax_volume'

    if days and days != '0':
        table = 'volume_seller_{}_days_mv'.format(days)

    try:
        result = session.execute(
            'SELECT SUM(wax_volume) AS wax_volume, SUM(usd_volume) AS usd_volume, SUM(sales) AS sales '
            'FROM {table} '
            'WHERE TRUE {type_clause}{collection_clause} '.format(
                table=table,
                volume_column=volume_column,
                collection_clause=' AND seller = :user ' if user and user != '*' else '',
                type_clause=' AND type = :type ' if type and type != 'all' else '',
            ), {
                'user': user,
                'type': type,
            }
        ).first()

        return {
            'waxVolume': float(result.wax_volume if result.wax_volume else 0),
            'usdVolume': float(result.usd_volume if result.usd_volume else 0),
            'sales': int(result.sales if result.sales else 0)
        }
    except SQLAlchemyError as e:
        logging.error(e)
        session.rollback()
        raise e
    finally:
        session.remove()


@cache.memoize(timeout=300)
def get_change(collection=None, type=None):
    session = create_session()

    try:
        result = session.execute(
            'SELECT SUM(wax_volume_1_day) AS wax_volume_1_day, '
            'SUM(wax_volume_2_days) - SUM(wax_volume_1_day) AS prev_wax_volume '
            'FROM ('
            '   SELECT SUM(wax_volume) AS wax_volume_1_day, 0 AS wax_volume_2_days '
            '   FROM volume_collection_1_days_mv m1 '
            '   WHERE TRUE {type_clause}{collection_clause} '
            '   UNION ALL '
            '   SELECT 0 AS wax_volume_1_day, SUM(wax_volume) AS wax_volume_2_days '
            '   FROM volume_collection_2_days_mv m2 '
            '   WHERE TRUE {type_clause}{collection_clause} '
            ') a '.format(
                collection_clause=' AND collection = :collection ' if collection and collection != '*' else '',
                type_clause=' AND type = :type ' if type and type != 'all' else ''
            ), {
                'collection': collection,
                'type': type,
            }
        ).first()

        return {
            'volumeChange': float(
                ((result.wax_volume_1_day - result.prev_wax_volume) / result.prev_wax_volume)
                if result.wax_volume_1_day and result.prev_wax_volume else 0),
        }
    except SQLAlchemyError as e:
        logging.error(e)
        session.rollback()
        raise e
    finally:
        session.remove()


@cache.memoize(timeout=300)
def get_market_cap(collection):
    session = create_session()

    try:
        mcap = session.execute(
            'SELECT SUM(wax_market_cap) AS wax_market_cap, SUM(usd_market_cap) AS usd_market_cap '
            'FROM collection_market_cap_mv WHERE TRUE {collection_clause}'.format(
                collection_clause=' AND collection = :collection ' if collection and collection != '*' else ''
            ),
            {'collection': collection}
        ).first()

        if mcap:
            return {
                'waxMarketCap': mcap['wax_market_cap'],
                'usdMarketCap': mcap['usd_market_cap'],
                'marketCap': mcap['usd_market_cap']
            }

        return {
            'waxMarketCap': None,
            'usdMarketCap': None,
            'marketCap': None
        }
    except SQLAlchemyError as e:
        logging.error(e)
        session.rollback()
        raise e
    finally:
        session.remove()


@cache.memoize(timeout=300)
def get_top_template_sales(days, template_id, limit, offset):
    session = create_session()
    try:
        template_clause = ''
        with_clause = ''
        join_clause = ''
        attribute_name = ''
        is1of1 = False
        attribute_value = ''
        attribute_id = None

        total_sql = (
            'SELECT num_minted AS total, attribute_ids '
            'FROM templates '
            'LEFT JOIN templates_minted_mv USING(template_id)'
            'WHERE template_id = :template_id LIMIT 1'
        )

        total_res = session.execute(
            total_sql,
            {'template_id': template_id}
        )

        sql = (
            'SELECT ts.wax_price, ts.usd_price, buyer, seller, ct.transaction_id AS buy_transaction_id, t.collection, '
            'cn.name AS display_name, ci.image AS collection_image, '
            'CASE WHEN taker IS NULL THEN market ELSE taker END AS market, asset_ids[1] AS asset_id, tn.name, a.mint, '
            'ti.image, t.template_id '
            'FROM template_sales ts '
            'LEFT JOIN sales s USING(seq) '
            'LEFT JOIN chronicle_transactions ct USING (seq) '
            'LEFT JOIN templates t USING(template_id) '
            'LEFT JOIN assets a ON asset_id = s.asset_ids[1] '
            'LEFT JOIN collections c ON (s.collection = c.collection) '
            'LEFT JOIN names cn ON c.name_id = cn.name_id '
            'LEFT JOIN images ci ON c.image_id = ci.image_id '
            'LEFT JOIN names tn ON t.name_id = tn.name_id '
            'LEFT JOIN images ti ON t.image_id = ti.image_id '
            'WHERE ts.template_id = :template_id {time_clause} {template_clause}'
            'ORDER BY usd_price DESC '
            'LIMIT :limit OFFSET :offset'.format(
                time_clause=' AND t.timestamp > (NOW() - INTERVAL :interval) at time zone \'utc\''
                if days and int(days) > 0 else '',
                template_clause=template_clause,
                with_clause=with_clause,
                join_clause=join_clause
            )
        )

        res = session.execute(sql, {
            'interval': '{} days'.format(days), 'limit': limit, 'offset': offset,
            'template_id': template_id, 'attribute_id': attribute_id
        })

        sales = []

        rank = 0
        for row in res:
            rank += 1
            sale = {
                'rank': rank,
                'collection': {
                    'name': row.collection,
                    'displayName': row.display_name,
                    'image': row.collection_image,
                },
                'asset': {
                    'assetId': row['asset_id'],
                    'name': row['name'],
                    'mint': row['mint'],
                    'image': row['image'],
                    'templateId': row['template_id']
                },
                'days': days,
                'waxPrice': row.wax_price,
                'usdPrice': row.usd_price,
                'buyer': row.buyer,
                'seller': row.seller,
                'tx': row.buy_transaction_id,
            }

            if is1of1:
                sale['attribute'] = {
                    'key': attribute_name,
                    'value': attribute_value
                }
            sales.append(sale)

        return sales
    except SQLAlchemyError as e:
        logging.error(e)
        session.rollback()
        raise e
    finally:
        session.remove()


@cache.memoize(timeout=300)
def get_top_sales_table(days, collection, limit, offset):
    session = create_session()
    try:
        res = session.execute(
            'SELECT wax_price, usd_price, buyer, seller, ct.transaction_id AS buy_transaction_id, t.collection, '
            'cn.name AS display_name, '
            'ci.image AS collection_image, '
            'CASE WHEN taker IS NULL THEN market ELSE taker END AS market, '
            'json_agg(json_build_object('
            '    \'asset_id\', asset_id, \'name\', an.name, \'mint\', mint, \'image\', ai.image, '
            '    \'template_id\', template_id'
            ')) as assets '
            'FROM sales t '
            'LEFT JOIN chronicle_transactions ct USING (seq) '
            'LEFT JOIN collections c USING (collection) '
            'LEFT JOIN names cn ON c.name_id = cn.name_id '
            'LEFT JOIN images ci ON c.image_id = ci.image_id '
            'LEFT JOIN assets a ON a.asset_id = ANY(asset_ids) '
            'LEFT JOIN names an ON a.name_id = an.name_id '
            'LEFT JOIN images ai ON a.image_id = ai.image_id '
            'WHERE NOT blacklisted {time_clause} {collection_clause} '
            'GROUP BY 1, 2, 3, 4, 5, 6, 7, 8, 9 '
            'ORDER BY wax_price DESC LIMIT :limit OFFSET :offset '.format(
                time_clause=' AND t.timestamp > (NOW() - INTERVAL :interval) at time zone \'utc\''
                if days and int(days) > 0 else '',
                collection_clause=' AND t.collection = :collection ' if collection and collection != '*' else ''
            ), {
                'interval': '{} days'.format(days), 'collection': collection, 'limit': limit, 'offset': offset
            }
        )

        sales = []

        rank = 0
        for row in res:
            rank += 1
            sales.append(
                {
                    'rank': rank,
                    'collection': {
                        'name': row.collection,
                        'displayName': row.display_name,
                        'image': row.collection_image,
                    },
                    'assets': _format_assets(row.assets),
                    'days': days,
                    'waxPrice': row.wax_price,
                    'usdPrice': row.usd_price,
                    'buyer': row.buyer,
                    'seller': row.seller,
                    'tx': row.buy_transaction_id,
                }
            )

        return sales
    except SQLAlchemyError as e:
        logging.error(e)
        session.rollback()
        raise e
    finally:
        session.remove()


@cache.memoize(timeout=300)
def get_market_table(days, collection, type):
    session = create_session()
    try:
        volume_column = 'volume_all_time'
        usd_volume_column = 'usd_volume_all_time'
        buyers_column = 'buyers_all_time'
        sellers_column = 'sellers_all_time'
        sales_column = 'sales_all_time'

        collection_table = ''
        time_table = 'all_time'

        if collection:
            collection_table = '_collection'

        if days and days != '0':
            time_table = days + '_days'

        table = 'volume_market{collection_table}_{time_table}_mv'.format(
            collection_table=collection_table, time_table=time_table
        )

        one_day_table = 'volume_market{collection_table}_1_days_mv'.format(
            collection_table=collection_table
        )

        two_days_table = 'volume_market{collection_table}_2_days_mv'.format(
            collection_table=collection_table
        )

        sql = (
            'SELECT * FROM (SELECT SUM(wax_volume) AS wax_volume, SUM(usd_volume) AS usd_volume, '
            'SUM(buyers) AS buyers, SUM(sellers) AS sellers, SUM(sales) AS sales, '
            'SUM(wax_volume_1_day) AS wax_volume_1_day, SUM(wax_volume_2_days) AS wax_volume_2_days, '
            't.market, '
            'ROW_NUMBER() OVER (ORDER BY SUM(wax_volume) DESC) AS rank '
            'FROM ('
            '   SELECT CASE WHEN u.taker IS NOT NULL THEN u.taker ELSE u.market END AS market, '
            '   SUM(u.wax_volume) * 0.5 AS wax_volume, SUM(u.usd_volume) * 0.5 AS usd_volume, '
            '   SUM(u.buyers) AS buyers, 0 AS sellers, '
            '   SUM(u.sales) AS sales, '
            '   SUM(m1.wax_volume) * 0.5 AS wax_volume_1_day, '
            '   SUM(m2.wax_volume) * 0.5 AS wax_volume_2_days, '
            '   \'a\' AS source '
            '   FROM {table} u '
            '   LEFT JOIN {one_day_table} m1 ON COALESCE(u.taker, \'\') = COALESCE(m1.taker, \'\') '
            '   AND u.market = m1.market AND COALESCE(u.maker, \'\') = COALESCE(m1.maker, \'\') '
            '   LEFT JOIN {two_days_table} m2 ON COALESCE(u.taker, \'\') = COALESCE(m2.taker, \'\') '
            '   AND u.market = m2.market AND COALESCE(u.maker, \'\') = COALESCE(m2.maker, \'\') '
            '   WHERE TRUE {type_clause} {collection_clause}'
            '   GROUP BY 1 '
            '   UNION SELECT CASE WHEN u.maker IS NOT NULL THEN u.maker ELSE u.market END AS market, '
            '   SUM(u.wax_volume) * 0.5 as volume, SUM(u.usd_volume) * 0.5 AS usd_volume, '
            '   0 AS buyers, SUM(u.sellers) AS sellers, '
            '   SUM(u.sales) AS sales, '
            '   SUM(m1.wax_volume) * 0.5 AS wax_volume_1_day, '
            '   SUM(m2.wax_volume) * 0.5 AS wax_volume_2_days, '
            '   \'b\' AS source '
            '   FROM {table} u '
            '   LEFT JOIN {one_day_table} m1 ON COALESCE(u.taker, \'\') = COALESCE(m1.taker, \'\') '
            '   AND u.market = m1.market AND COALESCE(u.maker, \'\') = COALESCE(m1.maker, \'\') '
            '   LEFT JOIN {two_days_table} m2 ON COALESCE(u.taker, \'\') = COALESCE(m2.taker, \'\') '
            '   AND u.market = m2.market AND COALESCE(u.maker, \'\') = COALESCE(m2.maker, \'\') '
            '   WHERE TRUE {type_clause} {collection_clause}'
            '   GROUP BY 1'
            ') t '
            'GROUP BY t.market ORDER BY 2 DESC) f '
            'GROUP BY 1, 2, 3, 4, 5, 6, 7, 8, 9 '
            'ORDER BY 9 ASC'.format(
                table=table, one_day_table=one_day_table, two_days_table=two_days_table,
                volume_column=volume_column, usd_volume_column=usd_volume_column,
                buyers_column=buyers_column, sellers_column=sellers_column, sales_column=sales_column,
                type_clause=' AND u.type = :type ' if type and type != 'all' else '',
                collection_clause=' AND collection = :collection ' if collection else '',
            )
        )

        market_results = session.execute(
            sql, {
                'type': type,
                'collection': collection
            }
        )

        markets = []

        for market in market_results:
            markets.append(
                {
                    'rank': market.rank,
                    'total': market_results.rowcount,
                    'market': market.market,
                    'stats': {
                        'days': days,
                        'waxVolume': float(market.wax_volume if market.wax_volume else 0),
                        'usdVolume': float(market.usd_volume if market.usd_volume else 0),
                        'change': float(
                            ((market.wax_volume_1_day - (market.wax_volume_2_days - market.wax_volume_1_day)) / (
                                    market.wax_volume_2_days - market.wax_volume_1_day))
                            if market.wax_volume_1_day and (market.wax_volume_2_days - market.wax_volume_1_day) else 0),
                        'buyers': int(market.buyers),
                        'sellers': int(market.sellers),
                        'sales': int(market.sales),
                    }
                }
            )

        return markets
    except SQLAlchemyError as e:
        logging.error(e)
        session.rollback()
    finally:
        session.remove()


@cache.memoize(timeout=300)
def get_collection_volume_graph(days, topx, type, collection):
    session = create_session()
    try:
        collections = {}

        top_collections = session.execute(
            'SELECT a.collection, n.name AS collection_name '
            'FROM collection_sales_by_date_mv a '
            'LEFT JOIN collections c USING (collection) '
            'LEFT JOIN names n USING (name_id) '
            'WHERE TRUE {date_clause} {type_clause} {collection_clause} '
            'GROUP BY 1, 2 '
            'ORDER BY SUM(wax_volume) DESC NULLS LAST '
            'LIMIT :topx'.format(
                type_clause=' AND type = :type ' if type and type != 'all' else '',
                date_clause=' AND to_date >= NOW() AT TIME ZONE \'utc\' - INTERVAL :interval' if days and int(
                    days) > 0 else '',
                collection_clause=' AND a.collection = :collection ' if collection and collection != '*' else ''
            ), {
                'interval': '{} days'.format(days),
                'topx': topx,
                'type': type,
                'collection': collection
            }
        )

        for top_collection in top_collections:
            collections[top_collection['collection']] = {'name': top_collection['collection_name']}

        top_x_collections = tuple(collections.keys())

        volumes = {
            'combined': {'name': 'Combined', 'graph': _create_empty_chart('waxVolume', int(days), 'usdVolume')},
            'others': {'name': 'Other', 'graph': _create_empty_chart('waxVolume', int(days), 'usdVolume')}
        }

        if len(top_x_collections) == 0:
            return volumes

        res = session.execute(
            'SELECT SUM(wax_volume) AS wax_volume, SUM(usd_volume) AS usd_volume, to_date AS date, '
            'CASE WHEN t.collection NOT IN :top THEN \'others\' ELSE t.collection END as collection '
            'FROM collection_sales_by_date_mv t '
            'WHERE TRUE {date_clause} '
            '{type_clause} {collection_clause} '
            'GROUP BY 3, 4 ORDER BY 3, 4'.format(
                type_clause=' AND type = :type ' if type and type != 'all' else '',
                date_clause=' AND to_date >= NOW() AT TIME ZONE \'utc\' - INTERVAL :interval' if days and int(
                    days) > 0 else '',
                collection_clause=' AND t.collection = :collection ' if collection and collection != '*' else ''
            ), {
                'interval': '{} days'.format(days),
                'top': top_x_collections,
                'type': type,
                'collection': collection
            }
        )

        for collection in top_x_collections:
            volumes[collection] = {
                'name': collections[collection]['name'],
                'graph': _create_empty_chart('waxVolume', int(days), 'usdVolume')
            }

        date_list = _create_date_list(int(days))

        for item in res:
            collection = item['collection']

            date = item['date'].strftime("%Y-%m-%d")
            try:
                index = date_list.index(date)

                if collection in top_x_collections:
                    volumes[collection]['graph'][index]['waxVolume'] = item['wax_volume'] if item['wax_volume'] else 0
                    volumes[collection]['graph'][index]['usdVolume'] = item['usd_volume'] if item['usd_volume'] else 0
                elif collection not in top_x_collections:
                    volumes['others']['graph'][index]['waxVolume'] = item['wax_volume'] if item['wax_volume'] else 0
                    volumes['others']['graph'][index]['usdVolume'] = item['usd_volume'] if item['usd_volume'] else 0

                volumes['combined']['graph'][index]['waxVolume'] += item['wax_volume'] if item['wax_volume'] else 0
                volumes['combined']['graph'][index]['usdVolume'] += item['usd_volume'] if item['usd_volume'] else 0
            except:
                continue

        return volumes
    except SQLAlchemyError as e:
        logging.error(e)
        session.rollback()
        raise e
    finally:
        session.remove()


@cache.memoize(timeout=300)
def get_collection_table(days, type, term, verified):
    session = create_session()
    try:
        table = 'volume_collection_{days}_mv'.format(days=days + '_days' if days and days != '0' else 'all_time')

        search_clause = ''
        if term and term != '*':
            search_clause = ' HAVING (collection ilike :term OR display_name ilike :term) '

        verified_clause = ''

        if verified == 'verified':
            verified_clause += ' AND c.verified '
        elif verified == 'unverified':
            verified_clause += (
                ' AND ('
                '   (c.verified IS NULL AND c.blacklisted IS NULL) OR (NOT c.verified AND NOT c.blacklisted)'
                ') '
            )
        elif verified == 'all':
            verified_clause += ' AND (NOT c.blacklisted OR c.blacklisted IS NULL) '
        elif verified == 'blacklisted':
            verified_clause += ' AND c.blacklisted '

        sql = (
            'SELECT * FROM (SELECT SUM(t.wax_volume) AS wax_volume, SUM(t.usd_volume) AS usd_volume, '
            'SUM(t.buyers) AS buyers, SUM(t.sellers) AS sellers, SUM(t.sales) AS sales, '
            '('
            '   SELECT SUM(wax_volume) FROM volume_collection_1_days_mv WHERE collection = t.collection'
            ') AS wax_volume_1_day, '
            '('
            '   SELECT SUM(wax_volume) FROM volume_collection_2_days_mv WHERE collection = t.collection'
            ') AS wax_volume_2_days, '
            't.collection AS collection, n.name AS display_name, i.image as collection_image, '
            'SUM(wax_volume_day_1) AS wax_volume_day_1, SUM(wax_volume_day_2) AS wax_volume_day_2, '
            'SUM(wax_volume_day_3) AS wax_volume_day_3, SUM(wax_volume_day_4) AS wax_volume_day_4, '
            'SUM(wax_volume_day_5) AS wax_volume_day_5, SUM(wax_volume_day_6) AS wax_volume_day_6, '
            'SUM(wax_volume_day_7) AS wax_volume_day_7, '
            'ROW_NUMBER() OVER (ORDER BY SUM(t.wax_volume) DESC) AS rank '
            'FROM ('
            '   SELECT wax_volume, usd_volume, buyers, sellers, sales, collection, type '
            '   FROM {table} '
            '   WHERE TRUE {type_clause}'
            ') t '
            'LEFT JOIN collections c USING (collection) '
            'LEFT JOIN names n USING (name_id) '
            'LEFT JOIN images i USING (image_id) '
            'LEFT JOIN (SELECT * FROM sales_seven_day_chart_mv WHERE TRUE {type_clause}) ssdc '
            'ON (t.collection = ssdc.collection AND t.type = ssdc.type) '
            'WHERE TRUE {verified_clause} '
            'GROUP BY t.collection, n.name, i.image ORDER BY 1 DESC) f '
            'GROUP BY 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18 '
            '{search_clause} '
            'ORDER BY 1 DESC'.format(
                table=table, search_clause=search_clause, verified_clause=verified_clause,
                type_clause=' AND type = :type ' if type and type != 'all' else '',
                time_clause=' AND timestamp > (NOW() - INTERVAL :full_interval) at time zone \'utc\''
                if days and int(days) > 0 else '',
            )
        )

        collection_results = session.execute(
            sql, {
                'full_interval': '{} days'.format(int(days) * 2),
                'interval': '{} days'.format(days),
                'type': type,
                'term': '%{}%'.format(term.lower()) if term else ''
            }
        )

        collections = []

        for collection in collection_results:
            try:
                collections.append(
                    {
                        'rank': collection.rank,
                        'total': collection_results.rowcount,
                        'collection': {
                            'name': collection.collection,
                            'image': collection.collection_image,
                            'displayName': collection.display_name,
                        },
                        'stats': {
                            'days': days,
                            'waxVolume': float(collection.wax_volume if collection.wax_volume else 0),
                            'usdVolume': float(collection.usd_volume if collection.usd_volume else 0),
                            'change': float(
                                ((collection.wax_volume_1_day - (
                                        collection.wax_volume_2_days - collection.wax_volume_1_day)
                                  ) / (collection.wax_volume_2_days - collection.wax_volume_1_day))
                                if collection.wax_volume_1_day and collection.wax_volume_2_days and (
                                        collection.wax_volume_2_days - collection.wax_volume_1_day) else 0),
                            'buyers': int(collection.buyers),
                            'sellers': int(collection.sellers),
                            'sales': int(collection.sales),
                            'trend': add_trend(collection)
                        }
                    }
                )
            except Exception as e:
                logging.error(e)

        return collections
    except SQLAlchemyError as e:
        logging.error(e)
        session.rollback()
    finally:
        session.remove()


@cache.memoize(timeout=300)
def get_number_of_assets(user, collection):
    session = create_session()
    table = 'collection_assets_mv'
    try:
        result = session.execute(
            'SELECT SUM(num_assets) AS num_assets, SUM(wax_value) AS wax_value, SUM(usd_value) AS usd_value '
            'FROM collection_users_mv '
            'WHERE TRUE {collection_clause} {user_clause}'.format(
                table=table,
                collection_clause='AND collection = :collection' if collection else '',
                user_clause='AND owner = :user' if user else ''
            ), {'collection': collection, 'user': user}).first()

        return {
            'numberOfAssets': int(result['num_assets']) if result['num_assets'] else 0,
            'estimatedWaxValue': float(result['wax_value']) if result['wax_value'] else 0,
            'estimatedUsdValue': float(result['usd_value']) if result['usd_value'] else 0,
        }
    except SQLAlchemyError as e:
        logging.error(e)
        session.rollback()
        raise e
    finally:
        session.remove()


@cache.memoize(timeout=300)
def get_number_of_users(collection):
    session = create_session()
    try:
        result = session.execute(
            'SELECT COUNT(1) AS num_users FROM collection_users_mv '
            'WHERE collection = :collection',
            {'collection': collection}
        ).first()

        return {
            'numberOfUsers': int(result['num_users']) if result['num_users'] else 0,
        }
    except SQLAlchemyError as e:
        logging.error(e)
        session.rollback()
        raise e
    finally:
        session.remove()


last_reported_seq = 0


@cache.memoize(timeout=300)
def get_price_history(asset_id=None, template_id=None):
    session = create_session()
    try:
        if asset_id:
            template_res = session.execute(
                'SELECT template_id FROM assets WHERE asset_id = :asset_id', {
                    'asset_id': asset_id
                }
            ).first()

            if template_res and template_res['template_id']:
                template_id = template_res['template_id']
            else:
                return {'priceHistory': []}

        result = session.execute(
            'SELECT wax_volume / sales as wax_price, usd_volume / sales as usd_price, sales, to_date '
            'FROM template_collection_sales_by_date_mv t '
            'WHERE {template_clause} '
            'ORDER BY to_date DESC LIMIT 100'.format(
                template_clause='t.template_id = :template_id ' if template_id else 't.template_id = (SELECT template_id FROM assets WHERE asset_id = :asset_id) '
            ),
            {'template_id': template_id}
        )

        price_history = {}

        for item in result:
            price_history[item['to_date'].strftime("%Y-%m-%d")] = {
                'waxPrice': item['wax_price'],
                'usdPrice': item['usd_price'],
                'sales': item['sales'],
            }

        date_list = []
        if len(price_history.keys()) > 0:
            min_date = datetime.datetime.strptime(sorted(price_history.keys())[0], '%Y-%m-%d')
            max_date = datetime.datetime.now()
            if min_date > max_date - datetime.timedelta(days=30):
                min_date = max_date - datetime.timedelta(days=30)

            delta = max_date - min_date

            for i in range(delta.days + 1):
                day = (min_date + datetime.timedelta(days=i)).strftime('%Y-%m-%d')
                if day not in price_history.keys():
                    date_list.append(
                        {
                            'date': day,
                            'waxPrice': None,
                            'usdPrice': None,
                            'sales': 0
                        }
                    )
                else:
                    date_list.append(
                        {
                            'date': day,
                            'waxPrice': price_history[day]['waxPrice'],
                            'usdPrice': price_history[day]['usdPrice'],
                            'sales': price_history[day]['sales']
                        }
                    )

        return {
            'priceHistory': sorted(
                date_list, key=lambda d: datetime.datetime.strptime(d['date'], '%Y-%m-%d')
            )
        }
    except SQLAlchemyError as e:
        logging.error(e)
        session.rollback()
        raise e
    finally:
        session.remove()


def get_newest_sales():
    session = create_session()

    global last_reported_seq

    try:
        sql = (
            'SELECT asset_id, an.name, t.collection, ai.image, wax_price, usd_price, cn.name as display_name, '
            't.timestamp, c.collection AS collection_name, ci.image as collection_image, t.taker, t.market, '
            't.listing_id, a.template_id, t.seq AS buy_seq '
            'FROM sales t '
            'LEFT JOIN collections c ON c.collection = t.collection '
            'LEFT JOIN assets a ON a.asset_id = asset_ids[1] '
            'LEFT JOIN names an ON a.name_id = an.name_id '
            'LEFT JOIN names cn ON c.name_id = cn.name_id '
            'LEFT JOIN images ai ON ai.image_id = a.image_id '
            'LEFT JOIN images ci ON ci.image_id = c.image_id '
            'WHERE verified AND ARRAY_LENGTH(asset_ids, 1) = 1 AND ai.image IS NOT NULL '
            'ORDER BY t.seq DESC limit 10'
        )

        sales_results = session.execute(
            sql
        )

        sales = []

        max_seq = 0

        has_new_element = False
        for sale in sales_results:
            if 'Testa' in sale.name:
                print(sale)
            dict = {
                'asset': {
                    'assetId': sale.asset_id,
                },
                'sale': {
                    'waxPrice': sale.wax_price,
                    'usdPrice': sale.usd_price,
                    'timestamp': sale.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                    'globalSequence': sale.buy_seq
                },
                'collection': {
                    'name': sale.collection_name if sale.collection_name else sale.collection,
                }
            }
            if sale.name:
                dict['asset']['name'] = sale.name.replace('\"', '\'')
            if sale.image and 'video:' in sale.image:
                dict['asset']['video'] = sale.image.replace('video:', '')
            elif sale.image:
                dict['asset']['image'] = sale.image

            if sale.template_id:
                dict['asset']['templateId'] = sale.template_id

            if sale.market:
                dict['sale']['market'] = sale.market
            if sale.market:
                dict['sale']['listingId'] = sale.listing_id

            if sale.taker:
                dict['sale']['taker'] = sale.taker

            if sale.display_name:
                dict['collection']['displayName'] = sale.display_name.replace('\'', '\\\'')

            if sale.collection_image:
                dict['collection']['image'] = sale.collection_image

            sales.append(dict)

            if sale.buy_seq > max_seq:
                max_seq = sale.buy_seq

            if max_seq > last_reported_seq:
                last_reported_seq = max_seq
                has_new_element = True

        return {'hasNewElement': 1 if has_new_element else 0, 'elements': sales}
    except SQLAlchemyError as e:
        logging.error(e)
        session.rollback()
    except Exception as e:
        print(e)
    finally:
        session.remove()
