import datetime
import json
import random
import time

from api import logging
from api import cache

from sqlalchemy.exc import SQLAlchemyError

from logic import _format_image, DATE_FORMAT_STRING, _format_banner, _format_thumbnail, _format_collection_thumbnail, \
    create_session, execute_sql


def _format_assets(assets):
    res = []
    for asset in assets:
        a = {}
        if 'category' in asset.keys() and asset['category']:
            a['schema'] = asset['category']
        if 'author' in asset.keys() and asset['author']:
            a['author'] = asset['author']
        if 'owner' in asset.keys() and asset['owner']:
            a['owner'] = asset['owner']
        if 'number' in asset.keys() and asset['number']:
            a['number'] = asset['number']
        if 'name' in asset.keys() and asset['name']:
            a['name'] = asset['name']
        if 'standard' in asset.keys() and asset['standard']:
            a['standard'] = asset['standard']
        if 'favorited' in asset.keys() and asset['favorited']:
            a['isFavorited'] = True
        if 'mint' in asset.keys() and asset['mint']:
            a['mint'] = asset['mint']
        if 'image' in asset.keys() and asset['image']:
            a['image'] = _format_image(asset['image'])
        if 'thumbnail' in asset.keys() and asset['thumbnail']:
            a['thumbnail'] = _format_thumbnail(asset['thumbnail']) if asset.keys() and asset['thumbnail'] else None,
        if 'backimg' in asset.keys() and asset['backimg']:
            a['backimg'] = _format_image(asset['backimg'])
        if 'author_image' in asset.keys() and asset['author_image']:
            a['authorImg'] = _format_image(asset['author_image'])
        if 'upliftium' in asset.keys() and asset['upliftium']:
            a['upliftium'] = float(asset['upliftium'])
        if 'variant' in asset.keys() and asset['variant']:
            a['variant'] = asset['variant']
        if 'rarity' in asset.keys() and asset['rarity']:
            a['rarity'] = asset['rarity']
        if 'color' in asset.keys() and asset['color']:
            a['color'] = asset['color']
        if 'border' in asset.keys() and asset['border']:
            a['border'] = asset['border']
        if 'type' in asset.keys() and asset['type']:
            a['type'] = asset['type']
        if 'attr7' in asset.keys() and asset['attr7']:
            a['attr7'] = asset['attr7']
        if 'attr8' in asset.keys() and asset['attr8']:
            a['attr8'] = asset['attr8']
        if 'attr9' in asset.keys() and asset['attr9']:
            a['attr9'] = asset['attr9']
        if 'attr10' in asset.keys() and asset['attr10']:
            a['attr10'] = asset['attr10']
        if 'total' in asset.keys() and asset['total']:
            a['total'] = asset['total']
        if 'burned' in asset.keys() and asset['burned']:
            a['burned'] = asset['burned']
        if 'average' in asset.keys() and asset['average']:
            a['average'] = asset['average']
        if 'verified' in asset.keys() and asset['verified']:
            a['verified'] = asset['verified']
        if 'usd_average' in asset.keys() and asset['usd_average']:
            a['usd_average'] = asset['usd_average']
        if 'average' in asset.keys() and asset['average']:
            a['average'] = asset['average']
        if 'lowest' in asset.keys() and asset['lowest']:
            a['lowest'] = asset['lowest']
        if 'usd_lowest' in asset.keys() and asset['usd_lowest']:
            a['usd_lowest'] = asset['usd_lowest']
        if 'last_sold' in asset.keys() and asset['last_sold']:
            a['last_sold'] = asset['last_sold']
        if 'usd_last_sold' in asset.keys() and asset['usd_last_sold']:
            a['usd_last_sold'] = asset['usd_last_sold']
        if 'num_sales' in asset.keys() and asset['num_sales']:
            a['num_sales'] = asset['num_sales']
        if 'rarity_score' in asset.keys() and asset['rarity_score']:
            a['rarity_score'] = asset['rarity_score']
        if 'asset_id' in asset.keys() and asset['asset_id']:
            a['assetId'] = asset['asset_id']
        if 'aasset_id' in asset.keys() and asset['aasset_id']:
            a['aAssetId'] = asset['aasset_id']
        if 'mdata' in asset.keys() and asset['mdata']:
            a['mdata'] = asset['mdata'] if 'mdata' in asset.keys() else None

        res.append(a)
    return res


