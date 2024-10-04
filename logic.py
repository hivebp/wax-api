import concurrent
import datetime
import json

from sqlalchemy.exc import SQLAlchemyError

from api import logging
from api import cache
from api import executor
from api import db

import time
import requests

DATE_FORMAT_STRING = "%Y-%m-%d %H:%M:%S"
DATE_FROM_STRING_FORMAT = "%Y-%m-%dT%H:%M:%S%z"
DATE_FROM_STRING_SPLIT_FORMAT = "%Y-%m-%dT%H:%M:%S"


def create_session():
    return db.session


def _format_video(video):
    if 'http' in video:
        return video
    return 'https://ipfs.hivebp.io/ipfs/{}'.format(video.replace('video:', '').strip())


def _format_image(image):
    if image and 'http' not in image and 'video:' not in image:
        return 'https://ipfs.hivebp.io/ipfs/{}'.format(image)
    return image if image else ''


def _format_thumbnail(image):
    if not image:
        return image
    if 'video:' in image:
        return 'https://ipfs.hivebp.io/video?hash={}'.format(
            image.replace('DUNGEONS-&-DRAGONS', 'DUNGEONS-%26-DRAGONS').replace('video:', '').strip())
    else:
        return 'https://ipfs.hivebp.io/thumbnail?hash={}'.format(
            image.replace('DUNGEONS-&-DRAGONS', 'DUNGEONS-%26-DRAGONS'))


def _format_collection_thumbnail(collection, image=None, size=80):
    if not image:
        return image
    return 'https://ipfs.hivebp.io/preview?collection={}&size={}&hash={}'.format(
        collection, size, image.replace('video:', '').replace('DUNGEONS-&-DRAGONS', 'DUNGEONS-%26-DRAGONS').strip()
    )


def _format_preview(image):
    return 'https://ipfs.hivebp.io/preview/{}'.format(image)


def _format_banner(image):
    return 'https://ipfs.hivebp.io/nfthive?ipfs={}'.format(image)


def _parse_mdata(asset):
    return json.loads(asset.mdata.replace('""', '","').replace('”', '"')) if asset.mdata else None


def _get_name(asset):
    mdata = _parse_mdata(asset)
    return mdata['name'] if mdata and 'name' in mdata.keys() else None


def _get_image(asset):
    mdata = _parse_mdata(asset)
    return mdata['img'] if mdata and 'img' in mdata.keys() else None


def to_camel_case(snake_str):
    return "".join(x.capitalize() for x in snake_str.lower().split("_"))


def to_lower_camel_case(snake_str):
    camel_string = to_camel_case(snake_str)
    return snake_str[0].lower() + camel_string[1:]


def _get_templates_object():
    return (
        'array_agg(json_build_object(\'template_id\', t.template_id, \'name\', tn.name, \'collection\', t.collection, '
        '\'schema\', t.schema, \'immutableData\', td.data, \'image\', ti.image, \'video\', tv.video, '
        '\'avgWaxPrice\', ts.avg_wax_price, \'avgUsdPrice\', ts.avg_usd_price, '
        '\'lastSoldWax\', ts.last_sold_wax, \'last_sold_usd\', ts.last_sold_usd, '
        '\'lastSoldListingId\', last_sold_listing_id, \'lastSoldTimestamp\', ts.last_sold_timestamp, '
        '\'floorPrice\', fp.floor_price, \'numBurned\', tm.num_burned, \'numMinted\', tm.num_minted, '
        '\'volumeWax\', ts.volume_wax, \'volumeUsd\', ts.volume_usd, \'numSales\', ts.num_sales, '
        '\'createdAt\', t.timestamp, \'createdBlockNum\', t.block_num, \'createdSeq\', t.seq, '
        '\'traits\', {attributes_obj})) AS templates '.format(
            attributes_obj=_get_template_attributes_object()
        )
    )


def _get_assets_object():
    return (
        'array_agg(json_build_object(\'asset_id\', a.asset_id, \'name\', n.name, \'collection\', a.collection, '
        '\'schema\', a.schema, \'mutable_data\', m.data, \'immutable_data\', i.data, \'template_immutable_data\', '
        'td.data, \'num_burned\', tm.num_burned, \'avg_wax_price\', ts.avg_wax_price, \'avg_usd_price\', '
        'ts.avg_usd_price, \'last_sold_wax\', ts.last_sold_wax, \'last_sold_usd\', ts.last_sold_usd, '
        '\'last_sold_listing_id\', last_sold_listing_id, \'last_sold_timestamp\', ts.last_sold_timestamp, '
        '\'owner\', a.owner, \'burned\', burned, \'floor_price\', fp.floor_price, \'rwax_symbol\', r.symbol, '
        '\'rwax_contract\', r.contract, \'rwax_max_assets\', r.max_assets, \'trait_factors\', rt.trait_factors, '
        '\'rwax_supply\', rt.maximum_supply, \'rwax_decimals\', rt.decimals, \'rwax_token_name\', rt.token_name, '
        '\'rwax_token_logo\', rt.token_logo, \'rwax_token_logo_lg\', rt.token_logo_lg, \'volume_wax\', ts.volume_wax, '
        '\'volume_usd\', ts.volume_usd, \'num_sales\', ts.num_sales, \'num_minted\', tm.num_minted, \'favorited\', '
        'f.user_name IS NOT NULL, \'template_id\', t.template_id, \'image\', img.image, \'video\', vid.video, '
        '\'mint\', a.mint, \'mint_timestamp\', a.timestamp, \'mint_block_num\', a.block_num, \'mint_seq\', a.seq, '
        '\'rarity_score\', p.rarity_score, \'num_traits\', p.num_traits, \'rank\', p.rank, '
        '\'traits\', {attributes_obj})) AS assets '.format(attributes_obj=_get_attributes_object())
    )


def _get_badges_object(prefix='a.'):
    return (
        '(SELECT array_agg(json_build_object(\'name\', b.name, \'level\', b.level, \'value\', b.value, '
        '\'timestamp\', b.timestamp)) FROM badges b WHERE collection = {}collection) AS badges '.format(prefix)
    )


def _get_tags_object(prefix='a.'):
    return (
        '(SELECT array_agg(json_build_object(\'tag_id\', tg.tag_id, \'tag_name\', tg.tag_name)) '
        'FROM tags_mv tg WHERE collection = {}collection) AS tags '.format(prefix)
    )


def _get_attributes_object():
    return (
        '(SELECT array_agg(json_build_object(\'attribute_id\', attribute_id, '
        '\'attribute_name\', attribute_name, \'string_value\', string_value, \'int_value\', int_value, '
        '\'float_value\', float_value, \'bool_value\', bool_value, \'floor_price\', floor_wax, '
        '\'rarity_score\', rarity_score, \'total_schema\', total_schema)) '
        'FROM assets '
        'INNER JOIN attributes ON attribute_id = ANY(attribute_ids) '
        'LEFT JOIN attribute_stats USING(attribute_id) '
        'WHERE asset_id = a.asset_id) '
    )


def _get_template_attributes_object():
    return (
        '(SELECT array_agg(json_build_object(\'attribute_id\', attribute_id, '
        '\'attribute_name\', attribute_name, \'string_value\', string_value, \'int_value\', int_value, '
        '\'float_value\', float_value, \'bool_value\', bool_value, \'floor_price\', floor_wax, '
        '\'rarity_score\', rarity_score, \'total_schema\', total_schema)) '
        'FROM templates '
        'INNER JOIN attributes ON attribute_id = ANY(attribute_ids) '
        'LEFT JOIN attribute_stats USING(attribute_id) '
        'WHERE template_id = t.template_id) '
    )


def isfloat(value):
    try:
        float(value)
        return True
    except ValueError:
        return False


def construct_category_clause(
    session, format_dict, collection, schema, attributes, prefix
):
    category_clause = ''

    attribute_ids = []
    if attributes:
        attr_arr = attributes.split(',')
        for attr in attr_arr:
            key = attr.split(':')[0]
            value = attr.split(':')[1]
            attr_sql = 'SELECT attribute_id FROM attributes WHERE collection = :collection '

            attr_dict = {
                'collection': collection
            }

            if schema:
                if ',' in schema:
                    attr_dict['schemas'] = tuple(schema.split(','))
                    attr_sql += ' AND schema IN :schemas'
                else:
                    attr_dict['schema'] = schema
                    attr_sql += ' AND schema = :schema'

            attr_dict['attribute_name'] = key

            if isinstance(value, bool) or value in ['f', 't']:
                column = 'bool_value'
            elif isinstance(value, int) or value.isnumeric():
                column = 'int_value'
                value = int(value)
                if value > 9223372036854775807 or value < -9223372036854775808:
                    value = str(value)
                    column = 'string_value'
            elif isinstance(value, float) or isfloat(value):
                column = 'float_value'
                value = float(value)
            else:
                column = 'string_value'

            attr_sql += ' AND attribute_name = :attribute_name AND {column} = :value '.format(column=column)

            attr_dict['value'] = value

            res = session.execute(attr_sql, attr_dict)

            for attribute_id in res:
                attribute_ids.append(attribute_id['attribute_id'])

    if len(attribute_ids) > 1:
        category_clause += ' AND :attribute_ids <@ {}attribute_ids '.format(prefix)
        format_dict['attribute_ids'] = attribute_ids
    elif len(attribute_ids) == 1:
        category_clause += ' AND :attribute_id = ANY({}attribute_ids) '.format(prefix)
        format_dict['attribute_id'] = attribute_ids[0]
    elif attributes and len(attribute_ids) == 0:
        category_clause += ' AND FALSE '

    return category_clause


def _format_date(date):
    return datetime.datetime.strptime(date, '%Y-%m-%dT%H:%M:%S' + ('.%f' if '.' in date else '')).strftime(
        DATE_FORMAT_STRING) if isinstance(date, str) else date.strftime(DATE_FORMAT_STRING)


def _format_tags(tags):
    tags_arr = []
    for tag in tags:
        if tag['tag_id']:
            tags_arr.append({
                'tagId': tag['tag_id'],
                'name': tag['tag_name']
            })
    return tags_arr


def _format_badges(badges):
    badge_arr = []
    for badge in badges:
        if badge['name']:
            badge_arr.append({
                'name': badge['name'],
                'level': badge['level'],
                'value': badge['value'],
                'timestamp': datetime.datetime.strptime(
                    badge['timestamp'].split('.')[0], DATE_FROM_STRING_SPLIT_FORMAT
                ).strftime(DATE_FORMAT_STRING) if badge['timestamp'] else None
            })
    return badge_arr


def _format_traits(traits):
    traits_arr = []
    for trait in traits:
        if trait['attribute_name']:
            trait_obj = {
                'name': trait['attribute_name']
            }
            if trait['rarity_score']:
                trait_obj['rarityScore'] = trait['rarity_score']
            if trait['total_schema']:
                trait_obj['totalSchema'] = trait['total_schema']
            if trait['floor_price']:
                trait_obj['floorPrice'] = trait['floor_price']
            if trait['string_value']:
                trait_obj['value'] = trait['string_value']
            elif trait['int_value'] or trait['int_value'] == 0:
                trait_obj['value'] = trait['int_value']
            elif trait['float_value'] or trait['float_value'] == 0.0:
                trait_obj['value'] = trait['float_value']
            else:
                trait_obj['value'] = trait['bool_value']
            traits_arr.append(trait_obj)
    return traits_arr


