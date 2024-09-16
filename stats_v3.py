import json

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
def get_collection_tokens(collection):
    session = create_session()
    try:
        sql = (
            'SELECT symbol, contract, ti,image AS token_image, collection_name, c.image as collection_image, '
            'c.name AS display_name, '
            'volume_1_day AS volume_1_day, '
            'usd_volume_2_days - usd_volume_1_day AS prev_usd_volume, '
            'volume_2_days - volume_1_day AS prev_volume, '
            'volume_1_day, usd_volume_1_day, '
            'volume_2_days, usd_volume_2_days, '
            'volume_3_days, usd_volume_3_days, '
            'volume_7_days, usd_volume_7_days, '
            'wax_price, usd_price, wax_price_prev, usd_price_prev '
            'FROM token_collection_mapping s '
            'LEFT JOIN token_volumes_s USING (symbol, contract) '
            'LEFT JOIN token_prices_mv USING (symbol, contract) '
            'LEFT JOIN collections c USING (collection_name) '
            'WHERE collection_name = :collection '
        )

        token_results = session.execute(
            sql, {
                'collection': collection
            }
        )

        tokens = []

        for token in token_results:
            tokens.append(
                {
                    'collection': {
                        'name': token.collection_name,
                        'image': token.collection_image,
                        'displayName': token.display_name,
                    },
                    'token': {
                        'contract': token.contract,
                        'symbol': token.symbol,
                        'image': token.token_image,
                    },
                    'stats': {
                        'usdVolume1Day': float(token.usd_volume_1_day if token.usd_volume_1_day else 0),
                        'volume1Day': float(token.volume_1_day if token.volume_1_day else 0),
                        'usdVolume1DayPrev': float(token.prev_usd_volume if token.prev_usd_volume else 0),
                        'volume1DayPrev': float(token.prev_volume if token.prev_volume else 0),
                        'usdVolume2Days': float(token.usd_volume_2_days if token.usd_volume_2_days else 0),
                        'volume2Days': float(token.volume_2_days if token.volume_2_days else 0),
                        'usdVolume3Days': float(token.usd_volume_3_days if token.usd_volume_3_days else 0),
                        'volume3Days': float(token.volume_3_days if token.volume_3_days else 0),
                        'usdVolume7Days': float(token.usd_volume_7_days if token.usd_volume_7_days else 0),
                        'volume7Days': float(token.volume_7_days if token.volume_7_days else 0),
                        'waxPrice': float(token.wax_price if token.wax_price else 0),
                        'usdPrice': float(token.usd_price if token.usd_price else 0),
                        'usdChange': float(
                            ((token.usd_price - token.usd_price_prev) / token.usd_price_prev)
                            if token.usd_price and token.usd_price_prev else 0),
                        'change': float(
                            ((token.wax_price - token.wax_price_prev) / token.wax_price_prev)
                            if token.wax_price and token.wax_price_prev else 0),
                    }
                }
            )

        return tokens
    except SQLAlchemyError as e:
        logging.error(e)
        session.rollback()
    finally:
        session.remove()


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
            'SELECT owner as user_name, value, usd_value, num_assets, image '
            'FROM users_mv '
            'LEFT JOIN user_pictures_mv up ON owner = user_name '
            'WHERE owner = :owner ',
            {'owner': user}
        ).first()

        if not res:
            return {
                'name': 'Error',
                'image': 'Error',
                'value': 'Error',
                'usdValue': 'Error',
                'numAssets': 'Error'
            }

        return {
            'name': res.user_name,
            'image': res.image,
            'value': float(res.value if res.value else 0),
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
            'SELECT date, SUM(volume) AS volume, SUM(usd_volume) AS usd_volume '
            'FROM monthly_volume_mv WHERE TRUE {type_clause} {date_clause} {collection_clause} '
            'GROUP BY 1 ORDER BY 1 ASC'.format(
                collection_clause=' AND collection = :collection ' if collection and collection != '*' else '',
                type_clause=' AND type = :type ' if type and type != 'all' else '',
                date_clause=' AND date >= NOW() AT TIME ZONE \'utc\' - INTERVAL :interval' if days and int(days) > 0 else '',
            ), {'type': type, 'collection': collection, 'interval': '{} days'.format(days)},
        )

        volumes = []

        for item in res:
            volumes.append({
                'date': item['date'].strftime("%Y-%m-%d"),
                'volume': item['volume'],
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

        dates = _create_empty_chart('volume', int(days), 'usdVolume', 'sales')
        for item in sales_volume:
            date = item['date'].strftime("%Y-%m-%d")
            for date_item in dates:
                if date_item['date'] == date:
                    date_item['volume'] = float(item['volume'])
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
        sales_volume = session.execute(
            'SELECT to_date, SUM(wax_volume) AS wax_volume, SUM(usd_volume) AS usd_volume, SUM(sales) AS sales '
            'FROM {template}collection_sales_by_date_mv t '
            'WHERE TRUE {date_clause}{collection_clause}{type_clause}{template_clause}'
            'GROUP BY 1 ORDER BY 1 DESC'.format(
                template='template_' if template_id else '',
                date_clause=' AND to_date >= NOW() AT TIME ZONE \'utc\' - INTERVAL :interval ' if days and int(
                    days) > 0 else '',
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

        dates = _create_empty_chart('volume', int(days), 'sales', 'usdVolume')
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
        usd_volume_column = 'usd_volume_all_time'
        volume_column = 'volume_all_time'
        buyers_column = 'claimers_all_time'
        amount_column = 'amount_all_time'

        table = 'drop_volumes_mv'

        if days and int(days) == 1:
            volume_column = 'volume_1_day'
            usd_volume_column = 'usd_volume_1_day'
            buyers_column = 'claimers_1_day'
            amount_column = 'amount_1_day'
        elif days and int(days) > 0:
            volume_column = 'volume_{}_days'.format(days)
            usd_volume_column = 'usd_volume_{}_days'.format(days)
            buyers_column = 'claimers_{}_days'.format(days)
            amount_column = 'amount_{}_days'.format(days)

        if days and 0 < int(days) < 15:
            table = 'drop_volumes_s_mv'

        total_result = session.execute(
            'SELECT COUNT(1) AS total_results '
            'FROM {table} tb '.format(
                table=table
            )
        ).first()

        drops_result = session.execute(
            'SELECT dv.drop_id, dv.market, d.display_data, d.author, c.name AS display_name, '
            'c.image AS collection_image, {volume_column} AS volume, {usd_volume_column} AS usd_volume, '
            '{buyers_column} AS buyers, {amount_column} AS claims, '
            'json_agg(json_build_object(\'template_id\', t.template_id, \'data\', t.idata)) AS template_data, '
            'COUNT(1) AS total_amount, ROW_NUMBER() OVER (ORDER BY {volume_column} DESC) AS rank '
            'FROM {table} dv '
            'LEFT JOIN drops d ON d.drop_id = dv.drop_id AND d.contract = dv.market '
            'LEFT JOIN templates t ON t.template_id = ANY(templates_to_mint) '
            'LEFT JOIN collections c ON c.collection_name = d.author '
            'GROUP BY 1,2,3,4,5,6,7,8,9,10 ORDER BY {volume_column} DESC '
            'LIMIT :limit OFFSET :offset'.format(
                table=table, volume_column=volume_column, usd_volume_column=usd_volume_column,
                buyers_column=buyers_column, amount_column=amount_column
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
                        'name': drop.author,
                        'displayName': drop.display_name,
                        'image': drop.collection_image,
                    },
                    'stats': {
                        'days': days,
                        'volume': float(drop.volume if drop.volume else 0),
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


def _parse_immutable_data(data):
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
            template_data = _parse_immutable_data(json.loads(template['idata']))
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
def get_attribute_asset_analytics(asset_id, template_id):
    session = create_session()
    if not asset_id and not template_id:
        return None
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
            'WHERE TRUE {template_clause} {asset_clause}'.format(
                template_clause=' AND template_id = :template_id ' if template_id else '',
                asset_clause=' AND a.asset_id = :asset_id' if asset_id else ' AND a.asset_id = (SELECT asset_id FROM attribute_assets WHERE template_id = :template_id AND rank = 1 LIMIT 1) '
            ), {'template_id': template_id, 'asset_id': asset_id}
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
                    'percentage': attribute['total'] / attribute['total_schema'] if attribute['total_schema'] else 0,
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
            'SELECT COUNT(1) AS total, a.mdata, aa.attribute_ids '
            'FROM attribute_assets aa INNER JOIN templates t USING(template_id) '
            'INNER JOIN assets a USING(asset_id) '
            'LEFT JOIN asset_summaries asu ON (asu.summary_id =  a.summary_id) '
            'WHERE aa.template_id = :template_id GROUP BY 2, 3',
            {'template_id': template_id}
        ).first()

        hasRarity = False

        template_data = json.loads(total_res['mdata'])

        if total_res and total_res['total'] == 1 and total_res['attribute_ids'] and len(total_res['attribute_ids']) > 0:
            is1of1 = True
            if 'rarity' in template_data.keys() or 'Rarity' in template_data.keys():
                hasRarity = True
                template = session.execute(
                    'SELECT idata, template_id, category, category_3 AS rarity, tb.author, c.name, c.image, floor, '
                    'usd_floor FROM rarity_floors_mv tb '
                    'INNER JOIN templates t USING(author, category) '
                    'INNER JOIN collections c ON (tb.author = collection_name) '
                    'WHERE template_id = :template_id AND tb.author = t.author AND tb.category = t.category '
                    'AND category_3 = :rarity',
                    {'template_id': template_id,
                     'rarity': template_data['rarity'] if 'rarity' in template_data.keys() else template_data['Rarity']}
                ).first()
            else:
                hasRarity = False
                template = session.execute(
                    'SELECT idata, template_id, category, tb.author, c.name, c.image, floor, usd_floor '
                    'FROM schema_floors_mv tb '
                    'INNER JOIN templates t USING(author, category) '
                    'INNER JOIN collections c ON (tb.author = collection_name) '
                    'WHERE template_id = :template_id',
                    {'template_id': template_id}
                ).first()
        else:
            is1of1 = False
            template = session.execute(
                'SELECT idata, template_id, category, tb.author, c.name, c.image, min_price AS floor, '
                'min_price_usd AS usd_floor '
                'FROM floor_template_mv tb '
                'INNER JOIN collections c ON (tb.author = collection_name) '
                'INNER JOIN templates t USING(template_id) '
                'WHERE template_id = :template_id',
                {'template_id': template_id}
            ).first()

        if template is None:
            return []

        template_data['template_id'] = template['template_id']
        template_data['schema'] = template['category']

        return {
            'template': template_data,
            'waxFloor': template.floor,
            'usdFloor': template.usd_floor,
            'is1of1': is1of1,
            'has1of1Rarity': hasRarity,
            'collection': {
                'name': template.author,
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

    table = 'volume_collection_1_days_mv'
    volume_column = 'wax_volume'

    if days and days != '0':
        table = 'volume_collection_{}_days_mv'.format(days)
    else:
        volume_column = 'volume_collection_all_time_mv'

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
            'waxVolume': float(result.usd_volume if result.usd_volume else 0),
            'usdVolume': float(result.usd_volume if result.usd_volume else 0),
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

        if template_id:
            template_clause = ' AND template_id = :template_id '
            total_res = session.execute(
                'SELECT SUM(total) AS total, attribute_ids '
                'FROM templates '
                'LEFT JOIN template_asset_summary_mapping tm USING (template_id) '
                'LEFT JOIN asset_summaries asu ON (asu.summary_id =  tm.summary_id) '
                'WHERE template_id = :template_id GROUP BY 2',
                {'template_id': template_id}
            ).first()

            if total_res and total_res['total'] == 1 and total_res['attribute_ids'] and len(
                    total_res['attribute_ids']) > 0:
                join_clause = 'INNER JOIN similar_templates USING (template_id) '
                attribute = session.execute(
                    'SELECT attribute_id, attribute_name, string_value, int_value, bool_value, float_value '
                    'FROM templates f '
                    'LEFT JOIN attribute_summaries af ON af.attribute_id = ANY(attribute_ids) '
                    'LEFT JOIN attributes a USING (attribute_id) '
                    'WHERE template_id = :template_id ORDER BY total ASC NULLS LAST ', {
                        'template_id': template_id
                    }
                ).first()

                if attribute:
                    template_clause = ' AND :attribute_id = ANY(attribute_ids) '
                    attribute_id = attribute['attribute_id']
                    attribute_name = attribute['attribute_name']
                    if attribute['string_value']:
                        attribute_value = attribute['string_value']
                    elif attribute['int_value'] or attribute['int_value'] == 0:
                        attribute_value = int(attribute['string_value'])
                    elif attribute['float_value'] or attribute['float_value'] == 0.0:
                        attribute_value = float(attribute['float_value'])
                    is1of1 = True

        res = session.execute(
            'SELECT price, usd_price, buyer, seller, buy_transaction_id, t.author, c.name AS display_name, '
            'c.image AS collection_image, CASE WHEN taker IS NULL THEN market ELSE taker END AS market, '
            'collection_name, asset_id, t.name, mint, t.image, template_id '
            'FROM trades t '
            'LEFT JOIN templates USING(template_id) '
            'LEFT JOIN collections c ON (t.author = collection_name) '
            'WHERE TRUE {time_clause} {template_clause} AND NOT bundle '
            'ORDER BY usd_price DESC '.format(
                time_clause=' AND t.timestamp > (NOW() - INTERVAL :interval) at time zone \'utc\''
                if days and int(days) > 0 else '',
                template_clause=template_clause,
                with_clause=with_clause,
                join_clause=join_clause
            ), {
                'interval': '{} days'.format(days), 'limit': limit, 'offset': offset,
                'template_id': template_id, 'attribute_id': attribute_id
            }
        )

        sales = []

        rank = 0
        for row in res:
            rank += 1
            sale = {
                'rank': rank,
                'collection': {
                    'name': row.author,
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
                'price': row.price,
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
def get_token_table(days, term):
    session = create_session()
    try:
        volume_column = 'volume_1_day'
        usd_volume_column = 'usd_volume_1_day'
        days_queried = 1

        search_clause = ''
        if term:
            search_clause = (
                ' HAVING ('
                'collection_name ilike :term '
                'OR display_name ilike :term '
                'OR symbol ilike :term '
                'OR contract ilike :term) '
            )

        if days and int(days) > 1 and int(days) in [2, 3, 7]:
            days_queried = int(days)
            volume_column = 'volume_{}_days'.format(days)
            usd_volume_column = 'usd_volume_{}_days'.format(days)

        sql = (
            'SELECT * '
            'FROM (SELECT symbol, contract, ti.image AS token_image, c.collection_name, c.image AS collection_image, '
            'c.name AS display_name, wax_price, usd_price, wax_price_prev, usd_price_prev, '
            'SUM({volume_column}) as volume, SUM({usd_volume_column}) AS usd_volume, '
            'SUM(volume_1_day) AS volume_1_day, '
            'SUM(volume_2_days) - SUM(volume_1_day) AS prev_usd_volume, '
            'ROW_NUMBER() OVER (ORDER BY SUM({volume_column}) DESC) AS rank '
            'FROM token_volumes_s s '
            'LEFT JOIN token_images ti USING (symbol, contract) '
            'LEFT JOIN token_prices_mv USING (symbol, contract) '
            'LEFT JOIN token_collection_mapping USING (symbol, contract) '
            'LEFT JOIN collections c USING (collection_name) '
            'GROUP BY 1, 2, 3, 4, 5, 6, 7, 8, 9, 10) f '
            'GROUP BY 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15 {search_clause} ORDER BY volume DESC ' 
            ''.format(
                search_clause=search_clause, volume_column=volume_column, usd_volume_column=usd_volume_column
            )
        )

        token_results = session.execute(
            sql, {
                'term': '%{}%'.format(term.lower()) if term else ''
            }
        )

        tokens = []

        index = 0
        for token in token_results:
            index += 1
            tokens.append(
                {
                    'rank': token.rank,
                    'total': token_results.rowcount,
                    'collection': {
                        'name': token.collection_name,
                        'image': token.collection_image,
                        'displayName': token.display_name,
                    },
                    'token': {
                        'contract': token.contract,
                        'symbol': token.symbol,
                        'image': token.token_image,
                    },
                    'stats': {
                        'days': days_queried,
                        'usdVolume': float(token.usd_volume if token.usd_volume else 0),
                        'volume': float(token.volume if token.volume else 0),
                        'waxPrice': float(token.wax_price if token.wax_price else 0),
                        'usdPrice': float(token.usd_price if token.usd_price else 0),
                        'usdChange': float(
                            ((token.usd_price - token.usd_price_prev) / token.usd_price_prev)
                            if token.usd_price and token.usd_price_prev else 0),
                        'change': float(
                            ((token.wax_price - token.wax_price_prev) / token.wax_price_prev)
                            if token.wax_price and token.wax_price_prev else 0),
                    }
                }
            )

        return tokens
    except SQLAlchemyError as e:
        logging.error(e)
        session.rollback()
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
                type_clause=' AND type = :type ' if type and type != 'all' else '',
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
def get_market_volume_graph(days, topx, type):
    session = create_session()
    try:
        markets = {}

        top_markets = session.execute(
            'SELECT market '
            'FROM market_collection_sales_by_date '
            'WHERE TRUE {date_clause} '
            ' {type_clause} '
            'GROUP BY 1 '
            'ORDER BY SUM(usd_price) DESC NULLS LAST '
            'LIMIT :topx'.format(
                type_clause=' AND type = :type ' if type and type != 'all' else '',
                date_clause=' AND date >= NOW() AT TIME ZONE \'utc\' - INTERVAL :interval' if days and int(days) > 0 else '',
            ), {
                'interval': '{} days'.format(days),
                'topx': topx,
                'type': type
            }
        )

        for top_market in top_markets:
            markets[top_market['market']] = {'name': top_market['market']}

        top_x_markets = tuple(markets.keys())

        volumes = {
            'combined': {'name': 'Combined', 'graph': _create_empty_chart('volume', int(days), 'usdVolume')},
            'others': {'name': 'Other', 'graph': _create_empty_chart('volume', int(days), 'usdVolume')}
        }

        res = session.execute(
            'SELECT SUM(price) AS volume, SUM(usd_price) AS usd_volume, date, '
            'CASE WHEN t.market NOT IN :top THEN \'others\' ELSE t.market END AS market '
            'FROM market_collection_sales_by_date t '
            'WHERE TRUE {date_clause} '
            '{type_clause} '
            'GROUP BY 3, 4 ORDER BY 3, 4'.format(
                type_clause=' AND type = :type ' if type and type != 'all' else '',
                date_clause=' AND date >= NOW() AT TIME ZONE \'utc\' - INTERVAL :interval' if days and int(days) > 0 else '',
            ), {
                'interval': '{} days'.format(days),
                'top': top_x_markets,
                'type': type
            }
        )

        for market in top_x_markets:
            volumes[market] = {
                'name': markets[market]['name'],
                'graph': _create_empty_chart('volume', int(days), 'usdVolume')
            }

        date_list = _create_date_list(int(days))

        for item in res:
            market = item['market']

            date = item['date'].strftime("%Y-%m-%d")
            try:
                index = date_list.index(date)

                if market in top_x_markets:
                    volumes[market]['graph'][index]['volume'] = item['volume'] if item['volume'] else 0
                    volumes[market]['graph'][index]['usdVolume'] = item['usd_volume'] if item['usd_volume'] else 0
                elif market not in top_x_markets:
                    volumes['others']['graph'][index]['volume'] = item['volume'] if item['volume'] else 0
                    volumes['others']['graph'][index]['usdVolume'] = item['usd_volume'] if item['usd_volume'] else 0

                volumes['combined']['graph'][index]['volume'] += item['volume'] if item['volume'] else 0
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
def get_collection_volume_graph(days, topx, type, collection):
    session = create_session()
    try:
        collections = {}

        top_collections = session.execute(
            'SELECT a.collection, n.name AS collection_name '
            'FROM collection_sales_by_date_from_2024_mv a '
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
            'combined': {'name': 'Combined', 'graph': _create_empty_chart('volume', int(days), 'usdVolume')},
            'others': {'name': 'Other', 'graph': _create_empty_chart('volume', int(days), 'usdVolume')}
        }

        if len(top_x_collections) == 0:
            return volumes

        res = session.execute(
            'SELECT SUM(wax_volume) AS wax_volume, SUM(usd_volume) AS usd_volume, date, '
            'CASE WHEN t.collection NOT IN :top THEN \'others\' ELSE t.collection END as collection '
            'FROM collection_sales_by_date_from_2024_mv t '
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
                'graph': _create_empty_chart('volume', int(days), 'usdVolume')
            }

        date_list = _create_date_list(int(days))

        for item in res:
            collection = item['author']

            date = item['date'].strftime("%Y-%m-%d")
            try:
                index = date_list.index(date)

                if collection in top_x_collections:
                    volumes[collection]['graph'][index]['volume'] = item['volume'] if item['volume'] else 0
                    volumes[collection]['graph'][index]['usdVolume'] = item['usd_volume'] if item['usd_volume'] else 0
                elif collection not in top_x_collections:
                    volumes['others']['graph'][index]['volume'] = item['volume'] if item['volume'] else 0
                    volumes['others']['graph'][index]['usdVolume'] = item['usd_volume'] if item['usd_volume'] else 0

                volumes['combined']['graph'][index]['volume'] += item['volume'] if item['volume'] else 0
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
            'SUM(m1.wax_volume) AS wax_volume_1_day, SUM(m2.wax_volume) AS wax_volume_2_days, '
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
            'LEFT JOIN volume_collection_1_days_mv m1 USING (collection) '
            'LEFT JOIN volume_collection_2_days_mv m2 USING (collection) '
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
                            if collection.wax_volume_1_day and (
                                    collection.wax_volume_2_days - collection.wax_volume_1_day) else 0),
                        'buyers': int(collection.buyers),
                        'sellers': int(collection.sellers),
                        'sales': int(collection.sales),
                        'trend': add_trend(collection)
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
def get_number_of_assets(collection):
    session = create_session()
    try:
        result = session.execute(
            'SELECT SUM(num_assets) AS num_assets FROM collection_assets_mv '
            'WHERE TRUE {collection_clause}'.format(
                collection_clause='AND collection = :collection' if collection else ''
            ), {'collection': collection}).first()

        return {
            'numberOfAssets': int(result['num_assets']) if result['num_assets'] else 0,
        }
    except SQLAlchemyError as e:
        logging.error(e)
        session.rollback()
        raise e
    finally:
        session.remove()


last_reported_seq = 0


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
            'WHERE verified AND NOT ARRAY_LENGTH(asset_ids, 1) = 1 AND ai.image IS NOT NULL '
            'ORDER BY t.seq DESC limit 10'
        )

        sales_results = session.execute(
            sql
        )

        sales = []

        max_seq = 0

        has_new_element = False
        for sale in sales_results:
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
                    'name': sale.collection_name if sale.collection_name else sale.author,
                }
            }
            if sale.name:
                dict['asset']['name'] = sale.name.replace('\'', '\\\'')
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
