import json
import tempfile
import time
from urllib.request import Request, urlopen

PRINTINGS_URL = "https://mtgjson.com/api/v5/AllPrintings.json"


def main():
    print("MTG Price Tracker")
    print("Testing MTGJSON AllPrintings download...", flush=True)

    request = Request(
        PRINTINGS_URL,
        headers={"User-Agent": "MTGPriceTracker/1.0"},
    )

    start = time.monotonic()
    total_bytes = 0

    with tempfile.TemporaryFile() as downloaded:
        with urlopen(request, timeout=180) as response:
            print("HTTP status:", response.status, flush=True)

            while True:
                chunk = response.read(1024 * 1024)
                if not chunk:
                    break

                downloaded.write(chunk)
                total_bytes += len(chunk)

        print(
            f"Downloaded {total_bytes / (1024 * 1024):.1f} MiB",
            flush=True,
        )

        downloaded.seek(0)
        payload = json.load(downloaded)

    sets = payload["data"]

    print("JSON validation successful!", flush=True)
    print("Total sets:", len(sets))

    # Inspect one card without printing the entire dataset.
    first_set_code = next(iter(sets))
    first_set = sets[first_set_code]
    first_card = first_set["cards"][0]

    print("Sample set code:", first_set_code)
    print("Sample card fields:", list(first_card.keys()))
    print("Sample card:")
    print(json.dumps({
        "name": first_card.get("name"),
        "uuid": first_card.get("uuid"),
        "number": first_card.get("number"),
        "finishes": first_card.get("finishes"),
        "isAlternative": first_card.get("isAlternative"),
    }, indent=2))

    print(
        f"Elapsed time: {time.monotonic() - start:.1f} seconds",
        flush=True,
    )


if __name__ == "__main__":
    main()
