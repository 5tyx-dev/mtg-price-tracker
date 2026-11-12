import json
import os
import tempfile
import time
from urllib.request import Request, urlopen

PRICES_URL = "https://mtgjson.com/api/v5/AllPricesToday.json"


def main():
    print("MTG Price Tracker")
    print("Testing MTGJSON pricing download...", flush=True)

    request = Request(
        PRICES_URL,
        headers={"User-Agent": "MTGPriceTracker/1.0"},
    )

    start = time.monotonic()
    total_bytes = 0

    with tempfile.TemporaryFile() as downloaded:
        with urlopen(request, timeout=120) as response:
            print("HTTP status:", response.status, flush=True)

            while True:
                chunk = response.read(1024 * 1024)
                if not chunk:
                    break

                downloaded.write(chunk)
                total_bytes += len(chunk)

        downloaded.seek(0)
        print(
            f"Downloaded {total_bytes / (1024 * 1024):.1f} MiB",
            flush=True,
        )

        # Check that the download contains valid JSON.
        metadata = json.load(downloaded)

    print("JSON validation successful!", flush=True)
    print("Top-level keys:", list(metadata.keys()), flush=True)
    print(
        f"Elapsed time: {time.monotonic() - start:.1f} seconds",
        flush=True,
    )


if __name__ == "__main__":
    main()
