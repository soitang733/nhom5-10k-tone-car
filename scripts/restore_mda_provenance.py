"""Propagate SEC Exhibit 13 URLs from the immutable extraction audit to views."""
from pathlib import Path
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
audit=pd.read_csv(ROOT/'data/extraction_audit.csv').set_index('accession')
lookup=audit.mda_source_url.dropna()
assert lookup.index.is_unique
assert len(lookup)==12,len(lookup)
paths=[ROOT/'data/tone_panel.csv']+[ROOT/'outputs/real'/rule/'car_panel.csv' for rule in ('same','next','acceptance')]
for path in paths:
    frame=pd.read_csv(path)
    before=frame.mda_source_url.notna().sum() if 'mda_source_url' in frame else 0
    frame['mda_source_url']=frame.accession.map(lookup)
    assert frame.mda_source_url.notna().sum()==12
    frame.to_csv(path,index=False)
    print(path.relative_to(ROOT),'exhibit URLs',before,'->',frame.mda_source_url.notna().sum())
