"""Loopback-only research dashboard. Serves a fixed public directory and read-only APIs."""
import argparse
import json
import math
import mimetypes
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

import pandas as pd
import statsmodels.formula.api as smf

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / 'web'
ALIGNMENTS = {'same', 'next', 'acceptance'}


def records(path):
    if not path.exists():
        return []
    try:
        frame = pd.read_csv(path)
    except pd.errors.EmptyDataError:
        return []
    return json.loads(frame.to_json(orient='records', date_format='iso', double_precision=15))


def data():
    panels, regressions, ar = {}, {}, {}
    for rule in ALIGNMENTS:
        base = ROOT / 'outputs/real' / rule
        panels[rule] = records(base / 'car_panel.csv')
        regressions[rule] = records(base / 'regressions.csv')
        ar[rule] = records(base / 'event_ar.csv')
    metadata = json.loads((ROOT / 'outputs/real/run_metadata.json').read_text(encoding='utf-8'))
    return {'panels': panels, 'regressions': regressions, 'ar': ar, 'metadata': metadata,
            'manifest': records(ROOT / 'data/filings_manifest.csv'),
            'audit': records(ROOT / 'data/extraction_audit.csv'),
            'exclusions': records(ROOT / 'data/exclusions.csv'),
            'generic': records(ROOT / 'data/generic_comparison.csv'),
            'earnings': records(ROOT / 'data/earnings_8k_flags.csv'),
            'review': records(ROOT / 'data/research_audit.csv'),
            'universe':records(ROOT / 'data/sample_universe.csv'),
            'fundamentals':records(ROOT / 'data/fundamentals_panel.csv'),
            'sample_comparison':records(ROOT / 'outputs/real/same/sample_comparison.csv')}


