"""Validate a supplied 100-company universe against SEC filing metadata."""
from pathlib import Path
import hashlib
import json

import pandas as pd
from dotenv import load_dotenv

from tonecar.data import SEC


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data/companies_100_input.csv"
OUT = ROOT / "outputs/qa/company_list_100_validation.csv"


def main():
    rows = pd.read_csv(SOURCE, dtype={"cik": str, "ticker": str})
    assert len(rows) == 100
    assert set(rows.columns) == {"cik", "company_name", "ticker", "exchange", "n_10k"}
    assert rows.cik.str.fullmatch(r"\d{10}").all()
    assert rows.ticker.str.fullmatch(r"[A-Z][A-Z0-9.-]*").all()
    assert rows.cik.is_unique and rows.ticker.is_unique
    assert rows.n_10k.eq(10).all()
    load_dotenv(ROOT / ".env")
    sec = SEC(ROOT)
    results = []
    for n, row in enumerate(rows.itertuples(index=False), 1):
        record = {"ticker": row.ticker, "cik": row.cik, "input_company_name": row.company_name,
                  "input_n_10k": int(row.n_10k)}
        try:
            info = json.loads(sec.get(f"https://data.sec.gov/submissions/CIK{row.cik}.json"))
            record["sec_name"] = info["name"]
            batches = [info["filings"]["recent"]]
            for history in info["filings"].get("files", []):
                if history.get("filingTo", "9999") >= "2016-01-01" and history.get("filingFrom", "0000") <= "2026-12-31":
                    batches.append(json.loads(sec.get("https://data.sec.gov/submissions/" + history["name"])))
            annual = []
            for batch in batches:
                for i, form in enumerate(batch["form"]):
                    report = batch.get("reportDate", [""] * len(batch["form"]))[i]
                    filing = batch["filingDate"][i]
                    if form == "10-K" and report and "2016-01-01" <= report <= "2026-12-31" and filing <= "2026-09-28":
                        annual.append((report, batch["accessionNumber"][i]))
            record["candidate_10k"] = len(set(annual))
            record["distinct_report_years_2016_2025"] = len({int(date[:4]) for date, _ in annual if 2016 <= int(date[:4]) <= 2025})
            record["status"] = "ok" if record["distinct_report_years_2016_2025"] >= 10 else "check_history"
        except Exception as exc:
            record["status"] = "error"
            record["error"] = str(exc)
        results.append(record)
        pd.DataFrame(results).to_csv(OUT, index=False)
        print(f"{n:3d}/100 {row.ticker:6s} {record['status']:14s} {record.get('candidate_10k', 0)}", flush=True)
    digest = hashlib.sha256(SOURCE.read_bytes()).hexdigest()
    print(json.dumps({"input_sha256": digest, "companies": len(rows),
                      "ok": sum(r["status"] == "ok" for r in results),
                      "needs_review": [r["ticker"] for r in results if r["status"] != "ok"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
