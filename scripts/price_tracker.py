import json
from urllib.request import Request, urlopen

PRINTINGS_URL = "https://mtgjson.com/api/v5/AllPrintings.json"
PRICES_URL = "https://mtgjson.com/api/v5/AllPricesToday.json"

TEST_CARDS = {
    "Abdel Adrian, Gorion's Ward",
    "Lae'zel, Vlaakith's Champion",
    "Cloudshift",
}


def download_json(url):
    request = Request(
        url,
        headers={"User-Agent": "MTGPriceTracker/1.0"},
    )
    with urlopen(request, timeout=180) as response:
        return json.load(response)["data"]


def main():
    print("MTG Price Tracker", flush=True)

    print("Downloading Card Kingdom pricing...", flush=True)
    prices = download_json(PRICES_URL)

    print("Downloading printing information...", flush=True)
    sets = download_json(PRINTINGS_URL)

    # Find relevant nonfoil printings.
    matches = {}

    for set_code, set_data in sets.items():
        for card in set_data.get("cards", []):
            name = card.get("name")

            if name not in TEST_CARDS:
                continue

            if "nonfoil" not in card.get("finishes", []):
                continue

            uuid = card.get("uuid")
            record = prices.get(uuid, {})

            retail = (
                record.get("paper", {})
                .get("cardkingdom", {})
                .get("retail", {})
                .get("normal", {})
            )

            if not retail:
                continue

            latest_date = max(retail)
            price = retail[latest_date]

            if not isinstance(price, (int, float)) or price <= 0:
                continue

            matches.setdefault(name, []).append({
                "set": set_code,
                "number": card.get("number"),
                "price": price,
                "uuid": uuid,
            })

    print("\nCHEAPEST NONFOIL PRINTINGS", flush=True)

    for name in sorted(TEST_CARDS):
        options = matches.get(name, [])

        if not options:
            print(f"\n{name}: No CK nonfoil price found")
            continue

        cheapest = min(
            options,
            key=lambda item: (item["price"], item["set"], str(item["number"])),
        )

        print(f"\n{name}")
        print(f"  Printing: {cheapest['set']} #{cheapest['number']}")
        print(f"  CK retail: ${cheapest['price']:.2f}")
        print(f"  Matching printings: {len(options)}")


if __name__ == "__main__":
    main()