def _format_asset(asset):
    try:
        asset_obj = {
            'assetId': asset['asset_id'],
            'name': asset['name'],
            'schema': asset['schema'],
            'owner': asset['owner'],
            'burned': asset['burned'],
            'mint': asset['mint'],
            'collection': asset['collection'],
            'mutableData': json.loads(asset['mutable_data']) if asset['mutable_data'] else '{}',
            'immutableData': json.loads(asset['immutable_data']) if asset['immutable_data'] else '{}',
            'createdAt': {
                'date': _format_date(asset['mint_timestamp']),
                'block': asset['mint_block_num'],
                'globalSequence': asset['mint_seq'],
            },
            'traits': _format_traits(asset['traits']) if asset['traits'] else [],
        }
        if 'display_name' in asset.keys():
            asset_obj['collection'] = {
                'collectionName': asset['collection'],
                'displayName': asset['display_name'],
                'collectionImage': asset['collection_image'],
                'tags': _format_tags(asset['tags']) if asset['tags'] else [],
                'badges': _format_badges(asset['badges']) if asset['badges'] else []
            }
        if asset['rarity_score']:
            asset_obj['rarityScore'] = asset['rarity_score']
            asset_obj['rank'] = asset['rank']
            asset_obj['numTraits'] = asset['num_traits']
        if 'rwax_symbol' in asset.keys() and asset['rwax_symbol']:
            asset_obj['rwax'] = {
                'symbol': asset['rwax_symbol'],
                'contract': asset['rwax_contract'],
                'decimals': asset['rwax_decimals'],
                'tokenName': asset['rwax_token_name'],
                'tokenLogo': asset['rwax_token_logo'],
                'tokenLogoLarge': asset['rwax_token_logo_lg'],
                'templateMaxAssets': asset['rwax_max_assets'],
                'templateSupply': asset['template_token_supply'],
                'totalSupply': asset['rwax_supply']
            }
        if asset['video']:
            asset_obj['video'] = asset['video']
        if asset['image']:
            asset_obj['image'] = asset['image']
        if 'template_id' in asset.keys() and asset['template_id']:
            stats_obj = {}
            if asset['avg_wax_price'] and asset['avg_usd_price']:
                stats_obj['averageWaxPrice'] = asset['avg_wax_price']
                stats_obj['averageUsd'] = asset['avg_usd_price']
            if asset['last_sold_wax'] and asset['last_sold_usd']:
                stats_obj['lastSoldWax'] = asset['last_sold_wax']
                stats_obj['lastSoldUsd'] = asset['last_sold_usd']
            if asset['last_sold_timestamp'] and asset['last_sold_listing_id'] and asset['last_sold_wax'] and asset[
                    'last_sold_usd']:
                stats_obj['lastSold'] = {
                    'date': _format_date(asset['last_sold_timestamp']),
                    'listingId': asset['last_sold_listing_id'],
                    'priceWax': asset['last_sold_wax'],
                    'priceUsd': asset['last_sold_usd']
                }
            if asset['volume_wax'] and asset['volume_usd']:
                stats_obj['volumeWax'] = asset['volume_wax']
                stats_obj['volumeUsd'] = asset['volume_usd']
            if asset['num_sales']:
                stats_obj['numSales'] = asset['num_sales']
            if asset['num_burned']:
                stats_obj['numBurned'] = asset['num_burned']
            if asset['num_minted']:
                stats_obj['numMinted'] = asset['num_minted']
            if asset['floor_price']:
                stats_obj['floorPrice'] = asset['floor_price']
            asset_obj['template'] = {
                'templateId': asset['template_id'],
                'immutableData': asset['template_immutable_data'],
                'stats': stats_obj,
            }
        return asset_obj
    except Exception as e:
        print(e)


def _format_schema(schema):
    asset_obj = {
        'schema': schema['schema'],
        'stats': {
            'numTemplates': schema['num_templates'],
            'numAssets': schema['num_minted'],
            'numBurned': schema['num_burned'],
            'volumeWAX': schema['volume_wax'],
            'volumeUSD': schema['volume_usd'],
        },
        'collection': {
            'collectionName': schema['collection'],
            'displayName': schema['display_name'],
            'collectionImage': schema['collection_image'],
            'tags': _format_tags(schema['tags']) if schema['tags'] else [],
            'badges': _format_badges(schema['badges']) if schema['badges'] else [],
            'verification': schema['verified']
        },
        'createdAt': {
            'date': schema['created_timestamp'].strftime(DATE_FORMAT_STRING),
            'block': schema['created_block_num'],
            'globalSequence': schema['created_seq'],
        }
    }
    return asset_obj


def _format_assets_object(items):
    assets = []

    for asset in items:
        assets.append(_format_asset(asset))

    return assets


def _format_listings(item):
    return {
        'date': item['timestamp'].strftime(DATE_FORMAT_STRING),
        'timestamp': datetime.datetime.timestamp(item['timestamp']), 'price': item['price'],
        'usdWax': item['usd_wax'], 'currency': item['currency'], 'market': item['market'],
        'maker': item['maker'], 'seller': item['seller'], 'listingId': item['listing_id'],
        'uniqueSaleId': item['sale_id'],
        'collection': {
            'collectionName': item['collection'],
            'displayName': item['display_name'],
            'collectionImage': item['collection_image'],
            'verification': item['verified']
        },
        'assets': _format_assets_object(item['assets'])
    }


def _get_search_term(session, term):
    template_id = None
    asset_id = None
    name = None
    collection = None
    if (isinstance(term, int) or (isinstance(term, str) and term.isnumeric())) and int(term) < 1099511627776:
        template = session.execute(
            'SELECT template_id, collection FROM templates WHERE template_id = :term', {
                'term': term
            }
        ).first()
        if template:
            template_id = template['template_id']
            collection = template['collection']
    elif (isinstance(term, int) or (isinstance(term, str) and term.isnumeric())) and int(term) >= 1099511627776:
        asset = session.execute(
            'SELECT asset_id, collection FROM assets WHERE asset_id = :term', {
                'term': term
            }
        ).first()
        if asset:
            asset_id = asset['asset_id']
            collection = asset['collection']
    else:
        name = term

    return name, asset_id, template_id, collection


def _add_mint_filter(min_mint, max_mint, search_clause, format_dict):
    if min_mint and max_mint:
        search_clause += (
            'AND a.mint BETWEEN :min_mint AND :max_mint '
        )
        format_dict['min_mint'] = min_mint
        format_dict['max_mint'] = max_mint
    elif min_mint:
        search_clause += (
            'AND a.mint >= :min_mint '
        )
        format_dict['min_mint'] = min_mint
    elif max_mint:
        search_clause += (
            'AND a.mint >= :max_mint '
        )
        format_dict['max_mint'] = max_mint
    return search_clause


def _add_recently_sold_filter(recently_sold, search_clause):
    if recently_sold:
        table = 'recently_sold_month_mv'
        if recently_sold == 'hour':
            table = 'recently_sold_hour_mv'
        elif recently_sold == 'day':
            table = 'recently_sold_day_mv'
        elif recently_sold == 'week':
            table = 'recently_sold_week_mv'

        search_clause += (
            ' AND a.template_id IN ('
            '   SELECT template_id FROM {table} WHERE template_id = a.template_id'
            ') '.format(table=table)
        )
    return search_clause


def parallel(requests):
    """Execute requests in parallel.

    Provided a dict of requests, execute them with the provided id and kwargs.
    Return the results of these requests in a dict keyed by keys in the
    requests parameter.
    """
    futures = {
        executor.submit(
            request['func'],
            *request['args']
        ): key for (key, request) in requests.items()
    }
    concurrent.futures.wait(futures)
    output = dict(map(lambda f: (futures[f], f.result()), futures))

    # Format the responses for errors, return as oto response
    return output


def newest_listings(collection, schema, template_id):
    global last_reported_order

    try:
        sales_results = listings(
            term=template_id, category=schema, collection=collection,
            order_by='date_desc', limit=24, search_type='sales'
        )

        sales = []

        max_order = 0

        has_new_element = False
        for sale in sales_results:
            new_sale = {}

            for key in sale.keys():
                if key != 'displayData':
                    if sale[key]:
                        new_sale[key] = sale[key].replace('\'', '') if isinstance(sale[key], str) else sale[key]

            if new_sale['verified']:
                new_sale['verified'] = 1
            new_sale.pop('mdata', None)

            sales.append(new_sale)

            if new_sale['orderId'] > max_order:
                max_order = new_sale['orderId']

            if template_id not in last_reported_order.keys():
                last_reported_order[template_id] = 0

            if max_order > last_reported_order[template_id]:
                last_reported_order[template_id] = max_order
                has_new_element = True

        return {'hasNewElement': 1 if has_new_element else 0, 'elements': sales}
    except Exception as e:
        print(e)
        return {'hasNewElement': 0, 'elements': []}


def _parse_order(order_by):
    order_dir = 'ASC'

    if '_asc' in order_by:
        order_dir = 'ASC'
        order_by = order_by.replace('_asc', '')
    elif '_desc' in order_by:
        order_dir = 'DESC'
        order_by = order_by.replace('_desc', '')

    return order_dir, order_by


def schemas(
    term=None, collection=None, schema=None, limit=100, order_by='name_asc', exact_search=False, offset=0,
    verified='verified'
):
    session = create_session()

    order_dir, order_by = _parse_order(order_by)

    try:
        format_dict = {'limit': limit, 'offset': offset}

        limit_clause = 'LIMIT :limit OFFSET :offset'

        search_clause = ''
        order_clause = ''
        personal_blacklist_clause = ''
        search_category_clause = ''

        if collection:
            format_dict['collection'] = collection

            search_category_clause += ' AND a.collection = :collection '

            if schema:
                format_dict['schema'] = schema
                search_category_clause += ' AND a.schema = :schema '
            search_clause += search_category_clause

        if term:
            if exact_search:
                search_clause += (
                    ' AND n.name = :search_name '
                )
                format_dict['search_name'] = '{}'.format(term)
            else:
                search_clause += (
                    ' AND n.name LIKE :search_name '
                )
                format_dict['search_name'] = '%{}%'.format(term)

        source_clause = (
            'schemas a '
        )

        columns_clause = (
            'a.schema, cn.name AS display_name, a.collection, col.verified, schema_format, {badges_object}, {tags_obj}, '
            'ci.image as collection_image, a.timestamp AS created_timestamp, a.block_num AS created_block_num, '
            'a.seq AS created_seq, ts.num_minted, ts.num_templates, ts.num_burned, ts.volume_wax, '
            'ts.volume_usd, (SELECT MIN(floor_price) '
            '   FROM templates t '
            '   INNER JOIN floor_prices_mv USING(template_id) '
            '   WHERE t.collection = a.collection AND t.schema = a.schema'
            ') AS floor_price'.format(
                badges_object=_get_badges_object(), tags_obj=_get_tags_object()
            )
        )

        if verified == 'verified':
            search_clause += ' AND col.verified '
        elif verified == 'unverified':
            search_clause += (
                ' AND ('
                '   (col.verified IS NULL AND col.blacklisted IS NULL) OR (NOT col.verified AND NOT col.blacklisted)'
                ') '
            )
        elif verified == 'all':
            search_clause += ' AND (NOT col.blacklisted OR col.blacklisted IS NULL) '
        elif verified == 'blacklisted':
            search_clause += ' AND col.blacklisted '

        if order_by == 'date':
            order_clause = 'ORDER BY a.seq {}'.format(order_dir)
        elif order_by == 'collection':
            order_clause = (
                'ORDER BY a.collection {}'
            ).format(order_dir)
        elif order_by == 'num_templates':
            order_clause = 'ORDER BY num_templates ' + order_dir
        elif order_by == 'num_assets':
            order_clause = 'ORDER BY num_assets ' + order_dir
        elif order_by == 'volume':
            order_clause = 'ORDER BY volume_wax ' + order_dir

        sql = (
            '   SELECT {columns_clause} '
            '   FROM {source_clause} '
            '   LEFT JOIN collections col USING (collection) '
            '   LEFT JOIN schema_stats_mv ts USING (collection, schema) '
            '   LEFT JOIN names cn ON (col.name_id = cn.name_id) '
            '   LEFT JOIN images ci ON (col.image_id = ci.image_id) '
            '   WHERE TRUE {search_clause} '
            '   {personal_blacklist_clause} '
            '   {order_clause} {limit_clause}'.format(
                columns_clause=columns_clause,
                source_clause=source_clause,
                search_clause=search_clause,
                order_clause=order_clause,
                limit_clause=limit_clause,
                personal_blacklist_clause=personal_blacklist_clause
            ))

        res = session.execute(sql, format_dict)

        results = []

        for row in res:
            try:
                result = _format_schema(row)

                results.append(result)
            except Exception as e:
                logging.error(e)

        return results
    except SQLAlchemyError as e:
        logging.error(e)
        session.rollback()
        raise e
    finally:
        session.remove()


