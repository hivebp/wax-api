import os

basedir = os.path.abspath(os.path.dirname(__file__))


class PostgresDevConfig(object):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DB')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 1,
        'max_overflow': 2,
        'pool_recycle': 30,
        'connect_args': {'options': '-c statement_timeout=600s'}
    }


class PostgresConfig(object):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DB')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 50,
        'max_overflow': 20,
        'pool_recycle': 30,
        'connect_args': {'options': '-c statement_timeout=40s'}
    }


class PostgresFillerConfig(object):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DB')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 10,
        'max_overflow': 10,
        'connect_args': {'options': '-c statement_timeout=3600s'}
    }


class PostgresConsumerConfig(object):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DB')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 5,
        'max_overflow': 5,
        'connect_args': {'options': '-c statement_timeout=3600s'}
    }


chronicle_settings = dict(
    host='0.0.0.0',
    port='PORT',
)

contracts = [
    'atomicassets',
    'atomicmarket',
    'simpleassets',
    'simplemarket',
    'neftyblocksd',  # Drops Contract
    'waxbuyoffers',  # Old NFTHive Buy offers, only relevant for Analytics
    'neftyblocksp',  # Pack Contract
    'atomicpacksx',  # Pack Contract
    'wax.gg',        # User Profile Picture Updates
    'market.myth',   # Old Marketplace, only relevant for Analytics
    'waxplorercom',  # Simpleassets Marketplace
    'nft.hive',      # FT Marketplace
    'atomicdropsx',  # Drops Contract
    'clltncattool',  # On chain categorization
    'nfthivedrops',  # Drops Contract
    'nfthivepacks',  # Pack Contract
    'atomhubtools',  # On chain account settings
    'neftyblocksa',  # On chain account settings
    'nfthivecraft',  # Crafting Contract
    'twitchreward',  # Drop Contract
    'redeemprtcol',  # Redeem API Contract
    'verifystatus',  # On chain Collection verification and rating
    'wufclaimtool',  # Airdrop Contract, most likely not relevant
    'rwax',          # NFT Tokenization and Redemption
    'waxtokenbase',  # Token Registration
    'waxdaobacker'   # Token Backing
]