def _format_response(item, size=240, blacklisted=False):
    response = {}

    if blacklisted or ('blacklisted' in item.keys() and item['blacklisted']):
        response['blacklisted'] = True

    for key in item.keys():
        if key == 'collection_name':
            response['collectionName'] = item['collection_name']
        elif key == 'pfp_attributes':
            if item['pfp_attributes'] and item['pfp_attributes'][0]:
                response['pfpAttributes'] = item['pfp_attributes']
        elif key == 'collection_image' and item['collection_image'] and 'author' in item.keys() and item['author']:
            response['collectionImage'] = _format_image(item['collection_image'])
            response['collectionThumbnail'] = _format_collection_thumbnail(item['author'], item['collection_image'])
        elif key == 'name_pattern':
            if item['name_pattern']:
                response['namePattern'] = item['name_pattern']
        elif key == 'is_pfp':
            if item['is_pfp']:
                response['isPFP'] = True
        elif key == 'pack_id':
            response['packId'] = item['pack_id']
        elif key == 'num_remaining':
            response['numRemaining'] = item['num_remaining']
        elif key == 'release_id':
            response['releaseId'] = item['release_id']
        elif key == 'read':
            response['read'] = item['read']
        elif key == 'attributes_floor':
            response['attributesFloor'] = item['attributes_floor']
        elif key == 'attribute_name':
            response['floorAttributeName'] = item['attribute_name']
        elif key == 'for_sale' and item['for_sale']:
            response['forSale'] = item['for_sale']
        elif key == 'string_value' or key == 'int_value' or key == 'bool_value' or key == 'float_value':
            if item['string_value']:
                response['floorAttributeValue'] = item['string_value']
            elif item['int_value'] or item['int_value'] == 0:
                response['floorAttributeValue'] = item['int_value']
            elif item['float_value'] or item['float_value'] == 0:
                response['floorAttributeValue'] = item['float_value']
            elif item['bool_value'] or item['bool_value'] == False:
                response['floorAttributeValue'] = item['bool_value']
        elif key == 'backed_tokens':
            response['backedTokens'] = item['backed_tokens']
        elif key == 'country':
            response['country'] = item['country']
        elif key == 'claimer':
            response['claimer'] = item['claimer']
        elif key == 'amount':
            response['amount'] = item['amount']
        elif key == 'referrer':
            response['referrer'] = item['referrer']
        elif key == 'listings':
            listings = []
            for listing in item['listings']:
                listings.append(_format_response(listing, size, blacklisted))
            response['listings'] = listings
        elif key == 'assets':
            assets = []
            for asset in item['assets']:
                assets.append(_format_response(asset, size, blacklisted))
            response['assets'] = assets
        elif key == 'templates':
            templates = []
            for template in item['templates']:
                if template['template_id']:
                    templates.append(_format_response(template, size, blacklisted))
            response['templates'] = templates
        elif key == 'transaction_id':
            response['transactionId'] = item['transaction_id']
        elif key == 'seq':
            response['globalSequence'] = item['seq']
        elif key == 'template_id':
            response['templateId'] = item['template_id']
        elif key == 'market':
            response['market'] = item['market']
        elif key == 'taker' and item['taker']:
            response['market'] = item['taker']
        elif key == 'seller':
            response['seller'] = item['seller']
        elif key == 'staker':
            response['sender'] = item['staker']
        elif key == 'action':
            response['action'] = item['action']
        elif key == 'sender':
            response['sender'] = item['sender']
        elif key == 'receiver':
            response['receiver'] = item['receiver']
        elif key == 'buyer':
            response['buyer'] = item['buyer']
        elif key == 'usd_wax':
            response['usd_wax'] = item['usd_wax']
        elif key == 'offer' and item['offer'] and item['offer'] > 0:
            response['offer'] = item['offer']
        elif key == 'usd_offer' and item['usd_offer'] and item['usd_offer'] > 0:
            response['usd_offer'] = item['usd_offer']
        elif key == 'price' and item['price'] and item['price'] > 0:
            response['price'] = item['price']
        elif key == 'bid' and item['bid'] and item['bid'] > 0:
            response['bid'] = item['bid']
        elif key == 'usd_price' and item['usd_price'] and item['usd_price'] > 0:
            response['usdPrice'] = item['usd_price']
        elif key == 'transaction_id':
            response['transactionId'] = item['transaction_id']
        elif key == 'transaction_id':
            response['transactionId'] = item['transaction_id']
        elif key == 'offer_type' and item['offer_type'] == 'auction':
            response['isAuction'] = True
        elif key == 'auction_id' and item['auction_id']:
            response['auctionId'] = item['auction_id']
        elif key == 'currency':
            response['currency'] = item['currency']
        elif key == 'name':
            response['name'] = item['name']
        elif key == 'description':
            response['description'] = item['description']
        elif key == 'bundle' and item['bundle']:
            response['bundle'] = item['bundle']
        elif key == 'standard' and item['standard']:
            response['standard'] = item['standard']
            if item['standard'] == 'simpleassets':
                response['transferable'] = True
                response['burnable'] = True
        elif key == 'category' and item['category']:
            response['schema'] = item['category']
        elif key == 'schema' and item['schema']:
            response['schema'] = item['schema']
        elif key == 'author' and item['author']:
            response['author'] = item['author']
        elif key == 'owner' and item['owner']:
            response['owner'] = item['owner']
        elif key == 'mdata' and item['mdata']:
            response['mdata'] = item['mdata']
        elif key == 'idata' and item['idata']:
            response['idata'] = item['idata']
        elif key == 'number' and item['number']:
            response['number'] = item['number']
        elif key == 'favorited' and item['favorited'] and item['favorited'] != '':
            response['isFavorited'] = True
        elif key == 'verified' and item['verified']:
            response['verified'] = item['verified']
        elif key == 'timestamp' and item['timestamp']:
            response['date'] = item['timestamp'].strftime(DATE_FORMAT_STRING)
            response['timestamp'] = datetime.datetime.timestamp(item['timestamp'])
        elif key == 'bidder' and item['bidder']:
            response['bidder'] = item['bidder']
        elif key == 'active' and item['active']:
            response['active'] = True
        elif key == 'num_bids' and item['num_bids']:
            response['numBids'] = item['num_bids']
        elif key == 'author_image' and item['author_image'] and 'author' in item.keys() and item['author']:
            response['collectionImage'] = _format_image(item['author_image'])
            response['collectionThumbnail'] = _format_collection_thumbnail(item['author'], item['author_image'])
        elif key == 'image' and item['image']:
            response['image'] = _format_image(item['image'])
            response['preview'] = _format_banner(item['image'])
        elif key == 'video' and item['video']:
            response['video'] = _format_image(item['video'])
            if 'image' not in response:
                response['image'] = _format_image('video:' + item['video'])
            response['preview'] = _format_banner('video:' + item['video'])
        elif key == 'backimg' and item['backimg']:
            response['backimg'] = _format_image(item['backimg'])
        elif key == 'variant' and item['variant']:
            response['variant'] = item['variant']
        elif key == 'category_2' and item['category_2']:
            response['variant'] = item['category_2']
        elif key == 'rarity' and item['rarity']:
            response['rarity'] = item['rarity']
        elif key == 'rank' and item['rank']:
            response['rank'] = item['rank']
        elif key == 'category_3' and item['category_3']:
            response['rarity'] = item['category_3']
        elif key == 'color' and item['color']:
            response['color'] = item['color']
        elif key == 'border' and item['border']:
            response['border'] = item['border']
        elif key == 'type' and item['type']:
            response['type'] = item['type']
        elif key == 'attr7' and item['attr7']:
            response['attr7'] = item['attr7']
        elif key == 'attr8' and item['attr8']:
            response['attr8'] = item['attr8']
        elif key == 'attr9' and item['attr9']:
            response['attr9'] = item['attr9']
        elif key == 'attr10' and item['attr10']:
            response['attr10'] = item['attr10']
        elif key == 'symbol' and item['symbol']:
            response['symbol'] = item['symbol']
        elif key == 'unpack_url' and item['unpack_url']:
            response['unpackUrl'] = item['unpack_url']
        elif key == 'contract' and item['contract']:
            response['contract'] = item['contract']
        elif key == 'asset_id' and item['asset_id']:
            response['assetId'] = item['asset_id']
        elif key == 'summary_id' and item['summary_id']:
            response['summaryId'] = item['summary_id']
        elif key == 'aasset_id' and item['aasset_id']:
            response['aAssetId'] = item['aasset_id']
        elif key == 'listing_id' and item['listing_id']:
            response['listingId'] = item['listing_id']
        elif key == 'mint' and item['mint']:
            response['mint'] = item['mint']
        elif key == 'my_mint' and item['my_mint']:
            response['myMint'] = item['my_mint']
        elif key == 'total' and item['total']:
            response['total'] = int(item['total'])
        elif key == 'floor_change' and item['floor_change']:
            response['floorChange'] = int(item['floor_change'])
        elif key == 'burnable' and item['burnable']:
            response['burnable'] = True
        elif key == 'transferable' and item['transferable']:
            response['transferable'] = True
        elif key == 'burned' and item['burned']:
            response['isBurned'] = int(item['burned'])
        elif key == 'num_burned' and item['num_burned']:
            response['numBurned'] = int(item['num_burned'])
            response['burned'] = int(item['num_burned'])
        elif key == 'average' and item['average']:
            response['average'] = float(item['average'])
        elif key == 'usd_average' and item['usd_average']:
            response['usd_average'] = float(item['usd_average'])
        elif key == 'lowest' and item['lowest']:
            response['lowest'] = float(item['lowest'])
        elif key == 'thumbnail' and item['thumbnail']:
            response['thumbnail'] = _format_thumbnail(item['thumbnail'])
        elif key == 'universal_preview' and item['universal_preview']:
            response['universalPreview'] = _format_collection_thumbnail(item['universal_preview'], item['author'], size)
        elif key == 'usd_lowest' and item['usd_lowest']:
            response['usd_lowest'] = float(item['usd_lowest'])
        elif key == 'last_sold' and item['last_sold']:
            response['last_sold'] = float(item['last_sold'])
        elif key == 'usd_last_sold' and item['usd_last_sold']:
            response['usd_last_sold'] = float(item['usd_last_sold'])
        elif key == 'revenue' and item['revenue']:
            response['revenue'] = item['revenue']
        elif key == 'usd_revenue' and item['usd_revenue']:
            response['usd_revenue'] = item['usd_revenue']
        elif key == 'num_sales' and item['num_sales']:
            response['num_sales'] = int(item['num_sales'])
        elif key == 'sale_id' and item['sale_id']:
            response['saleId'] = item['sale_id']
        elif key == 'rarity_score' and item['rarity_score']:
            response['rarityScore'] = item['rarity_score']
        elif key == 'ft_name' and item['ft_name']:
            response['ft_name'] = item['ft_name'] if hasattr(item, 'ft_name') and item['ft_name'] else None
        elif key == 'assets' and item['assets']:
            assets = []
            for asset in item['assets']:
                assets.append(_format_response(asset, size, blacklisted))
            response['assets'] = assets
        elif key == 'my_assets' and item['my_assets']:
            response['myAssets'] = _format_assets(item['my_assets'])
        elif key == 'num_owned' and item['num_owned']:
            response['numOwned'] = item['num_owned']
        elif key == 'balance' and (item['balance'] or item['balance'] == 0):
            response['balance'] = float(item['balance'])
        elif key == 'wax_cost' and item['wax_cost']:
            response['craftingCost'] = float(item['wax_cost'])
        elif key == 'max_supply' and item['max_supply']:
            response['maxSupply'] = item['max_supply']
        elif key == 'wax_usd' and item['wax_usd']:
            response['waxUsd'] = item['wax_usd']
        elif key == 'drop_id' and item['drop_id']:
            response['dropId'] = item['drop_id']
        elif key == 'templates_to_mint' and item['templates_to_mint']:
            templates_to_mint = []
            for template in item['templates_to_mint']:
                templates_to_mint.append(_format_response(template, size, blacklisted))
            response['templatesToMint'] = templates_to_mint
        elif key == 'fee' and item['fee']:
            response['fee'] = item['fee']
        elif key == 'start_time' and item['start_time']:
            response['startTime'] = item['start_time']
        elif key == 'unlock_time' and item['unlock_time']:
            response['unlockTime'] = item['unlock_time']
        elif key == 'recipe_templates':
            templates = []
            for template in item['recipe_templates']:
                templates.append(_format_response(template, size, blacklisted))
            response['recipeTemplates'] = templates
        elif key == 'outcome_templates':
            templates = []
            for template in item['outcome_templates']:
                templates.append(_format_response(template, size, blacklisted))
            response['outcomeTemplates'] = templates
        elif key == 'outcomes':
            response['outcomes'] = item['outcomes']
        elif key == 'recipe':
            response['recipe'] = item['recipe']
        elif key == 'num_crafted':
            response['numCrafted'] = item['num_crafted']
        elif key == 'craft_id' and item['craft_id']:
            response['craftId'] = item['craft_id']
        elif key == 'offer_time' and item['offer_time']:
            response['endTime'] = item['offer_time']
        elif key == 'end_time' and item['end_time']:
            response['endTime'] = item['end_time']
        elif key == 'listing_time' and item['listing_time']:
            response['listingTime'] = int(item['listing_time'])
        elif key == 'max_claimable' and item['max_claimable']:
            response['maxClaimable'] = item['max_claimable']
        elif key == 'num_bought' and item['num_bought']:
            response['numClaimed'] = item['num_bought']
        elif key == 'display_data' and item['display_data']:
            response['displayData'] = item['display_data']
        elif key == 'auth_required' and item['auth_required']:
            response['authRequired'] = item['auth_required']
        elif key == 'erased' and item['erased']:
            response['erased'] = item['erased']
        elif key == 'account_limit' and item['account_limit']:
            response['accountLimit'] = item['account_limit']
        elif key == 'num_claimed' and item['num_claimed']:
            response['currentClaimed'] = item['num_claimed']
        elif key == 'account_limit_cooldown' and item['account_limit_cooldown']:
            response['accountLimitCooldown'] = item['account_limit_cooldown']
        elif key == 'ready':
            response['ready'] = item['ready']
        elif key == 'result_id':
            response['resultId'] = item['result_id']
        elif key == 'crafter':
            response['crafter'] = item['crafter']
        elif key == 'result_asset_ids':
            response['assets'] = item['result_asset_ids']
        elif key == 'minted_templates':
            response['templates'] = item['minted_templates']
        elif key == 'token_results':
            response['token'] = item['token_results']
        elif key == 'airdrop_id':
            response['airdropId'] = item['airdrop_id']
        elif key == 'token':
            response['token'] = item['token']
        elif key == 'creator':
            response['creator'] = item['creator']
        elif key == 'min_amount':
            response['minAmount'] = item['min_amount']
        elif key == 'max_amount':
            response['maxAmount'] = item['max_amount']
        elif key == 'ready':
            response['ready'] = item['ready']
        elif key == 'snapshot_time':
            response['snapshotTime'] = item['snapshot_time']
        elif key == 'logo':
            response['logo'] = item['logo']
        elif key == 'holder_contract':
            response['holderContract'] = item['holder_contract']
        elif key == 'holder_contract_logo':
            response['holderContractLogo'] = item['holder_contract_logo']
        elif key == 'claimers':
            response['claimers'] = item['claimers']
        elif key == 'claims':
            response['claims'] = item['claims']
        elif key == 'estimated_wax_price':
            response['estimatedWaxPrice'] = item['estimated_wax_price']
        elif key == 'eligible':
            response['eligible'] = item['eligible']
        elif key == 'claimed':
            response['claimed'] = item['claimed']
        elif key == 'claim_transaction_id':
            response['claimTransactionId'] = item['claim_transaction_id']

    return response


