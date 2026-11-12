import csv
import json
from pathlib import Path
from urllib.request import Request, urlopen

PRINTINGS_URL = "https://mtgjson.com/api/v5/AllPrintings.json"
PRICES_URL = "https://mtgjson.com/api/v5/AllPricesToday.json"

INPUT_FILE = Path("data/card_names.csv")
OUTPUT_FILE = Path("output/ck_prices_test.csv")


def download_json(url):
    request = Request(
        url,
        headers={"User-Agent": "MTGPriceTracker/1.0"},
    )

    with urlopen(request, timeout=180) as response:
        return json.load(response)["data"]


def load_card_names():
    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"Card list not found: {INPUT_FILE}"
        )

    with INPUT_FILE.open(
        "r", newline="", encoding="utf-8-sig"
    ) as file:
        reader = csv.DictReader(file)

        if reader.fieldnames != ["Card Name"]:
            raise ValueError(
                "Expected a CSV with one column: Card Name"
            )

        names = {
            row["Card Name"].strip()
            for row in reader
            if row["Card Name"] and row["Card Name"].strip()
        }

    if not names:
        raise ValueError("Card list is empty.")

    return names


def main():
    print("MTG Price Tracker", flush=True)

    # Read unique card names from Google Sheets export.
    card_names = load_card_names()

    print(
        f"Unique cards requested: {len(card_names)}",
        flush=True,
    )

    print("Downloading Card Kingdom pricing...", flush=True)
    prices = download_json(PRICES_URL)

    print("Downloading printing information...", flush=True)
    sets = download_json(PRINTINGS_URL)

    matches = {}

    for set_code, set_data in sets.items():
        for card in set_data.get("cards", []):
            name = card.get("name")

            if name not in card_names:
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

            if (
                not isinstance(price, (int, float))
                or isinstance(price, bool)
                or price <= 0
            ):
                continue

            matches.setdefault(name, []).append({
                "name": name,
                "set": set_code,
                "number": card.get("number", ""),
                "uuid": uuid,
                "price": price,
            })

    # Choose the cheapest nonfoil printing per card.
    cheapest_cards = []
    missing_cards = []

    print("\nCHEAPEST NONFOIL PRINTINGS", flush=True)

    for name in sorted(card_names):
        options = matches.get(name, [])

        if not options:
            missing_cards.append(name)
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

    # Export prices using our existing five-column format.
    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

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

    print("\nEXPORT SUMMARY", flush=True)
    print(f"Cards requested: {len(card_names)}", flush=True)
    print(f"Cards exported: {len(cheapest_cards)}", flush=True)
    print(f"Cards without CK prices: {len(missing_cards)}", flush=True)
    print(f"CSV created: {OUTPUT_FILE}", flush=True)


if __name__ == "__main__":
    main()
