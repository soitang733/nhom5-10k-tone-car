"""Verify that every result has a local SEC original and exact input firm."""
from pathlib import Path
import hashlib
import json

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
source = pd.read_csv(ROOT/'data/companies_100_input.csv', dtype={'cik':str})
manifest = pd.read_csv(ROOT/'data/filings_manifest.csv',dtype={'cik':str})
tone = pd.read_csv(ROOT/'data/tone_panel.csv')
audit = pd.read_csv(ROOT/'data/extraction_audit.csv')
exhibit_audit = audit.set_index('accession')
exhibit_lookup = exhibit_audit.mda_source_url.dropna()
panels = {rule:pd.read_csv(ROOT/'outputs/real'/rule/'car_panel.csv') for rule in ('same','next','acceptance')}
expected = {(row.ticker, year) for row in source.itertuples() for year in range(2016,2026)}
checks = {
    'input_companies':len(source),
    'manifest_filings':len(manifest),
    'tone_filings':len(tone),
    'extraction_audit_filings':len(audit),
    'events_by_alignment':{rule:len(panel) for rule,panel in panels.items()},
    'accessions_unique':bool(manifest.accession.is_unique),
    'company_years_exact':set(zip(manifest.ticker,manifest.fiscal_year))==expected,
    'no_exclusions':pd.read_csv(ROOT/'data/exclusions.csv').empty,
}
assert len(source)==100 and len(manifest)==len(tone)==len(audit)==1000
assert checks['accessions_unique'] and checks['company_years_exact'] and checks['no_exclusions']
assert set(manifest.accession)==set(tone.accession)==set(audit.accession)
assert all(len(panel)==1000 and set(panel.accession)==set(manifest.accession) for panel in panels.values())
lookup = source.set_index('ticker').cik.to_dict()
assert all(str(row.cik).zfill(10)==lookup[row.ticker] for row in manifest.itertuples())
raw_bytes = 0
exhibits = 0
for row in tone.itertuples():
    stem = hashlib.sha256(row.source_url.encode()).hexdigest()
    path = ROOT/'data/raw/sec'/f'{stem}.raw'
    sidecar = ROOT/'data/raw/sec'/f'{stem}.json'
    assert path.exists() and sidecar.exists(),row.accession
    payload = path.read_bytes()
    digest = hashlib.sha256(payload).hexdigest()
    provenance = json.loads(sidecar.read_text(encoding='utf-8'))
    assert digest==row.raw_sha256==provenance['sha256'] and provenance['url']==row.source_url,row.accession
    assert (ROOT/'data/interim/mda'/f'{row.accession}.txt').exists(),row.accession
    raw_bytes += len(payload)
    exhibit_url = exhibit_lookup.get(row.accession)
    if pd.notna(exhibit_url) and exhibit_url != row.source_url:
        exhibit = ROOT/'data/raw/sec'/f'{hashlib.sha256(exhibit_url.encode()).hexdigest()}.raw'
        assert exhibit.exists(),row.accession
        assert hashlib.sha256(exhibit.read_bytes()).hexdigest()==exhibit_audit.loc[row.accession,'mda_raw_sha256'],row.accession
        exhibits += 1
checks.update({'raw_sec_files_verified':1000,'raw_primary_gib_verified':round(raw_bytes/2**30,3),
               'incorporated_exhibits_verified':exhibits,
               'input_sha256':hashlib.sha256((ROOT/'data/companies_100_input.csv').read_bytes()).hexdigest()})
out = ROOT/'outputs/qa/final_100_audit.json'
out.write_text(json.dumps(checks,ensure_ascii=False,indent=2),encoding='utf-8')
print(out)
print(json.dumps(checks,ensure_ascii=False))