def get_health():
    session = create_session()
    try:
        result = session.execute(
            'SELECT block_num, timestamp '
            'FROM chronicle_transactions '
            'WHERE seq = (SELECT MAX(seq) FROM chronicle_transactions)'
        ).first()

        if result:
            return {
                'success': 'true',
                'block_num': result['block_num'],
                'timestamp': result['timestamp'].strftime("%Y-%m-%d %H:%M:%S")
            }

        return {
            'success': 'false'
        }
    except SQLAlchemyError as e:
        logging.error(e)
        session.rollback()
        raise e
    finally:
        session.remove()


def filter_attributes(collection, schema=None, templates=None):
    session = create_session()

    search_dict = {
        'collection': collection
    }

    schema_clause = ''
    if schema:
        schema_clause += ' AND a.schema = :schema'
        search_dict['schema'] = schema

    if templates:
        search_dict['templates'] = tuple(templates.split(','))
        res = session.execute(
            'SELECT attribute_name, string_value, MIN(int_value) AS min_int_value, MAX(int_value) AS max_int_value, '
            'MIN(float_value) AS min_float_value, MAX(float_value) AS max_float_value, bool_value '
            'FROM assets a '
            'INNER JOIN attributes att ON attribute_id = ANY(attribute_ids) '
            'WHERE a.collection = :collection '
            '{schema_clause} '
            'AND template_id IN :templates '
            'GROUP BY 1, 2, 7 '
            'ORDER BY attribute_name ASC, string_value ASC'.format(
                schema_clause=schema_clause
            ),
            search_dict
        )
    else:
        res = session.execute(
            'SELECT attribute_name, string_value, MIN(int_value) AS min_int_value, MAX(int_value) AS max_int_value, '
            'MIN(float_value) AS min_float_value, MAX(float_value) AS max_float_value, bool_value '
            'FROM attributes a '
            'WHERE collection = :collection '
            '{schema_clause} '
            'GROUP BY 1, 2, 7 '
            'ORDER BY attribute_name ASC, string_value ASC'.format(
                schema_clause=schema_clause
            ),
            search_dict
        )

    attributes = {}

    for attribute in res:
        value = attribute['string_value']

        attribute_type = None
        min_value = 0
        max_value = 0

        if value:
            attribute_type = 'string'
        else:
            min_value = attribute['min_int_value']
            max_value = attribute['max_int_value']
            if min_value or max_value or max_value == 0:
                attribute_type = 'integer'
            else:
                min_value = attribute['min_float_value']
                max_value = attribute['max_float_value']
                if min_value or max_value or max_value == 0.0:
                    attribute_type = 'float'
        if not attribute_type:
            value = attribute['bool_value']
            attribute_type = 'boolean'

        if value and attribute_type in ['string', 'boolean']:
            if attribute['attribute_name'] in attributes.keys():
                attributes[attribute['attribute_name']]['values'].append(value)
            else:
                attributes[attribute['attribute_name']] = {
                    'values': [value],
                    'type': attribute_type
                }
        elif attribute_type in ['float', 'integer']:
            attributes[attribute['attribute_name']] = {
                'minValue': min_value,
                'maxValue': max_value,
                'type': attribute_type
            }

    return attributes


def collection_filters(collection):
    session = create_session()

    search_dict = {
        'collection': collection
    }

    res = session.execute(
        'SELECT attribute_name, string_value, MIN(int_value) AS min_int_value, MAX(int_value) AS max_int_value, '
        'MIN(float_value) AS min_float_value, MAX(float_value) AS max_float_value, bool_value '
        'FROM attributes a '
        'WHERE collection = :collection '
        'GROUP BY 1, 2, 7 '
        'ORDER BY attribute_name ASC, string_value ASC',
        search_dict
    )

    attributes = {}

    for attribute in res:
        value = attribute['string_value']

        attribute_type = None

        if value:
            attribute_type = 'string'
        else:
            min_value = attribute['min_int_value']
            max_value = attribute['max_int_value']
            if min_value or max_value or max_value == 0:
                attribute_type = 'integer'
            else:
                min_value = attribute['min_float_value']
                max_value = attribute['max_float_value']
                if min_value or max_value or max_value == 0.0:
                    value = attribute['float_value']
                    attribute_type = 'float'
        if not attribute_type:
            value = attribute['bool_value']
            attribute_type = 'boolean'

        if value and attribute_type in ['string', 'boolean']:
            if attribute['attribute_name'] in attributes.keys():
                attributes[attribute['attribute_name']]['values'].append(value)
            else:
                attributes[attribute['attribute_name']] = {
                    'values': [value],
                    'type': attribute_type
                }
        elif attribute_type in ['float', 'integer']:
            attributes[attribute['attribute_name']] = {
                'minValue': min_value,
                'maxValue': max_value,
                'type': attribute_type
            }

    return attributes


def assets(
    term=None, owner=None, collection=None, schema=None, tags=None, limit=100, order_by='date_desc',
    exact_search=False, search_type='assets', min_average=None, max_average=None, min_mint=None, max_mint=None,
    contract=None, offset=0, verified='verified', user='', favorites=False, backed=False, recently_sold=None,
    attributes=None
):
    session = create_session()

    name, asset_id, template_id, col = _get_search_term(session, term)

    if not collection:
        collection = col

    order_dir, order_by = _parse_order(order_by)

    if (isinstance(term, int) or (isinstance(term, str) and term.isnumeric())) and int(term) < 10000000000000:
        template = session.execute('SELECT template_id FROM templates WHERE template_id = :term', {
            'term': term
        }).first()
        if template:
            template_id = template['template_id']
    elif (isinstance(term, int) or (isinstance(term, str) and term.isnumeric())) and int(term) >= 10000000000000:
        asset = session.execute('SELECT asset_id FROM assets WHERE asset_id = :term', {
            'term': term
        }).first()
        if asset:
            asset_id = asset['asset_id']
    else:
        name = term

    try:
        format_dict = {'user': user, 'limit': limit, 'offset': offset}

        limit_clause = 'LIMIT :limit OFFSET :offset'

        join_clause = (
            'LEFT JOIN favorites f ON ((f.asset_id = a.asset_id OR f.template_id = a.template_id) '
            'AND f.user_name = :user) '
        ) if user else (
            'LEFT JOIN favorites f ON (f.asset_id IS NULL AND f.user_name IS NULL) '
        )

        search_clause = ''
        order_clause = ''
        with_clause = ''
        personal_blacklist_clause = ''
        search_category_clause = ''

        if collection:
            format_dict['collection'] = collection

            search_category_clause += ' AND a.collection = :collection '

            if schema:
                format_dict['schema'] = schema
                search_category_clause += ' AND a.schema = :schema '
                search_category_clause += construct_category_clause(
                    session, format_dict, collection, schema, attributes, 'a.'
                )
            search_clause += search_category_clause

        if name:
            if exact_search:
                search_clause += (
                    ' AND n.name = :search_name '
                )
                format_dict['search_name'] = '{}'.format(name)
            else:
                search_clause += (
                    ' AND n.name LIKE :search_name '
                )
                format_dict['search_name'] = '%{}%'.format(name)

        if asset_id:
            format_dict['asset_id'] = '{}'.format(asset_id)
            search_clause += ' AND a.asset_id = :asset_id '

        if template_id:
            format_dict['template_id'] = template_id
            search_clause += (
                ' AND a.template_id = :template_id '
            )

        source_clause = (
            'assets a '
        )
        columns_clause = (
            'a.asset_id, a.template_id, n.name, a.schema, f.user_name IS NOT NULL AS favorited, a.owner, a.burned, '
            'm.data AS mutable_data, i.data AS immutable_data, td.data AS template_immutable_data, tm.num_burned, '
            'a.mint, ts.avg_wax_price, ts.avg_usd_price, ts.last_sold_wax, ts.last_sold_usd, last_sold_listing_id, '
            'ts.last_sold_timestamp AS last_sold_timestamp, fp.floor_price, ts.volume_wax, '
            'ts.volume_usd, ts.num_sales, tm.num_minted AS num_minted, t.template_id, img.image, vid.video, '
            'cn.name AS display_name, a.collection, ci.image as collection_image, a.timestamp AS mint_timestamp, '
            'a.block_num AS mint_block_num, a.seq AS mint_seq, p.rarity_score, p.num_traits, p.rank, '
            'r.symbol AS rwax_symbol, r.contract AS rwax_contract, r.max_assets AS rwax_max_assets, rt.trait_factors, '
            'rt.maximum_supply AS rwax_supply, rt.decimals AS rwax_decimals, rt.token_name AS rwax_token_name, '
            'rt.token_logo AS rwax_token_logo, rt.token_logo_lg AS rwax_token_logo_lg, {badges_object}, {tags_obj}, '
            '{attributes_obj} AS traits'.format(
                badges_object=_get_badges_object(), tags_obj=_get_tags_object(), attributes_obj=_get_attributes_object()
            )
        )
        if search_type == 'packs':
            search_clause += (
                ' AND EXISTS (SELECT template_id FROM packs p WHERE template_id = a.template_id) '
            )
        if search_type == 'pfps':
            search_clause += (
                ' AND p.asset_id IS NOT NULL '
            )
        if search_type == 'rwax':
            search_clause += (
                ' AND ra.asset_id IS NOT NULL '
            )

        if verified == 'verified':
            search_clause += ' AND col.verified '
        elif verified == 'unverified':
            search_clause += (
                ' AND ((col.verified IS NULL AND col.blacklisted IS NULL) '
                '  OR (NOT col.verified AND NOT col.blacklisted))'
            )
        elif verified == 'all':
            search_clause += ' AND (NOT col.blacklisted OR col.blacklisted IS NULL) '
        elif verified == 'blacklisted':
            search_clause += ' AND col.blacklisted '

        if tags:
            tag_ids = tags.split(',')
            if len(tag_ids) == 1:
                search_clause += (
                    'AND EXISTS ('
                    '    SELECT tag_id FROM tags_mv '
                    '    WHERE collection = a.collection '
                    '    AND tag_id = :tag_id'
                    ') '
                )
                format_dict['tag_id'] = tag_ids[0]
            else:
                tag_int_arr = []
                for tag_id in tag_ids:
                    tag_int_arr.append(int(tag_id))
                with_clause += (
                    ', matched_collections AS ('
                    '    SELECT collection FROM collection_tag_ids_mv '
                    '    WHERE :tag_ids <@ tag_ids'
                    ')'
                )
                source_clause += (
                    'INNER JOIN matched_collections USING(collection) '
                )
                format_dict['tag_ids'] = tag_int_arr

        search_clause = _add_mint_filter(min_mint, max_mint, search_clause, format_dict)
        search_clause = _add_recently_sold_filter(recently_sold, search_clause)

        if contract:
            format_dict['contract'] = contract
            search_clause += ' AND a.contract = :contract'
        if favorites:
            search_clause += ' AND f.user_name IS NOT NULL'
        if backed:
            search_clause += ' AND ba.amount IS NOT NULL '
        if owner:
            format_dict['owner'] = '{}'.format(owner.lower().strip())
            if search_type == 'duplicates' or search_type == 'highest_duplicates':
                source_clause = (
                    'my_assets a '
                )
                with_clause += (
                    ', my_assets AS (SELECT a.*, COUNT(*) OVER ('
                    'PARTITION BY a.collection, a.template_id) cnt, MIN(a.asset_id) OVER ('
                    'PARTITION BY a.collection, a.template_id) AS min_mint, MAX(a.asset_id) OVER ('
                    'PARTITION BY a.collection, a.template_id) AS max_mint '
                    'FROM assets a '
                    '{personal_blacklist_clause} '
                    'WHERE owner = :owner AND NOT burned '
                    '{search_clause}) '.format(
                        search_clause=search_clause,
                        personal_blacklist_clause=personal_blacklist_clause
                    )
                )
                if search_type == 'duplicates':
                    search_clause += ' AND cnt > 1 AND a.asset_id > min_mint'
                else:
                    search_clause += ' AND cnt > 1 AND a.asset_id = max_mint'
            elif search_type == 'lowest_mints' or search_type == 'highest_mints':
                source_clause = ' my_assets a '
                with_clause += (
                    ', my_assets AS (SELECT a.*, '
                    'MIN(a.asset_id) OVER (PARTITION BY a.template_id) AS min_mint, '
                    'MAX(a.asset_id) OVER (PARTITION BY a.template_id) AS max_mint '
                    'FROM assets a '
                    '{personal_blacklist_clause} '
                    'WHERE owner = :owner AND a.mint > 0 '
                    '{search_clause}) '.format(
                        search_clause=search_clause,
                        personal_blacklist_clause=personal_blacklist_clause
                    )
                )
                if search_type == 'lowest_mints':
                    search_clause += ' AND a.asset_id = min_mint'
                else:
                    search_clause += ' AND a.asset_id = max_mint'
            else:
                search_clause += ' AND a.owner = :owner '
        if order_by == 'rarity_score' and search_type == 'pfps':
            order_clause = 'ORDER BY p.collection, p.schema, p.rarity_score {}'.format(order_dir)
        elif order_by == 'rarity_score':
            order_clause = 'ORDER BY a.collection, a.schema, p.rarity_score {}'.format(order_dir)
            search_clause += ' AND p.rarity_score IS NOT NULL '
        elif order_by == 'date' and search_type == 'bulk_multi_sell':
            order_clause = 'ORDER BY MAX(a.transferred) {}'.format(order_dir)
        elif order_by == 'owned' and search_type == 'bulk_multi_sell':
            order_clause = 'ORDER BY num_owned {}'.format(order_dir)
        elif order_by == 'date' and search_type == 'staked':
            order_clause = 'ORDER BY s.seq {}'.format(order_dir)
        elif order_by == 'date' and search_type == 'summaries':
            order_clause = 'ORDER BY a.template_id {}'.format(order_dir)
        elif order_by == 'date':
            order_clause = 'ORDER BY a.seq {}'.format(order_dir)
        elif order_by == 'volume' and search_type == 'summaries':
            order_clause = 'ORDER BY tsv.volume_7_days {} NULLS LAST'.format(order_dir)
        elif order_by == 'mint':
            search_clause += ' AND (a.mint IS NOT NULL AND a.mint > 0)'
            if search_type != 'bundles':
                order_clause = 'ORDER BY a1.mint {}'.format(order_dir)
        elif order_by == 'diff':
            search_clause += ' AND lp.price_diff IS NOT NULL '
            if search_type != 'bundles':
                order_clause = 'ORDER BY lp.price_diff {}'.format(order_dir)
        elif order_by == 'template_id':
            search_clause += ' AND a.template_id IS NOT NULL '
            order_clause = (
                'ORDER BY a.template_id {}'
            ).format(order_dir)
        elif order_by == 'collection':
            search_clause += ' AND a.collection IS NOT NULL '
            order_clause = (
                'ORDER BY a.collection {}'
            ).format(order_dir)
        elif order_by == 'average':
            search_clause += ' AND ts.usd_average IS NOT NULL '
            order_clause = (
                'ORDER BY ts.usd_average {}'
            ).format(order_dir)
        elif order_by == 'floor':
            search_clause += ' AND fp.floor_price IS NOT NULL '
            order_clause = (
                'ORDER BY fp.floor_price {}'
            ).format(order_dir)
        elif order_by == 'asset_id':
            order_clause = 'ORDER BY a.asset_id ' + order_dir

        if min_average and max_average:
            search_clause += (
                ' AND ts.usd_average BETWEEN :min_average AND :max_average '
            )
            format_dict['min_average'] = min_average
            format_dict['max_average'] = max_average
        elif min_average:
            search_clause += ' AND ts.usd_average >= :min_average '
            format_dict['min_average'] = min_average
        elif max_average:
            search_clause += ' AND ts.usd_average <= :max_average '
            format_dict['max_average'] = max_average

        sql = (
            'WITH usd_rate AS (SELECT usd FROM usd_prices ORDER BY timestamp DESC LIMIT 1) '
            '{with_clause} '
            'SELECT {columns_clause}, f.user_name IS NOT NULL AS favorited '
            'FROM {source_clause} '
            'LEFT JOIN backed_assets ba USING (asset_id) ' 
            'LEFT JOIN collections col ON a.collection = col.collection '
            'LEFT JOIN pfp_assets p USING(asset_id) '
            'LEFT JOIN rwax_assets ra USING(asset_id) '
            'LEFT JOIN rwax_templates r ON (a.template_id = r.template_id) '
            'LEFT JOIN rwax_tokens rt ON (r.contract = rt.contract AND r.symbol = rt.symbol) '
            'LEFT JOIN templates t ON (t.template_id = a.template_id) '
            'LEFT JOIN template_stats_mv ts ON (a.template_id = ts.template_id) '
            'LEFT JOIN templates_minted_mv tm ON (a.template_id = tm.template_id) '
            'LEFT JOIN template_floor_prices_mv fp ON (fp.template_id = a.template_id) '
            'LEFT JOIN names n ON (a.name_id = n.name_id) '
            'LEFT JOIN names tn ON (t.name_id = tn.name_id) '
            'LEFT JOIN names cn ON (col.name_id = cn.name_id) '
            'LEFT JOIN images img ON (a.image_id = img.image_id) '
            'LEFT JOIN images ci ON (col.image_id = ci.image_id) '
            'LEFT JOIN videos vid ON (a.video_id = vid.video_id) '
            'LEFT JOIN data m ON (a.mutable_data_id = m.data_id) '
            'LEFT JOIN data i ON (a.immutable_data_id = i.data_id) '
            'LEFT JOIN data td ON (t.immutable_data_id = td.data_id) '
            '{join_clause} '
            'WHERE TRUE {search_clause} '
            '{personal_blacklist_clause} '
            '{order_clause} {limit_clause}'.format(
                with_clause=with_clause.format(
                    search_clause=search_clause,
                    limit_clause=limit_clause,
                    order_clause=order_clause,
                    columns_clause=columns_clause
                ),
                columns_clause=columns_clause,
                source_clause=source_clause,
                search_clause=search_clause,
                order_clause=order_clause,
                limit_clause=limit_clause,
                join_clause=join_clause,
                personal_blacklist_clause=personal_blacklist_clause
            ))

        print(sql)

        res = session.execute(sql, format_dict)

        results = []

        for row in res:
            try:
                results.append(_format_asset(row))
            except Exception as e:
                logging.error(e)

        return results
    except SQLAlchemyError as e:
        logging.error(e)
        session.rollback()
        raise e
    finally:
        session.remove()


