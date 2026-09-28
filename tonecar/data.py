import hashlib
import json
import os
import re
import time
from pathlib import Path

import pandas as pd
import requests


class SEC:
    def __init__(self, root):
        self.root = Path(root)
        self.agent = os.getenv('SEC_USER_AGENT', '')
        if '@' not in self.agent or 'Your real' in self.agent:
            raise ValueError('Set SEC_USER_AGENT to a real group name and contact email in .env')
        self.last = 0
        self.session = requests.Session()

    def get(self, url):
        path = self.root / 'data/raw/sec' / (hashlib.sha256(url.encode()).hexdigest() + '.raw')
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.exists():
            return path.read_bytes()
        for attempt in range(4):
            time.sleep(max(0, .25 - (time.monotonic() - self.last)))
            self.last = time.monotonic()
            try:
                r = self.session.get(url, headers={'User-Agent': self.agent}, timeout=45)
                if r.status_code == 403:
                    raise RuntimeError('SEC denied access (403); stop and check requester identity/network')
                if r.status_code == 429 or r.status_code >= 500:
                    wait = r.headers.get('Retry-After', '')
                    time.sleep(float(wait) if wait.isdigit() else 2 ** attempt)
                    continue
                r.raise_for_status()
                path.write_bytes(r.content)
                path.with_suffix('.json').write_text(json.dumps({'url': url, 'downloaded_at': pd.Timestamp.now(tz='UTC').isoformat(), 'sha256': hashlib.sha256(r.content).hexdigest()}), encoding='utf-8')
                return r.content
            except requests.RequestException:
                if attempt == 3:
                    raise
                time.sleep(2 ** attempt)
        raise RuntimeError('SEC retries exhausted: ' + url)

    def filings(self, firms, years, predecessors=None):
        records = []
        issuers = [(ticker,cik,years[1]+1,'current') for ticker,cik in firms.items()]
        issuers += [(ticker,p['cik'],p['report_year_max'],'predecessor') for ticker,p in (predecessors or {}).items()]
        for ticker, cik, last_report_year, lineage in issuers:
            print('SEC filing history:', ticker, flush=True)
            data = json.loads(self.get(f'https://data.sec.gov/submissions/CIK{cik}.json'))
            batches = [data['filings']['recent']]
            for history in data['filings'].get('files', []):
                if history.get('filingTo','9999') < f'{years[0]}-01-01' or history.get('filingFrom','0000') > f'{years[1]+1}-12-31':
                    continue
                batches.append(json.loads(self.get('https://data.sec.gov/submissions/' + history['name'])))
            for batch in batches:
                for i, form in enumerate(batch['form']):
                    report = batch.get('reportDate', [''] * len(batch['form']))[i]
                    # Candidate buffer covers fiscal calendars ending in January.
                    if form != '10-K' or not report or not years[0] <= int(report[:4]) <= last_report_year:
                        continue
                    accession = batch['accessionNumber'][i]
                    document = batch['primaryDocument'][i]
                    url = f'https://www.sec.gov/Archives/edgar/data/{int(cik)}/{accession.replace("-", "")}/{document}'
                    records.append({'ticker': ticker, 'cik': cik, 'company_name': data['name'], 'issuer_lineage':lineage,
                                    'fiscal_year': int(report[:4]), 'report_date': report,
                                    'filing_date': batch['filingDate'][i], 'accession': accession,
                                    'acceptance': batch.get('acceptanceDateTime', [''] * len(batch['form']))[i],
                                    'source_url': url})
        if not records:
            raise ValueError('No eligible 10-K filings')
        df = pd.DataFrame(records).drop_duplicates('accession').sort_values(['ticker', 'report_date', 'filing_date'])
        df.to_csv(self.root / 'data/filing_candidates.csv', index=False)
        return df.drop_duplicates(['ticker', 'report_date'], keep='first')

    def exhibit13(self, filing):
        from bs4 import BeautifulSoup
        base=filing['source_url'].rsplit('/',1)[0]
        index=BeautifulSoup(self.get(base+'/'+filing['accession']+'-index.html'),'lxml')
        for row in index.select('table.tableFile tr'):
            cells=row.find_all('td')
            if len(cells)>=4 and re.fullmatch(r'EX-13(?:\.\d+)?', cells[3].get_text(strip=True).upper()):
                link=cells[2].find('a')
                if link:
                    from urllib.parse import urljoin
                    url=urljoin('https://www.sec.gov',link['href'])
                    if '/ix?doc=' in url:
                        url='https://www.sec.gov'+url.split('/ix?doc=',1)[1]
                    return url,self.get(url)
        raise ValueError('Referenced Exhibit 13 not found in SEC filing index')


def dictionary(root):
    path = Path(root) / 'data/external/lm.csv'
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        # The file ID is linked directly by the official Notre Dame SRAF page.
        url = 'https://drive.google.com/uc?export=download&id=1iq2RUf8qGFEAk1g8wQntP3habOnR3fXF'
        r = requests.get(url, timeout=90)
        r.raise_for_status()
        if b'Word' not in r.content[:1000] or b'Negative' not in r.content[:1000]:
            raise ValueError('Official dictionary download did not return CSV; place official CSV at data/external/lm.csv')
        path.write_bytes(r.content)
    return path


def prices(root, ticker, start, end):
    import yfinance as yf
    path = Path(root) / 'data/raw/market' / (ticker.replace('^', '') + '_' + start + '_' + end + '.csv')
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        frame = pd.read_csv(path, index_col=0, parse_dates=True)
        return frame['Close']
    frame = yf.download(ticker, start=start, end=end, auto_adjust=True, prepost=False, progress=False, threads=False)
    if frame.empty:
        raise ValueError('No market data: ' + ticker)
    close = frame['Close']
    if isinstance(close, pd.DataFrame):
        close = close.iloc[:, 0]
    close.index = pd.DatetimeIndex(close.index).tz_localize(None).normalize()
    close.rename('Close').to_frame().to_csv(path)
    return close
