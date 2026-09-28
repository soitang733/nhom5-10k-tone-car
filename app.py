"""Public, read-only Streamlit view of the verified 10-K tone/CAR snapshot."""
from pathlib import Path
import json
import re

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
import streamlit as st

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "snapshot"
ALIGNMENTS = {"Cùng phiên": "same", "Phiên kế tiếp": "next", "Theo giờ SEC": "acceptance"}
WINDOWS = {"[-1, +1]": "-1_1", "[-3, +3]": "-3_3", "[-5, +5]": "-5_5"}
SPECS = {
    "Tone gốc": ("tone", []),
    "Tone + năm": ("tone + C(fiscal_year)", []),
    "Tone + năm + doanh nghiệp": ("tone + C(fiscal_year) + C(ticker)", []),
    "Tỷ lệ tiêu cực + bất định": ("negative_rate + uncertainty_rate", []),
    "Thay đổi tone": ("delta_tone", ["delta_tone"]),
    "Thay đổi tone + năm": ("delta_tone + C(fiscal_year)", ["delta_tone"]),
    "Tone + biến tài chính + năm": ("tone + log_assets + liabilities_assets + roa + C(fiscal_year)", ["log_assets", "liabilities_assets", "roa"]),
}

st.set_page_config(page_title="Nhóm 5 · 10-K Tone & CAR", page_icon="📄", layout="wide")
st.markdown("""<style>
html,body,[class*="css"]{font-family:Arial,sans-serif}
[data-testid="stSidebar"]{background:#14233b;color:#f8fafc}
[data-testid="stSidebar"] *{color:#f8fafc}
[data-testid="stSidebar"] [data-baseweb="select"] *{color:#14233b!important}
[data-testid="stSidebar"] [data-baseweb="popover"] *{color:#14233b!important}
h1,h2,h3{color:#14233b}
.hero{background:#14233b;border-radius:14px;padding:28px 35px;color:#fff;margin:0 0 24px}
.hero h1{color:#fff;margin:0 0 10px;font-size:36px}
.hero p{color:#b8cee7;font-size:17px;margin:0}
.smallnote{font-size:13px;color:#65758d}
@media(max-width:650px){.hero{padding:20px}.hero h1{font-size:26px}}
</style>""", unsafe_allow_html=True)

@st.cache_data(show_spinner=False)
def csv(name: str) -> pd.DataFrame:
    return pd.read_csv(DATA / name)

@st.cache_data(show_spinner=False)
def metadata() -> dict:
    return json.loads((DATA / "metadata.json").read_text(encoding="utf-8"))

def vi(value: float, digits: int = 3) -> str:
    if pd.isna(value):
        return "—"
    return f"{value:,.{digits}f}".replace(",", "_").replace(".", ",").replace("_", ".")

def selected_panel(alignment: str, firm: str, year: str) -> pd.DataFrame:
    frame = csv(f"{alignment}_panel.csv")
    if firm != "Tất cả":
        frame = frame[frame.ticker == firm]
    if year != "Tất cả":
        frame = frame[frame.fiscal_year == int(year)]
    return frame.copy()

def section(name: str) -> None:
    path = ROOT / "docs" / (name + ".md")
    if path.exists():
        st.markdown(path.read_text(encoding="utf-8"))

meta = metadata()
base = csv("same_panel.csv")
with st.sidebar:
    st.markdown("## NHÓM 5 · FINTECH")
    st.markdown("### Textual Finance")
    st.caption("SEC EDGAR · Loughran–McDonald · Event Study")
    page = st.radio("Điều hướng", ["Tổng quan", "Khám phá báo cáo", "Kiểm định mô hình", "Phương pháp & audit", "Báo cáo & tài liệu"], label_visibility="collapsed")
    st.divider()
    alignment_label = st.selectbox("Ngày sự kiện", list(ALIGNMENTS))
    alignment = ALIGNMENTS[alignment_label]
    window_label = st.selectbox("Cửa sổ CAR", list(WINDOWS))
    car = "car_" + WINDOWS[window_label]
    firm = st.selectbox("Doanh nghiệp", ["Tất cả"] + sorted(base.ticker.unique().tolist()))
    year = st.selectbox("Năm tài chính", ["Tất cả"] + [str(x) for x in sorted(base.fiscal_year.unique())])
    st.caption("Snapshot dữ liệu thật · FY2016–2025")