def listings(
    term=None, owner=None, market=None, collection=None, schema=None, limit=100, order_by='name_asc',
    exact_search=False, search_type='listings', min_price=None, max_price=None,
    min_mint=None, max_mint=None, contract=None, offset=0,
    verified='verified', user='', favorites=False, backed=False, recently_sold=None,
    attributes=None, only=False
):
    session = create_session()

    name, asset_id, template_id, col = _get_search_term(session, term)

    if not collection:
        collection = col

    order_dir = 'ASC'

    if '_asc' in order_by:
        order_dir = 'ASC'
        order_by = order_by.replace('_asc', '')
    elif '_desc' in order_by:
        order_dir = 'DESC'
        order_by = order_by.replace('_desc', '')

    if (isinstance(term, int) or (isinstance(term, str) and term.isnumeric())) and int(term) < 1099511627776:
        template = session.execute('SELECT template_id FROM templates WHERE template_id = :term', {
            'term': term
        }).first()
        if template:
            template_id = template['template_id']
    elif (isinstance(term, int) or (isinstance(term, str) and term.isnumeric())) and int(term) >= 1099511627776:
        asset = session.execute('SELECT asset_id FROM assets WHERE asset_id = :term', {
            'term': term
        }).first()
        if asset:
            asset_id = asset['asset_id']
    else:
        name = term

    try:
        format_dict = {'user': user, 'limit': limit, 'offset': offset}

        if not user and search_type in ['missing']:
            return []

        limit_clause = 'LIMIT :limit OFFSET :offset'

        join_clause = (
            'LEFT JOIN favorites f ON ((f.asset_id = a.asset_id OR f.template_id = a.template_id) '
            'AND f.user_name = :user) '
        ) if user else (
            'LEFT JOIN favorites f ON (f.asset_id IS NULL AND f.user_name IS NULL) '
        )

        search_clause = ''
        order_clause = ''
        with_clause = ''
        personal_blacklist_clause = ''
        search_category_clause = ''

        if collection:
            format_dict['collection'] = collection

            search_category_clause += ' AND l.collection = :collection '

            if schema:
                format_dict['schema'] = schema
                search_category_clause += ' AND a.schema = :schema '
                search_category_clause += construct_category_clause(
                    session, format_dict, collection, schema, attributes, 'a.'
                )
            search_clause += search_category_clause

        if name:
            if exact_search:
                search_clause += (
                    ' AND n.name = :search_name '
                )
                format_dict['search_name'] = '{}'.format(name)
            else:
                search_clause += (
                    ' AND n.name LIKE :search_name '
                )
                format_dict['search_name'] = '%{}%'.format(name)

        if asset_id:
            format_dict['asset_id'] = '{}'.format(asset_id)
            search_clause += ' AND :asset_id = ANY(l.asset_ids) '

        if template_id:
            format_dict['template_id'] = template_id
            search_clause += (
                ' AND a.template_id = :template_id '
            )

        with_clause += (
            ', filtered_listings AS ('
            'SELECT l.sale_id, l.market, l.seller, l.timestamp, l.listing_id, l.currency, col.verified, '
            'l.maker, l.collection, l.price, l.collection, array_agg(asset_ids) AS assets '
            'FROM listings l '
            'LEFT JOIN listings_helper_mv h USING (sale_id) '
            'LEFT JOIN assets a ON (a.asset_id = asset_ids[1]) '
            'LEFT JOIN pfp_assets p USING(asset_id) '
            'LEFT JOIN rwax_assets ra USING (asset_id) '
            'LEFT JOIN backed_assets ba USING (asset_id) ' 
            'LEFT JOIN collections col ON (col.collection = l.collection) '
            'LEFT JOIN templates t ON (t.template_id = a.template_id) '
            'LEFT JOIN template_stats_mv ts ON (a.template_id = ts.template_id) '
            'LEFT JOIN templates_minted_mv tm ON (a.template_id = tm.template_id) '
            'LEFT JOIN template_floor_prices_mv fp ON (fp.template_id = a.template_id) '
            'LEFT JOIN names n ON (a.name_id = n.name_id) ' 
            'WHERE TRUE {search_clause} '
            'GROUP BY 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, estimated_wax_price '
            '{group_clause} {order_clause} {limit_clause}) '
        )

        source_clause = (
            'filtered_listings l2 '
            'INNER JOIN listings l USING (sale_id) '
            'LEFT JOIN listings_helper_mv h USING (sale_id) '
            'LEFT JOIN assets a ON (a.asset_id = ANY(asset_ids)) '
            'LEFT JOIN pfp_assets p USING (asset_id) '
            'LEFT JOIN rwax_assets ra USING (asset_id) '
            'LEFT JOIN backed_assets ba USING (asset_id) ' 
            'LEFT JOIN rwax_templates r ON (a.template_id = r.template_id) '
            'LEFT JOIN rwax_tokens rt ON (r.contract = rt.contract AND r.symbol = rt.symbol) '
            'LEFT JOIN collections col ON (col.collection = l.collection) '
            'LEFT JOIN templates t ON (t.template_id = a.template_id) '
            'LEFT JOIN template_stats_mv ts ON (a.template_id = ts.template_id) '
            'LEFT JOIN templates_minted_mv tm ON (a.template_id = tm.template_id) '
            'LEFT JOIN template_floor_prices_mv fp ON (fp.template_id = a.template_id) '
            'LEFT JOIN names n ON (a.name_id = n.name_id) '
            'LEFT JOIN names tn ON (t.name_id = tn.name_id) '
            'LEFT JOIN names cn ON (col.name_id = cn.name_id) '
            'LEFT JOIN images img ON (a.image_id = img.image_id) '
            'LEFT JOIN images ci ON (col.image_id = ci.image_id) '
            'LEFT JOIN videos vid ON (a.video_id = vid.video_id) '
            'LEFT JOIN data m ON (a.mutable_data_id = m.data_id) '
            'LEFT JOIN data i ON (a.immutable_data_id = i.data_id) '
            'LEFT JOIN data td ON (t.immutable_data_id = td.data_id) '
        )
        columns_clause = (
            'l.market, l.seller, l.timestamp AS timestamp, l.listing_id, l.currency, '
            'l.sale_id, col.verified, l.maker, l.collection, l.price, ci.image as collection_image, '
            'cn.name AS display_name, (SELECT usd FROM usd_prices ORDER BY timestamp DESC LIMIT 1) AS usd_wax, '
            '{badges_object}, {tags_obj}, {assets_object} '.format(
                badges_object=_get_badges_object('l.'),
                tags_obj=_get_tags_object('l.'),
                assets_object=_get_assets_object()
            )
        )
        group_clause = ' '
        if search_type == 'packs':
            search_clause += (
                ' AND EXISTS (SELECT template_id FROM packs p WHERE template_id = a.template_id) '
            )
        elif search_type == 'below_average':
            search_clause += (
                ' AND ts.avg_wax_price IS NOT NULL and l.estimated_wax_price < ts.avg_wax_price ')
        elif search_type == 'below_last_sold':
            search_clause += (
                ' AND ts.last_sold_wax IS NOT NULL and l.estimated_wax_price < ts.last_sold_wax ')
        elif search_type == 'floor':
            search_clause += (
                ' AND l.estimated_wax_price = fp.floor_price '
            )

        if verified == 'verified':
            search_clause += ' AND col.verified '
        elif verified == 'unverified':
            search_clause += (
                ' AND ((col.verified IS NULL AND col.blacklisted IS NULL)'
                '  OR (NOT col.verified AND NOT col.blacklisted))'
            )
        elif verified == 'all':
            search_clause += ' AND (NOT col.blacklisted OR col.blacklisted IS NULL) '
        elif verified == 'blacklisted':
            search_clause += ' AND col.blacklisted '

        search_clause = _add_mint_filter(min_mint, max_mint, search_clause, format_dict)
        search_clause = _add_recently_sold_filter(recently_sold, search_clause)

        if only == 'pfps':
            search_clause += (
                'AND p.asset_id IS NOT NULL '
            )
        elif only == 'rwax':
            search_clause += (
                'AND ra.asset_id IS NOT NULL '
            )

        if contract:
            format_dict['contract'] = contract
            search_clause += ' AND a.contract = :contract'

        if favorites:
            search_clause += ' AND f.user_name IS NOT NULL'

        if backed:
            search_clause += ' AND ba.amount IS NOT NULL '

        if min_price and max_price:
            search_clause += (
                ' AND estimated_wax_price BETWEEN :min_price AND :max_price '
            )
            format_dict['min_price'] = min_price
            format_dict['max_price'] = max_price
        elif min_price:
            search_clause += (
                ' AND estimated_wax_price >= :min_price '
            )
            format_dict['min_price'] = min_price
        elif max_price:
            search_clause += (
                ' AND estimated_wax_price <= :max_price '
            )
            format_dict['max_price'] = max_price
        if user:
            if search_type == 'bulk_buy':
                search_clause += ' AND l.seller != :user '
            elif search_type in ['missing', 'floor_missing']:
                with_clause = (
                    ', my_assets AS ( '
                    'SELECT template_id FROM '
                    '('
                    '   SELECT a.template_id FROM assets a WHERE NOT burned '
                    '   AND owner = :user AND a.template_id > 0 '
                    '   UNION '
                    '   SELECT a.template_id FROM listings l INNER JOIN assets a ON a.asset_id = l.asset_ids[1] '
                    '   WHERE seller = :user AND a.template_id > 0 ' 
                    '   UNION '
                    '   SELECT a.template_id FROM stakes rs '
                    '   INNER JOIN assets a USING(asset_id) '
                    '   WHERE staker = :user AND NOT burned AND a.template_id > 0'
                    ') a '
                    'GROUP BY 1) '
                    ', filtered_listings AS ('
                    'SELECT l.sale_id, l.market, l.seller, l.timestamp, l.listing_id, l.currency, col.verified, '
                    'l.maker, l.collection, l.price, l.collection, array_agg(asset_ids) AS assets '
                    'FROM listings l '
                    'LEFT JOIN assets a ON (asset_id = asset_ids[1]) '
                    'LEFT JOIN my_assets ma USING (template_id) '
                    'LEFT JOIN pfp_assets p ON (a.asset_id = p.asset_id) '
                    'LEFT JOIN rwax_assets ra ON (a.asset_id = ra.asset_id) '
                    'LEFT JOIN backed_assets ba ON (a.asset_id = ba.asset_id) '
                    'LEFT JOIN collections col ON (col.collection = l.collection) '
                    'LEFT JOIN templates t ON (t.template_id = a.template_id) '
                    'LEFT JOIN template_stats_mv ts ON (a.template_id = ts.template_id) '
                    'LEFT JOIN templates_minted_mv tm ON (a.template_id = tm.template_id) '
                    'LEFT JOIN template_floor_prices_mv fp ON (fp.template_id = a.template_id) '
                    'LEFT JOIN names n ON (a.name_id = n.name_id) '
                    'WHERE a.template_id > 0 AND ma.template_id IS NULL '
                    'GROUP BY 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, estimated_wax_price '
                    '{group_clause} {order_clause} {limit_clause}) '
                )

                source_clause += (
                    'LEFT JOIN my_assets ma ON a.template_id = ma.template_id '
                )
                source_clause += '{} JOIN listing_prices_mv lp USING(sale_id) '.format(
                    'INNER' if order_by in ['offer', 'diff'] else 'LEFT'
                )
                if search_type == 'floor_missing':
                    search_clause += ' AND fp.floor_price = estimated_wax_price '
            elif search_type == 'owned_lower_mints':
                with_clause = (
                    ', my_assets AS ( '
                    '    SELECT template_id, MIN(mint) AS mint FROM '
                    '    ('
                    '        SELECT a1.template_id, MIN(mint) AS mint FROM assets a1 '
                    '        WHERE owner = :user AND a1.template_id IS NOT NULL AND a1.mint IS NOT NULl '
                    '        AND NOT burned GROUP BY 1 '
                    '        UNION '
                    '        SELECT a2.template_id, MIN(a2.mint) AS mint FROM listings a1 '
                    '        INNER JOIN assets a2 ON asset_id = asset_ids[1] '
                    '        WHERE seller = :user AND a2.template_id IS NOT NULL AND a2.mint IS NOT NULL '
                    '        AND NOT burned GROUP BY 1 ' 
                    '        UNION '
                    '        SELECT a1.template_id, MIN(mint) AS mint FROM stakes rs '
                    '        INNER JOIN assets a1 USING(asset_id) '
                    '        WHERE staker = :user AND a1.template_id IS NOT NULL AND a1.mint IS NOT NULL '
                    '        AND NOT burned GROUP BY 1 '
                    '   ) a '
                    'GROUP BY 1 ORDER BY 1 ASC) '
                    ', filtered_listings AS ('
                    'SELECT l.sale_id, l.market, l.seller, l.timestamp, l.listing_id, l.currency, col.verified, '
                    'l.maker, l.collection, l.price, l.collection, array_agg(asset_ids) AS assets '
                    'FROM listings l '
                    'LEFT JOIN assets a ON (asset_id = asset_ids[1]) '
                    'LEFT JOIN my_assets ma USING (template_id) '
                    'LEFT JOIN pfp_assets p ON (a.asset_id = p.asset_id) '
                    'LEFT JOIN rwax_assets ra ON (a.asset_id = ra.asset_id) '
                    'LEFT JOIN backed_assets ba ON (a.asset_id = ba.asset_id) '
                    'LEFT JOIN collections col ON (col.collection = l.collection) '
                    'LEFT JOIN templates t ON (t.template_id = a.template_id) '
                    'LEFT JOIN template_stats_mv ts ON (a.template_id = ts.template_id) '
                    'LEFT JOIN templates_minted_mv tm ON (a.template_id = tm.template_id) '
                    'LEFT JOIN template_floor_prices_mv fp ON (fp.template_id = a.template_id) '
                    'LEFT JOIN names n ON (a.name_id = n.name_id) '
                    'WHERE a.mint < ma.mint {search_clause} '
                    'GROUP BY 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, estimated_wax_price '
                    '{group_clause} {order_clause} {limit_clause}) '
                )
        if market:
            format_dict['market'] = '{}'.format(market.lower().strip())
            search_clause += ' AND l.market = :market '
        if owner:
            format_dict['owner'] = '{}'.format(owner.lower().strip())
            if search_type == 'bulk_buy':
                search_clause += ' AND l.seller = :owner '
            elif search_type == 'my_exp_auctions':
                search_clause += ' AND a.owner = \'atomicmarket\' AND au.seller = :owner AND au.bidder IS NULL '
            elif search_type == 'my_auctions':
                search_clause += (
                    ' AND (a1.asset_id, a1.listing_id, a1.transaction_id) IN ('
                    '     SELECT asset_id, listing_id, transaction_id FROM auctions WHERE '
                    '     asset_id = a1.asset_id AND (bidder = :owner OR seller = :owner) '
                    ' ) '
                )
                search_clause += ' AND a1.mint = max_mint'
            else:
                search_clause += ' AND a1.seller = :search_owner '

        if order_by == 'rarity_score':
            order_clause = 'ORDER BY l.collection, h.schema, h.rarity_score {}'.format(order_dir)
            group_clause += ', l.collection, h.schema, h.rarity_score '
            search_clause += ' AND h.rarity_score IS NOT NULL '
        elif order_by == 'date':
            order_clause = 'ORDER BY l.seq {}'.format(order_dir)
            group_clause += ', l.seq '
        elif order_by == 'price':
            order_clause = 'ORDER BY estimated_wax_price {}'.format(order_dir)
            group_clause += ', estimated_wax_price '
        elif order_by == 'mint':
            group_clause += ', h.mint '
            search_clause += ' AND h.mint > 0 '
            order_clause = 'ORDER BY h.mint {}'.format(order_dir)
        elif order_by == 'template_id':
            search_clause += ' AND h.template_id IS NOT NULL '
            order_clause = (
                'ORDER BY h.template_id {}'
            ).format(order_dir)
            search_clause += ' AND h.template_id IS NOT NULL '
            group_clause += ', h.template_id '
        elif order_by == 'collection':
            order_clause = (
                'ORDER BY l.collection {}'
            ).format(order_dir)
        elif order_by == 'floor':
            search_clause += ' AND h.floor_price IS NOT NULL '
            order_clause = (
                'ORDER BY h.floor_price {}'
            ).format(order_dir)
            group_clause += ', h.floor_price '

        with_clause = with_clause.format(
            search_clause=search_clause,
            limit_clause=limit_clause,
            order_clause=order_clause,
            columns_clause=columns_clause,
            group_clause=group_clause
        )

        sql = (
            'WITH usd_rate AS (SELECT usd FROM usd_prices ORDER BY timestamp DESC LIMIT 1) '
            '{with_clause} '
            'SELECT {columns_clause}, f.user_name IS NOT NULL AS favorited '
            'FROM {source_clause} '
            '{join_clause} '
            '{personal_blacklist_clause} '
            'GROUP BY 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, l.timestamp, f.user_name {group_clause}'
            '{order_clause}'.format(
                with_clause=with_clause,
                columns_clause=columns_clause,
                source_clause=source_clause,
                group_clause=group_clause,
                order_clause=order_clause,
                limit_clause=limit_clause,
                join_clause=join_clause,
                personal_blacklist_clause=personal_blacklist_clause
            ))

        print(sql)
        res = session.execute(sql, format_dict)

        results = []

        for row in res:
            try:
                result = _format_listings(row)

                results.append(result)
            except Exception as e:
                logging.error(e)

        return results
    except SQLAlchemyError as e:
        logging.error(e)
        session.rollback()
        raise e
    finally:
        session.remove()


