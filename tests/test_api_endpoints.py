"""Integration tests for API endpoints."""
import time

import pytest
import requests


class TestListings(object):
    @pytest.mark.parametrize(
        'filter', [
            '&search_type=missing&order_by=collection_asc&user=t1.5c.wam&min_price=100&max_price=100',
            '&search_type=floor&order_by=name_desc&collection=alien.worlds&attributes=rarity:legendary',
            '&search_type=owned_lower_mints&order_by=collection_asc&user=t1.5c.wam&max_price=100',
            '&order_by=price_asc&collection=kogsofficial&attributes=type:Kog',
            '&search_type=below_average&order_by=floor_asc&collection=maiden.funko',
            '&search_type=below_last_sold&order_by=template_id_desc&collection=maiden.funko',
            '&search_type=bulk_buy&only=rwax&order_by=mint_asc&verified=all&user=scfay.wam',
            '&search_type=floor_missing&only=pfps&order_by=rarity_score_asc',
            '&order_by=price_desc&term=YOLASIC&verified=all&exact_search=true',
            '&contract=simpleassets&offset=1&collection=gpk.topps&schema=series1',
            '&user=t1.5c.wam&favorites=true',
            '&seller=t1.5c.wam&market=atomicmarket&max_mint=10',
            '&only=backed&market=atomicmarket&min_mint=10',
            '&recent=week&min_mint=2&max_mint=3',
        ]
    )
    def test_succeeds(self, filter):
        """Test successful response."""
        url = 'http://localhost:5003/api/listings?limit=1&{}'.format(filter)
        print(url)
        start = time.time()
        response = requests.get(url)
        end = time.time()
        print('Request Time: {}'.format(end-start))
        assert response.status_code == 200, 'Reason: {}, URL: {}'.format(
            response.reason, response.url)

        assert len(response.json()) == 1


class TestInitialListingFeed(object):
    @pytest.mark.parametrize(
        'filter', [
            '?collection=alien.worlds',
            '?collection=alien.worlds&schema=tool.worlds',
            '?collection=alien.worlds&schema=tool.worlds&template_id=19552',
        ]
    )
    def test_succeeds(self, filter):
        """Test successful response."""
        url = 'http://localhost:5003/api/initial-listing-feed{}'.format(filter)
        print(url)
        start = time.time()
        response = requests.get(url)
        end = time.time()
        print('Request Time: {}'.format(end-start))
        assert response.status_code == 200, 'Reason: {}, URL: {}'.format(
            response.reason, response.url)

        assert len(response.json()) > 0


class TestSchemas(object):
    @pytest.mark.parametrize(
        'filter', [
            '&term=series&order_by=num_templates_asc',
            '&schema=series1.drop&order_by=num_assets_desc',
            '&offset=1&order_by=volume_desc',
            '&term=series1.drop&exact_search=true',
        ]
    )
    def test_succeeds(self, filter):
        """Test successful response."""
        url = 'http://localhost:5003/api/schemas/maiden.funko?limit=1{}'.format(filter)
        print(url)
        start = time.time()
        response = requests.get(url)
        end = time.time()
        print('Request Time: {}'.format(end-start))
        assert response.status_code == 200, 'Reason: {}, URL: {}'.format(
            response.reason, response.url)

        assert len(response.json()) == 1


class TestTemplates(object):
    @pytest.mark.parametrize(
        'filter', [
            '&term=Eddie&collection=maiden.funko&order_by=template_id_asc',
            '&collection=maiden.funko&schema=series1.drop&order_by=collection_desc',
            '&offset=1&tags=20,53&order_by=average_desc',
            '&offset=1&recent=month&order_by=floor_asc&search_type=packs',
            '&term=Nanominer&collection=alien.worlds&verified=verified&exact_search=true',
            '&favorites=true&user=t1.5c.wam',
            '&search_type=pfps',
            '&search_type=rwax&verified=all',
        ]
    )
    def test_succeeds(self, filter):
        """Test successful response."""
        url = 'http://localhost:5003/api/templates?limit=1{}'.format(filter)
        print(url)
        start = time.time()
        response = requests.get(url)
        end = time.time()
        print('Request Time: {}'.format(end-start))
        assert response.status_code == 200, 'Reason: {}, URL: {}'.format(
            response.reason, response.url)

        assert len(response.json()) == 1


