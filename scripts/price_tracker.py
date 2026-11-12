import json
from urllib.request import Request, urlopen

PRICES_URL = "https://mtgjson.com/api/v5/AllPricesToday.json"


def main():
    print("MTG Price Tracker")
    print("Inspecting MTGJSON pricing structure...")

    request = Request(
        PRICES_URL,
        headers={"User-Agent": "MTGPriceTracker/1.0"},
    )

    with urlopen(request, timeout=120) as response:
        payload = json.load(response)

    cards = payload["data"]

    print("Total pricing records:", len(cards))

    # Inspect the structure of one card's pricing record.
    first_uuid = next(iter(cards))
    sample = cards[first_uuid]

    print("Sample UUID:", first_uuid)
    print("Available fields:", list(sample.keys()))
    print("Sample pricing record:")
    print(json.dumps(sample, indent=2)[:5000])


if __name__ == "__main__":
    main()
