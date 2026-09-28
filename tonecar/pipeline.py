import argparse
import hashlib
import json
import platform
import time
from collections import Counter
from pathlib import Path

import exchange_calendars as xcals
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from dotenv import load_dotenv

from .data import SEC, dictionary, prices
from .event import event_position, study
from .text import extract_mda, load_lm, score, tokenize, fiscal_year

def atomic_csv(frame, path):
    path=Path(path)
    temp=path.with_suffix(path.suffix+'.pending')
    frame.to_csv(temp,index=False)
    for attempt in range(10):
        try:
            temp.replace(path)
            return
        except PermissionError:
            if attempt == 9:
                raise
            time.sleep(.15 * (attempt + 1))


def regressions(panel, output):
    from statsmodels.stats.diagnostic import het_breuschpagan
    from statsmodels.stats.multitest import multipletests
    specs = ['tone', 'tone + C(fiscal_year)', 'tone + C(fiscal_year) + C(ticker)',
             'negative_rate + uncertainty_rate', 'generic_tone']
    if 'delta_tone' in panel and panel.delta_tone.notna().sum() >= 20:
        specs += ['delta_tone', 'delta_tone + C(fiscal_year)', 'delta_tone + C(fiscal_year) + C(ticker)']
    if all(c in panel for c in ['log_assets','liabilities_assets','roa']):
        specs += ['tone + log_assets + liabilities_assets + roa + C(fiscal_year)',
                  'delta_tone + log_assets + liabilities_assets + roa + C(fiscal_year)']
    results, diagnostics = [], []
    for outcome in ['car_-1_1', 'car_-3_3', 'car_-5_5', 'mar_-1_1']:
        for rhs in specs:
            needed = [c for c in ['tone','delta_tone','log_assets','liabilities_assets','roa'] if c in rhs.split(' + ')]
            if len(panel.dropna(subset=needed)) < 20:
                continue
            complete = panel.dropna(subset=needed)
            model = smf.ols(f'Q("{outcome}") ~ {rhs}', complete).fit(cov_type='HC3')
            if model.df_resid < 10 or np.linalg.matrix_rank(model.model.exog) < model.model.exog.shape[1]:
                continue
            diagnostics.append({'outcome': outcome, 'specification': rhs,
                                'condition_number': model.condition_number,
                                'bp_pvalue': het_breuschpagan(model.resid, model.model.exog)[1],
                                'residual_df': model.df_resid})
            for term in model.params.index:
                if term in ['tone', 'delta_tone', 'negative_rate', 'uncertainty_rate', 'generic_tone']:
                    ci = model.conf_int().loc[term]
                    results.append({'outcome': outcome, 'specification': rhs, 'term': term,
                                    'coefficient': model.params[term], 'se_HC3': model.bse[term],
                                    'p_value': model.pvalues[term], 'ci_low': ci.iloc[0], 'ci_high': ci.iloc[1],
                                    'n': model.nobs, 'r2': model.rsquared})
    result_frame = pd.DataFrame(results)
    if results:
        result_frame['p_holm_all_reported_tests'] = multipletests(result_frame.p_value, method='holm')[1]
    result_frame.to_csv(output / 'regressions.csv', index=False)
    pd.DataFrame(diagnostics).to_csv(output / 'diagnostics.csv', index=False)
    if not results:
        raise ValueError('Not enough independent observations for regression; need a larger sample')


def add_tone_changes(panel):
    """Only compare consecutive fiscal years of the same issuer/alignment."""
    panel = panel.copy()
    groups = ['ticker'] + (['alignment_rule'] if 'alignment_rule' in panel else [])
    panel = panel.sort_values(groups + ['fiscal_year'])
    grouped = panel.groupby(groups)
    previous_year = grouped.fiscal_year.shift(1)
    panel['previous_fiscal_year'] = previous_year
    panel['delta_tone'] = grouped.tone.diff().where(panel.fiscal_year - previous_year == 1)
    return panel


