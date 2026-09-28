import numpy as np
import pandas as pd
from tonecar.pipeline import add_tone_changes
from scripts.enrich_fundamentals import choose_fact

def test_changes_do_not_bridge_missing_year_or_cross_company():
    data=pd.DataFrame({'ticker':['A','A','A','B','B'],'fiscal_year':[2016,2017,2019,2016,2017],'tone':[.1,.2,.5,-.1,.2]})
    result=add_tone_changes(data)
    assert result.query("ticker=='A' and fiscal_year==2017").delta_tone.iloc[0]==.1
    assert np.isnan(result.query("ticker=='A' and fiscal_year==2019").delta_tone.iloc[0])
    assert result.query("ticker=='B' and fiscal_year==2017").delta_tone.iloc[0] == np.float64(.2)-np.float64(-.1)
    assert result.query('fiscal_year==2016').delta_tone.isna().all()

def test_changes_keep_alignments_separate():
    data=pd.DataFrame({'ticker':['A']*4,'alignment_rule':['same','next','same','next'],'fiscal_year':[2016,2016,2017,2017],'tone':[.1,.1,.2,.2]})
    result=add_tone_changes(data)
    assert result.query('fiscal_year==2017').delta_tone.eq(.1).all()

def test_facts_use_exact_filing_and_annual_duration():
    entries=[{'accn':'old','end':'2025-12-31','form':'10-K','start':'2025-01-01','val':10},
             {'accn':'new','end':'2025-12-31','form':'10-K','start':'2025-01-01','val':999},
             {'accn':'old','end':'2025-12-31','form':'10-K','start':'2025-10-01','val':4}]
    facts={'NetIncomeLoss':{'units':{'USD':entries}}}
    assert choose_fact(facts,['NetIncomeLoss'],'old','2025-12-31',True)[0]==10

def test_conflicting_facts_remain_missing():
    entries=[{'accn':'a','end':'2025-12-31','form':'10-K','val':10},{'accn':'a','end':'2025-12-31','form':'10-K','val':11}]
    assert np.isnan(choose_fact({'Assets':{'units':{'USD':entries}}},['Assets'],'a','2025-12-31')[0])

def test_legacy_split_item_and_bom_preserve_mda_boundaries():
    from tonecar.text import extract_mda
    raw='<p>It em 7. \ufeff Management’s Discussion and Analysis</p><p>'+('Revenue risk improves. '*300)+'</p><p>It em 7A. Quantitative and Qualitative Disclosures</p><p>EXCLUDED_MARKET_SECTION</p>'
    text,audit=extract_mda(raw)
    assert 'Revenue risk improves' in text
    assert 'EXCLUDED_MARKET_SECTION' not in text
    assert audit['word_count']>800

def test_comment_tail_is_retained_in_text_scoring():
    from tonecar.text import extract_mda,tokenize
    raw='<p>Item 7. Management Discussion</p><p>'+('revenue <!-- layout -->risk '*450)+'</p><p>Item 8. Financial Statements</p>'
    text,_=extract_mda(raw)
    assert tokenize(text).count('RISK')==450

def test_apostrophe_encodings_produce_identical_tokens_and_scores():
    from tonecar.text import tokenize,score
    examples=["We're discussing management's risk and growth.","We’re discussing management’s risk and growth.","We\x92re discussing management\x92s risk and growth."]
    lex={'positive':{'GROWTH'},'negative':{'RISK'},'uncertainty':set()}
    assert all(tokenize(x)==tokenize(examples[0]) for x in examples)
    assert all(score(x,lex)==score(examples[0],lex) for x in examples)
