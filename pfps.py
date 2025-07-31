import json

from api import logging
from api import cache

from sqlalchemy.exc import SQLAlchemyError

from logic import create_session, execute_sql


def _format_trait(trait):
    return {
        'name': trait['attribute_name'] if trait['attribute_name'] != 'num_traits' else 'Number of Traits',
        'value': trait['string_value'],
        'total': trait['total'],
        'totalSchema': trait['total_schema'],
        'percentage': float(trait['total'] / trait['total_schema']),
        'rarityScore': trait['rarity_score'],
        'floor': str(trait['floor']) + ' WAX' if trait['floor'] else 'Not listed',
    }


@cache.memoize(timeout=60)
def get_pfp_asset(asset_id):
    session = create_session()
    try:

        sql = (
            'SELECT asset_id, a.template_id, a.timestamp, a.mdata, a.author, a.category, aa.rarity_score, aa.rank, '
            'owner, a.name, a.burned, array_agg(json_build_object(\'total\', asu.total, \'floor\', asu.floor, '
            '\'total_schema\', asu.total_schema, \'rarity_score\', asu.rarity_score, '
            '\'attribute_name\', attribute_name, \'string_value\', string_value)) AS attributes '
            'FROM attribute_assets aa '
            'INNER JOIN assets a USING(asset_id) '
            'INNER JOIN attributes att ON att.attribute_id = ANY(aa.attribute_ids) '
            'INNER JOIN attribute_summaries asu USING(attribute_id) '
            'WHERE asset_id = :asset_id GROUP BY 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11 '
        )

        item = execute_sql(session, 
            sql,
            {'asset_id': asset_id}
        ).first()

        if item:
            traits = []
            for trait in item['attributes']:
                traits.append(_format_trait(trait))

            asset = {
                'asset': {
                    'assetId': item['asset_id'],
                    'templateId': item['template_id'],
                    'name': item['name'],
                    'timestamp': item['timestamp'].strftime("%Y-%m-%d %H:%M:%S UTC"),
                    'data': json.loads(item['mdata']),
                    'collection': item['author'],
                    'schema': item['category'],
                },
                'owner': item['owner'],
                'burned': item['burned'],
                'rank': item['rank'],
                'rarityScore': item['rarity_score'],
                'traits': traits
            }

            return asset
        return {}
    except SQLAlchemyError as e:
        logging.error(e)
        session.rollback()
        raise e
    finally:
        session.remove()


@cache.memoize(timeout=60)
def get_pfp_trait_list(collection, schema, limit=100, offset=0):
    session = create_session()
    try:

        sql = (
            'SELECT asu.author, asu.category AS schema, asu.total, asu.floor, asu.total_schema, asu.rarity_score, '
            'attribute_name, string_value '
            'FROM attribute_summaries asu '
            'INNER JOIN attributes a USING(attribute_id) '
            'WHERE asu.author = :collection AND asu.category = :schema '
            'ORDER BY rarity_score DESC LIMIT :limit OFFSET :offset '
        )

        res = execute_sql(session, 
            sql,
            {'collection': collection, 'schema': schema, 'limit': limit, 'offset': offset}
        )

        ranking = []

        for item in res:
            ranking.append({
                'collection': item['author'],
                'schema': item['schema'],
                'name': item['attribute_name'] if item['attribute_name'] != 'num_traits' else 'Number of Traits',
                'value': item['string_value'],
                'total': item['total'],
                'totalSchema': item['total_schema'],
                'percentage': float(item['total'] / item['total_schema']),
                'rarityScore': item['rarity_score'],
                'floor': str(item['floor']) + ' WAX' if item['floor'] else 'Not listed',
            })

        return ranking
    except SQLAlchemyError as e:
        logging.error(e)
        session.rollback()
        raise e
    finally:
        session.remove()


@cache.memoize(timeout=60)
def get_pfp_top_holders(collection, schema, limit=100, offset=0):
    session = create_session()
    try:

        sql = (
            'SELECT p.* '
            'FROM pfp_top_owners_mv p '
            'WHERE author = :collection AND schema = :schema '
            'ORDER BY count DESC LIMIT :limit OFFSET :offset'
        )

        res = execute_sql(session, 
            sql,
            {'collection': collection, 'schema': schema, 'limit': limit, 'offset': offset}
        )

        ranking = []

        for item in res:
            ranking.append({
                'collection': item['collection'],
                'schema': item['schema'],
                'owner': item['owner'],
                'total': item['count'],
            })

        return ranking
    except SQLAlchemyError as e:
        logging.error(e)
        session.rollback()
        raise e
    finally:
        session.remove()


