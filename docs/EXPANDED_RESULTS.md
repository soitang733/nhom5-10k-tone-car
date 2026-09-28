
## Phụ lục G. Kết quả mở rộng 50 công ty và phương pháp bổ sung

Mẫu mục tiêu cố định 50 công ty, 500 firm-years. Manifest có 500 filings, trích được 500 MD&A và baseline có 500 sự kiện hợp lệ thuộc 50 công ty. Danh sách được chọn trước kết quả mới, không thay công ty theo dấu hệ số hoặc p-value. Các nhóm ngành sau là nhóm phân tích tự định nghĩa, không phải GICS chính thức. Cỡ mẫu lớn hơn không bảo đảm statistical significance.

| ticker | analytical_group | sample_status | valid_events | target_events |
|---|---|---|---|---|
| AAPL | Technology | original | 10 | 10 |
| MSFT | Technology | original | 10 | 10 |
| AMZN | Technology | original | 10 | 10 |
| GOOGL | Technology | original | 10 | 10 |
| NVDA | Technology | original | 10 | 10 |
| ORCL | Technology | added | 10 | 10 |
| IBM | Technology | added | 10 | 10 |
| INTC | Technology | added | 10 | 10 |
| CSCO | Technology | added | 10 | 10 |
| ADBE | Technology | added | 10 | 10 |
| CRM | Technology | added | 10 | 10 |
| QCOM | Technology | added | 10 | 10 |
| TXN | Technology | added | 10 | 10 |
| AMD | Technology | added | 10 | 10 |
| JPM | Financials | original | 10 | 10 |
| BAC | Financials | added | 10 | 10 |
| C | Financials | added | 10 | 10 |
| WFC | Financials | added | 10 | 10 |
| GS | Financials | added | 10 | 10 |
| MS | Financials | added | 10 | 10 |
| BLK | Financials | added | 10 | 10 |
| AXP | Financials | added | 10 | 10 |
| JNJ | Healthcare | original | 10 | 10 |
| UNH | Healthcare | added | 10 | 10 |
| PFE | Healthcare | added | 10 | 10 |
| MRK | Healthcare | added | 10 | 10 |
| ABBV | Healthcare | added | 10 | 10 |
| ABT | Healthcare | added | 10 | 10 |
| BMY | Healthcare | added | 10 | 10 |
| AMGN | Healthcare | added | 10 | 10 |
| WMT | Consumer | original | 10 | 10 |
| PG | Consumer | original | 10 | 10 |
| KO | Consumer | added | 10 | 10 |
| PEP | Consumer | added | 10 | 10 |
| COST | Consumer | added | 10 | 10 |
| HD | Consumer | added | 10 | 10 |
| MCD | Consumer | added | 10 | 10 |
| NKE | Consumer | added | 10 | 10 |
| DIS | Consumer | added | 10 | 10 |
| CAT | Industrials | added | 10 | 10 |
| HON | Industrials | added | 10 | 10 |
| UPS | Industrials | added | 10 | 10 |
| LMT | Industrials | added | 10 | 10 |
| UNP | Industrials | added | 10 | 10 |
| XOM | Energy | original | 10 | 10 |
| CVX | Energy | added | 10 | 10 |
| COP | Energy | added | 10 | 10 |
| SLB | Energy | added | 10 | 10 |
| NEE | Utilities | added | 10 | 10 |
| DUK | Utilities | added | 10 | 10 |


So sánh cùng thiết kế baseline giữa snapshot 100 và mẫu mở rộng:

| sample | N | b | SE_HC3 | p |
|---|---|---|---|---|
| Original 10 firms | 100 | -0.226326 | 0.883157 | 0.797743 |
| Expanded 50-firm target | 500 | -0.058633 | 0.285987 | 0.837558 |


Chênh lệch hệ số giữa hai mẫu phản ánh bổ sung công ty và thay đổi thành phần mẫu. Không thể coi đó là thí nghiệm chứng minh cỡ mẫu gây thay đổi hệ số. Cần đọc SE, CI và độ phủ; baseline gốc vẫn giữ trong archive.

Delta_tone bằng tone năm hiện tại trừ năm liền trước của cùng công ty. Chỉ dùng hai fiscal years liên tiếp, không nối qua năm thiếu và không gán delta năm đầu bằng 0. Vì thế N nhỏ hơn mô hình tone mức. Đặc tả delta đơn có N=450, b=1.898472, SE HC3=1.665164, p=0.254240, CI [-1.365189; 5.162133]. Khoảng tin cậy chứa 0.