def output_results(panel, ars, output, label):
    if not {'relative_day','abnormal_return','event_id'}.issubset(ars.columns):
        raise ValueError('Event return table must retain relative_day, abnormal_return and event_id columns')
    panel = add_tone_changes(panel)
    output.mkdir(parents=True, exist_ok=True)
    panel.to_csv(output / 'car_panel.csv', index=False)
    ars.to_csv(output / 'event_ar.csv', index=False)
    panel.select_dtypes('number').describe().T.to_csv(output / 'descriptive.csv')
    regressions(panel, output)
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.scatter(panel.tone, panel['car_-1_1'] * 100, alpha=.65)
    ax.set(xlabel='LM net tone', ylabel='CAR [-1,+1] (%)', title=label)
    fig.tight_layout(); fig.savefig(output / 'tone_car.png', dpi=180); plt.close(fig)
    path = ars.groupby('relative_day').abnormal_return.mean().cumsum()
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(path.index, path * 100, marker='o'); ax.axvline(0, color='gray', linestyle='--')
    ax.set(xlabel='Trading days relative to filing', ylabel='Cumulative average AR from day -5 (%)', title=label)
    fig.tight_layout(); fig.savefig(output / 'caar.png', dpi=180); plt.close(fig)


def demo(root):
    """Deterministic test data; never presented as empirical findings."""
    rng = np.random.default_rng(42)
    sessions = pd.bdate_range('2020-01-01', periods=330)
    market = pd.Series(rng.normal(0, .01, len(sessions)), index=sessions)
    panel, ars = [], []
    for i in range(60):
        tone = rng.uniform(-.025, .01)
        stock = .0002 + 1.1 * market + rng.normal(0, .008, len(sessions))
        stock.iloc[200:203] += tone * .2
        stats, ar = study(stock, market, sessions, 201)
        row = {'ticker': f'DEMO{i % 10}', 'fiscal_year': 2019 + i // 10, 'event_id': f'SYNTHETIC_{i}',
               'tone': tone, 'negative_rate': .03 - tone, 'uncertainty_rate': rng.uniform(.005, .02),
               'generic_tone': tone + rng.normal(0, .01), 'data_kind': 'SYNTHETIC'}
        panel.append(row | stats); ar['event_id'] = row['event_id']; ars.append(ar)
    output_results(pd.DataFrame(panel), pd.concat(ars), root / 'outputs/demo', 'SYNTHETIC DEMO - not research evidence')


