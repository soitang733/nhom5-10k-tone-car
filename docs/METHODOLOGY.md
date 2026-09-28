# Hướng dẫn phương pháp và tái lập chi tiết

## Phạm vi

Năm tài chính 2016–2025; 50 ticker trong config.json; ngày khóa 27/09/2026. Giữ 10-K gốc, accession duy nhất, lấy filing đầu tiên cho cùng kỳ. Loại 10-K/A khỏi thiết kế baseline. Kiểm tra DEI trước khi quyết định một báo cáo thuộc năm nào.

## Chạy online

Thiết lập SEC_USER_AGENT trong .env bằng danh tính nhóm và email thật. Chạy python -m tonecar.pipeline --mode real. Dùng --reuse-text khi chỉ mở rộng mẫu và các quy tắc parser cũ vẫn hợp lệ; bỏ tùy chọn này khi sửa parser ảnh hưởng nội dung đã trích xuất. Cache tránh tải lại raw filing. Không vượt giới hạn request của SEC.

Sau pipeline: chạy python scripts/finalize.py để screening 8-K; python scripts/complete_project.py để tạo bảng robustness và báo cáo; python scripts/build_notebook.py để tạo notebook; thực thi notebook; python scripts/package_project.py để đóng gói. Mỗi bước phụ thuộc bước trước, không chạy đồng thời khi đang xuất dữ liệu cùng thư mục.

## Chạy offline

Mở notebooks/final_analysis.ipynb với môi trường chứa requirements-lock.txt. Notebook dùng MD&A và các bảng đã đóng gói để tái tính tone, CAR và baseline. Không cần SEC hoặc Yahoo cho phần xác minh offline. Dùng start-local.ps1 để mở dashboard; server chỉ lắng nghe loopback. ZIP không chứa .env hay email cấu hình.

## Từ điển dữ liệu

| Biến | Đơn vị và ý nghĩa |
|---|---|
| ticker / cik | Mã giao dịch và định danh SEC; ticker không phải khóa lịch sử hoàn hảo |
| accession | Khóa duy nhất của filing SEC |
| fiscal_year | Năm tài chính; khác filing_date |
| report_date | Ngày kết thúc kỳ báo cáo |
| acceptance | Timestamp SEC nhận tài liệu; phải chuyển múi giờ trước căn phiên |
| total_words | Số token chữ cái hợp lệ, tối thiểu 2 ký tự |
| positive / negative / uncertainty | Số lượt token thuộc nhóm LM, không phải số từ duy nhất |
| tone | (Positive − Negative) / Total words; tỷ lệ thập phân |
| negative_rate / uncertainty_rate | Số lượt nhóm / Total words |
| generic_tone | Tỷ lệ theo dấu word list VADER, cùng mẫu số |
| car_-1_1 | Tổng AR của 3 phiên, dạng lợi suất thập phân |
| car_-3_3 / car_-5_5 | Tổng AR của 7 / 11 phiên |
| mar_-1_1 | Lợi suất market-adjusted, giả định alpha=0 beta=1 |
| raw_sha256 / lm_sha256 | Dấu kiểm tra snapshot đầu vào |
| alignment_rule | same, next hoặc acceptance |

## Công thức và ví dụ

Nếu MD&A có 10.000 token, 100 positive và 300 negative thì tone = −0,02. Nếu 200 uncertainty thì uncertainty_rate = 0,02. Ví dụ chỉ minh họa phép tính, không phải quan sát thật của mẫu.

Ước lượng Ri,t = alpha + beta Rm,t + epsilon trên 101 phiên [-120,-20], yêu cầu ít nhất 80 cặp return hợp lệ. AR = return thực tế − return dự báo. CAR cộng AR bao gồm cả hai đầu mút. Nếu alpha=0,0002, beta=1,1, Rm=0,01 và Ri=0,008 thì return dự báo=0,0112 và AR=−0,0032, tức −0,32%. Ví dụ này không thay thế dữ liệu thực tế.

## Đặc tả và suy luận

Baseline: CAR[-1,+1] = intercept + b Tone + error, OLS với HC3. Đối chứng thêm year FE, firm FE, negativity/uncertainty, generic_tone, MAR, căn ngày khác và loại cờ 8-K. Các đặc tả FE cần ma trận đầy hạng và bậc tự do đủ. Cluster SE theo ticker có 50 cụm; đọc như kiểm tra độ nhạy. Holm điều chỉnh nhóm hệ số xuất trong mỗi alignment, không bảo đảm mọi thao tác bộ lọc được điều chỉnh multiple testing.

## Quy trình kiểm tra lỗi

Nếu extraction thất bại, đọc exclusions.csv, raw HTML và đầu/cuối audit. Nếu thiếu CAR, kiểm tra giá trong estimation và event window; không fill forward để làm đủ mẫu. Nếu hệ số thay đổi sau cập nhật, so manifest, năm tài chính, checksum và thời điểm căn ngày trước khi diễn giải khác biệt kinh tế. Nếu giao diện hiện N cũ, dùng Cập nhật dữ liệu; mọi trang phải nêu rõ khoảng mẫu hiện hành.

## Các giới hạn phải trình bày

Mẫu có chủ đích, survivorship bias, retrospective dictionary, parser heuristic, stock adjusted price so với benchmark price index, ít clusters và thông tin công bố trước filing. Không có causal identification hoặc backtest chiến lược. Phần audit cấu trúc tự động không phải human annotation toàn văn.

## Kiểm định thay đổi tone và fundamentals

Delta_tone = Tone(t) − Tone(t−1), chỉ tính cho hai fiscal years liên tiếp cùng ticker. Không nối qua năm thiếu, không thay NaN bằng 0. Trong phạm vi mười năm, mỗi công ty có nhiều nhất chín quan sát delta. Year/firm FE và controls là đặc tả phụ đã công bố, không lựa chọn để đạt p<0,05.

SEC Company Facts cung cấp Assets, Liabilities và NetIncomeLoss/ProfitLoss theo đơn vị USD. Chỉ lấy fact có accession đúng filing đang phân tích, end đúng report_date và form 10-K. Net income phải là kỳ năm 330–385 ngày, không lấy quý hoặc số comparative năm cũ. Nếu nhiều giá trị khác nhau cho cùng tag/kỳ/accession, đánh dấu ambiguous và để thiếu. Có thể suy Liabilities = Assets − StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest khi cả hai có cùng kỳ/accession. Không lấy equity chỉ của công ty mẹ để suy tổng liabilities khi thiếu noncontrolling interest.

Log_assets = ln(tổng tài sản USD), là proxy quy mô theo tài sản, không phải market capitalization. Liabilities_assets = tổng nợ phải trả/tổng tài sản, không đồng nghĩa interest-bearing debt ratio. ROA = net income/tài sản cuối năm, không dùng tài sản bình quân. Báo cáo controls dùng complete cases và công bố N; tuyệt đối không điền số thiếu bằng 0. Các chỉ tiêu này cùng có trong filing nên mang tính đồng thời, không tự giải quyết nội sinh.

Chạy scripts/enrich_fundamentals.py sau pipeline và trước finalize/complete_project. API nguồn: https://www.sec.gov/search-filings/edgar-application-programming-interfaces . Dữ liệu đã chọn và tag/provenance ở data/fundamentals_panel.csv.
