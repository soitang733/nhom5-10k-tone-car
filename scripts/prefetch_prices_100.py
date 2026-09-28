"""Cache market prices for the frozen 100-firm manifest with audit results."""
from pathlib import Path
import json
import time

import pandas as pd

from tonecar.data import prices


ROOT = Path(__file__).resolve().parents[1]


def main():
    cfg = json.loads((ROOT / "config.json").read_text(encoding="utf-8"))
    manifest = pd.read_csv(ROOT / "data/filings_manifest.csv")
    start = (pd.to_datetime(manifest.filing_date).min() - pd.Timedelta(days=300)).date().isoformat()
    end = (pd.to_datetime(manifest.filing_date).max() + pd.Timedelta(days=35)).date().isoformat()
    results = []
    for n, ticker in enumerate([cfg["benchmark"], *cfg["firms"]], 1):
        record = {"ticker": ticker, "start": start, "end": end}
        for attempt in range(3):
            try:
                series = prices(ROOT, ticker, start, end)
                record.update({"rows": len(series), "first_price_date": str(series.index.min().date()),
                               "last_price_date": str(series.index.max().date()), "status": "ok"})
                break
            except Exception as exc:
                record.update({"status": "error", "error": str(exc)})
                if attempt < 2:
                    time.sleep(3 * (attempt + 1))
        results.append(record)
        pd.DataFrame(results).to_csv(ROOT / "outputs/qa/prices_100_validation.csv", index=False)
        print(f"{n:3d}/101 {ticker:6s} {record['status']}", flush=True)
        time.sleep(.3)
    print("Market errors:", [x["ticker"] for x in results if x["status"] != "ok"])


if __name__ == "__main__":
    main()
