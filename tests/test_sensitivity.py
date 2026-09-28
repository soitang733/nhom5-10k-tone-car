import numpy as np
from lxml import html
from tonecar.sensitivity import numeric_table,excess_buy_hold
from tonecar.text import extract_mda
import pytest

def table(label='Revenue'):
    return html.fromstring(f'<table><tr><td>{label}</td><td>2025</td><td>2024</td></tr><tr><td>Income</td><td>100</td><td>90</td></tr></table>')

def test_numeric_table_and_heading_protection():
    assert numeric_table(table())
    assert not numeric_table(table('ITEM 7 MANAGEMENT DISCUSSION'))

def test_layout_and_prose_safeguards():
    node=html.fromstring('<table><tr><td>Discussion of business risks</td><td>'+html.tostring(table(),encoding='unicode')+'</td></tr></table>')
    assert not numeric_table(node)
    assert not numeric_table(table(' '.join(['explanation']*61)))

def test_buy_hold_compounds_each_series_separately():
    value=excess_buy_hold([.1,-.1],[.02,.03])
    assert np.isclose(value,.99-1.0506)
    assert not np.isclose(value,sum([.1-.02,-.1-.03]))

def test_chevron_substantive_heading_and_income_discussion_retained():
    title="Management's Discussion and Analysis of Financial Condition and Results of Operations"
    raw=f'<p>{title}</p><p>24 7A. Quantitative disclosures 8. Financial statements</p><p>Business description</p><p>{title}</p><p>Key Financial Results</p><p>'+('Operating earnings increased. '*300)+'</p><p>Consolidated Statement of Income</p><p>'+('Continued business discussion. '*300)+"</p><p>Management's Responsibility for Financial Statements</p>"
    section,_=extract_mda(raw,issuer='CVX')
    assert 'Continued business discussion' in section
    assert 'Business description' not in section
    assert 'Responsibility for Financial Statements' not in section

def test_ibm_cross_reference_cannot_pass_word_count_threshold():
    raw='<p>management discussion overview—pages 27 to 30.</p><p>'+('Executive officers unrelated chapter. '*400)+'</p><p>Report of Independent Auditors</p>'
    with pytest.raises(ValueError,match='Cross-reference'):
        extract_mda(raw,issuer='IBM')
