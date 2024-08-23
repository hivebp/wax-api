"""Integration tests for API endpoints."""

import pytest
import requests


#@pytest.mark.skip
class TestListings(object):
    @pytest.mark.parametrize(
        'search_type', [
            '&order_by=price_asc',
        ]
    )
    @pytest.mark.parametrize(
        'filter', [
            '&collection=kogsofficial&attributes=type:Kog'
        ]
    )
    def test_succeeds(self, search_type, filter):
        """Test successful response."""
        url = 'http://localhost:5001/api/listings?limit=1&{}{}'.format(search_type, filter)
        print(url)
        response = requests.get(url)
        assert response.status_code == 200, 'Reason: {}, URL: {}'.format(
            response.reason, response.url)

        assert len(response.json()) <= 1


class TestFloorListings(object):
    @pytest.mark.parametrize(
        'search_type', [
            '&search_type=floor&order_by=name_desc',
        ]
    )
    @pytest.mark.parametrize(
        'filter', [
            '&collection=alien.worlds&attributes=rarity:legendary'
        ]
    )
    def test_succeeds(self, search_type, filter):
        """Test successful response."""
        url = 'http://localhost:5001/api/listings?limit=1&{}{}'.format(search_type, filter)
        print(url)
        response = requests.get(url)
        assert response.status_code == 200, 'Reason: {}, URL: {}'.format(
            response.reason, response.url)

        assert len(response.json()) <= 1


class TestMissingListings(object):
    @pytest.mark.parametrize(
        'search_type', [
            '&search_type=missing&order_by=collection_asc&user=t1.5c.wam',
        ]
    )
    @pytest.mark.parametrize(
        'filter', [
            '&min_price=100&max_price=100'
        ]
    )
    def test_succeeds(self, search_type, filter):
        """Test successful response."""
        url = 'http://localhost:5001/api/listings?limit=1{}{}'.format(search_type, filter)
        print(url)
        response = requests.get(url)
        assert response.status_code == 200, 'Reason: {}, URL: {}'.format(
            response.reason, response.url)

        assert len(response.json()) <= 1


class TestOwnedLowerMintsListings(object):
    @pytest.mark.parametrize(
        'search_type', [
            '&search_type=owned_lower_mints&order_by=collection_asc&user=t1.5c.wam',
        ]
    )
    @pytest.mark.parametrize(
        'filter', [
            '&min_price=100&max_price=100'
        ]
    )
    def test_succeeds(self, search_type, filter):
        """Test successful response."""
        url = 'http://localhost:5001/api/listings?limit=1{}{}'.format(search_type, filter)
        print(url)
        response = requests.get(url)
        assert response.status_code == 200, 'Reason: {}, URL: {}'.format(
            response.reason, response.url)

        assert len(response.json()) <= 1
