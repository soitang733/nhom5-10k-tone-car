"""Predefined sensitivity analyses; never overwrite baseline or select by p-value."""
from pathlib import Path
import sys,re,json,hashlib,os
import numpy as np
import pandas as pd
from bs4 import UnicodeDammit
from lxml import html,etree
import statsmodels.formula.api as smf
from statsmodels.stats.multitest import multipletests
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R))
from tonecar.text import extract_mda,tokenize,score,load_lm
OUT=R/'outputs/limitations';OUT.mkdir(exist_ok=True)
DEST=R/'data/interim/mda_numeric_tables_removed';DEST.mkdir(exist_ok=True)
lex=load_lm(R/'data/external/lm.csv')
panel=pd.read_csv(R/'data/tone_panel.csv');audit=pd.read_csv(R/'data/extraction_audit.csv').set_index('accession')
shard=int(os.environ.get('TONECAR_SENSITIVITY_SHARD','-1'))
shards=int(os.environ.get('TONECAR_SENSITIVITY_SHARDS','3'))
aggregate=os.environ.get('TONECAR_SENSITIVITY_AGGREGATE')=='1'
if shard>=0:
    assert shard<shards
    panel=panel.iloc[shard::shards]
records=[];tables=[]
from tonecar.sensitivity import numeric_table,excess_buy_hold
for i,row in enumerate(() if aggregate else panel.itertuples()):
    a=audit.loc[row.accession];url=a.mda_source_url if pd.notna(a.mda_source_url) else row.source_url
    rawpath=R/'data/raw/sec'/(hashlib.sha256(url.encode()).hexdigest()+'.raw')
    raw=UnicodeDammit(rawpath.read_bytes(),is_html=True).unicode_markup
    if row.ticker=='WMT' and row.fiscal_year in {2016,2017}:
        raw=re.sub(r'Item(\s|&nbsp;|&#160;)*2','Item 7',raw,flags=re.I)
        raw=re.sub(r'Item(\s|&nbsp;|&#160;)*3','Item 8',raw,flags=re.I)
    root=html.fromstring(re.sub(r'^\s*<\?xml[^>]*\?>','',raw))
    selected=[n for n in root.xpath('//table') if numeric_table(n)]
    for n in selected:
        n.text=' ZZTABLEBEGINZZ '+(n.text or '')
        if len(n):n[-1].tail=(n[-1].tail or '')+' ZZTABLEENDZZ '
        else:n.text+=' ZZTABLEENDZZ '
    status='applied'
    try:
        marked,diag=extract_mda(etree.tostring(root,encoding='unicode'),issuer=row.ticker)
    except ValueError:
        # Annotation may disrupt headings in unusual layout tables. Retain the
        # original section instead of accepting a different section boundary.
        marked,diag=extract_mda(raw,issuer=row.ticker)
        status='retained_original_annotation_boundary_guard'
    unmarked=marked.replace('ZZTABLEBEGINZZ','').replace('ZZTABLEENDZZ','')
    baseline=(R/'data/interim/mda'/(row.accession+'.txt')).read_text(encoding='utf-8')
    assert tokenize(unmarked)==tokenize(baseline),(row.accession,'annotation altered extraction boundary')
    segments=re.findall(r'ZZTABLEBEGINZZ(.*?)ZZTABLEENDZZ',marked,re.S)
    cleaned=re.sub(r'ZZTABLEBEGINZZ.*?ZZTABLEENDZZ','\n',marked,flags=re.S)
    values=score(cleaned,lex)
    assert values['word_count']<=row.word_count and values['word_count']>0
    (DEST/(row.accession+'.txt')).write_text(cleaned,encoding='utf-8')
    records.append({'accession':row.accession,'ticker':row.ticker,'fiscal_year':row.fiscal_year,
        **{'clean_'+k:v for k,v in values.items()},'numeric_tables_removed':len(segments),
        'words_removed':row.word_count-values['word_count'],'source_url':url,
        'source_sha256':hashlib.sha256(rawpath.read_bytes()).hexdigest(),
        'same_boundary_tokens_verified':True,'table_processing_status':status})
    for j,segment in enumerate(segments):
        tables.append({'accession':row.accession,'ticker':row.ticker,'fiscal_year':row.fiscal_year,
            'table_number':j+1,'removed_words':len(tokenize(segment)),'excerpt':re.sub(r'\s+',' ',segment)[:900]})
    if (i+1)%50==0:print('Table sensitivity',i+1,flush=True)
