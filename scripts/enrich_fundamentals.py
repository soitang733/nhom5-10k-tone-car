"""Use SEC facts from the exact 10-K accession and period, never later filings."""
from pathlib import Path
import argparse, json, sys
import numpy as np
import pandas as pd
from dotenv import load_dotenv
root=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(root))
from tonecar.data import SEC
from tonecar.pipeline import output_results

def choose_fact(facts, tags, accession, end, duration=False):
    for tag in tags:
        entries=facts.get(tag,{}).get('units',{}).get('USD',[])
        rows=[e for e in entries if e.get('accn')==accession and e.get('end')==end and e.get('form')=='10-K']
        if duration:
            rows=[e for e in rows if e.get('start') and 330 <= (pd.Timestamp(e['end'])-pd.Timestamp(e['start'])).days <= 385]
        else:
            rows=[e for e in rows if not e.get('start')]
        values={float(e['val']) for e in rows if e.get('val') is not None}
        if len(values)==1:
            return values.pop(),tag,rows[0].get('start','')
        if len(values)>1:
            return np.nan,'ambiguous_'+tag,''
    return np.nan,'not_available_same_accession_period',''

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--prefetch',action='store_true');args=parser.parse_args()
    load_dotenv(root/'.env');sec=SEC(root)
    cfg=json.loads((root/'config.json').read_text(encoding='utf-8'))
    payloads={};errors=[]
    issuers=list(cfg['firms'].items())+[(ticker,p['cik']) for ticker,p in cfg.get('predecessor_ciks',{}).items()]
    for ticker,cik in issuers:
        print('SEC companyfacts:',ticker,flush=True)
        try:payloads[cik]=json.loads(sec.get(f'https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json'))
        except Exception as exc:errors.append({'ticker':ticker,'error':str(exc)})
    pd.DataFrame(errors,columns=['ticker','error']).to_csv(root/'data/fundamental_download_errors.csv',index=False)
    if args.prefetch:return
    manifest=pd.read_csv(root/'data/filings_manifest.csv');records=[]
    for row in manifest.itertuples():
        filing_cik=str(int(row.cik)).zfill(10)
        facts=payloads.get(filing_cik,{}).get('facts',{}).get('us-gaap',{})
        assets,atag,_=choose_fact(facts,['Assets'],row.accession,row.report_date)
        liabilities,ltag,_=choose_fact(facts,['Liabilities'],row.accession,row.report_date)
        income,itag,start=choose_fact(facts,['NetIncomeLoss','ProfitLoss'],row.accession,row.report_date,True)
        equity,etag,_=choose_fact(facts,['StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest'],row.accession,row.report_date)
        if pd.isna(liabilities) and not pd.isna(assets) and not pd.isna(equity):
            liabilities=assets-equity;ltag='Assets_minus_StockholdersEquityIncludingNoncontrolling'
        valid=pd.notna(assets) and assets>0
        records.append({'accession':row.accession,'ticker':row.ticker,'cik':filing_cik,'fiscal_year':row.fiscal_year,'report_date':row.report_date,'assets_usd':assets,'liabilities_usd':liabilities,'net_income_usd':income,'log_assets':np.log(assets) if valid else np.nan,'liabilities_assets':liabilities/assets if valid else np.nan,'roa':income/assets if valid else np.nan,'assets_tag':atag,'liabilities_tag':ltag,'income_tag':itag,'income_start':start,'fact_match':'exact_accession_exact_period','source_url':f"https://data.sec.gov/api/xbrl/companyfacts/CIK{filing_cik}.json"})
    frame=pd.DataFrame(records);frame.to_csv(root/'data/fundamentals_panel.csv',index=False)
    keep=['accession','assets_usd','liabilities_usd','net_income_usd','log_assets','liabilities_assets','roa']
    for rule in ['same','next','acceptance']:
        folder=root/'outputs/real'/rule
        panel=pd.read_csv(folder/'car_panel.csv').drop(columns=[c for c in keep[1:] if c in pd.read_csv(folder/'car_panel.csv',nrows=1).columns])
        panel=panel.merge(frame[keep],on='accession',how='left',validate='one_to_one')
        ar=pd.read_csv(folder/'event_ar.csv')
        output_results(panel,ar,folder,f'SEC 10-K: tone and market reaction - {len(cfg["firms"])}-firm exploratory study')
    print('Fundamental complete cases:',frame[['log_assets','liabilities_assets','roa']].notna().all(axis=1).sum(),'/',len(frame),flush=True)

if __name__=='__main__':main()