def _format_video(video):
    if video and 'http' in video and 'https://gateway.pinata.cloud/ipfs' not in video:
        return video
    elif video and 'https://gateway.pinata.cloud/ipfs' in video:
        video = video.replace('https://gateway.pinata.cloud/ipfs/', '')
    return 'https://ipfs.hivebp.io/ipfs/{}'.format(video.replace('video:', '').strip())


@cache.memoize(timeout=300)
def load_banners_from_db(source=None):
    session = create_session()
    try:
        res = execute_sql(session,
            'SELECT * FROM banners WHERE end_date > NOW() AND NOW() > start_date {source_clause}'.format(
                source_clause='AND (source = \'both\' OR source = :source)' if source else ''
            ), {'source': source}
        )

        banners = []

        for banner in res:
            banners.append({
                'image': _format_image(banner['image']),
                'url': banner['url']
            })

        return banners
    except SQLAlchemyError as e:
        logging.error(e)
        session.rollback()
        return []
    finally:
        session.remove()


@cache.cached(timeout=60)
def get_banners():
    banners = load_banners_from_db()

    random.shuffle(banners)
    if len(banners) > 0:
        return banners
    else:
        return {}


def get_wuffi_airdrop(airdrop_id, username):
    session = create_session()
    try:
        search_dict = {
            'airdrop_id': airdrop_id
        }
        claim_clause = ''
        if username:
            claim_clause = (
                ', ('
                '   SELECT transaction_id '
                '   FROM wuffi_airdrop_claims w '
                '   LEFT JOIN chronicle_transactions USING (seq) WHERE w.account = :username '
                '   AND airdrop_id = wa.airdrop_id '
                ') AS claim_transaction_id '
            )
            search_dict['username'] = username

        sql = (
            'SELECT airdrop_id, token, contract, creator, min_amount, max_amount, display_data, ready, et.symbol, '
            'et.logo, extract(epoch from snapshot_time AT time zone \'Europe/Berlin\')::bigint AS snapshot_time, '
            'et2.logo AS holder_contract_logo, holder_contract, '
            '(SELECT COUNT(DISTINCT claimer) FROM wuffi_airdrop_claimers WHERE airdrop_id = wa.airdrop_id) AS claimers,'
            '(SELECT COUNT(DISTINCT account) FROM wuffi_airdrop_claims WHERE airdrop_id = wa.airdrop_id) AS claims '
            '{claim_clause} '
            'FROM wuffi_airdrops wa '
            'LEFT JOIN eos_tokens et ON et.account = wa.contract AND position(et.symbol IN token) > 0 '
            'LEFT JOIN eos_tokens et2 ON et2.account = wa.holder_contract AND position(et2.symbol IN min_amount) > 0 '
            'WHERE airdrop_id = :airdrop_id '
            'GROUP BY 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13'.format(claim_clause=claim_clause)
        )

        airdrop = execute_sql(
            session,
            sql,
            search_dict
        ).first()

        if airdrop:
            return _format_response(airdrop)

        return None
    except SQLAlchemyError as e:
        logging.error(e)
        session.rollback()
        raise e
    finally:
        session.remove()


def get_num_drops(collection):
    session = create_session()
    try:
        res = execute_sql(session,
            'SELECT COUNT(1) AS num_drops FROM drops '
            'WHERE NOT erased AND NOT is_hidden AND collection = :collection ', {
                'collection': collection
            }
        ).first()

        if res:
            return {'numDrops': res['num_drops']}
        else:
            return {'numDrops': 0}
    except SQLAlchemyError as e:
        logging.error(e)
        session.rollback()
        return []
    finally:
        session.remove()


def get_num_auctions(collection):
    session = create_session()
    try:
        res = execute_sql(session,
            'SELECT COUNT(1) AS num_auctions '
            'FROM auctions au '
            'LEFT JOIN assets ON asset_id = asset_ids[1] '
            'WHERE au.collection = :collection AND au.end_time > NOW() ', {
                'collection': collection
            }
        ).first()

        if res:
            return {'numAuctions': res['num_auctions']}
        else:
            return {'numAuctions': 0}
    except SQLAlchemyError as e:
        logging.error(e)
        session.rollback()
        return []
    finally:
        session.remove()