if shard>=0:
    pd.DataFrame(records).to_csv(OUT/f'text_sensitivity_panel_shard_{shard}.csv',index=False)
    pd.DataFrame(tables).to_csv(OUT/f'removed_table_review_shard_{shard}.csv',index=False)
    print('Finished shard',shard,len(records),flush=True)
    sys.exit(0)
if aggregate:
    clean=pd.concat([pd.read_csv(OUT/f'text_sensitivity_panel_shard_{i}.csv') for i in range(shards)],ignore_index=True)
    tables=pd.concat([pd.read_csv(OUT/f'removed_table_review_shard_{i}.csv') for i in range(shards)],ignore_index=True)
    panel=pd.read_csv(R/'data/tone_panel.csv')
    assert len(clean)==len(panel)==1000 and clean.accession.is_unique
else:
    clean=pd.DataFrame(records)
    tables=pd.DataFrame(tables)
clean.to_csv(OUT/'text_sensitivity_panel.csv',index=False)
tables.to_csv(OUT/'removed_table_review.csv',index=False)
results=[]
for rule in ['same','next','acceptance']:
    p=pd.read_csv(R/'outputs/real'/rule/'car_panel.csv').merge(clean,on=['accession','ticker','fiscal_year'],validate='one_to_one',suffixes=('','_clean'))
    ar=pd.read_csv(R/'outputs/real'/rule/'event_ar.csv')
    days=ar[ar.relative_day.between(0,3)]
    bh=days.groupby('event_id').apply(lambda d:excess_buy_hold(d.stock,d.market),include_groups=False)
    assert days.groupby('event_id').size().eq(4).all()
    p['bhar_0_3']=p.event_id.map(bh)
    p['negativity']=p.negative_rate;p['clean_negativity']=p.clean_negative_rate
    p=p.sort_values(['ticker','fiscal_year']);g=p.groupby('ticker')
    p['clean_delta_tone']=p.clean_tone-g.clean_tone.shift()
    p.loc[p.fiscal_year-g.fiscal_year.shift()!=1,'clean_delta_tone']=np.nan
    specs=[('baseline_tone','car_-1_1','tone'),('numeric_tables_removed_tone','car_-1_1','clean_tone'),
        ('numeric_tables_removed_delta','car_-1_1','clean_delta_tone'),
        ('negativity_car','car_-1_1','negativity'),('negativity_bhar','bhar_0_3','negativity'),
        ('clean_negativity_bhar','bhar_0_3','clean_negativity')]
    for name,y,x in specs:
        frame=p.dropna(subset=[y,x]);fit=smf.ols(f'Q("{y}") ~ {x}',frame).fit(cov_type='cluster',cov_kwds={'groups':frame.ticker,'use_correction':True},use_t=True)
        ci=fit.conf_int().loc[x]
        results.append({'alignment':rule,'specification':name,'outcome':y,'term':x,'coefficient':fit.params[x],
            'se_cluster':fit.bse[x],'p_cluster':fit.pvalues[x],'ci_low':ci.iloc[0],'ci_high':ci.iloc[1],
            'N':int(fit.nobs),'clusters':frame.ticker.nunique()})
    p.to_csv(OUT/(rule+'_sensitivity_panel.csv'),index=False)
results=pd.DataFrame(results)
# One family across all 18 reported sensitivity tests, including baseline comparisons.
results['p_holm']=multipletests(results.p_cluster,method='holm')[1]
results.to_csv(OUT/'sensitivity_models.csv',index=False)
summary={'reports':len(clean),'reports_with_tables_removed':int((clean.numeric_tables_removed>0).sum()),
    'numeric_tables_removed':int(clean.numeric_tables_removed.sum()),'words_removed':int(clean.words_removed.sum()),
    'median_removed_fraction':float((clean.words_removed/panel.set_index('accession').loc[clean.accession].word_count.to_numpy()).median()),
    'same_boundary_tokens_verified':len(clean),'models':len(results),'holm_family':len(results),
    'baseline_unchanged':True,'raw_unchanged':True,'table_rule_version':'leaf-numeric-v1-20260928'}
(OUT/'checks.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
print(json.dumps(summary,indent=2));print(results.to_string(index=False))