class TestAssets(object):
    @pytest.mark.parametrize(
        'filter', [
            '&term=Eddie&collection=maiden.funko&order_by=template_id_asc',
            '&collection=maiden.funko&schema=series1.drop&owner=t1.5c.wam&order_by=average_desc',
            '&offset=1&tags=20,53&order_by=collection_desc',
            '&offset=1&recent=week&order_by=floor_asc&search_type=packs',
            '&term=Nanominer&collection=alien.worlds&verified=verified&exact_search=true',
            '&favorites=true&user=t1.5c.wam&min_mint=2',
            '&search_type=pfps&order_by=rarity_score_desc',
            '&search_type=rwax&verified=all',
            '&search_type=packs&max_mint=10',
            '&search_type=highest_duplicates&order_by=mint_asc&owner=t1.5c.wam',
            '&search_type=duplicates&min_mint=2&max_mint=10&owner=t1.5c.wam',
            '&search_type=highest_mints&owner=t1.5c.wam&order_by=asset_id_asc',
            '&search_type=lowest_mints&owner=t1.5c.wam&order_by=asset_id_desc',
            '&search_type=duplicates&min_mint=2&max_mint=10&owner=t1.5c.wam',
            '&order_by=floor_desc&min_average=100&max_average=200',
            '&order_by=average_asc&min_average=100',
            '&order_by=mint_asc&max_average=200',
            '&search_type=staked&order_by=date_asc&verified=all',
            '&backed=true&order_by=rarity_score_desc',
            '&contract=simpleassets',
            '&favorites=true&user=t1.5c.wam',
            '&collection=maiden.funko&attributes=variant:Silver',
            '&collection=maiden.funko&schema=series1.drop&attributes=cardid:11',
        ]
    )

    def test_succeeds(self, filter):
        """Test successful response."""
        url = 'http://localhost:5003/api/assets?limit=1{}'.format(filter)
        print(url)
        start = time.time()
        response = requests.get(url)
        end = time.time()
        print('Request Time: {}'.format(end-start))
        assert response.status_code == 200, 'Reason: {}, URL: {}'.format(
            response.reason, response.url)

        assert len(response.json()) == 1


class TestFilterAttributes(object):
    def test_succeeds(self):
        """Test successful response."""
        url = 'http://localhost:5003/api/filter-attributes/alien.worlds'
        print(url)
        start = time.time()
        response = requests.get(url)
        end = time.time()
        print('Request Time: {}'.format(end-start))
        assert response.status_code == 200, 'Reason: {}, URL: {}'.format(
            response.reason, response.url)

        assert len(response.json()) > 1


class TestCollectionFilters(object):
    def test_succeeds(self):
        """Test successful response."""
        url = 'http://localhost:5003/api/collection-filters/alien.worlds'
        print(url)
        start = time.time()
        response = requests.get(url)
        end = time.time()
        print('Request Time: {}'.format(end-start))
        assert response.status_code == 200, 'Reason: {}, URL: {}'.format(
            response.reason, response.url)

        assert len(response.json()) > 1


class TestCollections(object):
    @pytest.mark.parametrize(
        'filter', [
            '&collection=alien',
            '&only_pfps=true&verified=all',
            '&owner=t1.5c.wam',
            '&market=nfthivedrops',
            '&trending=true&offset=1',
            '&tag_id=10',
            '&type=pfps',
            '&type=5',
            '&search_type=packs&max_mint=10',
        ]
    )

    def test_succeeds(self, filter):
        """Test successful response."""
        url = 'http://localhost:5003/api/collections?limit=1{}'.format(filter)
        print(url)
        start = time.time()
        response = requests.get(url)
        end = time.time()
        print('Request Time: {}'.format(end-start))
        assert response.status_code == 200, 'Reason: {}, URL: {}'.format(
            response.reason, response.url)

        assert len(response.json()) == 1


class TestCrafts(object):
    @pytest.mark.parametrize(
        'filter', [
            '&collection=nfthivedrive&verified=all&order_by=craft_id_asc',
            '&craft_id=115&verified=all&order_by=date_asc',
            '&offset=1&order_by=collection_asc',
        ]
    )

    def test_succeeds(self, filter):
        """Test successful response."""
        url = 'http://localhost:5003/api/crafts?limit=1{}'.format(filter)
        print(url)
        start = time.time()
        response = requests.get(url)
        end = time.time()
        print('Request Time: {}'.format(end-start))
        assert response.status_code == 200, 'Reason: {}, URL: {}'.format(
            response.reason, response.url)

        assert len(response.json()) == 1


class TestDrops(object):
    @pytest.mark.parametrize(
        'filter', [
            '&market=nfthivedrops&collection=nfthivedrive&verified=all&order_by=drop_id_asc',
            '&currency=WUF&verified=all&order_by=date_asc',
            '&user=t1.5c.wam&upcoming=true&order_by=collection_asc',
            '&home=true',
            '&token=HONEY&order_by=price_asc',
            '&drop_id=460&market=nfthivedrops',
            '&term=Legendary&market=nfthivedrops&order_by=price_desc&verified=all',
        ]
    )

    def test_succeeds(self, filter):
        """Test successful response."""
        url = 'http://localhost:5003/api/drops?limit=1{}'.format(filter)
        print(url)
        start = time.time()
        response = requests.get(url)
        end = time.time()
        print('Request Time: {}'.format(end-start))
        assert response.status_code == 200, 'Reason: {}, URL: {}'.format(
            response.reason, response.url)

        assert len(response.json()) == 1