def get_num_crafts(collection):
    session = create_session()
    try:
        res = execute_sql(
            session,
            'SELECT COUNT(1) AS num_crafts FROM crafts '
            'WHERE NOT erased AND collection = :collection ', {
                'collection': collection
            }
        ).first()

        if res:
            return {'numCrafts': res['num_crafts']}
        else:
            return {'numCrafts': 0}
    except SQLAlchemyError as e:
        logging.error(e)
        session.rollback()
        return []
    finally:
        session.remove()


def get_collection_clause(author, prefix=''):
    author_clause = ''
    if author and author != '*':
        if isinstance(author, tuple):
            author_clause = ' AND {}collection IN :collection '.format(prefix)
        else:
            author_clause = ' AND {}collection = :collection '.format(prefix)
    return author_clause


def get_collection_drops(collection, limit, offset, include_erased):
    session = create_session()
    try:
        author_clause = get_collection_clause(collection, 'd2.')

        search_dict = {'limit': limit, 'offset': offset}

        if collection and collection != '*':
            search_dict['collection'] = collection

        res = execute_sql(session,
            'WITH usd_rate AS (SELECT usd FROM usd_prices ORDER BY timestamp DESC LIMIT 1) '
            'SELECT drop_id, price, currency, fee, '
            'extract(epoch from start_time AT time zone \'Europe/Berlin\')::bigint AS start_time, '
            'extract(epoch from end_time AT time zone \'Europe/Berlin\')::bigint AS end_time, '
            'd2.timestamp, account_limit, is_hidden, '
            'account_limit_cooldown, max_claimable, '
            '('
            '   SELECT SUM(amount) FROM drop_actions da '
            '   WHERE da.drop_id = d2.drop_id AND da.contract = d2.contract'
            ') AS num_claimed, c.verified, display_data, '
            '(SELECT usd FROM usd_rate) as wax_usd, contract, cn.name as collection_name, t.collection, auth_required, '
            'pd.drop_id AS is_pfp, json_agg(json_build_object('
            '\'template_id\', template_id, \'schema\', t.schema, \'name\', tn.name, \'image\', ti.image, '
            '\'max_supply\', t.max_supply, \'idata\', td.data)) templates_to_mint '
            'FROM drops d2 '
            'INNER JOIN templates t ON (t.template_id = ANY(d2.templates_to_mint)) '
            'LEFT JOIN names tn ON t.name_id = tn.name_id '
            'LEFT JOIN images ti ON t.image_id = ti.image_id '
            'LEFT JOIN data td ON t.immutable_data_id = td.data_id '
            'LEFT JOIN pfp_drop_data pd USING(drop_id, contract) '
            'INNER JOIN collections c ON (d2.collection = c.collection) '
            'LEFT JOIN names cn ON (cn.name_id = c.name_id) '
            'WHERE {erased_clause} {author_clause} AND contract = \'nfthivedrops\' '
            'GROUP BY 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20 '
            'ORDER BY d2.timestamp DESC LIMIT :limit OFFSET :offset '.format(
                author_clause=author_clause,
                erased_clause='NOT erased' if not include_erased else 'TRUE'
            ),
            search_dict
        )

        drops = []

        for drop in res:
            drops.append(_format_response(drop))

        return drops
    except SQLAlchemyError as e:
        logging.error(e)
        session.rollback()
        raise e
    finally:
        session.remove()


def get_collection_total_drops(collection):
    session = create_session()
    try:
        author_clause = get_collection_clause(collection, 'd2.')

        search_dict = {}

        if collection and collection != '*':
            search_dict['collection'] = collection

        res = execute_sql(session,
            'SELECT COUNT(1) as cnt '
            'FROM drops d2 '
            'WHERE NOT erased {author_clause} '
            'AND contract = \'nfthivedrops\' '.format(author_clause=author_clause),
            search_dict
        ).first()

        return {'total': res['cnt']}
    except SQLAlchemyError as e:
        logging.error(e)
        session.rollback()
        raise e
    finally:
        session.remove()


def get_collection_crafts(collection, limit, offset, include_erased):
    session = create_session()
    try:
        author_clause = get_collection_clause(collection, 'b.')

        search_dict = {'limit': limit, 'offset': offset}

        if collection and collection != '*':
            search_dict['collection'] = collection

        res = execute_sql(session,
            'SELECT b.*, b2.outcomes, b2.recipe FROM ('
            'SELECT craft_id, extract(epoch from unlock_time AT time zone \'Europe/Berlin\')::bigint AS unlock_time, '
            'b.timestamp, num_crafted, total, display_data, c.verified, '
            'ci.image AS collection_image, cn.name AS collection_name, b.collection, b.ready, '
            'array_agg(json_build_object(\'template_id\', outcome_template_id, \'collection\', t1.collection, '
            '\'image\', t1i.image, \'video\', t1v.video, \'schema\', t1.schema)) AS outcome_templates, '
            'array_agg(json_build_object(\'template_id\', recipe_template_id, \'collection\', t2.collection, '
            '\'image\', t2i.image, \'video\', t2v.video, \'schema\', t2.schema)) AS recipe_templates ' 
            'FROM ('
            '    SELECT craft_id, unlock_time, timestamp, display_data, collection, ready, (SELECT COUNT(1) '
            '    FROM craft_actions WHERE craft_id = b.craft_id) AS num_crafted, total, '
            '    CAST(json_array_elements(outcomes->\'outcomes\')->>\'template_id\' AS bigint) AS outcome_template_id, '
            '    CAST(json_array_elements(recipe->\'ingredients\')->>\'template_id\' AS bigint) AS recipe_template_id, '
            '    json_array_elements(outcomes->\'token_outcomes\') AS token_outcomes, '
            '    json_array_elements(recipe->\'ingredients\')AS token_ingredients '
            '    FROM crafts b WHERE {erased_clause} {author_clause}'
            ') b '
            'LEFT JOIN collections c ON (c.collection = b.collection) '
            'LEFT JOIN names cn ON (cn.name_id = c.name_id) '
            'LEFT JOIN images ci ON (ci.image_id = c.image_id) '
            'LEFT JOIN templates t1 ON (outcome_template_id = t1.template_id) '
            'LEFT JOIN videos t1v ON (t1v.video_id = t1.video_id) '
            'LEFT JOIN images t1i ON (t1i.image_id = t1.image_id) '
            'LEFT JOIN templates t2 ON (recipe_template_id = t2.template_id) '
            'LEFT JOIN videos t2v ON (t2v.video_id = t2.video_id) '
            'LEFT JOIN images t2i ON (t2i.image_id = t2.image_id) '
            'GROUP BY 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11 '
            'ORDER BY b.timestamp DESC '
            'LIMIT :limit OFFSET :offset'
            ') b LEFT JOIN crafts b2 USING(craft_id)'
            'ORDER BY b.timestamp DESC '.format(
                author_clause=author_clause,
                erased_clause='NOT erased' if not include_erased else 'TRUE'
            ),
            search_dict
        )

        drops = []

        for drop in res:
            drops.append(_format_response(drop))

        return drops
    except SQLAlchemyError as e:
        logging.error(e)
        session.rollback()
        raise e
    finally:
        session.remove()


def get_minting_state(drop_id):
    session = create_session()
    try:
        drop = execute_sql(session,
            'SELECT COUNT(1) AS num_claimed, '
            'SUM(CASE when ipfs IS NOT NULL THEN 1 ELSE 0 END) AS rendered, '
            '(SELECT COUNT(1) FROM pfp_mints WHERE drop_id = :drop_id) as minted '
            'FROM pfp_results WHERE drop_id = :drop_id ',
            {'drop_id': drop_id}).first()

        if drop:
            return {'numClaimed': drop['num_claimed'], 'numRendered': drop['rendered'], 'numMinted': drop['minted']}
        return {'numClaimed': 0, 'numRendered': 0, 'numMinted': 0}
    except SQLAlchemyError as e:
        logging.error(e)
        session.rollback()
        raise e
    finally:
        session.remove()


