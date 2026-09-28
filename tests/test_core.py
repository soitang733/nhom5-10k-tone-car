import numpy as np
import pandas as pd
import pytest
from tonecar.text import extract_mda, load_lm, score, fiscal_year
from tonecar.event import event_position, study


def test_legacy_fiscal_year_cover_label():
    assert fiscal_year('<p>For the fiscal year ended June 30, 2016</p>', 2017) == (2016, 'cover_fiscal_year_ended')


def test_split_item_label_and_exhibit_end():
    raw = '<h2>I TEM 7. MANAGEMENT Discussion and Analysis</h2><p>' + 'Operating earnings growth. ' * 400 + '</p><h2>CONSOLIDATED STATEMENTS OF INCOME</h2><p>Audited figures not MD&amp;A</p>'
    section, audit = extract_mda(raw, issuer='WMT')
    assert audit['word_count'] > 1000
    assert 'Audited figures' not in section


def test_parser_skips_toc():
    raw = '<p>Item 7. Management Discussion</p><p>Item 7A. Quantitative Market risk</p>'
    raw += '<h2>Item 7. Management Discussion and Analysis</h2><p>' + 'Revenue growth uncertain. ' * 400 + '</p><h2>Item 8. Financial Statements</h2>'
    section, audit = extract_mda(raw)
    assert audit['word_count'] > 1000
    assert 'Revenue' in section


def test_fiscal_year_differs_from_report_year():
    raw = '<ix:nonNumeric name="dei:DocumentFiscalYearFocus">2020</ix:nonNumeric>'
    assert fiscal_year(raw, 2021) == (2020, 'dei:DocumentFiscalYearFocus')


def test_parser_does_not_end_at_prose_reference():
    raw = '<h2>Item 7. Management Discussion</h2><p>See Item 8 of this report. ' + 'Operating results stable. ' * 400 + '</p><h2>Item 7A. Quantitative risk</h2>'
    section, audit = extract_mda(raw)
    assert audit['word_count'] > 1000
    assert 'Operating results' in section


def test_parser_requires_block_heading_not_reference_title():
    raw = '<p>See Item 7. Management Discussion elsewhere.</p><p>' + 'Wrong section words. ' * 500 + '</p>'
    raw += '<h2>Item <span>7.</span> Management Discussion</h2><p>See Item 7A. Quantitative risk for details. ' + 'Right section earnings. ' * 400 + '</p><h2>Item 7A. Quantitative risk</h2>'
    section, audit = extract_mda(raw)
    assert 'Wrong section words' not in section
    assert section.count('Right section earnings') == 400


def test_embedded_annual_report_is_not_whole_filing():
    raw = '<h2>Item 7. Management Discussion</h2><p>Incorporated by reference</p><h2>Item 7A. Quantitative risk</h2>'
    raw += '<h2>Management’s discussion and analysis</h2><p>The following is Management discussion. ' + 'Earnings grew steadily. ' * 400 + '</p><h2>Five-Year Stock Performance</h2><p>Not MD&A.</p>'
    section, audit = extract_mda(raw, issuer='JPM')
    assert audit['extraction_method'] == 'embedded_annual_report_JPM'
    assert 'Not MD&A' not in section


def test_parser_fails_instead_of_full_document():
    with pytest.raises(ValueError, match='manual review'):
        extract_mda('<p>No recognizable section</p>')


def test_removed_category_and_counts(tmp_path):
    path = tmp_path / 'lm.csv'
    path.write_text('Word,Positive,Negative,Uncertainty\nGAIN,2011,0,0\nLOSS,0,2011,0\nOLD,0,-2020,0\nMAY,0,0,2011\n')
    lexicon = load_lm(path)
    result = score('GAIN gain LOSS old MAY', lexicon)
    assert result['positive_count'] == 2
    assert result['negative_count'] == 1
    assert result['tone'] == pytest.approx(.2)


def test_alignment_weekend_and_after_close():
    sessions = pd.bdate_range('2024-01-01', periods=10)
    assert sessions[event_position(sessions, '2024-01-06')] == pd.Timestamp('2024-01-08')
    assert sessions[event_position(sessions, '2024-01-05', '2024-01-05T22:00:00Z', 'acceptance')] == pd.Timestamp('2024-01-08')
    assert sessions[event_position(sessions, '2024-01-05', rule='next')] == pd.Timestamp('2024-01-08')


def test_known_market_model_and_car():
    idx = pd.bdate_range('2020-01-01', periods=250)
    market = pd.Series(np.random.default_rng(1).normal(0, .01, 250), index=idx)
    stock = .001 + 1.5 * market
    stock.iloc[149:152] += .01
    result, _ = study(stock, market, idx, 150)
    assert result['alpha'] == pytest.approx(.001)
    assert result['beta'] == pytest.approx(1.5)
    assert result['car_-1_1'] == pytest.approx(.03)


def test_missing_event_price_excluded_not_shifted():
    idx = pd.bdate_range('2020-01-01', periods=250)
    market = pd.Series(np.random.default_rng(1).normal(0, .01, 250), index=idx)
    stock = market.copy(); stock.iloc[150] = np.nan
    with pytest.raises(ValueError, match='Missing event'):
        study(stock, market, idx, 150)