def real(root, cfg, reuse_text=False):
    from nltk.sentiment import SentimentIntensityAnalyzer
    import nltk
    if not (root / 'data/external/nltk/sentiment/vader_lexicon.zip').exists():
        if not nltk.download('vader_lexicon', download_dir=str(root / 'data/external/nltk'), quiet=True):
            raise RuntimeError('VADER word list download failed')
    nltk.data.path.insert(0, str(root / 'data/external/nltk'))
    generic = SentimentIntensityAnalyzer()
    sec = SEC(root)
    lm_path = dictionary(root)
    lexicon = load_lm(lm_path)
    previous_tones = pd.read_csv(root / 'data/tone_panel.csv') if reuse_text and (root / 'data/tone_panel.csv').exists() else pd.DataFrame()
    previous_audit = pd.read_csv(root / 'data/extraction_audit.csv') if reuse_text and (root / 'data/extraction_audit.csv').exists() else pd.DataFrame()
    archive = root / 'outputs/archive/baseline_100'
    if reuse_text and archive.exists():
        previous_tones = pd.concat([previous_tones, pd.read_csv(archive / 'tone_panel.csv')]).drop_duplicates('accession',keep='first')
        previous_audit = pd.concat([previous_audit, pd.read_csv(archive / 'extraction_audit.csv')]).drop_duplicates('accession',keep='first')
    manifest = sec.filings(cfg['firms'], cfg['years'],cfg.get('predecessor_ciks'))
    manifest = manifest[manifest.filing_date <= cfg.get('as_of', '9999-12-31')].copy()
    manifest.to_csv(root / 'data/filings_manifest.csv', index=False)
    tones, audit, errors = [], [], []
    generic_noise = Counter()
    section_dir = root / 'data/interim/mda'; section_dir.mkdir(parents=True, exist_ok=True)
    for _, row in manifest.iterrows():
        item = row.to_dict()
        print('Text:', item['ticker'], item['report_date'], flush=True)
        try:
            raw = sec.get(item['source_url'])
            from bs4 import UnicodeDammit
            html = UnicodeDammit(raw, is_html=True).unicode_markup
            html = html.translate({n: bytes([n]).decode('cp1252', errors='replace') for n in range(128,160)})
            existing = previous_tones[previous_tones.accession == item['accession']] if not previous_tones.empty else pd.DataFrame()
            if not existing.empty and existing.iloc[0].raw_sha256 == hashlib.sha256(raw).hexdigest():
                item['fiscal_year'], item['fiscal_year_source'] = int(existing.iloc[0].fiscal_year), existing.iloc[0].fiscal_year_source
            else:
                item['fiscal_year'], item['fiscal_year_source'] = fiscal_year(html, item['fiscal_year'])
            report_year = int(item['report_date'][:4])
            report_month = int(item['report_date'][5:7])
            # These issuers close a 52/53-week fiscal year in Jan/Feb. Older
            # cover-page regexes report the calendar end year, whereas later
            # DEI values correctly label the prior fiscal year.
            if item['ticker'] in {'DG', 'ROST', 'ULTA', 'WSM', 'TDY'} and report_month <= 2:
                item['fiscal_year'] = report_year - 1
                item['fiscal_year_source'] = 'issuer_52_53_week_Jan_Feb_end_previous_year'
            if item['ticker'] == 'KHC' and report_month <= 2:
                item['fiscal_year'] = report_year - 1
                item['fiscal_year_source'] = 'KHC_53_week_January_end_previous_year'
            if item['ticker'] in {'ACGL', 'WRB', 'FCX'} and report_month == 12 and item['fiscal_year'] != report_year:
                item['fiscal_year'] = report_year
                item['fiscal_year_source'] = 'audited_December_cover_period_overrides_stale_DEI_or_cache'
            if item['ticker'] == 'JNJ' and item['report_date'][5:7] == '01' and item['fiscal_year_source'] != 'dei:DocumentFiscalYearFocus':
                item['fiscal_year'] = int(item['report_date'][:4]) - 1
                item['fiscal_year_source'] = 'JNJ_52_53_week_year_January_ending_previous_year'
            if item['ticker']=='HD' and int(item['report_date'][:4])<=2019:
                item['fiscal_year']=int(item['report_date'][:4])-1
                item['fiscal_year_source']='HD_fiscal_glossary_52_53_week_year_previous_calendar_year'
            if item['accession']=='0000773840-22-000018':
                item['fiscal_year']=2021
                item['fiscal_year_source']='audited_override_DEI_2020_conflicts_with_cover_and_period_2021'
            if item['accession']=='0001108524-26-000060':
                item['fiscal_year']=2026
                item['fiscal_year_source']='audited_override_DEI_2025_conflicts_with_cover_and_fiscal_label_2026'
            manifest.loc[manifest.accession == item['accession'], 'fiscal_year'] = item['fiscal_year']
            if not cfg['years'][0] <= item['fiscal_year'] <= cfg['years'][1]:
                continue
            cached = previous_tones[previous_tones.accession == item['accession']] if not previous_tones.empty else pd.DataFrame()
            cached_audit = previous_audit[previous_audit.accession == item['accession']] if not previous_audit.empty else pd.DataFrame()
            section_path = section_dir / (item['accession'] + '.txt')
            if not cached.empty and not cached_audit.empty and section_path.exists() and cached.iloc[0].raw_sha256 == hashlib.sha256(raw).hexdigest() and cached.iloc[0].lm_sha256 == hashlib.sha256(lm_path.read_bytes()).hexdigest():
                text = section_path.read_text(encoding='utf-8')
                diagnostics = cached_audit.iloc[0].to_dict()
                if len(tokenize(text)) != int(diagnostics['word_count']):
                    raise ValueError('Cached section failed token-count integrity check')
                if pd.notna(diagnostics.get('mda_source_url')):
                    item['mda_source_url'] = diagnostics['mda_source_url']
            else:
                if item['ticker'] == 'WMT' and item['fiscal_year'] in {2016, 2017}:
                    item['mda_source_url'] = item['source_url'].rsplit('/', 1)[0] + f"/wmtars-131{item['fiscal_year']}.htm"
                    exhibit = sec.get(item['mda_source_url'])
                    exhibit_html = UnicodeDammit(exhibit, is_html=True).unicode_markup
                    # Annual-report Exhibit 13 uses Item 2 for MD&A and Item 3
                    # for financial statements. Preserve the original provenance.
                    import re
                    exhibit_html = re.sub(r'Item(\s|&nbsp;|&#160;)*2', 'Item 7', exhibit_html, flags=re.I)
                    exhibit_html = re.sub(r'Item(\s|&nbsp;|&#160;)*3', 'Item 8', exhibit_html, flags=re.I)
                    text, diagnostics = extract_mda(exhibit_html, cfg['min_words'], issuer='WMT')
                    diagnostics['extraction_method'] = 'incorporated_Exhibit_13_WMT'
                    diagnostics['mda_source_url'] = item['mda_source_url']
                    diagnostics['mda_raw_sha256'] = hashlib.sha256(exhibit).hexdigest()
                else:
                    try:
                        text, diagnostics = extract_mda(html, cfg['min_words'], issuer=item['ticker'])
                    except ValueError:
                        if item['ticker'] not in {'CCL','CVX','IBM','MLM','NUE','PFE','UNP','WFC'}:
                            raise
                        item['mda_source_url'],exhibit=sec.exhibit13(item)
                        if exhibit.startswith(b'%PDF'):
                            import pymupdf,html as html_module
                            document=pymupdf.open(stream=exhibit,filetype='pdf')
                            exhibit_html=''.join('<p>'+html_module.escape(line)+'</p>' for page in document for line in page.get_text().splitlines())
                            source_format='PDF'
                        else:
                            exhibit_html=UnicodeDammit(exhibit,is_html=True).unicode_markup
                            source_format='HTML'
                        text,diagnostics=extract_mda(exhibit_html,cfg['min_words'],issuer=item['ticker'])
                        diagnostics.update({'extraction_method':'incorporated_Exhibit_13_'+item['ticker'],'mda_source_url':item['mda_source_url'],'mda_source_format':source_format,'mda_raw_sha256':hashlib.sha256(exhibit).hexdigest()})
            manifest.loc[manifest.accession == item['accession'], 'fiscal_year'] = item['fiscal_year']
            manifest.loc[manifest.accession == item['accession'], 'fiscal_year_source'] = item['fiscal_year_source']
            if diagnostics.get('mda_source_url') and pd.notna(diagnostics['mda_source_url']):
                manifest.loc[manifest.accession == item['accession'], 'mda_source_url'] = diagnostics['mda_source_url']
            (section_dir / (item['accession'] + '.txt')).write_text(text, encoding='utf-8')
            audit.append({'accession': item['accession']} | diagnostics)
            tokens = tokenize(text)
            generic_words = generic.lexicon
            generic_pos = sum(generic_words.get(w.lower(), 0) > 0 for w in tokens)
            generic_neg = sum(generic_words.get(w.lower(), 0) < 0 for w in tokens)
            generic_noise.update(w for w in tokens if generic_words.get(w.lower(), 0) < 0 and w not in lexicon['negative'])
            tones.append(item | score(text, lexicon) | {'generic_tone': (generic_pos - generic_neg) / len(tokens),
                         'generic_positive_rate': generic_pos / len(tokens), 'generic_negative_rate': generic_neg / len(tokens),
                         'raw_sha256': hashlib.sha256(raw).hexdigest(),
                         'lm_sha256': hashlib.sha256(lm_path.read_bytes()).hexdigest()})
        except Exception as exc:
            errors.append({'stage': 'text', 'event_id': item['accession'], 'error': str(exc)})
            print('Excluded:', item['ticker'], item['accession'], str(exc), flush=True)
        # Durable checkpoints allow retries to reuse completed extractions.
        if tones:
            atomic_csv(pd.DataFrame(tones), root / 'data/tone_panel.csv')
            atomic_csv(pd.DataFrame(audit), root / 'data/extraction_audit.csv')
        (root / 'outputs/run_progress.json').write_text(json.dumps({'stage':'text','ticker':item['ticker'],'processed':len(tones)+len(errors),'successful_texts':len(tones),'errors':len(errors),'target':len(manifest)}),encoding='utf-8')
    manifest = manifest[manifest.fiscal_year.between(*cfg['years'])].copy()
    pd.DataFrame(audit).to_csv(root / 'data/extraction_audit.csv', index=False)
    manifest.to_csv(root / 'data/filings_manifest.csv', index=False)
    pd.DataFrame(tones).to_csv(root / 'data/tone_panel.csv', index=False)
    pd.DataFrame(generic_noise.most_common(100), columns=['generic_negative_not_lm_negative', 'occurrences']).to_csv(root / 'data/generic_comparison.csv', index=False)
    if not tones:
        pd.DataFrame(errors).to_csv(root / 'data/exclusions.csv', index=False)
        raise ValueError('All text extractions failed; see exclusions.csv')
    start = (pd.to_datetime(manifest.filing_date).min() - pd.Timedelta(days=300)).date().isoformat()
    end = (pd.to_datetime(manifest.filing_date).max() + pd.Timedelta(days=35)).date().isoformat()
    cal = xcals.get_calendar('XNYS', start=start, end=end)
    sessions = cal.sessions.tz_localize(None)
    market_close = prices(root, cfg['benchmark'], start, end).reindex(sessions)
    market = market_close.pct_change(fill_method=None)
    stocks = {}
    for ticker in cfg['firms']:
        print('Market:', ticker, flush=True)
        stocks[ticker] = prices(root, ticker, start, end).reindex(sessions).pct_change(fill_method=None)
    rows, all_ar = [], []
    for item in tones:
        for rule in ['same', 'next', 'acceptance']:
            try:
                pos = event_position(sessions, item['filing_date'], item['acceptance'], rule)
                if rule == 'acceptance' and item['acceptance']:
                    stamp = pd.Timestamp(item['acceptance'])
                    stamp = stamp.tz_localize('America/New_York') if stamp.tzinfo is None else stamp.tz_convert('America/New_York')
                    day = stamp.tz_localize(None).normalize()
                    ix = int(sessions.searchsorted(day))
                    if ix < len(sessions) and sessions[ix] == day:
                        close = cal.session_close(cal.sessions[ix])
                        pos = ix + int(stamp.tz_convert('UTC') >= close)
                stats, ar = study(stocks[item['ticker']], market, sessions, pos, cfg['estimation'], cfg['min_estimation'], cfg['windows'])
                event_id = item['accession'] + '_' + rule
                rows.append(item | stats | {'alignment_rule': rule, 'event_id': event_id})
                ar['event_id'] = event_id; ar['alignment_rule'] = rule; all_ar.append(ar)
            except Exception as exc:
                errors.append({'stage': 'event_' + rule, 'event_id': item['accession'], 'error': str(exc)})
    pd.DataFrame(errors, columns=['stage', 'event_id', 'error']).to_csv(root / 'data/exclusions.csv', index=False)
    if not rows:
        raise ValueError('All market events failed; see exclusions.csv')
    panel = pd.DataFrame(rows); ars = pd.concat(all_ar)
    for rule in ['same', 'next', 'acceptance']:
        subset = panel[panel.alignment_rule == rule]
        if not subset.empty:
            output_results(subset, ars[ars.alignment_rule == rule], root / 'outputs/real' / rule, 'SEC 10-K: tone and market reaction - exploratory study')
    (root / 'outputs/real/run_metadata.json').write_text(json.dumps({'config': cfg, 'python': platform.python_version(),
         'timestamp': pd.Timestamp.now(tz='UTC').isoformat(), 'candidate_filings': len(manifest),
         'successful_texts': len(tones), 'exclusions': len(errors), 'parser_audit_completed': False,
         'warning': 'No causal interpretation; fiscal year from DEI when available, otherwise report date year requires review.'}, indent=2), encoding='utf-8')
    (root / 'outputs/run_progress.json').write_text(json.dumps({'stage':'complete','successful_texts':len(tones),'events':{r:int((panel.alignment_rule==r).sum()) for r in ['same','next','acceptance']},'errors':len(errors)}),encoding='utf-8')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--mode', choices=['demo', 'real'], default='demo')
    parser.add_argument('--config', default='config.json')
    parser.add_argument('--reuse-text', action='store_true', help='Reuse previously reviewed MD&A after raw/LM checksum and token-count integrity checks; omit after changing parser rules affecting existing sections.')
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    load_dotenv(root / '.env')
    (root / 'data').mkdir(exist_ok=True)
    cfg = json.loads((root / args.config).read_text(encoding='utf-8'))
    demo(root) if args.mode == 'demo' else real(root, cfg, reuse_text=args.reuse_text)
    print('Finished:', root / 'outputs' / args.mode)


if __name__ == '__main__':
    main()