def get_minting_state_craft(craft_id):
    session = create_session()
    try:
        drop = execute_sql(session,
            'SELECT COUNT(1) AS num_claimed, SUM(CASE when mm.ipfs IS NOT NULL THEN 1 ELSE 0 END) AS rendered, '
            'SUM(CASE when mm.ipfs IS NOT NULL THEN 1 ELSE 0 END) as minted '
            'FROM mirror_results mr '
            'LEFT JOIN mirror_mints mm ON (CAST(mr.result_id AS varchar) = mm.result_id) '
            'WHERE craft_id = :craft_id ',
            {'craft_id': craft_id}).first()

        if drop:
            return {'numClaimed': drop['num_claimed'], 'numRendered': drop['rendered'], 'numMinted': drop['minted']}
        return {'numClaimed': 0, 'numRendered': 0, 'numMinted': 0}
    except SQLAlchemyError as e:
        logging.error(e)
        session.rollback()
        raise e
    finally:
        session.remove()


def get_usd_wax():
    session = create_session()
    try:
        result = execute_sql(session,
            'SELECT usd FROM usd_prices ORDER BY timestamp DESC LIMIT 1'
        ).first()

        return {'usd_wax': result['usd']}
    except SQLAlchemyError as e:
        logging.error(e)
        session.rollback()
        raise e
    finally:
        session.remove()


def get_schema_templates(collection, schema):
    session = create_session()
    try:
        templates = []
        res = execute_sql(
            session,
            'SELECT t.template_id, ti.image, tn.name, t.burnable, t.transferable, '
            '   coalesce(sup.num_minted, 0) AS issued_supply, t.max_supply '
            'FROM templates t '
            'LEFT JOIN images ti ON ti.image_id = t.image_id '
            'LEFT JOIN names tn ON tn.name_id = t.name_id '
            'LEFT JOIN templates_minted_mv sup USING(template_id) '
            'WHERE t.collection = :collection '
            'AND t.schema = :schema '
            'ORDER BY t.template_id DESC', {
                'collection': collection,
                'schema': schema
            }
        )

        if res:
            for row in res:
                templates.append({
                    'templateId': row['template_id'],
                    'image': row['image'],
                    'name': row['name'],
                    'burnable': row['burnable'],
                    'transferable': row['transferable'],
                    'issuedSupply': int(row['issued_supply']),
                    'maxSupply': int(row['max_supply'])
                })
        return templates

    except SQLAlchemyError as e:
        logging.error(e)
        session.rollback()
        return []
    finally:
        session.remove()


@cache.memoize(timeout=300)
def quick_search(term):
    session = create_session()
    try:
        res = execute_sql(session,
            'SELECT name, type '
            'FROM search_names_mv '
            'LEFT JOIN collection_volumes_mv USING(author) '
            'WHERE name ilike :term '
            'ORDER BY volume_168h DESC NULLS LAST, type DESC, name ASC LIMIT 10',
            {'term': '%{}%'.format(term)}
        )
        names = []
        for item in res:
            names.append({'label': item['name'], 'type': item['type']})
        return names
    except SQLAlchemyError as e:
        logging.error(e)
        session.rollback()
    finally:
        session.remove()


@cache.memoize(timeout=300)
def search_term(term, name):
    #if name == 'assets':
    #    if _is_asset_name(term) or _is_asset(term) or _is_template(term):
    #        return {'assets': search_assets(term)}
    #    else:
    #        return {'assets': []}
    #if name == 'sales':
    #    if _is_asset_name(term) or _is_asset(term) or _is_template(term):
    #        return {'sales': search_sales(term)}
    #    else:
    #        return {'sales': []}
    #if name == 'collections':
    #    if _is_asset(term) or _is_template(term):
    #        return {'collections': []}
    #    else:
    #        return {'collections': search_collections(term)}
    #if name == 'schemas':
    #    if _is_asset(term) or _is_template(term):
    #        return {'schemas': []}
    #    else:
    #        return {'schemas': search_schemas(term)}
    #if name == 'users':
    #    if _is_asset(term) or _is_template(term):
    #        return {'users': []}
    #    else:
    #        return {'users': get_users(None, term, 40)}
    #if name == 'crafts':
    #    if _is_asset(term) or _is_template(term):
    #        return {'crafts': []}
    #    else:
    #        return {'crafts': get_craft_term(term)}
    #if name == 'drops':
    #    if _is_asset(term) or _is_template(term):
    #        return {'drops': []}
    #    else:
    #        return {'drops': get_drops_term(term)}
    return None


@cache.memoize(timeout=300)
def get_users(collection, term, limit):
    users = []
    session = create_session()
    try:
        if term and len(term) > 12:
            return users
        if term:
            if collection and collection != '*':
                res = execute_sql(
                    session,
                    'SELECT owner, image, num_assets, wax_value, usd_value '
                    'FROM collection_users_mv u '
                    'LEFT JOIN user_pictures_mv p ON (owner = user_name) '
                    'WHERE collection = :collection {owner_term} '
                    'ORDER BY usd_value DESC NULLS LAST LIMIT :limit'.format(
                        owner_term=' AND owner = :term ' if term else ''), {
                        'collection': collection, 'limit': 1, 'term': term
                    }
                ).first()
            else:
                res = execute_sql(
                    session,
                    'SELECT owner, image, num_assets, wax_value, usd_value '
                    'FROM users_mv u '
                    'LEFT JOIN user_pictures_mv p ON (owner = user_name) '
                    'WHERE TRUE {owner_term} '
                    'ORDER BY usd_value DESC NULLS LAST LIMIT :limit'.format(
                        owner_term=' AND owner = :term ' if term else ''), {
                        'limit': limit, 'term': term
                    }
                ).first()

            if res:
                users.append({
                    'user': res['owner'],
                    'image': res['image'],
                    'numAssets': int(res['num_assets']) if res['num_assets'] else 0,
                    'value': float(res['wax_value']) if res['wax_value'] else 0,
                    'usdValue': float(res['usd_value']) if res['usd_value'] else 0
                })
                return users

        if collection and collection != '*':
            res = execute_sql(
                session,
                'SELECT owner, image, num_assets, wax_value, usd_value '
                'FROM collection_users_mv u '
                'LEFT JOIN user_pictures_mv p ON (owner = user_name) '
                'WHERE collection = :collection {owner_term} '
                'ORDER BY usd_value DESC NULLS LAST LIMIT :limit'.format(
                    owner_term=' AND owner like :term' if term else ''), {
                    'collection': collection, 'limit': limit, 'term': '{}%'.format(term)
                }
            )
        else:
            res = execute_sql(
                session,
                'SELECT owner, image, num_assets, wax_value, usd_value '
                'FROM users_mv u '
                'LEFT JOIN user_pictures_mv p ON (owner = user_name) '
                'WHERE TRUE {owner_term} '
                'ORDER BY usd_value DESC NULLS LAST LIMIT :limit'.format(
                    owner_term=' AND owner like :term' if term else ''), {
                    'limit': limit, 'term': '{}%'.format(term)
                }
            )

        if res:
            for row in res:
                users.append({
                    'user': row['owner'],
                    'image': row['image'],
                    'numAssets': int(row['num_assets']) if row['num_assets'] else 0,
                    'value': float(row['wax_value']) if row['wax_value'] else 0,
                    'usdValue': float(row['usd_value']) if row['usd_value'] else 0
                })

        return users
    except SQLAlchemyError as e:
        logging.error(e)
        session.rollback()
        return []
    finally:
        session.remove()


def get_buy_offer_assets(seller, buyoffer_id):
    session = create_session()
    try:
        res = execute_sql(session,
            'SELECT asset_id, mint '
            'FROM assets WHERE owner = :seller AND (collection, template_id) = ('
            'SELECT collection, template_id FROM atomicmarket_template_buy_offers '
            'WHERE buyoffer_id = :buyoffer_id) '
            'AND NOT burned AND contract = \'atomicassets\'',
            {'buyoffer_id': buyoffer_id, 'seller': seller}
        )

        assets = []

        for asset in res:
            assets.append({
                'assetId': asset['asset_id'],
                'mint': asset['mint'],
            })

        return assets
    except SQLAlchemyError as e:
        logging.error(e)
        session.rollback()
        raise e
    finally:
        session.remove()


