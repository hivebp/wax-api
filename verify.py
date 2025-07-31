from api import logging
from api import cache

from sqlalchemy.exc import SQLAlchemyError

from logic import _format_image, _format_collection_thumbnail, create_session, execute_sql


@cache.memoize(timeout=60)
def get_verify_status(collection):
    session = create_session()
    try:

        sql = (
            'SELECT market, list_name, c.name as collection_name, c.image as collection_image '
            'FROM market_statuses ms '
            'LEFT JOIN collections c ON (ms.collection = c.collection_name) '
            'WHERE ms.collection = :collection '
        )

        res = execute_sql(
            session,
            sql,
            {'collection': collection})

        statuses = []

        collection_name = ''
        image = ''

        for status in res:
            collection_name = status['collection_name']
            image = status['collection_image']
            statuses.append({'market': status['market'], 'status': status['list_name']})

        return {
            'collection': {
                'name': collection,
                'displayName': collection_name,
                'image': _format_image(image),
                'thumbnail': _format_collection_thumbnail(collection, image),
            }, 'statuses': statuses}
    except SQLAlchemyError as e:
        logging.error(e)
        session.rollback()
        raise e
    finally:
        session.remove()


def get_voting_status(collection):
    session = create_session()
    try:
        sql = (
            'SELECT voter, amount '
            'FROM collection_votes '
            'WHERE collection = :collection '
        )

        res = execute_sql(session, sql,
            {'collection': collection})

        votes = []

        downvotes = 0
        upvotes = 0
        total_votes = 0
        for status in res:
            if status['amount'] < 0:
                downvotes -= status['amount']
            elif status['amount'] > 0:
                upvotes += status['amount']
            total_votes += status['amount']
            votes.append({'voter': status['voter'], 'amount': status['amount']})

        return {
            'collection': collection, 'upvotes': upvotes, 'downvotes': downvotes,
            'totalVotes': total_votes, 'voters': votes, 'totalVoters': len(votes)
        }
    except SQLAlchemyError as e:
        logging.error(e)
        session.rollback()
        raise e
    finally:
        session.remove()


@cache.memoize(timeout=60)
def get_top_voted_collections(limit, offset):
    session = create_session()
    try:
        sql = (
            'SELECT v.*, c.name as collection_name, c.image AS collection_image '
            'FROM total_votes_v v '
            'LEFT JOIN collections c ON (c.collection_name = v.collection) '
            'ORDER BY total_voters DESC LIMIT :limit OFFSET :offset '
        )

        res = execute_sql(session, sql, {'limit': limit, 'offset': offset})

        collections = []

        for status in res:
            collections.append(
                {'collection': {
                    'name': status['collection'],
                    'displayName': status['collection_name'],
                    'image': _format_image(status['collection_image']),
                    'thumbnail': _format_collection_thumbnail(status['collection'], status['collection_image'])
                }, 'stats': {
                    'totalVotes': status['total_votes'],
                    'upvotes': status['upvotes'],
                    'downvotes': status['downvotes'],
                    'ratio': status['ratio'],
                    'totalVoters': status['total_voters']
                }}
            )

        return collections
    except SQLAlchemyError as e:
        logging.error(e)
        session.rollback()
        raise e
    finally:
        session.remove()


@cache.memoize(timeout=60)
def get_top_voted_collections_total_rows():
    session = create_session()
    try:
        sql = (
            'SELECT count(*) AS total_rows FROM total_votes_v'
        )

        res = execute_sql(session, sql)

        total_rows = {'totalRows': res.first()[0]}

        return total_rows
    except SQLAlchemyError as e:
        logging.error(e)
        session.rollback()
        raise e
    finally:
        session.remove()