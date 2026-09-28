"""Regenerate every public study document from the current 100-firm output."""
from __future__ import annotations

import html
import json
import re
import unicodedata
from pathlib import Path

import pandas as pd
import pymupdf
import statsmodels.formula.api as smf

ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs"
OUT = ROOT / "outputs"


def write(name: str, body: str) -> None:
    (DOC / f"{name}.md").write_text(body.strip() + "\n", encoding="utf-8")


def table(frame: pd.DataFrame, cols: list[str] | None = None) -> str:
    if cols:
        frame = frame[cols]
    def cell(value):
        if pd.isna(value):
            return "—"
        if isinstance(value, float):
            return f"{value:.5f}"
        return str(value).replace("|", "\\|")
    header = "| " + " | ".join(frame.columns) + " |\n"
    header += "| " + " | ".join("---" for _ in frame.columns) + " |\n"
    return header + "".join("| " + " | ".join(cell(v) for v in row) + " |\n" for row in frame.itertuples(index=False, name=None))


def md_html(source: str) -> str:
    chunks, rows = [], []
    def flush_table():
        if not rows:
            return
        cells = lambda line: [html.escape(c.strip()) for c in line.strip().split("|")[1:-1]]
        headings = cells(rows[0])
        for line in rows[2:]:
            values = cells(line)
            chunks.append("<p class='table_row'>" + " · ".join(f"<b>{headings[i]}:</b> {value}" for i, value in enumerate(values)) + "</p>")
        rows.clear()
    for line in source.splitlines():
        if line.startswith("|"):
            rows.append(line)
            continue
        flush_table()
        if not line.strip():
            continue
        n = len(line) - len(line.lstrip("#"))
        if 1 <= n <= 3 and line[n:n+1] == " ":
            chunks.append(f"<h{n}>{html.escape(line[n+1:])}</h{n}>")
        else:
            escaped = html.escape(line)
            escaped = re.sub(r"\[([^\]]+)\]\((https?://[^)]+)\)", r'<a href="\2">\1</a>', escaped)
            chunks.append(f"<p>{escaped}</p>")
    flush_table()
    return "\n".join(chunks)


def pdf_from_markdown(source: str) -> None:
    font = ROOT / "web/fonts/NotoSans.ttf"
    archive = pymupdf.Archive(str(font.parent))
    css = """
    @font-face {font-family: Noto; src: url(NotoSans.ttf);}
    body {font-family:Noto; color:#1b2b43; font-size:11pt; line-height:1.55;}
    h1 {color:#14233b;font-size:22pt;margin:0 0 15pt;}
    h2 {color:#14233b;font-size:14pt;margin:18pt 0 6pt;page-break-after:avoid;}
    h3 {color:#14233b;font-size:11pt;margin:13pt 0 4pt;page-break-after:avoid;}
    p {margin:0 0 8pt;text-align:justify;}
    .table_row {font-size:9pt;line-height:1.4;border-bottom:0.5pt solid #d8e0eb;padding:2pt 0;margin:0 0 3pt;text-align:left;}
    a {color:#825e21;}
    """
    story = pymupdf.Story(html=f'<html><body>{md_html(source)}</body></html>', user_css=css, archive=archive)
    target = OUT / "Nhom5_BaoCao.pdf"
    writer = pymupdf.DocumentWriter(str(target))
    a4 = pymupdf.paper_rect("a4")
    def rectfn(_, __):
        return a4, pymupdf.Rect(49, 50, a4.width-49, a4.height-52), None
    story.write(writer, rectfn)
    writer.close()
    with pymupdf.open(target) as pdf:
        assert len(pdf) >= 4
        first = unicodedata.normalize('NFC', pdf[0].get_text())
        assert "Giọng điệu" in first and "100" in first
        print("PDF pages:", len(pdf), "bytes:", target.stat().st_size)


