"""Make a clean, output-free notebook for the actual 100-company study."""
from pathlib import Path
import nbformat as nbf

root = Path(__file__).resolve().parents[1]
nb = nbf.v4.new_notebook()
nb.metadata['kernelspec'] = {'display_name':'Python 3','language':'python','name':'python3'}
nb.cells = [
    nbf.v4.new_markdown_cell('# Nhóm 5 · 100 công ty · 10-K MD&A → Tone → CAR\n\nNotebook tái kiểm dữ liệu thật FY2016–2025 đã lưu trong dự án. Không dùng dữ liệu mô phỏng. Nguồn và hạn chế ở `docs/REPORT.md`.'),
    nbf.v4.new_code_cell("from pathlib import Path\nimport sys\nroot=Path.cwd()\nif root.name=='notebooks': root=root.parent\nif str(root) not in sys.path:sys.path.insert(0,str(root))\nimport numpy as np,pandas as pd\nfrom IPython.display import display\nfrom tonecar.text import load_lm,score\nimport statsmodels.formula.api as smf\nfrom statsmodels.stats.multitest import multipletests\nprint(root)"),
    nbf.v4.new_markdown_cell('## 1. Đối chiếu danh sách và SEC manifest\n\nDanh sách gốc là 100 ticker/CIK người dùng đưa. Mỗi ticker–FY chỉ có một accession; URL có thể mở trực tiếp tại SEC.'),
    nbf.v4.new_code_cell("source=pd.read_csv(root/'data/companies_100_input.csv')\nmanifest=pd.read_csv(root/'data/filings_manifest.csv')\npanel=pd.read_csv(root/'outputs/real/same/car_panel.csv')\nassert len(source)==100 and len(manifest)==1000 and len(panel)==1000\nassert panel.ticker.nunique()==100\nassert panel.accession.is_unique and not panel.duplicated(['ticker','fiscal_year']).any()\nassert set(panel.accession)==set(manifest.accession)\ndisplay(manifest[['ticker','fiscal_year','accession','report_date','filing_date','source_url']].head())"),
    nbf.v4.new_markdown_cell('## 2. Tái tính tone từ MD&A đã trích\n\nTone=(Positive−Negative)/TotalWords. Chạy cell này sẽ đọc 1.000 văn bản MD&A và từ điển LM, không cần mạng.'),
    nbf.v4.new_code_cell("lexicon=load_lm(root/'data/external/lm.csv')\nfor row in panel.itertuples():\n    text=(root/'data/interim/mda'/(row.accession+'.txt')).read_text(encoding='utf-8')\n    result=score(text,lexicon)\n    assert result['word_count']==row.word_count\n    assert np.isclose(result['tone'],row.tone,atol=1e-12)\nprint('Đúng',len(panel),'điểm tone');display(panel[['ticker','fiscal_year','positive_rate','negative_rate','uncertainty_rate','tone']].head(15))"),
    nbf.v4.new_markdown_cell('## 3. Tái tính CAR từ AR từng phiên\n\nPhiên t=0 căn ngày nộp SEC; mô hình thị trường được ước lượng ở [-120,-20]. Kiểm tra tổng AR bằng ba cửa sổ.'),
    nbf.v4.new_code_cell("ar=pd.read_csv(root/'outputs/real/same/event_ar.csv')\nfor lo,hi in [(-1,1),(-3,3),(-5,5)]:\n    sums=ar[ar.relative_day.between(lo,hi)].groupby('event_id').abnormal_return.sum()\n    assert np.allclose(panel.event_id.map(sums),panel[f'car_{lo}_{hi}'])\nprint('CAR khớp cả ba cửa sổ cho',len(panel),'event')"),
    nbf.v4.new_markdown_cell('## 4. Hồi quy chính và ba cách căn ngày'),
    nbf.v4.new_code_cell("fit=smf.ols('Q(\"car_-1_1\") ~ tone',panel).fit(cov_type='HC3')\nreported=pd.read_csv(root/'outputs/real/same/regressions.csv')\nbase=reported[(reported.outcome=='car_-1_1')&(reported.specification=='tone')].iloc[0]\nassert np.isclose(fit.params['tone'],base.coefficient) and np.isclose(fit.pvalues['tone'],base.p_value)\ndisplay(pd.DataFrame({'coefficient':fit.params,'HC3_SE':fit.bse,'p':fit.pvalues}))\nfor rule in ['same','next','acceptance']:\n    frame=pd.read_csv(root/'outputs/real'/rule/'regressions.csv')\n    display(frame[(frame.outcome=='car_-1_1')&(frame.specification=='tone')][['coefficient','p_value','ci_low','ci_high','n']].assign(alignment=rule))"),
    nbf.v4.new_markdown_cell('## 5. Kiểm định độ nhạy và kiểm toán\n\nHolm điều chỉnh toàn bộ 18 kiểm định định trước. Kiểm toán ranh giới là hỗ trợ AI và kiểm tra cấu trúc, chưa có nhãn toàn văn của con người.'),
    nbf.v4.new_code_cell("models=pd.read_csv(root/'outputs/limitations/sensitivity_models.csv')\nassert len(models)==18 and np.allclose(multipletests(models.p_cluster,method='holm')[1],models.p_holm)\nassert pd.read_csv(root/'data/exclusions.csv').empty\nassert pd.read_csv(root/'data/extraction_audit.csv').accession.nunique()==1000\ndisplay(models[['alignment','specification','coefficient','p_cluster','p_holm','N']])\ndisplay(pd.read_csv(root/'outputs/real/same/cluster_se.csv'))"),
    nbf.v4.new_markdown_cell('## Diễn giải\n\nXem cả hệ số, CI, mẫu và độ nhạy; không chọn kết quả chỉ vì p-value nhỏ. Mẫu 100 công ty có chủ đích và dữ liệu giá công khai không chứng minh quan hệ nhân quả hoặc chiến lược giao dịch. Xem `docs/REPORT.md` và `docs/LIMITATIONS_REMEDIATION.md`.'),
]
(root/'notebooks').mkdir(exist_ok=True)
nbf.write(nb,root/'notebooks/final_analysis.ipynb')
print('Notebook ready:',len(nb.cells),'cells')
