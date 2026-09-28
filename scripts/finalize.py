import json
from pathlib import Path
import pandas as pd
import re
import exchange_calendars as xcals
import statsmodels.formula.api as smf

root = Path(__file__).resolve().parents[1]
panel_path = root / 'outputs/real/same/car_panel.csv'
if panel_path.exists():
    panel = pd.read_csv(panel_path)
    reg = pd.read_csv(panel_path.parent / 'regressions.csv')
    baseline = reg[(reg.outcome == 'car_-1_1') & (reg.specification == 'tone')].iloc[0]
    metadata = json.loads((root / 'outputs/real/run_metadata.json').read_text())
    # Screen cached submissions for earnings-related 8-K Item 2.02 filings.
    earnings = []
    cik_to_ticker = {v: k for k, v in metadata['config']['firms'].items()}
    cik_to_ticker.update({v['cik']: k for k,v in metadata['config'].get('predecessor_ciks',{}).items()})
    for sidecar in (root / 'data/raw/sec').glob('*.json'):
        provenance = json.loads(sidecar.read_text())
        match = re.search(r'/submissions/CIK(\d{10})', provenance['url'])
        if not match or match[1] not in cik_to_ticker:
            continue
        payload = json.loads(sidecar.with_suffix('.raw').read_bytes())
        batch = payload.get('filings', {}).get('recent', payload)
        for i, form in enumerate(batch.get('form', [])):
            items = batch.get('items', [''] * len(batch['form']))[i]
            if form == '8-K' and '2.02' in items:
                earnings.append((cik_to_ticker[match[1]], batch['filingDate'][i], batch['accessionNumber'][i]))
    start = (pd.to_datetime(panel.filing_date).min() - pd.Timedelta(days=20)).date().isoformat()
    end = (pd.to_datetime(panel.filing_date).max() + pd.Timedelta(days=20)).date().isoformat()
    sessions = xcals.get_calendar('XNYS', start=start, end=end).sessions.tz_localize(None)
    flags = []
    for item in panel.itertuples():
        pos = int(sessions.searchsorted(pd.Timestamp(item.event_session)))
        nearby = set(sessions[max(0, pos - 1):pos + 2])
        hits = []
        for ticker, day, accession in earnings:
            if ticker == item.ticker:
                ix = int(sessions.searchsorted(pd.Timestamp(day)))
                if ix < len(sessions) and sessions[ix] in nearby:
                    hits.append(accession)
        flags.append({'event_id': item.event_id, 'flagged_8k_item202': bool(hits), 'related_accessions': ';'.join(sorted(set(hits)))})
    flag_frame = pd.DataFrame(flags)
    flag_frame.to_csv(root / 'data/earnings_8k_flags.csv', index=False)
    clean = panel.merge(flag_frame, on='event_id').query('flagged_8k_item202 == False')
    if len(clean) >= 12:
        fit = smf.ols('Q("car_-1_1") ~ tone', clean).fit(cov_type='HC3')
        pd.DataFrame([{'n': len(clean), 'tone_coefficient': fit.params['tone'], 'se_HC3': fit.bse['tone'], 'p_value': fit.pvalues['tone']}]).to_csv(panel_path.parent / 'excluding_8k202.csv', index=False)
    text = f'''# Kết quả sơ bộ dữ liệu thật

Mẫu mục tiêu {len(metadata['config']['firms']) * (metadata['config']['years'][1] - metadata['config']['years'][0] + 1)} filings; manifest có {metadata['candidate_filings']} filings. Tách được {metadata['successful_texts']} MD&A, còn {len(panel)} event trong baseline cùng phiên. Cần xem exclusions.csv cho lý do loại; số exclusion gồm cả các alignment đối chứng.

Baseline CAR [-1,+1] = intercept + b × tone, HC3: b = {baseline.coefficient:.6f}; SE = {baseline.se_HC3:.6f}; p = {baseline.p_value:.6f}; CI 95% [{baseline.ci_low:.6f}, {baseline.ci_high:.6f}]; R² = {baseline.r2:.6f}. Tăng tone 0.01 liên hệ CAR thay đổi {baseline.coefficient:.4f} điểm phần trăm. Đây là quan hệ ước lượng trong mẫu, không phải tác động nhân quả.

Kết quả chưa phải bản nộp cuối: audit parser và kiểm tra sự kiện earnings/8-K còn thiếu. Metadata đánh dấu parser_audit_completed=false. Xem regressions.csv của same, next, acceptance để đánh giá độ nhạy, CI và Holm p-value; không chọn alignment dựa vào hệ số đẹp hơn.
'''
    (root / 'docs/REAL_RESULTS.md').write_text(text, encoding='utf-8')
    display_cols = ['outcome', 'specification', 'coefficient', 'p_value', 'ci_low', 'ci_high', 'n']
    table = reg[reg.term == 'tone'][display_cols].copy()
    table_text = '| ' + ' | '.join(display_cols) + ' |\n|' + '|'.join(['---'] * len(display_cols)) + '|\n'
    for row in table.itertuples(index=False, name=None):
        table_text += '| ' + ' | '.join(str(round(v, 5)) if isinstance(v, float) else str(v) for v in row) + ' |\n'
    with (root / 'docs/REAL_RESULTS.md').open('a', encoding='utf-8') as stream:
        stream.write('\n## Các mô hình tone cùng phiên\n\n' + table_text)
        stream.write('\n## Đánh giá baseline\n\n')
        stream.write('Khoảng tin cậy chứa 0; mẫu này chưa cung cấp bằng chứng thống kê rõ về liên hệ tone với CAR [-1,+1]. Không diễn giải điều này thành việc tone không có giá trị thông tin.\n' if baseline.ci_low <= 0 <= baseline.ci_high else 'Khoảng tin cậy baseline loại 0. Cần xem hiệu chỉnh nhiều kiểm định, robustness và confounding trước khi kết luận có bằng chứng vững.\n')
        for rule in ['next', 'acceptance']:
            other_path = root / 'outputs/real' / rule / 'regressions.csv'
            if other_path.exists():
                other = pd.read_csv(other_path)
                selected = other[(other.outcome == 'car_-1_1') & (other.specification == 'tone')].iloc[0]
                stream.write(f'\nAlignment {rule}: b={selected.coefficient:.5f}, p={selected.p_value:.5f}, N={int(selected.n)}.\n')
        stream.write(f'\nScreening 8-K Item 2.02 trong cửa sổ cùng phiên [-1,+1]: {int(flag_frame.flagged_8k_item202.sum())} event được gắn cờ; còn {len(clean)} event khi loại chúng. Đây chỉ là screening theo metadata đã cache, không bao phủ mọi earnings release hoặc tin ngoài SEC. Xem data/earnings_8k_flags.csv và excluding_8k202.csv.\n')
else:
    (root / 'docs/REAL_RESULTS.md').write_text('# Trạng thái dữ liệu thật\nChưa tạo được kết quả thực nghiệm. Demo không phải bằng chứng thị trường. Xem log chạy để biết bước bị chặn.\n', encoding='utf-8')

print('Finished SEC 8-K screening; project remains available directly in its folder.')
