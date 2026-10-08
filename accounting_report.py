"""Monthly WAX receipts, matching the filler's accounting report."""

import os
from datetime import datetime, timezone
from decimal import Decimal

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
    receipts = []
    skip = 0
    while True:
        response = requests.get(
            f"{history_url}/v2/history/get_actions",
            params={
                "account": "waxhiveguild",
                "filter": "eosio.token:transfer",
                "skip": skip,
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
        actions = payload["actions"]
        for action in actions:
            data = action["act"]["data"]
            timestamp = datetime.fromisoformat(action["timestamp"].replace("Z", "+00:00"))
            if timestamp.tzinfo is None:
                timestamp = timestamp.replace(tzinfo=timezone.utc)
            amount = Decimal(str(data["amount"]))
            if data["to"] == "waxhiveguild" and amount > 100 and start <= timestamp < end:
                receipts.append({
                    "timestamp": action["timestamp"],
                    "date": timestamp.astimezone(timezone.utc).date(),
                    "amount": amount,
                    "sender": data["from"],
                    "transaction": f"https://waxblock.io/transaction/{action['trx_id']}",
                })
        if len(actions) < 100:
            break
        skip += len(actions)

    prices = {
        row["date"]: row["usd"]
        for row in session.execute(
            text(
                "SELECT DATE(timestamp) AS date, MIN(usd) AS usd "
                "FROM usd_prices WHERE timestamp >= :start AND timestamp < :end "
                "GROUP BY DATE(timestamp)"
            ),
            {"start": start, "end": end},
        ).mappings()
    }

    for receipt in receipts:
        price = prices.get(receipt["date"])
        if price is None:
            raise AccountingError(f"No USD rate found for {receipt['date']}.")
        receipt["usd"] = str(price)
        receipt["amount"] = str(receipt["amount"])
        del receipt["date"]
    return receipts