def health():
    session = create_session()
    try:
        result = session.execute(
            'SELECT block_num, timestamp FROM chronicle_transactions WHERE seq = ('
            'SELECT max(seq) FROM chronicle_transactions WHERE ingested)'
        ).first()

        if result:
            return {
                'success': 'true',
                'block_num': result['block_num'],
                'timestamp': result['timestamp'].strftime("%Y-%m-%d %H:%M:%S")
            }

        return {
            'success': 'false'
        }
    except SQLAlchemyError as e:
        logging.error(e)
        session.rollback()
        raise e
    finally:
        session.remove()


def _format_collection_overview(row, type, size=80):
    return {
        'collection': row['collection'],
        'name': row['name'],
        'authorized': row['authorized'],
        'image': _format_image(row['image']),
        'thumbnail': _format_collection_thumbnail(row['collection'], row['image'], size),
        'verified': row['verified'],
        'blacklisted': row['blacklisted'],
        'waxVolume24h': row['wax_volume_1_day'],
        'usdVolume24h': row['usd_volume_1_day'],
        'waxVolume48h': row['wax_volume_2_days'],
        'usdVolume48h': row['usd_volume_2_days'],
        'waxVolume7d': row['wax_volume_7_days'],
        'usdVolume7d': row['usd_volume_7_days'],
        'waxVolume14d': row['wax_volume_14_days'],
        'usdVolume14d': row['usd_volume_14_days'],
        'waxMarketCap': row['wax_market_cap'],
        'usdMarketCap': row['usd_market_cap'],
        'collectionType': type,
        'allTimeVolume': row['wax_volume_all_time'] if 'wax_volume_all_time' in row.keys() else None,
        'allTimeUsdVolume': row['usd_volume_all_time'] if 'usd_volume_all_time' in row.keys() else None,
        'growth24h': (row['wax_volume_1_day'] - (row['wax_volume_2_days'] - row['wax_volume_1_day'])) / max(
            row['wax_volume_2_days'] - row['wax_volume_1_day'], 1),
        'growth7d': (row['wax_volume_7_days'] - (row['wax_volume_14_days'] - row['wax_volume_7_days'])) / max(
            row['wax_volume_14_days'] - row['wax_volume_7_days'], 1)
    }