Các đặc tả chính và phụ cho CAR[-1,+1]:

| specification | term | coefficient | se_HC3 | p_value | ci_low | ci_high | n | p_holm_all_reported_tests |
|---|---|---|---|---|---|---|---|---|
| tone | tone | -0.058633 | 0.285987 | 0.837558 | -0.619158 | 0.501892 | 500.0 | 1.0 |
| tone + C(fiscal_year) | tone | -0.040205 | 0.287885 | 0.888932 | -0.604449 | 0.52404 | 500.0 | 1.0 |
| tone + C(fiscal_year) + C(ticker) | tone | 1.31728 | 1.62175 | 0.416644 | -1.861292 | 4.495852 | 500.0 | 1.0 |
| delta_tone | delta_tone | 1.898472 | 1.665164 | 0.25424 | -1.365189 | 5.162133 | 450.0 | 1.0 |
| delta_tone + C(fiscal_year) | delta_tone | 1.846003 | 1.742831 | 0.28951 | -1.569883 | 5.261888 | 450.0 | 1.0 |
| delta_tone + C(fiscal_year) + C(ticker) | delta_tone | 1.767462 | 1.568753 | 0.259883 | -1.307237 | 4.842162 | 450.0 | 1.0 |
| tone + log_assets + liabilities_assets + roa + C(fiscal_year) | tone | -0.2922 | 0.45828 | 0.523733 | -1.190413 | 0.606012 | 441.0 | 1.0 |
| delta_tone + log_assets + liabilities_assets + roa + C(fiscal_year) | delta_tone | 1.756585 | 2.000005 | 0.379786 | -2.163353 | 5.676523 | 397.0 | 1.0 |


Fundamentals từ SEC Company Facts chọn đúng accession 10-K và report_date, units USD. Log_assets đo quy mô theo tài sản; liabilities_assets là tỷ lệ tổng nợ phải trả trên tài sản; ROA dùng lợi nhuận năm chia tài sản cuối năm. Các biến không được lấy từ báo cáo nộp sau sự kiện hoặc từ quý gần nhất. Giá trị thiếu/khác nhau giữa các facts được công bố, không tự điền 0. Mô hình controls dùng complete cases nên phải so sánh N riêng. Chỉ tiêu của công ty tài chính và phi tài chính có ý nghĩa kinh tế khác nhau; pooled controls không tự giải quyết khác biệt ngành.

Các mô hình delta, fixed effects và controls là kiểm định phụ. Holm tính cho toàn bộ hệ số mục tiêu xuất trong mỗi alignment; không điều chỉnh toàn bộ lựa chọn giao diện. Không sử dụng kết quả có p nhỏ nhất để thay câu hỏi nghiên cứu sau khi nhìn dữ liệu. FinBERT và earnings surprise chưa có kết quả trong đợt này; không được diễn giải như đã thực hiện.

Độ phủ biến kiểm soát (số filing có dữ liệu):

| variable | available |
|---|---|
| log_assets | 500 |
| liabilities_assets | 441 |
| roa | 500 |


Đối chứng sai số chuẩn cluster theo công ty (finite-sample correction, phân phối t):

| specification | term | coefficient | se_cluster | p_cluster | ci_low | ci_high | N | clusters |
|---|---|---|---|---|---|---|---|---|
| tone | tone | -0.058633 | 0.185194 | 0.752891 | -0.430794 | 0.313529 | 500 | 50 |
| delta_tone | delta_tone | 1.898472 | 1.733818 | 0.278885 | -1.585766 | 5.38271 | 450 | 50 |
| delta_year | delta_tone | 1.846003 | 1.789709 | 0.307392 | -1.750553 | 5.442558 | 450 | 50 |
| delta_firm | delta_tone | 1.767462 | 1.695656 | 0.302366 | -1.640085 | 5.17501 | 450 | 50 |
| tone_controls | tone | -0.2922 | 0.245221 | 0.239673 | -0.786101 | 0.2017 | 441 | 46 |
| delta_controls | delta_tone | 1.756585 | 1.717542 | 0.312025 | -1.704893 | 5.218063 | 397 | 45 |
| tone_same_controls_sample | tone | -0.067847 | 0.195099 | 0.729645 | -0.460797 | 0.325103 | 441 | 46 |

Mô hình tone_same_controls_sample giữ đúng các complete cases của mô hình controls, giúp phân biệt thay đổi thành phần mẫu với việc thêm biến. Các p-value cluster trong bảng này chưa điều chỉnh đa kiểm định; dùng cùng bảng Holm và không chọn đặc tả theo p-value.
