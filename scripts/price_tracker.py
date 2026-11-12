import csv
import json
from pathlib import Path
from urllib.request import Request, urlopen

PRINTINGS_URL = "https://mtgjson.com/api/v5/AllPrintings.json"
PRICES_URL = "https://mtgjson.com/api/v5/AllPricesToday.json"

TEST_CARDS = {
    "Abdel Adrian, Gorion's Ward",
    "Lae'zel, Vlaakith's Champion",
    "Cloudshift",
}

OUTPUT_FILE = Path("output/ck_prices_test.csv")


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
                "name": name,
                "set": set_code,
                "number": card.get("number"),
                "uuid": uuid,
                "price": price,
            })

    # Choose the cheapest printing for each card.
    cheapest_cards = []

    for name in sorted(TEST_CARDS):
        options = matches.get(name, [])

        if not options:
            print(f"No CK price found: {name}", flush=True)
            continue

        cheapest = min(
            options,
            key=lambda item: (
                item["price"],
                item["set"],
                str(item["number"]),
            ),
        )

        cheapest_cards.append(cheapest)

        print(
            f"{name}: {cheapest['set']} "
            f"#{cheapest['number']} - "
            f"${cheapest['price']:.2f}",
            flush=True,
        )

    # Export the results to a CSV file.
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    with OUTPUT_FILE.open(
        "w", newline="", encoding="utf-8"
    ) as file:
        writer = csv.writer(file)

        writer.writerow([
            "Card Name",
            "Set Code",
            "Collector Number",
            "MTGJSON UUID",
            "CK Nonfoil USD",
        ])

        for card in cheapest_cards:
            writer.writerow([
                card["name"],
                card["set"],
                card["number"],
                card["uuid"],
                f"{card['price']:.2f}",
            ])

    print(f"CSV created: {OUTPUT_FILE}", flush=True)
    print(f"Cards exported: {len(cheapest_cards)}", flush=True)


if __name__ == "__main__":
    main()
