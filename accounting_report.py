"""Monthly WAX receipts, matching the filler's accounting report."""

import os
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


def run_accounting(year, month, session):
    start, end = month_bounds(year, month)
    history_url = os.environ.get("WAX_HISTORY_URL", "https://wax.eosusa.io").rstrip("/")
    response = requests.get(
        f"{history_url}/v2/history/get_actions",
        params={
            "account": "waxhiveguild",
            "filter": "eosio.token:transfer",
            "skip": 0,
            "limit": 100,
            "sort": "asc",
            "after": start.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
            "before": end.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
            "simple": "false",
        },
        timeout=60,
    )
    response.raise_for_status()
    payload = response.json()
    if not isinstance(payload, dict) or not isinstance(payload.get("actions"), list):
        raise AccountingError("WAX history returned an invalid actions response.")

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