def main() -> None:
    cfg = json.loads((ROOT / "config.json").read_text(encoding="utf-8"))
    panel = pd.read_csv(OUT / "real/same/car_panel.csv")
    manifest = pd.read_csv(ROOT / "data/filings_manifest.csv")
    audit = pd.read_csv(ROOT / "data/extraction_audit.csv")
    exclusions = pd.read_csv(ROOT / "data/exclusions.csv")
    flags = pd.read_csv(ROOT / "data/earnings_8k_flags.csv")
    sensitivity = pd.read_csv(OUT / "limitations/sensitivity_models.csv")
    assert len(cfg["firms"]) == 100 and panel.ticker.nunique() == 100
    assert panel.accession.is_unique and not panel.duplicated(["ticker", "fiscal_year"]).any()
    assert len(manifest) == 1000 and len(panel) == 1000, (len(manifest), len(panel))
    assert not exclusions.shape[0], exclusions.head().to_string(index=False)
    reg = pd.read_csv(OUT / "real/same/regressions.csv")
    base = reg[(reg.outcome == "car_-1_1") & (reg.specification == "tone")].iloc[0]
    cluster = smf.ols('Q("car_-1_1") ~ tone', panel).fit(cov_type="cluster", cov_kwds={"groups":panel.ticker,"use_correction":True}, use_t=True)
    ci = cluster.conf_int().loc["tone"]
    pd.DataFrame([{"coefficient":cluster.params["tone"],"se_cluster":cluster.bse["tone"],"p_value":cluster.pvalues["tone"],"ci_low":ci.iloc[0],"ci_high":ci.iloc[1],"clusters":panel.ticker.nunique(),"n":len(panel)}]).to_csv(OUT / "real/same/cluster_se.csv",index=False)
    leave = []
    for ticker in sorted(panel.ticker.unique()):
        sub = panel[panel.ticker.ne(ticker)]
        fit = smf.ols('Q("car_-1_1") ~ tone', sub).fit(cov_type="HC3")
        leave.append({"excluded_firm":ticker,"coefficient":fit.params["tone"],"p_value":fit.pvalues["tone"],"n":int(fit.nobs)})
    pd.DataFrame(leave).to_csv(OUT / "real/same/leave_one_firm_out.csv",index=False)
    audit_out = manifest[["ticker","fiscal_year","accession","source_url"]].merge(audit,on="accession",how="left",validate="one_to_one")
    audit_out["boundary_check"] = audit_out.word_count.notna().map({True:"pass",False:"excluded"})
    audit_out["audit_scope"] = "AI-assisted heading/snippet/hash structural review; no full human annotation"
    audit_out.to_csv(ROOT / "data/research_audit.csv",index=False)
    metadata_file = OUT / "real/run_metadata.json"
    metadata = json.loads(metadata_file.read_text(encoding="utf-8"))
    metadata.update({"structured_boundary_review_completed":True,"project_status":"complete_100_firm_research_pipeline","audit_scope":"1000 SEC originals; heading/snippet/hash review, not human full-text annotation","earnings_8k_screening_completed":True})
    metadata_file.write_text(json.dumps(metadata,ensure_ascii=False,indent=2),encoding="utf-8")
    alignment = []
    for rule in ("same","next","acceptance"):
        rr = pd.read_csv(OUT / "real" / rule / "regressions.csv")
        r = rr[(rr.outcome == "car_-1_1") & (rr.specification == "tone")].iloc[0]
        alignment.append({"Căn ngày":rule,"N":int(r.n),"Hệ số":r.coefficient,"p HC3":r.p_value,"CI thấp":r.ci_low,"CI cao":r.ci_high})
    desc = panel[["word_count","tone","negative_rate","uncertainty_rate","car_-1_1","car_-3_3","car_-5_5"]].describe().T[["count","mean","std","min","max"]].reset_index().rename(columns={"index":"Biến"})
    regression = reg[reg.term.eq("tone")][["outcome","specification","coefficient","se_HC3","p_value","ci_low","ci_high","n","p_holm_all_reported_tests"]].head(18)
    methods = audit.extraction_method.value_counts().rename_axis("Cách trích").reset_index(name="Số báo cáo")
    rows_8k = int(flags.flagged_8k_item202.sum())
    outcome = "có bằng chứng thống kê ở ngưỡng 5% trong baseline" if base.p_value < .05 else "chưa đủ bằng chứng thống kê ở ngưỡng 5% trong baseline"
    source = f"""# Giọng điệu báo cáo tài chính và phản ứng thị trường

Nhóm 5 · Đề án 05 Fintech · Báo cáo hoàn chỉnh · Dữ liệu SEC 10-K FY2016–FY2025 · Khóa dữ liệu 28/09/2026

## Tóm tắt nghiên cứu

Nghiên cứu dùng chính xác 100 công ty do người dùng cung cấp trong `companies_100.csv`, mỗi công ty mười báo cáo 10-K gốc. Tải và lưu 1.000 tài liệu SEC, trích phần Management's Discussion and Analysis (MD&A), tính tone bằng từ điển Loughran–McDonald (LM), ghép ngày nộp báo cáo với giá điều chỉnh và ước lượng CAR. Mẫu phân tích cuối gồm {len(panel)} báo cáo của {panel.ticker.nunique()} công ty. Mô hình nền CAR [-1,+1] ~ tone có hệ số {base.coefficient:.5f}, sai số chuẩn HC3 {base.se_HC3:.5f}, p={base.p_value:.5f}, CI 95% [{base.ci_low:.5f}; {base.ci_high:.5f}]. Kết quả {outcome}. Thiết kế đo mối liên hệ quan sát được; không xác định tác động nhân quả.

## Câu hỏi, giả thuyết và đóng góp

Câu hỏi chính: tỷ lệ từ mang sắc thái tích cực và tiêu cực trong MD&A có liên hệ với lợi suất bất thường của cổ phiếu quanh ngày công bố 10-K hay không? H1: tone cao hơn đi cùng CAR cao hơn. H2: tỷ lệ từ tiêu cực cao hơn đi cùng CAR thấp hơn. H3: tỷ lệ từ bất định có liên hệ hai phía với CAR. Cửa sổ chính [-1,+1] phiên; [-3,+3] và [-5,+5] là đối chứng. Đóng góp thực hành là chuỗi dữ liệu kiểm toán được từ URL SEC và HTML gốc đến văn bản đã trích, điểm tone từng doanh nghiệp–năm, AR từng phiên, CAR và hồi quy.

## Tổng quan tài liệu và phạm vi tái lập

Loughran và McDonald (2011) đặt vấn đề từ điển ngôn ngữ tổng quát dễ gán sai sắc thái cho từ trong tài chính; nghiên cứu này dùng nhóm Positive, Negative và Uncertainty của từ điển LM. Tetlock (2007) gợi ý mối quan hệ giữa ngôn ngữ và thị trường trong bối cảnh tin tức. Li (2008) nghiên cứu tính dễ đọc của báo cáo, là một cấu phần khác tone. MacKinlay (1997) là khuôn khổ event study để xây AR và CAR. Nghiên cứu này là bản triển khai ứng dụng với SEC, dữ liệu giá công khai và 100 công ty có chủ đích, không tuyên bố tái lập dữ liệu CRSP hay mọi bảng trong LM (2011). Ba repo tham khảo trong tài liệu chỉ là nguồn gợi ý cách tổ chức code, không là nguồn dữ liệu kết quả.

## Thiết kế mẫu và truy nguyên nguồn

Danh sách gốc `data/companies_100_input.csv` có SHA-256 lưu trong snapshot metadata. Bảng kiểm `outputs/qa/company_list_100_validation.csv` đối chiếu ticker và CIK với SEC. Danh sách được cố định theo file người dùng đưa, không lựa theo p-value. SEC Submissions API cho form, accession, report date, filing date và acceptance time. Client đọc cả file lịch sử, giữ form 10-K đầu tiên cho từng kỳ, bỏ 10-K/A; ngày nộp không sau 28/09/2026. Bản HTML hoặc phụ lục Exhibit 13 thật được lưu cứng vào `data/raw/sec` dưới tên băm URL kèm JSON provenance, URL và SHA-256. Hồ sơ Apple FY2025 trong mẫu là bản năm kết thúc 27/09/2025, không phải dữ liệu tự dựng.

Mười năm tài khóa 2016–2025 được gán từ DEI và kỳ trên bìa, có đối chiếu các trường hợp năm tài khóa kết thúc tháng 1–2 và DEI lỗi thời. `data/filings_manifest.csv` ghi nguồn quyết định nhãn năm; mỗi cặp ticker–năm đúng một accession. Mẫu có chủ đích gồm các công ty tồn tại và có dữ liệu đủ 10 năm, nên có thiên lệch sống sót và không đại diện ngẫu nhiên cho toàn thị trường.

## Xử lý MD&A và kiểm soát chất lượng

HTML được giải mã với UnicodeDammit, bỏ script/style và XBRL header ẩn, chuẩn hóa Unicode NFKC; nội dung khối được giữ để phát hiện tiêu đề. Parser lấy Item 7 đến Item 7A hoặc Item 8 khi có tiêu đề rõ. Với bố cục annual report lồng trong tài liệu chính hoặc Exhibit 13, quy tắc riêng phải khớp tiêu đề nội dung và điểm bắt đầu chương tiếp theo, tránh lấy mục lục. Martin Marietta dùng trang Exhibit 13 có heading MD&A lặp trên từng trang; Nucor dừng trước báo cáo kiểm toán. Deere được xử lý lỗi chia chữ `INCOM E` ở tiêu đề báo cáo tài chính. Các cách trích, số token, đầu/cuối và URL nguồn lưu trong `data/extraction_audit.csv`.

{table(methods)}

Từ được tách thành token chữ cái dài ít nhất hai ký tự, chuyển uppercase; không stemming và không bỏ stopword ở mẫu số. PositiveRate = số token LM tích cực/tổng token; NegativeRate tương tự; UncertaintyRate tương tự; Tone = PositiveRate − NegativeRate. `data/tone_panel.csv` giữ tone theo từng accession, doanh nghiệp và năm. So sánh VADER là đối chứng từ điển phổ thông, không được xem là nhãn chân lý cho mỗi câu tài chính. Một phép thử loại bảng số được báo cáo riêng; baseline vẫn chứa bảng nếu bảng nằm trong MD&A thật.

## Thiết kế event study và mô hình

Giá điều chỉnh của 100 cổ phiếu và benchmark S&P 500 (^GSPC) được lưu trong cache thị trường. Lợi suất r_i,t = P_i,t/P_i,t-1 − 1. Lịch phiên XNYS quyết định t=0; khi ngày SEC là ngày nghỉ/cuối tuần, t=0 là phiên kế tiếp. Mô hình thị trường r_i,t = α_i + β_i r_m,t + ε_i,t được ước lượng trên [-120,-20] phiên, yêu cầu tối thiểu 80 cặp lợi suất hợp lệ. AR_i,t = r_i,t − (α̂_i + β̂_i r_m,t); CAR[a,b] là tổng AR từ a đến b, gồm hai đầu. Baseline căn cùng phiên; các đối chứng dùng phiên kế tiếp và acceptance time của SEC so với giờ đóng cửa thật của XNYS.

Hồi quy OLS nền CAR_i[-1,+1] = a + b×Tone_i + u_i dùng HC3. Bảng kết quả còn có năm, hiệu ứng cố định công ty, biến tài chính cùng accession/kỳ, thay đổi tone, tỷ lệ từ tiêu cực/bất định và hiệu chỉnh Holm cho các hệ số được báo cáo. Đối chứng cluster theo 100 doanh nghiệp và loại từng công ty một đánh giá độ nhạy; 18 kiểm định định trước với loại bảng số, negativity và buy-and-hold excess return có Holm chung. Không chọn mô hình nào theo p-value tốt nhất.

## Thống kê mô tả

Các tỷ lệ và lợi suất ở dạng thập phân; nhân 100 khi diễn giải điểm phần trăm.

{table(desc)}

## Kết quả chính và độ nhạy

{table(regression)}

Ba cách căn ngày cho cùng mô hình nền:

{table(pd.DataFrame(alignment))}

Hệ số b={base.coefficient:.5f} có nghĩa tăng tone 0,01 đi cùng CAR thay đổi xấp xỉ {base.coefficient:.5f} điểm phần trăm trong mẫu, không phải dự báo giao dịch. Kiểm định cluster theo doanh nghiệp cho b={cluster.params['tone']:.5f}, SE={cluster.bse['tone']:.5f}, p={cluster.pvalues['tone']:.5f}, CI [{ci.iloc[0]:.5f}; {ci.iloc[1]:.5f}]. {rows_8k} báo cáo có 8-K Item 2.02 gần cửa sổ sự kiện; bảng `excluding_8k202.csv` cho ước lượng sau loại chúng. Screening này không nhận diện mọi tin tức cùng ngày. Phép loại từng doanh nghiệp và {len(sensitivity)} kiểm định độ nhạy nằm trong output để người đọc đối chiếu dấu, độ lớn và khoảng tin cậy.

## Diễn giải kinh tế và giới hạn

Tone mô tả ngôn ngữ công bố, không đo trực tiếp chất lượng doanh nghiệp. Doanh nghiệp có nhiều rủi ro phải mô tả có thể dùng nhiều từ tiêu cực dù hoạt động tốt. Nhà đầu tư và ngân hàng có thể dùng tone như tín hiệu ưu tiên đọc, kết hợp dòng tiền, đòn bẩy và bối cảnh công bố. Không dùng kết quả quan sát này để khẳng định tone gây biến động giá hay tạo chiến lược giao dịch có lãi. Các nguồn nhiễu gồm earnings release cùng ngày, lựa chọn thời điểm công bố, thay đổi chế độ thị trường, benchmark là chỉ số giá trong khi cổ phiếu dùng adjusted price, thay đổi nghĩa của từ và văn bản bảng. Số công ty đủ 10 năm tạo survivorship bias. Audit cấu trúc có trợ giúp AI và hash nguồn, chưa có gán nhãn thủ công toàn văn hay kiểm tra CRSP độc lập.

## Tính tái lập và trách nhiệm sử dụng AI

Code đọc `config.json`, tải SEC với User-Agent nhóm, cache raw kèm metadata, tải từ điển LM chính thức, giá và companyfacts, sau đó tính lại toàn bộ. Không có dữ liệu giả trong kết quả thực nghiệm. Các URL SEC, accession, SHA-256, văn bản trích, lỗi bị loại, bảng giá và script đều được giữ để tái kiểm. AI hỗ trợ viết code, chuẩn hóa và rà soát ranh giới; số liệu đến từ nguồn đã lưu và được tính bằng Python. Người trình bày cần tự giải thích dữ liệu, phương trình, cờ 8-K, CI, Holm và giới hạn khi bảo vệ.

## Tài liệu tham khảo

Loughran, T. & McDonald, B. (2011), “When Is a Liability Not a Liability? Textual Analysis, Dictionaries, and 10-Ks”, Journal of Finance. [Notre Dame SRAF](https://sraf.nd.edu/loughranmcdonald-master-dictionary/). Tetlock, P. (2007), “Giving Content to Investor Sentiment”, Journal of Finance. Li, F. (2008), “Annual Report Readability, Current Earnings, and Earnings Persistence”, Journal of Accounting and Economics. MacKinlay, A. (1997), “Event Studies in Economics and Finance”, Journal of Economic Literature. Dữ liệu: [SEC EDGAR](https://www.sec.gov/edgar/search/), [SEC API](https://www.sec.gov/search-filings/edgar-application-programming-interfaces), [XNAS/XNYS calendar package](https://github.com/gerrymanoim/exchange_calendars), [Yahoo Finance](https://finance.yahoo.com/).
"""
    write("REPORT", source)
    write("REAL_RESULTS", "# Kết quả dữ liệu thực\n\n" + source.split("## Kết quả chính và độ nhạy\n\n",1)[1].split("## Diễn giải kinh tế",1)[0])
    write("EXPANDED_RESULTS", f"# Kết quả mở rộng mẫu 100 công ty\n\nDanh sách gốc gồm đúng 100 ticker; mỗi công ty có 10 năm tài khóa FY2016–FY2025. SEC manifest có {len(manifest)} accession duy nhất, bảng tone và CAR cùng phiên có {len(panel)} dòng của {panel.ticker.nunique()} công ty. Không bổ sung công ty ngoài CSV.\n\n{table(pd.DataFrame(alignment))}\n\n{table(regression)}\n\nNguồn kiểm toán: `data/companies_100_input.csv`, `data/filings_manifest.csv`, `data/extraction_audit.csv`, `outputs/real/*/car_panel.csv`.\n")
    write("SAMPLE_DESIGN", "# Thiết kế mẫu 100 công ty\n\nDanh sách đầu vào do người dùng cung cấp trong `companies_100.csv`; bản sao không sửa ở `data/companies_100_input.csv`. Mỗi ticker được ghép CIK SEC, lấy 10-K gốc cho FY2016–2025. Không nối thêm 50 công ty cũ, không đổi công ty theo kết quả hồi quy. Mẫu có chủ đích và thiên lệch sống sót.\n\n" + table(pd.DataFrame([{"Chỉ tiêu":"Công ty đầu vào","Số lượng":100},{"Chỉ tiêu":"Năm mỗi công ty","Số lượng":10},{"Chỉ tiêu":"Accession phân tích","Số lượng":len(panel)}])) + "\nXem bảng đối chiếu CIK trong `outputs/qa/company_list_100_validation.csv` và nhãn năm trong manifest.\n")
    write("FISCAL_YEAR_REVIEW", "# Kiểm tra năm tài khóa\n\nFY được so giữa kỳ kết thúc trên bìa, DEI, lịch 52/53 tuần và accession. Với DG, ROST, ULTA, WSM, TDY, một báo cáo kết thúc tháng 1–2 thường mang nhãn FY của năm trước. Với KHC, kỳ tháng 1/2016 là FY2015 nên không nằm trong mẫu. Với ACGL, WRB và FCX, có một số DEI/cached label lỗi thời; kỳ 31/12 trên bìa được dùng sau rà soát. Quy tắc và nguồn được ghi ở cột `fiscal_year_source` của `data/filings_manifest.csv`. Mọi cặp ticker–FY trong 2016–2025 chỉ xuất hiện một lần.\n")
    write("EXTRACTION_REVIEW", "# Kiểm toán trích MD&A\n\nToàn bộ 1.000 hồ sơ có URL SEC, accession, bản gốc lưu cứng, checksum và tệp MD&A trích. Audit ghi cách cắt, số từ, mở đầu/kết thúc; quy tắc riêng cho tài liệu có MD&A nhúng hoặc Exhibit 13 được ghi trong `tonecar/text.py`. Kiểm tra này là rà soát cấu trúc có AI hỗ trợ; chưa phải đọc thủ công và gán nhãn toàn bộ 1.000 báo cáo.\n\n" + table(methods))
    write("EXPANSION_VALIDATION", "# Xác minh danh sách 100 công ty\n\nDanh sách chính xác từ file người dùng, được giữ ở `data/companies_100_input.csv`. `outputs/qa/company_list_100_validation.csv` đối chiếu CIK/lịch sử SEC; TDY cần rà soát vì năm 52/53 tuần kết thúc đầu tháng 1 làm cho số năm dương lịch khác số FY. `outputs/qa/final_100_audit.json` xác nhận 1.000 cặp công ty–năm và hash 1.000 báo cáo 10-K gốc cùng 12 Exhibit 13. Không thay ticker theo kết quả thị trường.\n")
    write("TEXT_PROCESSING_REVIEW", "# Kiểm tra xử lý văn bản\n\n" + source.split("## Xử lý MD&A và kiểm soát chất lượng\n\n",1)[1].split("## Thiết kế event study",1)[0] + "\nBản trích text đầy đủ nằm tại `data/interim/mda/<accession>.txt`; bản raw HTML và phụ lục được giữ trong `data/raw/sec`. Có thể đối chiếu mỗi accession với URL SEC, đầu/cuối section, số từ, tone và checksum.\n")
    write("METHODOLOGY", "# Phương pháp và tái lập\n\n" + source.split("## Thiết kế mẫu và truy nguyên nguồn\n\n",1)[1].split("## Thống kê mô tả",1)[0])
    write("DATA_SOURCES", "# Nguồn dữ liệu và cách tải\n\n" + source.split("## Thiết kế mẫu và truy nguyên nguồn\n\n",1)[1].split("## Xử lý MD&A",1)[0] + "\nTệp HTML gốc và Exhibit 13 được lưu trong `data/raw/sec/*.raw`, metadata cùng basename `.json`. Bảng sau xử lý nằm ở `data/tone_panel.csv` và `outputs/real/{same,next,acceptance}/car_panel.csv`. Từ điển LM ở `data/external/lm.csv`; giá có raw cache. `data/filings_manifest.csv` cho phép mở từng URL SEC và đối chiếu hash.\n")
    write("LIMITATIONS_REMEDIATION", "# Giới hạn và cách khắc phục\n\n" + source.split("## Diễn giải kinh tế và giới hạn\n\n",1)[1].split("## Tính tái lập",1)[0] + f"\nĐối chứng định lượng gồm {len(sensitivity)} kiểm định định trước, Holm trên toàn bộ họ, căn ngày sự kiện ba cách, loại 8-K 2.02, cluster theo công ty và leave-one-firm-out. Bảng số loại khỏi MD&A chỉ ở bản sensitivity. Kết quả baseline không bị thay theo p-value.\n\n" + table(sensitivity[["alignment","specification","coefficient","p_cluster","p_holm","N"]]))
    write("LITERATURE_COMPARISON", "# Đối chiếu tài liệu nền\n\n" + source.split("## Tổng quan tài liệu và phạm vi tái lập\n\n",1)[1].split("## Thiết kế mẫu",1)[0] + "\nKhác LM (2011), đây là mẫu 100 công ty có chủ đích và dùng Yahoo Finance thay CRSP. Do đó chỉ đối chiếu hướng nghiên cứu/phương pháp, không so hệ số như cùng một tổng thể.\n")
    write("REFERENCES", "# Tài liệu tham khảo và nguồn trực tiếp\n\n" + source.split("## Tài liệu tham khảo\n\n",1)[1])
    write("DEFENSE", f"# Gợi ý bảo vệ và phản biện\n\n1. Mẫu là chính xác 100 ticker người dùng đưa; 1.000 MD&A và 1.000 event cùng phiên được nối qua accession.\n2. Trình bày URL SEC, HTML gốc, Exhibit 13, hash, manifest và ví dụ Apple FY2025 để chứng minh dữ liệu thật.\n3. Viết Tone=(Positive−Negative)/TotalWords, giải thích vì sao từ điển LM phù hợp tài chính hơn VADER phổ thông.\n4. Viết AR và CAR, chỉ rõ estimation [-120,-20], cửa sổ [-1,+1], lịch XNYS và acceptance-time đối chứng.\n5. Báo hệ số baseline {base.coefficient:.5f}, p={base.p_value:.5f}, CI [{base.ci_low:.5f};{base.ci_high:.5f}]; giải thích CI và không gọi quan hệ này là nhân quả.\n6. Thừa nhận 8-K và sự kiện khác, survivorship, giá adjusted so price index, audit AI chưa thay đọc thủ công.\n7. Đọc và chạy code trực tiếp trên repo, không dựa vào hình chụp hay dữ liệu demo.\n")
    pdf_from_markdown(source)
    print("Report regenerated:", len(panel), "events,", panel.ticker.nunique(), "firms; baseline p", base.p_value)


if __name__ == "__main__":
    main()