def regression(query):
    rule = query.get('alignment', ['same'])[0]
    window = query.get('window', ['-1_1'])[0]
    spec = query.get('spec', ['tone'])[0]
    covariance = query.get('covariance', ['HC3'])[0]
    if rule not in ALIGNMENTS or window not in {'-1_1', '-3_3', '-5_5'}:
        raise ValueError('Invalid alignment/window')
    specs = {'tone': 'tone', 'year': 'tone + C(fiscal_year)', 'firm': 'tone + C(fiscal_year) + C(ticker)',
             'negative': 'negative_rate + uncertainty_rate', 'generic': 'generic_tone',
             'delta':'delta_tone', 'delta_year':'delta_tone + C(fiscal_year)', 'delta_firm':'delta_tone + C(fiscal_year) + C(ticker)',
             'controls':'tone + log_assets + liabilities_assets + roa + C(fiscal_year)',
             'delta_controls':'delta_tone + log_assets + liabilities_assets + roa + C(fiscal_year)'}
    if spec not in specs or covariance not in {'HC3', 'cluster'}:
        raise ValueError('Invalid specification/covariance')
    panel_path = ROOT / 'outputs/real' / rule / 'car_panel.csv'
    if not panel_path.exists():
        panel_path = ROOT / 'snapshot' / f'{rule}_panel.csv'
    frame = pd.read_csv(panel_path)
    ticker = query.get('ticker', ['all'])[0]
    year = query.get('year', ['all'])[0]
    if ticker != 'all':
        frame = frame[frame.ticker == ticker]
    if year != 'all':
        frame = frame[frame.fiscal_year == int(year)]
    if query.get('clean', ['0'])[0] == '1':
        flags = records(ROOT / 'data/earnings_8k_flags.csv')
        blocked = {f['event_id'].rsplit('_', 1)[0] for f in flags if f['flagged_8k_item202']}
        frame = frame[~frame.accession.isin(blocked)]
    if spec.startswith('delta'):
        if 'delta_tone' not in frame:
            return {'available':False,'reason':'Snapshot này chưa có biến thay đổi tone.', 'n':0}
        frame = frame.dropna(subset=['delta_tone'])
    if 'controls' in spec:
        needed=['log_assets','liabilities_assets','roa']
        if not all(c in frame for c in needed):
            return {'available':False,'reason':'Chưa có đủ dữ liệu fundamentals trong snapshot này.','n':0}
        frame=frame.dropna(subset=needed)
    if len(frame) < 8:
        return {'available': False, 'reason': 'Mẫu lọc có ít hơn 8 quan sát; không xuất hồi quy thiếu tin cậy.', 'n': len(frame)}
    model = smf.ols(f'Q("car_{window}") ~ {specs[spec]}', frame)
    if len(frame) - model.exog.shape[1] < 5:
        return {'available': False, 'reason': 'Không đủ bậc tự do cho đặc tả đã chọn.', 'n': len(frame)}
    import numpy as np
    if np.linalg.matrix_rank(model.exog) < model.exog.shape[1]:
        return {'available': False, 'reason': 'Ma trận biến giải thích không đủ hạng; đổi bộ lọc hoặc mô hình.', 'n': len(frame)}
    if covariance == 'cluster':
        if frame.ticker.nunique() < 5:
            return {'available': False, 'reason': 'Cần ít nhất 5 công ty cho đối chứng cluster; số clusters nhỏ vẫn là hạn chế.', 'n': len(frame)}
        fit = model.fit(cov_type='cluster', cov_kwds={'groups': frame.ticker, 'use_correction': True}, use_t=True)
    else:
        fit = model.fit(cov_type='HC3')
    rows = []
    for term in fit.params.index:
        if term not in {'Intercept', 'tone', 'delta_tone', 'log_assets', 'liabilities_assets', 'roa', 'negative_rate', 'uncertainty_rate', 'generic_tone'}:
            continue
        ci = fit.conf_int().loc[term]
        values = {'term': term, 'coefficient': fit.params[term], 'se': fit.bse[term],
                  'p': fit.pvalues[term], 'low': ci.iloc[0], 'high': ci.iloc[1]}
        rows.append({k: (float(v) if math.isfinite(float(v)) else None) if k != 'term' else v for k, v in values.items()})
    return {'available': True, 'n': int(fit.nobs), 'r2': fit.rsquared, 'clusters': frame.ticker.nunique(),
            'rows': rows, 'formula': f'CAR[{window.replace("_", ",")}] ~ {specs[spec]}', 'covariance': covariance,
            'note': 'Hồi quy khám phá theo bộ lọc; p-value chưa hiệu chỉnh cho mọi lựa chọn tương tác. Không suy luận nhân quả.'}


DOWNLOADS = {'report': ROOT / 'outputs/Nhom5_BaoCao.html',
             'pdf': ROOT / 'outputs/Nhom5_BaoCao.pdf',
             'panel': ROOT / 'outputs/real/same/car_panel.csv',
             'regressions': ROOT / 'outputs/real/same/regressions.csv',
             'audit': ROOT / 'data/research_audit.csv',
             'zip': ROOT.parent / 'Nhom5_Tone_CAR.zip'}


