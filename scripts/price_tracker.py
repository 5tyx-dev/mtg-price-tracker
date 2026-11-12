import json
from urllib.request import Request, urlopen

PRICES_URL = "https://mtgjson.com/api/v5/AllPricesToday.json"


def main():
    print("MTG Price Tracker")
    print("Searching for Card Kingdom nonfoil retail prices...")

    request = Request(
        PRICES_URL,
        headers={"User-Agent": "MTGPriceTracker/1.0"},
    )

    with urlopen(request, timeout=120) as response:
        payload = json.load(response)

    cards = payload["data"]
    matching = 0
    examples = []

    for uuid, record in cards.items():
        prices = (
            record.get("paper", {})
            .get("cardkingdom", {})
            .get("retail", {})
            .get("normal", {})
        )

        if not prices:
            continue

        matching += 1

        if len(examples) < 5:
            latest_date = max(prices)
            examples.append({
                "uuid": uuid,
                "date": latest_date,
                "price": prices[latest_date],
            })

    print("Total printing records:", len(cards))
    print("Printings with CK nonfoil retail prices:", matching)
    print("Sample prices:")

    for example in examples:
        print(json.dumps(example, indent=2))


if __name__ == "__main__":
    main()