def get_pfps(collection):
    session = create_session()
    try:
        res = execute_sql(
            session,
            'SELECT collection, schema FROM pfp_schemas '
            'LEFT JOIN volume_collection_1_days_mv USING(collection) '
            '{author_clause} '
            'ORDER BY wax_volume DESC NULLS LAST '
            ''.format(author_clause='WHERE collection = :collection' if collection != '*' else ''), {
                'collection': collection
            }
        )

        pfps = {}
        for item in res:
            if item['collection'] not in pfps:
                pfps[item['collection']] = []
            pfps[item['collection']].append(item['schema'])

        if res:
            return pfps
    except SQLAlchemyError as e:
        logging.error(e)
        session.rollback()
        return []
    finally:
        session.remove()


def get_user_picture(user):
    session = create_session()
    try:
        result = execute_sql(
            session,
            'SELECT image FROM user_pictures_mv WHERE user_name = :user LIMIT 1',
            {'user': user}
        ).first()

        if result:
            return {
                'image': result['image']
            }

        return {
            'image': None
        }
    except SQLAlchemyError as e:
        logging.error(e)
        session.rollback()
        raise e
    finally:
        session.remove()


def get_wuffi_airdrops(ready, creator, username, contract):
    session = create_session()
    try:
        search_clause = ''
        eligible_clause = ''
        search_dict = {}

        if ready:
            search_clause += ' AND ready'
        if creator:
            search_clause += ' AND creator = :creator'
            search_dict['creator'] = creator
        if username:
            eligible_clause += (
                ', ('
                '   SELECT w.claimer IS NOT NULL '
                '   FROM wuffi_airdrop_claimers w '
                '   WHERE w.airdrop_id = wa.airdrop_id AND claimer = :username'
                ') AS eligible, ('
                '   SELECT wc.account IS NOT NULL '
                '   FROM wuffi_airdrop_claims wc '
                '   WHERE wc.airdrop_id = wa.airdrop_id AND account = :username'
                ' ) AS claimed '
            )
            search_dict['username'] = username
        if contract:
            search_clause += ' holder_contract = :contract'
            search_dict['contract'] = contract

        sql = (
            'SELECT airdrop_id, token, contract, creator, min_amount, max_amount, display_data, ready, symbol, logo, '
            'extract(epoch from snapshot_time AT time zone \'Europe/Berlin\')::bigint AS snapshot_time '
            '{eligible_clause} '
            'FROM wuffi_airdrops wa '
            'LEFT JOIN eos_tokens et ON et.account = wa.contract AND position(et.symbol IN token) > 0 '
            'WHERE TRUE {search_clause} '
            'ORDER BY airdrop_id DESC'.format(search_clause=search_clause, eligible_clause=eligible_clause)
        )

        res = execute_sql(
            session,
            sql,
            search_dict
        )

        airdrops = []

        for airdrop in res:
            airdrops.append(_format_response(airdrop))

        return airdrops
    except SQLAlchemyError as e:
        logging.error(e)
        session.rollback()
        raise e
    finally:
        session.remove()


def _format_tags(res):
    tags = []
    for tag in res:
        if tag['tag_id'] and tag['tag_name']:
            tags.append({'tagId': tag['tag_id'], 'tagName': tag['tag_name']})

    return tags


def get_personal_blacklist(user, term, limit, session=None):
    users = []
    if not session:
        session = create_session()
    try:
        if term and len(term) > 12:
            return users
        if term:
            res = execute_sql(session,
                'SELECT collection '
                'FROM personal_blacklist_mv '
                'WHERE account = :user {author_term} '
                'LIMIT :limit'.format(
                    author_term=' AND collection = :term ' if term else ''), {
                    'user': user, 'limit': 1, 'term': term
                }
            ).first()

            if res:
                users.append({
                    'collection': res['collection']
                })
                return users

        res = execute_sql(session,
            'SELECT collection '
            'FROM personal_blacklist_mv '
            'WHERE account = :user {author_term} '
            'ORDER BY collection DESC LIMIT :limit'.format(
                author_term=' AND collection like :term' if term else ''), {
                'user': user, 'limit': limit, 'term': '{}%'.format(term)
            }
        )

        if res:
            for row in res:
                users.append({
                    'collection': row['collection']
                })

        return users
    except SQLAlchemyError as e:
        logging.error(e)
        session.rollback()
        return []
    finally:
        session.remove()


@cache.memoize(timeout=60)
def get_ownership_info(asset_id, owner):
    session = create_session()
    try:
        if not asset_id.isnumeric():
            logging.error('Tried loading assetId {}. Asset: {}'.format(asset_id, 'get_price_info_template'))
            return {}

        info = {}

        search_dict = {
            'asset_id': asset_id,
            'owner': owner
        }

        res = execute_sql(session,
            'SELECT COUNT(1) AS num_assets, MIN(mint) as min_mint '
            'FROM assets WHERE summary_id = (SELECT summary_id FROM assets WHERE asset_id = :asset_id) '
            'AND owner = :owner AND NOT burned',
            search_dict
        ).first()

        info['numAssets'] = res['num_assets']
        if res['min_mint']:
            info['minMint'] = res['min_mint']

        return info
    except SQLAlchemyError as e:
        logging.error(e)
        session.rollback()
        return {
            'numAssets': 0
        }
    finally:
        session.remove()


@cache.memoize(timeout=60)
def get_ownership_info_template(template_id, owner):
    session = create_session()
    try:
        if not template_id.isnumeric():
            logging.error('Tried loading assetId {}. Asset: {}'.format(template_id, 'get_price_info_template'))
            return {}

        info = {}

        search_dict = {
            'template_id': template_id,
            'owner': owner
        }

        res = execute_sql(session,
            'SELECT COUNT(1) AS num_assets, MIN(mint) as min_mint '
            'FROM assets WHERE template_id = :template_id AND owner = :owner AND NOT burned',
            search_dict
        ).first()

        info['numAssets'] = res['num_assets']
        if res['min_mint']:
            info['minMint'] = res['min_mint']

        return info
    except SQLAlchemyError as e:
        logging.error(e)
        session.rollback()
        return {
            'numAssets': 0
        }
    finally:
        session.remove()