class Handler(BaseHTTPRequestHandler):
    def send(self, body, mime='application/json; charset=utf-8', status=200, filename=None):
        if isinstance(body, (dict, list)):
            body = json.dumps(body, ensure_ascii=False, allow_nan=False).encode('utf-8')
        elif isinstance(body, str):
            body = body.encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', mime)
        self.send_header('Content-Length', str(len(body)))
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.send_header('Cache-Control', 'no-store')
        if filename:
            self.send_header('Content-Disposition', f'attachment; filename="{filename}"')
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        request = urlparse(self.path)
        query = parse_qs(request.query)
        try:
            if request.path == '/api/health':
                return self.send({'status': 'ok', 'project': 'Nhom 5 Tone CAR'})
            if request.path == '/api/data':
                return self.send(data())
            if request.path == '/raw-filing':
                import hashlib
                accession = query.get('accession', [''])[0]
                filing = next((r for r in records(ROOT / 'data/filings_manifest.csv') if r['accession'] == accession), None)
                if filing is None:
                    return self.send({'error': 'Unknown filing'}, status=404)
                part=query.get('part',['primary'])[0]
                if part not in {'primary','mda'}:
                    raise ValueError('Invalid filing part')
                source=filing.get('mda_source_url') if part=='mda' else filing['source_url']
                source=source or filing['source_url']
                raw_path = ROOT / 'data/raw/sec' / (hashlib.sha256(source.encode()).hexdigest() + '.raw')
                if not raw_path.exists():
                    return self.send({'error': 'Saved raw filing not found'}, status=404)
                content=raw_path.read_bytes()
                return self.send(content, 'application/pdf' if content.startswith(b'%PDF') else 'text/html')
            if request.path == '/api/regression':
                return self.send(regression(query))
            if request.path == '/api/section':
                accession = query.get('accession', [''])[0]
                manifest = records(ROOT / 'data/filings_manifest.csv')
                row = next((r for r in manifest if r['accession'] == accession), None)
                if row is None:
                    return self.send({'error': 'Unknown filing'}, status=404)
                path = ROOT / 'data/interim/mda' / (accession + '.txt')
                if not path.exists():
                    return self.send({'error': 'Filing được loại do không có MD&A đủ rõ.', 'source_url': row['source_url']}, status=404)
                from .text import load_lm
                lexicon = load_lm(ROOT / 'data/external/lm.csv')
                return self.send({'text': path.read_text(encoding='utf-8'), 'filing': row,
                                  'lexicon': {k: sorted(v) for k, v in lexicon.items()}})
            if request.path == '/api/document':
                doc = query.get('name', ['REPORT'])[0]
                if doc not in {'REPORT', 'METHODOLOGY', 'DEFENSE', 'REFERENCES', 'REAL_RESULTS', 'EXTRACTION_REVIEW', 'DATA_SOURCES', 'SAMPLE_DESIGN', 'EXPANDED_RESULTS', 'LITERATURE_COMPARISON', 'TEXT_PROCESSING_REVIEW', 'LIMITATIONS_REMEDIATION'}:
                    raise ValueError('Unknown document')
                return self.send({'text': (ROOT / 'docs' / (doc + '.md')).read_text(encoding='utf-8')})
            if request.path == '/download':
                path = DOWNLOADS.get(query.get('file', [''])[0])
                if path is None or not path.exists():
                    return self.send({'error': 'Download not found'}, status=404)
                return self.send(path.read_bytes(), mimetypes.guess_type(str(path))[0] or 'application/octet-stream', filename=path.name)
            if request.path == '/report':
                return self.send(DOWNLOADS['report'].read_bytes(), 'text/html; charset=utf-8')
            relative = 'index.html' if request.path == '/' else request.path.lstrip('/')
            path = (PUBLIC / relative).resolve()
            if not path.is_relative_to(PUBLIC.resolve()) or not path.is_file():
                return self.send({'error': 'Not found'}, status=404)
            mime = mimetypes.guess_type(str(path))[0] or 'application/octet-stream'
            if path.suffix in {'.html', '.css', '.js'}:
                mime += '; charset=utf-8'
            return self.send(path.read_bytes(), mime)
        except (ValueError, KeyError) as exc:
            self.send({'error': str(exc)}, status=400)
        except Exception as exc:
            self.log_error('%s', exc)
            self.send({'error': 'Không đọc được dữ liệu. Kiểm tra log local.'}, status=500)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default=8765)
    args = parser.parse_args()
    server = ThreadingHTTPServer(('127.0.0.1', args.port), Handler)
    print(f'Nhóm 5 dashboard: http://127.0.0.1:{args.port}', flush=True)
    server.serve_forever()


if __name__ == '__main__':
    main()
