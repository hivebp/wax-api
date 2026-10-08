"""Monthly WAX receipts, matching the filler's accounting report."""

import logging
import os
import random
from datetime import datetime, timedelta, timezone

import requests
from sqlalchemy import text


class AccountingError(Exception):
    pass


def month_bounds(year, month):
    start = datetime(year, month, 1, tzinfo=timezone.utc)
    end = datetime(
        year + (month == 12), 1 if month == 12 else month + 1, 1,
        tzinfo=timezone.utc,
    )
    return start, end


HYPERIONS = [
    "https://wax-history.eosdac.io",
    "https://hyperion7.sentnl.io",
    "https://history.waxsweden.org",
]


def get_actions(start, end):
    configured = os.environ.get("WAX_HISTORY_URL")
    urls = [configured.rstrip("/")] if configured else list(HYPERIONS)
    if not configured:
        random.shuffle(urls)
    params = {
        "account": "waxhiveguild",
        "filter": "eosio.token:transfer",
        "skip": 0,
        "limit": 100,
        "sort": "asc",
        "after": start.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
        "before": end.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
        "simple": "false",
    }
    # Some Hyperion nodes have gaps in their index and answer with an empty
    # list, so keep trying other nodes like filler.get_valid_response does.
    payload = None
    for url in urls:
        try:
            response = requests.get(f"{url}/v2/history/get_actions", params=params, timeout=60)
            response.raise_for_status()
            candidate = response.json()
        except (requests.RequestException, ValueError):
            logging.exception("Accounting history request to %s failed", url)
            continue
        if not isinstance(candidate, dict) or not isinstance(candidate.get("actions"), list):
            continue
        if candidate["actions"]:
            return candidate
        payload = candidate
    if payload is None:
        raise AccountingError("No WAX history server returned a valid response.")
    return payload


def run_accounting(year, month, session):
    start, end = month_bounds(year, month)
    payload = get_actions(start, end)

    dates = {}
    while start <= end:
        row = session.execute(
            text(
                "SELECT MIN(usd) AS usd FROM usd_prices "
                "WHERE timestamp BETWEEN :date AND :date + INTERVAL '24 hours' "
                "ORDER BY MIN(timestamp) DESC LIMIT 1"
            ),
            {"date": start},
        ).mappings().first()
        dates[start.strftime("%Y-%m-%d")] = row["usd"]
        start += timedelta(days=1)

    receipts = []
    for action in payload["actions"]:
        data = action["act"]["data"]
        if data["to"] == "waxhiveguild":
            usd = dates[action["timestamp"][0:10]]
            if data["amount"] > 100:
                receipts.append({
                    "timestamp": action["timestamp"],
                    "amount": str(data["amount"]),
                    "usd": str(usd),
                    "sender": data["from"],
                    "transaction": f"https://waxblock.io/transaction/{action['trx_id']}",
                })
    return receipts