@cache.memoize(timeout=300)
def get_collection_table(verified='verified', term='', market='', type='', owner='', collection='', pfps_only=False):
    start_time = time.time()
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
            join_clause = ' INNER JOIN drops d ON (d.collection = c.collection AND NOT d.erased AND d.contract = :market) '
            search_dict['market'] = market

    if type == 'crafts':
        join_clause = ' INNER JOIN crafts d ON (d.collection = c.collection AND NOT d.erased) '

    if type in ['assets', 'bulk_burn', 'bulk_distribute', 'bulk_transfer', 'bulk_multi_sell', 'bulk_sell',
                'bulk_sell_dupes', 'bulk_sell_highest_duplicates', 'bulk_transfer_duplicates',
                'bulk_transfer_lowest_mints', 'inventory'] and owner:
        with_clause = 'WITH user_assets AS (SELECT collection, COUNT(1) AS cnt FROM assets WHERE owner = :owner AND NOT burned GROUP BY 1)'
        join_clause = ' INNER JOIN user_assets ua USING (collection) '
        order_clause = 'ua.cnt DESC'
        cnt_clause = ', ua.cnt'

    if type == 'my_packs' and owner:
        with_clause = (
            'WITH user_assets AS ('
            'SELECT a.collection, COUNT(1) AS cnt FROM assets a '
            'INNER JOIN packs p ON ('
            '   a.template_id = p.template_id AND p.pack_id = ('
            '       SELECT MAX(pack_id) FROM packs WHERE template_id = a.template_id'
            ')) '
            'WHERE owner = :owner '
            'GROUP BY 1)'
        )
        join_clause = ' INNER JOIN user_assets ua USING (collection) '
        order_clause = 'ua.cnt DESC'
        cnt_clause = ', ua.cnt'

    if type in ['sales', 'bulk_edit', 'bulk_cancel', 'listings'] and owner:
        with_clause = 'WITH user_assets AS (SELECT collection, COUNT(1) AS cnt FROM listings WHERE seller = :owner GROUP BY 1)'
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
        collection_clause = ' AND ac.collection != :collection '
        search_dict['collection'] = collection
        search_dict['limit'] = 99

    if pfps_only or type == 'pfps':
        join_clause += ' INNER JOIN pfp_schemas USING(collection) '

    try:
        categories = {
            'collections': [],
            'images': {},
            'names': {},
            'verified': {},
            'blacklisted': {},
            'volume24h': {}
        }

        if collection:
            result1 = execute_sql(
                session,
                'SELECT c.collection, ci.image, cn.name, verified, blacklisted, cv.wax_volume '
                'FROM collections c '
                'LEFT JOIN images ci USING(image_id) '
                'LEFT JOIN names cn USING(name_id) '
                'LEFT JOIN volume_collection_1_days_mv cv ON c.collection = cv.collection '
                'WHERE ac.collection = :collection '
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

                if collection not in categories['collections']:
                    categories['collections'].append(collection)
                    categories['images'][collection] = _format_collection_thumbnail(collection, image)
                    categories['names'][collection] = name
                    categories['verified'][collection] = verified
                    categories['blacklisted'][collection] = blacklisted
                    categories['volume24h'][collection] = volume_24h

        result = execute_sql(
            session,
            '{with_clause} '
            'SELECT c.collection, ci.image, cn.name, verified, blacklisted, cv.wax_volume {cnt_clause} '
            'FROM collections c '
            'LEFT JOIN images ci USING(image_id) '
            'LEFT JOIN names cn USING(name_id) '
            '{join_clause} '
            'LEFT JOIN volume_collection_1_days_mv cv ON c.collection = cv.collection '
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

            if collection not in categories['collections']:
                categories['collections'].append(collection)
                categories['images'][collection] = _format_collection_thumbnail(collection, image)
                categories['names'][collection] = name
                categories['verified'][collection] = verified
                categories['blacklisted'][collection] = blacklisted
                categories['volume24h'][collection] = volume_24h

        end_time = time.time()
        print('collections: {}'.format(end_time-start_time))
        return categories
    except SQLAlchemyError as e:
        logging.error(e)
        session.rollback()
        raise e
    finally:
        session.remove()


@cache.cached(timeout=300)
def get_wax_tokens():
    tokens = []
    session = create_session()
    try:
        res = execute_sql(session,
            'SELECT * FROM eos_tokens WHERE chain = \'wax\''
        )

        for token in res:
            tokens.append({
                'name': token['name'],
                'logo': token['logo'],
                'logo_lg': token['logo_lg'],
                'symbol': token['symbol'],
                'account': token['account'],
                'chain': token['chain'],
            })

        return tokens
    except SQLAlchemyError as e:
        logging.error(e)
        session.rollback()
        raise e
    finally:
        session.remove()


@cache.cached(timeout=300)
def get_currencies():
    session = create_session()
    try:
        res = execute_sql(session,
            'SELECT dt.contract, symbol, decimals '
            'FROM drop_token_actions dt INNER JOIN drop_prices_mv dp ON symbol = ANY(currencies) '
            'INNER JOIN drops d ON (d.drop_id = dp.drop_id AND d.contract = dp.contract) '
            'WHERE NOT erased AND (end_time IS NULL OR end_time < NOW()) '
            'GROUP BY 1, 2, 3'
        )

        tokens = []

        for token in res:
            tokens.append({
                'symbol': token['symbol'],
                'contract': token['contract'],
                'decimals': token['decimals']
            })

        return tokens
    except SQLAlchemyError as e:
        logging.error(e)
        session.rollback()
        raise e
    finally:
        session.remove()


@cache.memoize(timeout=300)
def get_minimal_drop(drop_id, contract):
    session = create_session()
    try:
        if not str(drop_id).isnumeric():
            logging.error('Tried loading dropId {}. Asset: {}'.format(drop_id, 'get_minimal_drop'))
            return None
        drop = execute_sql(session,
            'SELECT drop_id, td.data AS idata, display_data, tn.name, ti.image, tv.video '
            'FROM drops d '
            'INNER JOIN templates t ON t.template_id = ANY(d.templates_to_mint) '
            'LEFT JOIN names tn ON t.name_id = tn.name_id '
            'LEFT JOIN data td ON t.immutable_data_id = td.data_id '
            'LEFT JOIN images ti ON t.image_id = ti.image_id '
            'LEFT JOIN videos tv ON t.video_id = tv.video_id '
            'WHERE drop_id = :drop_id AND contract = :contract', {'drop_id': drop_id, 'contract': contract}
        ).first()

        if not drop:
            return {}

        try:
            data = json.loads(drop['display_data'])
        except Exception:
            data = json.loads(drop['idata'])

        img = data['preview_img'] if data and 'preview_img' in data else drop['image'] if drop['image'] else None
        vid = data['preview_video'] if data and 'preview_video' in data else drop['video'] if drop['video'] else None
        name = data['name'] if data and 'name' in data else drop['name'] if drop['name'] else None

        return {
            'dropId': drop.drop_id,
            'previmg': _format_thumbnail('video:' + vid) if vid else _format_thumbnail(img) if img else None,
            'image': img,
            'video': vid,
            'preview': _format_banner('video:' + vid) if vid else _format_banner(img) if img else None,
            'idata': drop.idata,
            'displayData': drop.display_data,
            'name': name,
        }
    except SQLAlchemyError as e:
        logging.error(e)
        session.rollback()
        raise e
    finally:
        session.remove()


def get_minimal_template(template_id):
    session = create_session()
    try:
        if not str(template_id).isnumeric():
            logging.error('Tried loading templateId {}. Asset: {}'.format(template_id, 'get_minimal_template'))
            return None
        template = execute_sql(session,
            'SELECT template_id, collection, video, tn.name, ti.image, cn.name as collection_name, '
            'ci.image as collection_image '
            'FROM templates t '
            'LEFT JOIN collections c USING(collection) '
            'LEFT JOIN names tn ON tn.name_id = t.name_id '
            'LEFT JOIN images ti ON ti.image_id = t.image_id '
            'LEFT JOIN videos tv ON tv.video_id = t.video_id '
            'LEFT JOIN names cn ON cn.name_id = c.name_id '
            'LEFT JOIN images ci ON ci.image_id = c.image_id '
            'WHERE template_id = :template_id', {'template_id': template_id}
        ).first()

        if not template:
            return {}

        response = {}

        if 'name' in template.keys():
            response['name'] = template['name']
        if 'collection' in template.keys():
            response['collection'] = template['collection']
        if 'video' in template.keys():
            response['video'] = template['video']
        if 'image' in template.keys():
            response['image'] = template['image']
        if 'collection_name' in template.keys():
            response['collectionName'] = template['collection_name']
        if 'collection_image' in template.keys():
            response['collectionImage'] = _format_image(template['collection_image'])
        response['templateId'] = template['template_id'] if template else template_id

        return response
    except SQLAlchemyError as e:
        logging.error(e)
        session.rollback()
        raise e
    finally:
        session.remove()


@cache.memoize(timeout=300)
def get_minimal_asset(asset_id):
    session = create_session()
    start = time.time()
    try:
        if not str(asset_id).isnumeric():
            logging.error('Tried loading assetId {}. Asset: {}'.format(asset_id, 'get_asset'))
            return None
        asset = execute_sql(
            session,
            'SELECT a.asset_id, an.name, a.contract, a.collection, a.schema, ai.image, a.mint, a.template_id, '
            'cn.name as collection_name, ci.image as collection_image, ai.image AS image, av.video as video '
            'FROM assets a '
            'LEFT JOIN names an ON a.name_id = an.name_id '
            'LEFT JOIN images ai ON a.image_id = ai.image_id '
            'LEFT JOIN videos av ON a.video_id = av.video_id '
            'LEFT JOIN collections c USING (collection) '
            'LEFT JOIN names cn ON c.name_id = cn.name_id '
            'LEFT JOIN images ci ON c.image_id = ci.image_id '
            'WHERE asset_id = :asset_id', {'asset_id': asset_id}
        ).first()

        if not asset:
            return {}

        return {
            'name': asset.name,
            'contract': asset.contract,
            'schema': asset.schema,
            'image': _format_image(asset.image) if asset.image else None,
            'preview': _format_collection_thumbnail(
                asset.collection_name, asset.video if asset.video else asset.image, 240
            ) if asset.image or asset.video else None,
            'mint': asset.mint,
            'collection': {
                'collectionName': asset.collection,
                'displayName': asset.collection_name,
                'collectionImage': _format_image(asset.collection_image)
            },
            'assetId': asset.asset_id,
            'templateId': asset.template_id if asset.template_id else None
        }
    except SQLAlchemyError as e:
        logging.error(e)
        session.rollback()
        raise e
    finally:
        end = time.time()
        print(end - start)
        session.remove()


@cache.memoize(timeout=300)
def get_minimal_auction(market, auction_id):
    session = create_session()
    try:
        params = {'auction_id': auction_id, 'market': market}

        result = execute_sql(session,
            'SELECT current_bid, (SELECT usd FROM usd_prices ORDER BY timestamp DESC LIMIT 1) AS usd_wax, '
            'currency, seller, market, an.name, a.collection, ai.image, a.template_id, '
            'ci.image as collection_image, cn.name as collection_name, auction_id '
            'FROM auction_logs s1 '
            'LEFT JOIN assets a ON (s1.asset_ids[1] = a.asset_id) '
            'LEFT JOIN names an ON a.name_id = an.name_id '
            'LEFT JOIN images ai ON a.image_id = ai.image_id '
            'LEFT JOIN collections c ON (a.collection = c.collection) '
            'LEFT JOIN names cn ON (c.name_id = cn.name_id) '
            'LEFT JOIN images ci ON (c.image_id = ci.image_id) '
            'WHERE s1.auction_id = :auction_id AND s1.market = :market',
            params
        )

        listings = []

        for sale in result:
            listings.append(_format_response(sale))

        return listings
    except SQLAlchemyError as e:
        logging.error(e)
        session.rollback()
        raise e
    finally:
        session.remove()


def get_active_sales(sales):
    session = create_session()
    try:
        sale_ids = tuple(map(lambda a: int(a), list(sales)))
        result = execute_sql(session,
            'SELECT sale_id FROM listings '
            'WHERE {sale_id_clause}'.format(
                sale_id_clause='sale_id IN :sale_ids' if len(sales) > 1 else (
                    'sale_id = :sale_ids ' if len(sales) == 1 else ''
                )
            ),
            {'sale_ids': sale_ids if len(sale_ids) > 1 else (sale_ids[0] if len(sale_ids) == 1 else '')}
        )

        available_ids = []
        for res in result:
            available_ids.append(res['sale_id'])

        return available_ids
    except SQLAlchemyError as e:
        logging.error(e)
        session.rollback()
        raise e
    finally:
        session.remove()


def get_all_owned(asset_id):
    session = create_session()
    try:
        if not str(asset_id).isnumeric():
            logging.error('Tried loading assetId {}. Asset: {}'.format(asset_id, 'get_asset'))
            return []
        result = execute_sql(
            session,
            'WITH my_asset AS (SELECT template_id, owner FROM assets WHERE asset_id = :asset_id LIMIT 1) '
            'SELECT asset_id, contract, '
            'FROM assets a LEFT JOIN listings s ON asset_id = ANY(asset_ids) '
            'WHERE owner = (SELECT owner FROM my_asset) '
            'AND s.sale_id IS NULL AND NOT burned AND a.template_id IS NOT NULL '
            'AND a.template_id = (SELECT template_id FROM my_asset)',
            {'asset_id': asset_id}
        )

        if not result or result.rowcount == 0:
            return []

        assets = []

        for asset in result:
            assets.append(_format_response(asset))

        return assets
    except SQLAlchemyError as e:
        logging.error(e)
        session.rollback()
        raise e
    finally:
        session.remove()


def get_all_for_sale(template_id):
    session = create_session()
    try:
        result = execute_sql(
            session,
            'WITH my_template AS ('
            '   SELECT template_id, collection FROM templates WHERE template_id = :template_id LIMIT 1'
            ') '
            'SELECT a.contract, s2.market, s2.listing_id, a.asset_id, '
            's2.price, (SELECT usd FROM usd_prices ORDER BY timestamp DESC LIMIT 1) AS usd_wax, s2.currency, '
            's2.estimated_wax_price '
            'FROM listings s2 '
            'LEFT JOIN assets a ON asset_id = asset_ids[1] '
            'WHERE s2.collection = (SELECT collection FROM my_template) '
            'AND array_length(asset_ids, 1) = 1 AND a.template_id = (SELECT template_id FROM my_template) '
            'ORDER BY s2.estimated_wax_price ASC LIMIT 100',
            {'template_id': template_id}
        )

        if not result or result.rowcount == 0:
            return []

        sales = []

        for sale in result:
            sales.append(_format_response(sale))

        return sales
    except SQLAlchemyError as e:
        logging.error(e)
        session.rollback()
        raise e
    finally:
        session.remove()


def get_top_honey_earner(days):
    session = create_session()
    try:

        result = execute_sql(
            session,
            'SELECT CASE WHEN seller IS NOT null then seller else buyer END AS earner, SUM(price) / 100 AS honey '
            'FROM honey_rewards '
            'WHERE timestamp > NOW () AT time zone \'utc\' - INTERVAL \':days days\''
            'AND NOT washtrade '
            'GROUP BY 1 ORDER BY 2 DESC LIMIT 1', {'days': int(days)}
        ).first()

        if result:
            return {'earner': result['earner'], 'amount': result['honey']}
        else:
            return {'earner': None, 'amount': 0}
    except SQLAlchemyError as e:
        logging.error(e)
        session.rollback()
        raise e
    finally:
        session.remove()


@cache.memoize(timeout=300)
def get_collection(collection):
    session = create_session()
    try:
        res = execute_sql(
            session,
            'SELECT c.collection, name, image, description, url, market_fee, c.author, '
            'verified, blacklisted, c.socials, c.creator_info, c.images, c.authorized, '
            'json_agg(json_build_object(\'tag_id\', tag_id, \'tag_name\', tag_name)) AS tags '
            'FROM collections c '
            'LEFT JOIN images USING (image_id) '
            'LEFT JOIN names USING (name_id) '
            'LEFT JOIN collection_tag_ids_mv tm ON (c.collection = tm.collection) '
            'LEFT JOIN tags t ON (tag_id = ANY(tag_ids)) '
            'WHERE c.collection = :collection '
            'GROUP BY 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13 ',
            {'collection': collection}
        ).first()
        if res:
            creator_info = ''
            socials = ''
            images = ''
            try:
                creator_info = json.loads(res['creator_info']) if res['creator_info'] else None
            except Exception as err:
                print(err)
            try:
                socials = json.loads(res['socials']) if res['socials'] else None
            except Exception as err:
                print(err)
            prev_img = res['image']
            try:
                images = json.loads(res['images']) if res['images'] else None
                for image in images.keys():
                    if image == 'logo_512x512' and images[image]:
                        prev_img = images[image]
            except Exception as err:
                print(err)
            return {
                'collectionName': res['collection'],
                'author': res['author'],
                'creatorInfo': creator_info,
                'images': images,
                'socials': socials,
                'name': res['name'],
                'verified': res['verified'],
                'blacklisted': res['blacklisted'],
                'image': _format_image(prev_img),
                'preview': _format_banner(prev_img),
                'description': res['description'],
                'url': res['url'],
                'marketFee': int(res['market_fee'] * 100),
                'tags': _format_tags(res['tags']),
                'authorized': res['authorized']
            }
        return None
    except SQLAlchemyError as e:
        logging.error(e)
        session.rollback()
        raise e
    finally:
        session.remove()