frame = selected_panel(alignment, firm, year)
st.markdown("<div class='hero'><h1>Phân tích văn bản báo cáo tài chính</h1><p>Từ ngôn ngữ MD&A trong 10-K đến phản ứng thị trường.</p></div>", unsafe_allow_html=True)

if page == "Tổng quan":
    st.subheader("Kết quả nghiên cứu")
    saved = csv(f"{alignment}_regressions.csv")
    baseline = saved[(saved.outcome == car) & (saved.specification == "tone")].iloc[0]
    k1,k2,k3,k4 = st.columns(4)
    k1.metric("Báo cáo", len(frame), f"{frame.ticker.nunique()} doanh nghiệp")
    k2.metric("Tone trung bình", vi(frame.tone.mean(), 4))
    k3.metric("CAR trung bình", vi(100 * frame[car].mean(), 2) + "%")
    k4.metric("p baseline · HC3", vi(baseline.p_value, 3))
    st.info(f"Toàn mẫu: b = {vi(baseline.coefficient, 5)}, p = {vi(baseline.p_value, 5)}, CI 95% [{vi(baseline.ci_low, 4)}; {vi(baseline.ci_high, 4)}], N = {int(baseline.n)}. Kết quả không chứng minh nhân quả. Bộ lọc phía trái chỉ thay biểu đồ; hệ số này thuộc toàn mẫu.")
    a,b = st.columns(2)
    with a:
        st.markdown("#### Tone và CAR")
        if not frame.empty:
            st.scatter_chart(frame, x="tone", y=car, color="ticker", height=330)
    with b:
        st.markdown("#### CAR bất thường tích lũy quanh filing")
        if not frame.empty:
            ids = frame.event_id.unique()
            ar = csv(f"{alignment}_event_ar.csv")
            ar = ar[ar.event_id.isin(ids)]
            caar = ar.groupby("relative_day").abnormal_return.mean().sort_index().cumsum().mul(100)
            st.line_chart(caar, x_label="Phiên so với ngày sự kiện", y_label="CAAR (%)", height=330)
    st.caption("Dữ liệu: 500 10-K thật, 50 doanh nghiệp; bảng kết quả đã được tính lại sau sửa 14 ranh giới MD&A. Các đối chứng không đạt mức 5% sau Holm.")

elif page == "Khám phá báo cáo":
    st.subheader("Báo cáo và tone từng doanh nghiệp")
    if frame.empty:
        st.warning("Không có báo cáo với bộ lọc này.")
    else:
        cols = ["ticker", "fiscal_year", "filing_date", "word_count", "positive_count", "negative_count", "uncertainty_count", "tone", car, "accession"]
        st.dataframe(frame[cols].sort_values(["ticker", "fiscal_year"]), hide_index=True, width="stretch")
        accession = st.selectbox("Chọn báo cáo để đọc MD&A", frame.accession.tolist(), format_func=lambda x: f"{frame.loc[frame.accession.eq(x), 'ticker'].iloc[0]} · FY{frame.loc[frame.accession.eq(x), 'fiscal_year'].iloc[0]} · {x}")
        row = frame[frame.accession.eq(accession)].iloc[0]
        st.write(f"**{row.ticker} · FY{row.fiscal_year}** — {int(row.word_count):,} token; tone {vi(row.tone, 5)}")
        source = row.mda_source_url if pd.notna(row.mda_source_url) else row.source_url
        st.markdown(f"[Mở MD&A hoặc Exhibit gốc trên SEC]({source}) · [Mở hồ sơ 10-K trên SEC]({row.source_url})")
        path = DATA / "mda" / (accession + ".txt")
        if path.exists():
            full = path.read_text(encoding="utf-8")
            search = st.text_input("Tìm từ trong bản trích")
            if search:
                st.caption(f"{len(re.findall(re.escape(search), full, flags=re.I))} lần xuất hiện trong bản trích")
            st.text_area("MD&A đã trích · trình bày gọn khoảng trắng", value=" ".join(full.split())[:30000], height=490)
            if len(full) > 30000:
                st.caption("Khung xem trước 30.000 ký tự; tải bản text bên dưới để xem toàn bộ.")
            st.download_button("Tải bản trích MD&A đầy đủ", full.encode("utf-8"), file_name=f"{row.ticker}_{row.fiscal_year}_MDA.txt", mime="text/plain")