@cache.memoize(timeout=300)
def get_collections_overview(
    collection, type, tag_id, verified, trending, market, owner, pfps_only, limit=100, offset=0
):
    session = create_session()

    sort_clause = '7 DESC'

    tag_clause = ''

    if tag_id:
        tag_clause = (
            ' AND c.collection IN ('
            '   SELECT collection FROM tags_mv WHERE collection = ac.collection AND tag_id = :tag_id'
            ')'
        )

    type_tag_id_mapping = {
        '2': 65,
        '3': 69,
        '4': 66,
        '5': 67,
        '6': 68,
        '7': 70
    }

    rel_tag_id = ''
    if type in ['2', '3', '4', '5', '6', '7']:
        rel_tag_id = type_tag_id_mapping[type]
        tag_clause += (
            ' AND c.collection IN ('
            '   SELECT collection FROM tags_mv WHERE collection = c.collection AND tag_id = :rel_tag_id'
            ')'
        )

    if type == '4':
        sort_clause = '11 DESC'

    if type == '5' or type == '6' or type == '3':
        sort_clause = '11 DESC'

    if type == '0': #other
        tag_clause = (
            'AND c.collection NOT IN ('
            '   SELECT collection FROM tags_mv WHERE tag_id BETWEEN 64 AND 70 AND collection = c.collection'
            ') '
        )

    if type == '1': #all
        tag_clause = ''

    if verified == 'verified':
        verified_clause = ' AND verified '
    elif verified == 'unverified':
        verified_clause = (
            ' AND NOT verified AND NOT blacklisted '
        )
        sort_clause = '7 DESC'
    elif verified == 'all':
        verified_clause = ' AND NOT blacklisted '
        sort_clause = 'verified DESC NULLS LAST, ' + sort_clause
    elif verified == 'blacklisted':
        verified_clause = ' AND blacklisted '
        sort_clause = 'verified DESC NULLS LAST, ' + sort_clause
    else:
        verified_clause = ''

    search_dict = {
        'term': '%{}%'.format(collection), 'type': type, 'tag_id': tag_id, 'limit': limit,
        'rel_tag_id': rel_tag_id, 'offset': offset, 'owner': owner
    }

    join_clause = ''
    with_clause = ''
    cnt_clause = ''

    if type == 'drops':
        join_clause = ' INNER JOIN drops d ON (d.collection = c.collection AND NOT d.erased) '
        if market:
            join_clause = (
                ' INNER JOIN drops d ON (d.collection = c.collection AND NOT d.erased AND d.contract = :market) '
            )
            search_dict['market'] = market

    if type == 'crafts':
        join_clause = ' INNER JOIN crafts d ON (d.collection = c.collection AND NOT d.erased) '

    if type in ['assets', 'bulk_burn', 'bulk_distribute', 'bulk_transfer', 'bulk_multi_sell', 'bulk_sell',
                'bulk_sell_dupes', 'bulk_sell_highest_duplicates', 'bulk_transfer_duplicates',
                'bulk_transfer_lowest_mints', 'inventory'] and owner:
        with_clause = (
            'WITH user_assets AS (SELECT collection, COUNT(1) AS cnt FROM assets WHERE owner = :owner GROUP BY 1)'
        )
        join_clause = ' INNER JOIN user_assets ua USING (collection) '
        sort_clause = 'cnt DESC'
        cnt_clause = ', cnt'

    if type == 'my_packs' and owner:
        with_clause = (
            'WITH user_assets AS ('
            'SELECT a.collection, COUNT(1) AS cnt FROM assets a '
            'INNER JOIN packs p ON (a.template_id = p.template_id AND p.pack_id = ('
            '   SELECT MAX(pack_id) FROM packs WHERE template_id = a.template_id)'
            ') '
            'WHERE owner = :owner '
            'GROUP BY 1)'
        )
        join_clause = ' INNER JOIN user_assets ua USING (collection) '
        sort_clause = 'cnt DESC'
        cnt_clause = ', cnt'

    if type in ['sales', 'bulk_edit', 'bulk_cancel'] and owner:
        with_clause = (
            'WITH user_assets AS (SELECT collection, COUNT(1) AS cnt FROM listings WHERE seller = :owner GROUP BY 1)'
        )
        join_clause = ' INNER JOIN user_assets ua USING (collection) '
        sort_clause = 'cnt DESC'
        cnt_clause = ', cnt'

    if (type == 'sells' or type == 'buys') and owner:
        with_clause = (
            'WITH user_assets AS (SELECT collection, COUNT(1) AS cnt '
            'FROM sales WHERE seller = :owner GROUP BY 1)'
        )
        join_clause = ' INNER JOIN user_assets ua USING (collection) '
        sort_clause = ' cnt DESC NULLS LAST '
        cnt_clause = ', cnt'

    if verified == 'verified':
        verified_clause = ' AND verified '
    elif verified == 'unverified':
        verified_clause = (
            ' AND NOT verified '
            ' AND NOT blacklisted '
        )
    elif verified == 'all':
        verified_clause = ' AND NOT blacklisted '
    elif verified == 'blacklisted':
        verified_clause = ' AND blacklisted '

    if pfps_only or type == 'pfps':
        join_clause = ' INNER JOIN pfp_schemas USING(collection) '

    search_clause = ''
    type_join = False
    if trending:
        sort_clause = (
            ' (SUM(COALESCE(cv1.wax_volume, 0)) - '
            '(SUM(COALESCE(cv2.wax_volume, 0)) - SUM(COALESCE(cv1.wax_volume, 0)))) '
            '/ (SUM(COALESCE(cv2.wax_volume, 0)) - SUM(COALESCE(cv1.wax_volume, 0))) DESC '
        )
        search_clause = (
            ' AND COALESCE(cv1.wax_volume, 0) > 1000'
            ' AND (COALESCE(cv2.wax_volume, 0) - COALESCE(cv1.wax_volume, 0)) > 0 '
            ' AND COALESCE(cv1.wax_volume, 0) > (COALESCE(cv2.wax_volume, 0) - COALESCE(cv1.wax_volume, 0))'
        )
        type_join = True

    try:
        result = session.execute(
            '{with_clause} '
            'SELECT c.*, '
            'SUM(COALESCE(cv1.wax_volume, 0)) AS wax_volume_1_day, '
            'SUM(COALESCE(cv1.usd_volume, 0)) AS usd_volume_1_day, '
            'SUM(COALESCE(cv2.wax_volume, 0)) AS wax_volume_2_days, '
            'SUM(COALESCE(cv2.usd_volume, 0)) AS usd_volume_2_days, '
            'SUM(COALESCE(cv7.wax_volume, 0)) AS wax_volume_7_days, '
            'SUM(COALESCE(cv7.usd_volume, 0)) AS usd_volume_7_days, '
            'SUM(COALESCE(cv14.wax_volume, 0)) AS wax_volume_14_days, '
            'SUM(COALESCE(cv14.usd_volume, 0)) AS usd_volume_14_days, '
            'SUM(COALESCE(cvat.wax_volume, 0)) AS wax_volume_all_time, '
            'SUM(COALESCE(cvat.usd_volume, 0)) AS usd_volume_all_time, '
            'wax_market_cap, usd_market_cap{cnt_clause} '
            'FROM ('
            '   SELECT c.collection, c.authorized, ci.image, name, verified, blacklisted{cnt_clause} '
            '   FROM collections c '
            '   LEFT JOIN images ci USING (image_id) '
            '   LEFT JOIN names cn USING (name_id) '
            '   {join_clause} '
            '   WHERE TRUE {collection_clause} {tag_clause} {verified_clause} {search_clause} '
            ') c '
            'LEFT JOIN collection_market_cap_mv cmc ON (c.collection = cmc.collection) '
            'LEFT JOIN volume_collection_1_days_mv cv1 ON (c.collection = cv1.collection {cv1_type_join}) '
            'LEFT JOIN volume_collection_2_days_mv cv2 ON (c.collection = cv2.collection {cv2_type_join}) '
            'LEFT JOIN volume_collection_7_days_mv cv7 ON (c.collection = cv7.collection {cv7_type_join}) '
            'LEFT JOIN volume_collection_14_days_mv cv14 ON (c.collection = cv14.collection {cv14_type_join}) '
            'LEFT JOIN volume_collection_all_time_mv cvat ON (c.collection = cvat.collection {cvat_type_join}) '
            'GROUP BY 1, 2, 3, 4, 5, 6, wax_market_cap, usd_market_cap{cnt_clause} '
            'ORDER BY {sort_clause}, c.collection ASC LIMIT :limit offset :offset'.format(
                collection_clause=(
                    ' AND (c.collection ilike :term OR cn.name ilike :term) '
                ) if collection and collection != '*' else '',
                sort_clause=sort_clause,
                tag_clause=tag_clause,
                search_clause=search_clause,
                verified_clause=verified_clause,
                join_clause=join_clause,
                with_clause=with_clause,
                cnt_clause=cnt_clause,
                cv1_type_join=' AND cv1.type = \'sales\'' if type_join else '',
                cv2_type_join=' AND cv2.type = \'sales\'' if type_join else '',
                cv7_type_join=' AND cv7.type = \'sales\'' if type_join else '',
                cv14_type_join=' AND cv14.type = \'sales\'' if type_join else '',
                cvat_type_join=' AND cvat.type = \'sales\'' if type_join else ''
            ), search_dict
        )

        collections = []

        for row in result:
            collections.append(_format_collection_overview(row, type, 240))

        return collections
    except SQLAlchemyError as e:
        logging.error(e)
        session.rollback()
        raise e
    finally:
        session.remove()


def get_tags(collection):
    session = create_session()
    try:
        res = session.execute(
            'SELECT * FROM tags_mv t INNER JOIN tags USING(tag_id) '
            'WHERE collection = :collection ', {'collection': collection})
        tags = []
        for tag in res:
            tags.append({'tagId': tag['tag_id'], 'tagName': tag['tag_name']})

        return tags
    except SQLAlchemyError as e:
        logging.error(e)
        session.rollback()
        raise e
    finally:
        session.remove()


def _format_templates(templates):
    response = []
    for template in templates:
        if template['traits']:
            traits = []
            for trait in template['traits']:
                formatted_trait = {}
                formatted_trait['name'] = trait['attribute_name']
                if trait['int_value'] or trait['int_value'] == 0:
                    formatted_trait['value'] = trait['int_value']
                elif trait['float_value'] or trait['float_value'] == 0.0:
                    formatted_trait['value'] = trait['float_value']
                elif trait['string_value']:
                    formatted_trait['value'] = trait['string_value']
                else:
                    formatted_trait['value'] = trait['bool_value']
                if trait['floor_price']:
                    formatted_trait['floorPrice'] = trait['floor_price']
                if trait['rarity_score']:
                    formatted_trait['rarityScore'] = trait['rarity_score']
                if trait['total_schema']:
                    formatted_trait['totalSchema'] = trait['total_schema']
                traits.append(formatted_trait)
            template['traits'] = traits
        response.append(template)

    return response