@cache.memoize(timeout=60)
def get_pfp_ranking(collection, schema, limit=100, offset=0):
    session = create_session()
    try:

        sql = (
            'SELECT p.*, n.name, d.data AS mdata, a.template_id, a.timestamp, '
            'array_agg(json_build_object(\'total\', asu.total, \'floor\', asu.floor, '
            '\'total_schema\', asu.total_schema, \'rarity_score\', asu.rarity_score, '
            '\'attribute_name\', attribute_name, \'string_value\', string_value)) AS attributes '
            'FROM pfp_ranking_mv p '
            'INNER JOIN pfp_assets aa USING (asset_id) ' 
            'INNER JOIN assets a USING(asset_id) ' 
            'LEFT JOIN names n USING(name_id) '
            'LEFT JOIN data d ON d.data_id = a.mutable_data_id '
            'INNER JOIN attributes att ON att.attribute_id = ANY(aa.attribute_ids) ' 
            'INNER JOIN attribute_stats asu USING(attribute_id) '
            'WHERE p.author = :collection AND p.schema = :schema AND NOT burned '
            'GROUP BY 1, 2, 3, 4, 5, 6, 7, 8, 9, 10 ORDER BY rank ASC LIMIT :limit OFFSET :offset '
        )

        res = execute_sql(session, 
            sql,
            {'collection': collection, 'schema': schema, 'limit': limit, 'offset': offset}
        )

        ranking = []

        for item in res:
            traits = []
            for trait in item['attributes']:
                traits.append(_format_trait(trait))
            ranking.append({
                'asset': {
                    'assetId': item['asset_id'],
                    'templateId': item['template_id'],
                    'name': item['name'],
                    'timestamp': item['timestamp'].strftime("%Y-%m-%d %H:%M:%S UTC"),
                    'data': json.loads(item['mdata']),
                    'collection': item['collection'],
                    'schema': item['schema'],
                },
                'owner': item['owner'],
                'rank': item['rank'],
                'rarityScore': item['rarity_score'],
                'traits': traits
            })

        return ranking
    except SQLAlchemyError as e:
        logging.error(e)
        session.rollback()
        raise e
    finally:
        session.remove()


@cache.memoize(timeout=60)
def get_pfp_collections_info(collection, limit=100, offset=0):
    session = create_session()
    try:

        sql = (
            'SELECT c.collection_name, c.name, c.image, images, socials, creator_info, url, market_fee, '
            'description, a.schema, a.asset_count, a.owner_count '
            'FROM pfp_schemas_mv a '
            'INNER JOIN collections c ON a.author = c.collection_name '
            'WHERE collection_name = :collection LIMIT :limit OFFSET :offset'
        ) if collection else (
            'SELECT c.collection_name, c.name, c.image, images, socials, creator_info, url, market_fee, '
            'description, a.schema, a.asset_count, a.owner_count '
            'FROM pfp_schemas_mv a '
            'INNER JOIN collections c ON a.author = c.collection_name '
            'WHERE collection_name NOT IN (SELECT author FROM blacklisted_authors WHERE author = c.collection_name) '
            'LIMIT :limit OFFSET :offset'
        )

        res = execute_sql(session, 
            sql,
            {'collection': collection, 'limit': limit, 'offset': offset}
        )

        collections = {}

        for item in res:
            collection_name = item['collection_name']
            schema = item['schema']
            if collection_name not in collections:
                collections[collection_name] = {
                    'schemas': {}
                }
            if schema not in collections[collection_name]:
                collections[collection_name]['schemas'][schema] = {}
            collections[collection_name]['image'] = item['image']
            collections[collection_name]['images'] = json.loads(item['images']) if item['images'] else {}
            collections[collection_name]['socials'] = json.loads(item['socials']) if item['socials'] else {}
            collections[collection_name]['creator_info'] = json.loads(item['creator_info']) if item['creator_info'] else {}
            collections[collection_name]['description'] = item['description']
            collections[collection_name]['url'] = item['url']
            collections[collection_name]['schemas'][schema]['assets'] = item['asset_count']
            collections[collection_name]['schemas'][schema]['collectors'] = item['owner_count']

        collection_arr = []

        for collection_name in collections.keys():
            collection = collections[collection_name]
            schema_arr = []
            for schema_name in collection['schemas'].keys():
                schema = collection['schemas'][schema_name]
                schema['name'] = schema_name
                schema_arr.append(schema)
            collection['name'] = collection_name
            collection['schemas'] = schema_arr
            collection_arr.append(collection)

        return collection_arr
    except SQLAlchemyError as e:
        logging.error(e)
        session.rollback()
        raise e
    finally:
        session.remove()