elif page == "Kiểm định mô hình":
    st.subheader("Ước lượng và kiểm định")
    spec_label = st.selectbox("Đặc tả", list(SPECS))
    covariance = st.selectbox("Sai số chuẩn", ["HC3", "Cluster theo doanh nghiệp"])
    remove_flags = st.checkbox("Loại sự kiện có 8-K Item 2.02 trong cửa sổ", value=False)
    rhs, required = SPECS[spec_label]
    model_frame = frame.dropna(subset=required + [car]).copy()
    if remove_flags:
        flags = csv("earnings_8k_flags.csv")
        blocked = set(flags.loc[flags.flagged_8k_item202.astype(bool), "event_id"].str.rsplit("_", n=1).str[0])
        model_frame = model_frame[~model_frame.accession.isin(blocked)]
    formula = f'Q("{car}") ~ {rhs}'
    if len(model_frame) < 8:
        st.warning("Mẫu lọc có ít hơn 8 sự kiện; không chạy hồi quy.")
    elif covariance.startswith("Cluster") and model_frame.ticker.nunique() < 5:
        st.warning("Cần ít nhất 5 doanh nghiệp để hiển thị đối chứng cluster.")
    else:
        try:
            model = smf.ols(formula, model_frame)
            if model.exog.shape[0] - model.exog.shape[1] < 5 or np.linalg.matrix_rank(model.exog) < model.exog.shape[1]:
                st.warning("Không đủ bậc tự do hoặc ma trận giải thích thiếu hạng.")
            else:
                fit = model.fit(cov_type="HC3") if covariance == "HC3" else model.fit(cov_type="cluster", cov_kwds={"groups": model_frame.ticker, "use_correction": True}, use_t=True)
                st.code(formula)
                st.caption(f"N = {int(fit.nobs)} · {model_frame.ticker.nunique()} doanh nghiệp · R² = {vi(fit.rsquared, 4)}")
                result = pd.DataFrame({"biến":fit.params.index,"hệ số":fit.params.values,"SE":fit.bse.values,"p":fit.pvalues.values,"CI thấp":fit.conf_int().iloc[:,0].values,"CI cao":fit.conf_int().iloc[:,1].values})
                st.dataframe(result, hide_index=True, width="stretch")
        except (ValueError, KeyError, np.linalg.LinAlgError) as exc:
            st.warning(f"Không ước lượng được bộ lọc này: {exc}")
    st.markdown("#### 18 đối chứng đã công bố trước khi xem kết quả")
    sensitivity = csv("sensitivity_models.csv")
    st.dataframe(sensitivity[sensitivity.alignment.eq(alignment)], hide_index=True, width="stretch")
    st.caption("p_Holm hiệu chỉnh chung 18 kiểm định; kết quả trên không phải replication chính xác LM 2011.")

elif page == "Phương pháp & audit":
    st.subheader("Dữ liệu, truy nguyên và giới hạn")
    st.write("**500** filing · **50** doanh nghiệp · **FY2016–2025** · **14** ranh giới MD&A đã sửa · **500/500** bản trích khớp khi kiểm tra lại")
    doc = st.selectbox("Tài liệu", ["METHODOLOGY", "DATA_SOURCES", "EXTRACTION_REVIEW", "SAMPLE_DESIGN", "FISCAL_YEAR_REVIEW", "LIMITATIONS_REMEDIATION"])
    section(doc)

else:
    st.subheader("Báo cáo và tài liệu")
    pdf = ROOT / "Nhom5_BaoCao.pdf"
    if pdf.exists():
        st.download_button("Tải báo cáo PDF · 20 trang", pdf.read_bytes(), file_name=pdf.name, mime="application/pdf")
    doc = st.selectbox("Chọn tài liệu", ["REPORT", "LIMITATIONS_REMEDIATION", "LITERATURE_COMPARISON", "EXPANDED_RESULTS", "REFERENCES", "DEFENSE"])
    section(doc)