def _format_rwax_templates(templates, templates_supply):
    template_list = []

    supply_dict = json.loads(templates_supply)

    for template in templates:
        for supply in supply_dict:
            if supply['template_id'] == template['template_id']:
                template['maxAssets'] = supply['max_assets']
        template_list.append(template)

    return template_list


def calc_avg_factor(trait_factors, nfts):
    for trait in trait_factors:
        total_factor = 0
        for nft in nfts:
            for trait_name in nft.keys():
                factor = 0
                trait_value = nft[trait_name]
                if trait_name == trait['trait_name']:
                    if len(trait['values']) > 0:
                        for value in trait['values']:
                            if value['value'] == trait_value:
                                factor = value['factor']
                    else:
                        min_value = trait['min_value']
                        max_value = trait['max_value']
                        local_min_factor = trait['min_factor']
                        local_max_factor = trait['max_factor']
                        factor = get_factor(trait_value, local_max_factor, local_min_factor, max_value, min_value)
                total_factor += factor
        trait['avg_factor'] = total_factor / len(nfts)

    return trait_factors


def get_average_factor(trait_factors):
    avg_factor = 1
    for factor in trait_factors:
        avg_factor *= factor['avg_factor']

    return avg_factor


def get_factor(x, max_factor, min_factor, max_value, min_value):
    return ((max_factor - min_factor) / (max_value - min_value)) * (x - min_value) + min_factor


def test_rwax_stuff():
    trait_factors = [
        {
            'trait_name': 'rarity', 'min_factor': 1.0, 'max_factor': 5.0, 'values': [
                {'value': 'common', 'factor': 1.0, 'amount': 5},
                {'value': 'epic', 'factor': 2.0, 'amount': 3},
                {'value': 'legendary', 'factor': 5.0, 'amount': 2}
            ], 'token_share': 5000.00000
        },
        {
            'trait_name': 'level', 'min_factor': 1.0, 'max_factor': 10.0, 'min_value': 1,
            'max_value': 5, 'values': [], 'token_share': 2000.00000
        },
        {
            'trait_name': 'charge', 'min_factor': 1.0, 'max_factor': 4.0, 'min_value': 0,
            'max_value': 1, 'values': [], 'token_share': 1000.00000
        },
        {
            'trait_name': 'energy', 'min_factor': 1.0, 'max_factor': 100.0, 'min_value': 0,
            'max_value': 100, 'values': [], 'token_share': 1000.00000
        },
    ]

    nfts = [
        {'rarity': 'common', 'level': 1, 'charge': 0.0, 'energy': 5.0},
        {'rarity': 'common', 'level': 1, 'charge': 0.1, 'energy': 69.1},
        {'rarity': 'common', 'level': 2},
        {'rarity': 'common', 'charge': 0.2, 'energy': 31.2},
        {'rarity': 'common', 'level': 3, 'charge': 0.31, 'energy': 5.51},
        {'rarity': 'common', 'level': 1, 'charge': 0.1, 'energy': 90.1},
        {'rarity': 'common', 'level': 2, 'charge': 0.12, 'energy': 20.12},
        {'rarity': 'common', 'charge': 0.2},
        {'rarity': 'common', 'level': 3, 'charge': 0.31, 'energy': 20.1},
        {'rarity': 'epic', 'level': 4, 'charge': 0.5, 'energy': 56.5},
        {'rarity': 'epic', 'charge': 0.52, 'energy': 52},
        {'rarity': 'epic', 'level': 4, 'energy': 7.6},
        {'rarity': 'legendary', 'level': 5, 'charge': 0.9, 'energy': 10.20},
        {'rarity': 'legendary', 'level': 5, 'energy': 22.0},
    ]

    tokens = 10000.0000

    total_share = 0

    trait_factors = calc_avg_factor(trait_factors, nfts)

    trait_factor_tokens = 0
    for trait in trait_factors:
        trait_factor_tokens += trait['token_share']

    for nft in nfts:
        share = 0
        for trait_name in nft.keys():
            factor = 1
            trait_value = nft[trait_name]
            for trait in trait_factors:
                token_share = trait['token_share']
                avg_factor = trait['avg_factor']
                if trait_name == trait['trait_name']:
                    if len(trait['values']) > 0:
                        for value in trait['values']:
                            if value['value'] == trait_value:
                                factor = value['factor']
                    else:
                        min_value = trait['min_value']
                        max_value = trait['max_value']
                        local_min_factor = trait['min_factor']
                        local_max_factor = trait['max_factor']
                        factor = get_factor(trait_value, local_max_factor, local_min_factor, max_value, min_value)
                    share += (token_share / len(nfts)) * (factor / avg_factor)
        share += (tokens - trait_factor_tokens) / len(nfts)
        print('Tokens for this NFT: ' + str(share))
        total_share += share
    print('Tokens Total: ' + str(total_share))


def get_rwax_tokens(collection):
    session = create_session()

    try:
        res = session.execute(
            'SELECT symbol, contract, decimals, maximum_supply, token_name, token_logo, token_logo_lg, '
            'rt.timestamp,c.collection, cn.name AS display_name, ci.image AS collection_image, '
            'c.verified, CAST(trait_factors AS text) AS trait_factors, '
            'CAST(templates_supply AS text) AS templates_supply, {templates_obj} '
            'FROM rwax_tokens rt '
            'LEFT JOIN collections c USING (collection) '
            'LEFT JOIN images ci USING (image_id) '
            'LEFT JOIN names cn USING (name_id) '
            'LEFT JOIN templates t ON t.template_id = ANY(template_ids) '
            'LEFT JOIN template_stats_mv ts USING (template_id) '
            'LEFT JOIN templates_minted_mv tm USING (template_id) '
            'LEFT JOIN template_floor_prices_mv fp USING (template_id) '
            'LEFT JOIN images ti ON (t.image_id = ti.image_id) '
            'LEFT JOIN videos tv ON (t.video_id = tv.video_id) '
            'LEFT JOIN data td ON (t.immutable_data_id = td.data_id) '
            'LEFT JOIN names tn ON (t.name_id = tn.name_id) '
            'WHERE NOT blacklisted {collection_clause} '
            'GROUP BY 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14'.format(
                templates_obj=_get_templates_object(),
                collection_clause=' AND rt.collection = :collection ' if collection and collection != '*' else ''
            ), {'collection': collection})
        tokens = []
        for token in res:
            templates = _format_templates(token['templates'])
            tokens.append({
                'collection': {
                    'collectionName': token['collection'],
                    'displayName': token['display_name'],
                    'collectionImage': token['collection_image'],
                    'verification': token['verified'],
                },
                'symbol': token['symbol'],
                'contract': token['contract'],
                'decimals': token['decimals'],
                'maxSupply': token['maximum_supply'],
                'templates': _format_rwax_templates(templates, token['templates_supply']),
                'traitFactors': json.loads(token['trait_factors']),
                'name': token['token_name'],
                'tokenLogo': token['token_logo'],
                'tokenLogoLarge': token['token_logo_lg'],
                'created': token['timestamp'].strftime(DATE_FORMAT_STRING)
            })

        return tokens
    except SQLAlchemyError as e:
        logging.error(e)
        session.rollback()
        raise e
    finally:
        session.remove()


def get_collection_schemas(collection):
    session = create_session()
    try:
        res = session.execute(
            'SELECT schema, collection, timestamp, json_agg(json_build_object('
            '\'rarity\', CASE WHEN string_value IS NULL THEN \'\' ELSE string_value END, \'num_assets\', num_assets, '
            '\'num_templates\', num_templates '
            ')) AS rarities, SUM(num_templates) AS num_templates, SUM(num_assets) AS num_assets, '
            'SUM(volume_wax) AS volume_wax, SUM(volume_usd) AS volume_usd '
            'FROM ('
            '   SELECT t.schema, t.collection, s.timestamp, a.string_value, COUNT(1) AS num_templates, '
            '   SUM(total - COALESCE(num_burned, 0)) AS num_assets, SUM(volume_wax) AS volume_wax, '
            '   SUM(volume_usd) AS volume_usd '
            '   FROM schemas s '
            '   LEFT JOIN templates t USING(collection, schema) '
            '   LEFT JOIN template_stats_mv USING(template_id) '
            '   LEFT JOIN attributes a ON s.schema = a.schema AND s.collection = a.collection '
            '   AND a.attribute_id = ANY(attribute_ids) AND LOWER(attribute_name) = \'rarity\' '
            '   WHERE s.collection = :collection '
            '   GROUP BY 1, 2, 3, 4'
            ') b GROUP BY 1, 2, 3 HAVING SUM(num_assets) > 0 ORDER BY 6 DESC ', {
                'collection': collection
            }
        )

        schemas = []

        for schema in res:
            item = {
                'collection': schema['collection'],
                'schema': schema['schema'],
                'timestamp': datetime.datetime.timestamp(schema['timestamp']),
                'volumeWax': schema['volume_wax'],
                'volumeUsd': schema['volume_usd'],
                'numTemplates': int(schema['num_templates']) if schema['num_templates'] else 0,
                'numAssets': int(schema['num_assets']) if schema['num_assets'] else 0,
            }
            rarities = schema['rarities']
            item['rarities'] = []
            for rarity in sorted(filter(lambda x: x['num_assets'], rarities), key=lambda x: x['num_assets']):
                if rarity['rarity']:
                    item['rarities'].append({
                        'rarity': rarity['rarity'],
                        'numAssets': rarity['num_assets'],
                        'numTemplates': rarity['num_templates']
                    })
            schemas.append(item)

        return schemas
    except SQLAlchemyError as e:
        logging.error(e)
        session.rollback()
        return []
    finally:
        session.remove()


