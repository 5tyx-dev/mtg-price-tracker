import json
from datetime import datetime, timezone
from urllib.request import Request, urlopen

MTGJSON_META_URL = "https://mtgjson.com/api/v5/Meta.json"


def main():
    print("MTG Price Tracker")
    print("Checking MTGJSON connection...")

    request = Request(
        MTGJSON_META_URL,
        headers={"User-Agent": "MTGPriceTracker/1.0"},
    )

    with urlopen(request, timeout=30) as response:
        metadata = json.load(response)

    print("Connection successful!")
    print("MTGJSON metadata:", metadata)
    print("Checked at:", datetime.now(timezone.utc).isoformat())


if __name__ == "__main__":
    main()
