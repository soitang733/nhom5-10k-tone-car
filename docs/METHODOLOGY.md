# Phương pháp và tái lập

Danh sách gốc `data/companies_100_input.csv` có SHA-256 lưu trong snapshot metadata. Bảng kiểm `outputs/qa/company_list_100_validation.csv` đối chiếu ticker và CIK với SEC. Danh sách được cố định theo file người dùng đưa, không lựa theo p-value. SEC Submissions API cho form, accession, report date, filing date và acceptance time. Client đọc cả file lịch sử, giữ form 10-K đầu tiên cho từng kỳ, bỏ 10-K/A; ngày nộp không sau 28/09/2026. Bản HTML hoặc phụ lục Exhibit 13 thật được lưu cứng vào `data/raw/sec` dưới tên băm URL kèm JSON provenance, URL và SHA-256. Hồ sơ Apple FY2025 trong mẫu là bản năm kết thúc 27/09/2025, không phải dữ liệu tự dựng.

Mười năm tài khóa 2016–2025 được gán từ DEI và kỳ trên bìa, có đối chiếu các trường hợp năm tài khóa kết thúc tháng 1–2 và DEI lỗi thời. `data/filings_manifest.csv` ghi nguồn quyết định nhãn năm; mỗi cặp ticker–năm đúng một accession. Mẫu có chủ đích gồm các công ty tồn tại và có dữ liệu đủ 10 năm, nên có thiên lệch sống sót và không đại diện ngẫu nhiên cho toàn thị trường.

## Xử lý MD&A và kiểm soát chất lượng

HTML được giải mã với UnicodeDammit, bỏ script/style và XBRL header ẩn, chuẩn hóa Unicode NFKC; nội dung khối được giữ để phát hiện tiêu đề. Parser lấy Item 7 đến Item 7A hoặc Item 8 khi có tiêu đề rõ. Với bố cục annual report lồng trong tài liệu chính hoặc Exhibit 13, quy tắc riêng phải khớp tiêu đề nội dung và điểm bắt đầu chương tiếp theo, tránh lấy mục lục. Martin Marietta dùng trang Exhibit 13 có heading MD&A lặp trên từng trang; Nucor dừng trước báo cáo kiểm toán. Deere được xử lý lỗi chia chữ `INCOM E` ở tiêu đề báo cáo tài chính. Các cách trích, số token, đầu/cuối và URL nguồn lưu trong `data/extraction_audit.csv`.

| Cách trích | Số báo cáo |
| --- | --- |
| item7_block_heading | 936 |
| issuer_heading_boundaries_CAH | 10 |
| issuer_substantive_heading_DE | 10 |
| issuer_substantive_heading_LVS | 10 |
| issuer_substantive_heading_FCX | 10 |
| incorporated_Exhibit_13_CCL | 6 |
| issuer_substantive_heading_MELI | 6 |
| issuer_substantive_heading_FDX | 5 |
| incorporated_Exhibit_13_MLM | 3 |
| incorporated_Exhibit_13_NUE | 3 |
| issuer_heading_boundaries_CCL | 1 |


Từ được tách thành token chữ cái dài ít nhất hai ký tự, chuyển uppercase; không stemming và không bỏ stopword ở mẫu số. PositiveRate = số token LM tích cực/tổng token; NegativeRate tương tự; UncertaintyRate tương tự; Tone = PositiveRate − NegativeRate. `data/tone_panel.csv` giữ tone theo từng accession, doanh nghiệp và năm. So sánh VADER là đối chứng từ điển phổ thông, không được xem là nhãn chân lý cho mỗi câu tài chính. Một phép thử loại bảng số được báo cáo riêng; baseline vẫn chứa bảng nếu bảng nằm trong MD&A thật.

## Thiết kế event study và mô hình

Giá điều chỉnh của 100 cổ phiếu và benchmark S&P 500 (^GSPC) được lưu trong cache thị trường. Lợi suất r_i,t = P_i,t/P_i,t-1 − 1. Lịch phiên XNYS quyết định t=0; khi ngày SEC là ngày nghỉ/cuối tuần, t=0 là phiên kế tiếp. Mô hình thị trường r_i,t = α_i + β_i r_m,t + ε_i,t được ước lượng trên [-120,-20] phiên, yêu cầu tối thiểu 80 cặp lợi suất hợp lệ. AR_i,t = r_i,t − (α̂_i + β̂_i r_m,t); CAR[a,b] là tổng AR từ a đến b, gồm hai đầu. Baseline căn cùng phiên; các đối chứng dùng phiên kế tiếp và acceptance time của SEC so với giờ đóng cửa thật của XNYS.

Hồi quy OLS nền CAR_i[-1,+1] = a + b×Tone_i + u_i dùng HC3. Bảng kết quả còn có năm, hiệu ứng cố định công ty, biến tài chính cùng accession/kỳ, thay đổi tone, tỷ lệ từ tiêu cực/bất định và hiệu chỉnh Holm cho các hệ số được báo cáo. Đối chứng cluster theo 100 doanh nghiệp và loại từng công ty một đánh giá độ nhạy; 18 kiểm định định trước với loại bảng số, negativity và buy-and-hold excess return có Holm chung. Không chọn mô hình nào theo p-value tốt nhất.