@cache.memoize(timeout=300)
def get_collection_filter(verified='verified', term='', market='', type='', owner='', collection='', pfps_only=False):
    session = create_session()

    verified_clause = ''
    join_clause = ''
    with_clause = ''

    search_dict = {'term': '%{}%'.format(term)} if term else {}
    search_dict['owner'] = owner
    search_dict['limit'] = 100

    order_clause = 'cv.wax_volume DESC NULLS LAST'
    cnt_clause = ''

    if type == 'drops':
        join_clause = ' INNER JOIN drops d ON (d.collection = c.collection AND NOT d.erased) '
        if market:
            join_clause = (
                ' INNER JOIN drops d ON (d.collection = c.collection AND NOT d.erased AND d.contract = :market) '
            )
            search_dict['market'] = market

    if type == 'crafts':
        join_clause = ' INNER JOIN crafts d ON (d.collection = c.collection AND NOT d.erased) '

    if type in ['assets', 'bulk_burn', 'bulk_distribute', 'bulk_transfer', 'bulk_multi_sell', 'bulk_sell',
                'bulk_sell_dupes', 'bulk_sell_highest_duplicates', 'bulk_transfer_duplicates',
                'bulk_transfer_lowest_mints', 'inventory'] and owner:
        with_clause = (
            'WITH user_assets AS (SELECT collection, COUNT(1) AS cnt FROM assets WHERE owner = :owner GROUP BY 1)'
        )
        join_clause = ' INNER JOIN user_assets ua USING (collection) '
        order_clause = 'ua.cnt DESC'
        cnt_clause = ', ua.cnt'

    if type == 'my_packs' and owner:
        with_clause = (
            'WITH user_assets AS ('
            'SELECT a.collection, COUNT(1) AS cnt FROM assets a '
            'INNER JOIN packs p ON (a.template_id = p.template_id AND p.pack_id = ('
            '   SELECT MAX(pack_id) FROM packs WHERE template_id = a.template_id)'
            ') '
            'WHERE owner = :owner '
            'GROUP BY 1)'
        )
        join_clause = ' INNER JOIN user_assets ua USING (collection) '
        order_clause = 'ua.cnt DESC'
        cnt_clause = ', ua.cnt'

    if type in ['sales', 'bulk_edit', 'bulk_cancel'] and owner:
        with_clause = (
            'WITH user_assets AS (SELECT collection, COUNT(1) AS cnt FROM listings WHERE seller = :owner GROUP BY 1)'
        )
        join_clause = ' INNER JOIN user_assets ua USING (collection) '
        order_clause = 'ua.cnt DESC'
        cnt_clause = ', ua.cnt'

    if (type == 'sells' or type == 'buys') and owner:
        with_clause = (
            'WITH user_assets AS (SELECT collection, COUNT(1) AS cnt '
            'FROM sales WHERE seller = :owner GROUP BY 1)'
        )
        join_clause = ' INNER JOIN user_assets ua USING (collection) '
        order_clause = 'ua.cnt DESC'
        cnt_clause = ', ua.cnt'

    if verified == 'verified':
        verified_clause = ' AND verified '
    elif verified == 'unverified':
        verified_clause = (
            ' AND NOT verified '
            ' AND NOT blacklisted '
        )
    elif verified == 'all':
        verified_clause = ' AND NOT blacklisted '
    elif verified == 'blacklisted':
        verified_clause = ' AND blacklisted '

    collection_clause = ''
    if collection:
        collection_clause = ' AND c.collection != :collection '
        search_dict['collection'] = collection
        search_dict['limit'] = 99

    if pfps_only or type == 'pfps':
        join_clause = ' INNER JOIN pfp_schemas USING(collection) '

    try:
        collections = {
            'collections': [],
            'images': {},
            'names': {},
            'verified': {},
            'blacklisted': {},
            'volume24h': {}
        }

        if collection:
            result1 = session.execute(
                'SELECT c.collection, ci.image, cn.name, verified, blacklisted, cv.wax_volume '
                'FROM collections c '
                'LEFT JOIN names cn ON (c.name_id = cn.name_id) '
                'LEFT JOIN images ci ON (c.image_id = ci.image_id) '
                'LEFT JOIN collection_volumes_1_mv cv ON c.collection = cv.collection '
                'WHERE c.collection = :collection '
                'GROUP BY 1, 2, 3, 4, 5, 6 '
                'LIMIT 1',
                search_dict
            )

            for row in result1:
                collection = row.collection
                name = row.name
                image = row.image
                verified = row.verified
                blacklisted = row.blacklisted
                volume_24h = row.wax_volume

                if collection not in collections['collection']:
                    collections['collections'].append(collection)
                    collections['images'][collection] = _format_collection_thumbnail(collection, image)
                    collections['names'][collection] = name
                    collections['verified'][collection] = verified
                    collections['blacklisted'][collection] = blacklisted
                    collections['volume24h'][collection] = volume_24h

        result = session.execute(
            '{with_clause} '
            'SELECT c.collection, ci.image, cn.name, verified, blacklisted, cv.wax_volume {cnt_clause} '
            'FROM collections c '
            'LEFT JOIN names cn ON (c.name_id = cn.name_id) '
            'LEFT JOIN images ci ON (c.image_id = ci.image_id) '
            '{join_clause} '
            'LEFT JOIN collection_volumes_1_mv cv ON c.collection = cv.collection '
            'WHERE TRUE {verified_clause} {term_clause} {collection_clause} '
            'GROUP BY 1, 2, 3, 4, 5, 6 {cnt_clause} '
            'ORDER BY {order_clause}, collection ASC '
            'LIMIT :limit'.format(
                verified_clause=verified_clause,
                join_clause=join_clause,
                with_clause=with_clause,
                collection_clause=collection_clause,
                order_clause=order_clause,
                cnt_clause=cnt_clause,
                term_clause=' AND (c.collection ilike :term OR cn.name ilike :term) ' if term else ''
            ), search_dict
        )

        for row in result:
            collection = row.collection
            name = row.name
            image = row.image
            verified = row.verified
            blacklisted = row.blacklisted
            volume_24h = row.wax_volume

            if collection not in collections['collections']:
                collections['collections'].append(collection)
                collections['images'][collection] = _format_collection_thumbnail(collection, image)
                collections['names'][collection] = name
                collections['verified'][collection] = verified
                collections['blacklisted'][collection] = blacklisted
                collections['volume24h'][collection] = volume_24h

        return collections
    except SQLAlchemyError as e:
        logging.error(e)
        session.rollback()
        raise e
    finally:
        session.remove()


def get_drops(
    drop_id, collection, schema, term, limit, order_by, offset, verified, market, token, highlight, upcoming, user_name,
    currency, home
):
    session = create_session()
    try:
        order_dir = 'DESC'
        if '_asc' in order_by:
            order_dir = 'ASC'
            order_by = order_by.replace('_asc', '')
        elif '_desc' in order_by:
            order_dir = 'DESC'
            order_by = order_by.replace('_desc', '')

        search_dict = {'limit': limit, 'offset': offset, 'order_dir': order_dir}

        market_clause = ''
        if market:
            market_clause = ' AND contract = :contract '
            search_dict['contract'] = market

        collection_clause = ''

        if collection and collection != '*':
            search_dict['collection'] = collection
            collection_clause = ' AND d2.collection = :collection '

        order_clause = ''

        if order_by == 'drop_id':
            order_clause = 'ORDER BY drop_id {}'.format(order_dir)

        if order_by == 'template_id':
            order_clause = 'ORDER BY d2.template_id {}'.format(order_dir)

        if order_by == 'collection':
            order_clause = 'ORDER BY d2.collection {}'.format(order_dir)

        if order_by == 'date' and upcoming:
            order_clause = (
                'ORDER BY d2.start_time {dir} NULLS LAST, drop_id {dir}'.format(dir=order_dir)
            )
        elif order_by == 'date':
            order_clause = (
                'ORDER BY COALESCE(d2.start_time, d2.timestamp) {dir} NULLS LAST, drop_id {dir}'.format(dir=order_dir)
            )

        if order_by == 'price':
            order_clause = (
                'ORDER BY (CASE WHEN currency = \'WAX\' THEN price ELSE price / (SELECT usd FROM usd_rate) END) {}'
            ).format('ASC' if order_dir == 'ASC' else 'DESC')

        search_clause = ''

        if home:
            search_clause += (
                ' AND (d2.drop_id = ('
                '   SELECT MAX(drop_id) FROM drops WHERE contract = \'nfthivedrops\' AND collection = d2.collection'
                ') OR highlighted OR 10 > (SELECT COUNT(1) FROM drops '
                'WHERE contract = \'nfthivedrops\' AND collection = d2.collection '
                'AND timestamp > NOW() AT time zone \'UTC\' - INTERVAL \'7 days\' )) '
                'AND ('
                '   SELECT COUNT(1) FROM drop_updates '
                '   WHERE drop_id = d2.drop_id AND contract = \'nfthivedrops\' '
                '   AND start_time is NOT NULL'
                ') < 3 '
            )

        if highlight:
            search_clause += (
                ' AND highlighted '
            )

        if schema:
            search_clause += (
                ' AND t.category = :schema '
            )
            search_dict['schema'] = schema

        if term:
            if isinstance(term, int) or (isinstance(term, str) and term.isnumeric()):
                template = session.execute('SELECT template_id FROM templates WHERE template_id = :term', {
                    'term': term
                }).first()
                if template:
                    search_dict['template_id'] = template['template_id']
                    search_clause += (
                        ' AND t.template_id = :template_id '
                    )
            else:
                search_dict['name'] = term
                search_clause += (
                    ' AND tn.name LIKE :name '
                )

        if currency:
            search_clause += (
                ' AND (drop_id, contract) IN (SELECT drop_id, contract FROM drop_prices_mv '
                ' WHERE :currency = ANY(currencies) AND drop_id = d2.drop_id AND contract = d2.contract) '
            )
            search_dict['currency'] = currency.upper()

        if upcoming:
            search_clause += (
                ' AND start_time > NOW() '
            )
        else:
            search_clause += (
                'AND (d2.start_time IS NULL OR d2.start_time < NOW()) '
            )

        if verified == 'verified':
            search_clause += ' AND verified '
        elif verified == 'unverified':
            search_clause += (
                ' AND NOT verified AND NOT blacklisted '
            )
        elif verified == 'all':
            search_clause += ' AND NOT blacklisted '

        if drop_id:
            search_dict['drop_id'] = drop_id
            search_clause += ' AND drop_id = :drop_id '

        if token:
            search_clause += ' AND currency ilike :token '
            search_dict['token'] = token

        if user_name and (not collection or collection == '*'):
            search_clause += (
                ' AND d2.collection NOT IN (SELECT collection FROM tags_mv WHERE tag_id IN ('
                '   SELECT tag_id FROM tag_filters_mv WHERE user_name = :user_name)'
                ') '
                ' AND d2.collection NOT IN (SELECT collection FROM personal_blacklist_mv WHERE account = :user_name) '
            )
            search_dict['user_name'] = user_name

        sql = (
            'WITH usd_rate AS (SELECT usd FROM usd_prices ORDER BY timestamp DESC LIMIT 1) '
            'SELECT drop_id, price, currency, fee, '
            'extract(epoch from start_time AT time zone \'Europe/Berlin\')::bigint AS start_time, '
            'extract(epoch from end_time AT time zone \'Europe/Berlin\')::bigint AS end_time, d2.timestamp, '
            'account_limit, account_limit_cooldown, max_claimable, num_claimed, verified, '
            'display_data, (SELECT usd FROM usd_rate) as wax_usd, contract, cn.name as display_name, t.collection, '
            'auth_required, ci.image AS collection_image, name_pattern, pd.drop_id AS is_pfp, '
            '(SELECT SUM(amount) FROM drop_actions '
            'WHERE drop_id = d2.drop_id AND contract = d2.contract AND '
            'action = \'claim\') AS num_bought, {templates_obj} '
            'FROM drops d2 '
            'INNER JOIN templates t ON (t.template_id = ANY(d2.templates_to_mint)) '
            'LEFT JOIN template_stats_mv ts USING (template_id) '
            'LEFT JOIN templates_minted_mv tm USING (template_id) '
            'LEFT JOIN template_floor_prices_mv fp USING (template_id) '
            'LEFT JOIN images ti ON (t.image_id = ti.image_id) '
            'LEFT JOIN videos tv ON (t.video_id = tv.video_id) '
            'LEFT JOIN data td ON (t.immutable_data_id = td.data_id) '
            'LEFT JOIN names tn ON (t.name_id = tn.name_id) '
            'LEFT JOIN pfp_drop_data pd USING (drop_id, contract) '
            'INNER JOIN collections c ON (d2.collection = c.collection) '
            'LEFT JOIN names cn ON (c.name_id = cn.name_id) '
            'LEFT JOIN images ci ON (c.image_id = ci.image_id) '
            'WHERE TRUE '
            'AND (end_time IS NULL OR end_time >= NOW() AT time zone \'UTC\') '
            'AND NOT erased AND NOT is_hidden {collection_clause} {search_clause} '
            'AND (currency IS NOT NULL OR price IS NULL OR price = 0) '
            '{market_clause} '
            'GROUP BY 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21 '
            '{order_clause} LIMIT :limit OFFSET :offset'.format(
                order_clause=order_clause,
                market_clause=market_clause,
                collection_clause=collection_clause,
                search_clause=search_clause,
                templates_obj=_get_templates_object()
            )
        )

        res = session.execute(
            sql,
            search_dict)

        drops = []

        for drop in res:
            templates = _format_templates(drop['templates'])
            drops.append({
                'dropId': drop['drop_id'],
                'price': drop['price'],
                'currency': drop['currency'],
                'startTime': drop['start_time'],
                'endTime': drop['end_time'],
                'createdAt': datetime.datetime.timestamp(drop['timestamp']),
                'accountLimit': drop['account_limit'],
                'accountLimitCooldown': drop['account_limit_cooldown'],
                'maxClaimable': drop['max_claimable'],
                'numClaimed': drop['num_claimed'],
                'verified': drop['verified'],
                'displayData': drop['display_data'],
                'authRequired': drop['auth_required'],
                'namePattern': drop['name_pattern'],
                'isPfp': drop['is_pfp'],
                'collection': {
                    'collectionName': drop['collection'],
                    'displayName': drop['display_name'],
                    'collectionImage': drop['collection_image'],
                    'verification': drop['verified'],
                },
                'templatesToMint': templates
            })

        return drops
    except SQLAlchemyError as e:
        logging.error(e)
        session.rollback()
        raise e
    finally:
        session.remove()
