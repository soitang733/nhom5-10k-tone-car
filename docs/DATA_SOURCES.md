# Dữ liệu dự án lấy từ đâu, lấy như thế nào?

Dự án sử dụng dữ liệu công khai của doanh nghiệp Mỹ. Ba repo người dùng đưa là tài liệu tham khảo kiến trúc/phương pháp; các hệ số và dữ liệu kết quả không lấy từ kết quả của những repo đó. Code trong thư mục này tải dữ liệu nguồn và tính lại.

## 1. Báo cáo tài chính và ngày công bố: SEC EDGAR

Mẫu có chủ đích mở rộng từ 10 lên 50 công ty thuộc bảy nhóm phân tích; danh sách cố định trong data/sample_universe.csv, mục tiêu 500 báo cáo năm tài chính 2016–2025. Độ phủ thực tế và lý do loại xem EXPANDED_RESULTS.md. BlackRock, Disney và Exxon Mobil nối đúng CIK tiền nhiệm; giữ CIK thực của từng filing. Đây không phải mẫu chọn ngẫu nhiên hoặc toàn thị trường.

Client Python requests gọi SEC Submissions API bằng CIK của từng công ty, ví dụ https://data.sec.gov/submissions/CIK0000320193.json cho Apple. API trả danh sách filing gần đây và tên các file lịch sử. Client tải cả những file lịch sử để lấy đủ mười năm; lọc form 10-K, giữ accession duy nhất và filing đầu tiên của cùng report period, loại 10-K/A khỏi baseline.

API cung cấp accession, ngày kết thúc kỳ, ngày nộp và timestamp acceptance. Từ accession và primaryDocument, chương trình dựng URL HTML trong SEC Archives rồi tải báo cáo gốc. Năm tài chính đọc DEI hoặc trang bìa; có xử lý lịch 52/53 tuần của JNJ. Chỉ giữ fiscal year 2016–2025 và filing_date không muộn hơn 27/09/2026. Báo cáo fiscal year 2025 nộp năm 2026 vẫn hợp lệ.

Requests khai báo User-Agent theo tên nhóm và email đã cấu hình riêng trong .env. Giới hạn khoảng 4 request/giây, có retry/backoff, dùng cache để không tải lại tài liệu đã có. Không cần SEC API key. Metadata của mỗi raw response ghi URL, thời điểm tải và SHA256.

BeautifulSoup đọc HTML, bỏ script/style và hidden XBRL header, giữ ranh giới block để tách Item 7 MD&A đến trước Item 7A hoặc Item 8. JPM/XOM có annual report nhúng nên có quy tắc tiêu đề riêng. Walmart 2016–2017 dẫn chiếu MD&A sang Exhibit 13; chương trình tải đúng exhibit cùng accession, giữ URL và checksum riêng trong audit. Không dùng đoạn dẫn chiếu ngắn thay cho MD&A.

Nguồn: https://www.sec.gov/search-filings/edgar-application-programming-interfaces

## 2. Từ điển tài chính: Loughran–McDonald

Tải CSV Master Dictionary từ liên kết chính thức của Notre Dame SRAF. File đang dùng có tên cột Word, Positive, Negative và Uncertainty. Chỉ membership > 0 được tính thuộc nhóm; không xem membership âm là từ đang thuộc nhóm.

Chuẩn hóa văn bản, tách token chữ cái, chuyển uppercase, giữ token tối thiểu hai ký tự. Không stemming và không bỏ stopwords khỏi mẫu số. Đếm số lượt positive, negative và uncertainty trong từng MD&A. Tone = (positive − negative)/total_words. Đây là phương pháp đếm từ, không phải mô hình hiểu đầy đủ ngữ cảnh hoặc FinBERT.

VADER word list được dùng làm từ điển tổng quát đối chứng, theo dấu điểm từ và cùng mẫu số với LM; không dùng compound score. Từ điển LM hiện hành áp dụng hồi cứu cho báo cáo cũ nên có giới hạn look-ahead nếu dùng kết quả cho giao dịch thời gian thực.

Nguồn: https://sraf.nd.edu/loughranmcdonald-master-dictionary/

## 3. Giá cổ phiếu và thị trường: Yahoo Finance

Python yfinance tải giá Close ngày của 50 ticker và chỉ số S&P 500, mã ^GSPC. Lệnh dùng auto_adjust=True: Close cổ phiếu đã được điều chỉnh. Khoảng tải bắt đầu trước filing sớm nhất 300 ngày lịch và kết thúc sau filing muộn nhất 35 ngày để có đủ các phiên estimation/event.

Lịch giao dịch XNYS căn chuỗi giá vào phiên thực, xử lý ngày nghỉ và đóng cửa sớm. Return đơn = P_t/P_(t−1) − 1; không fill forward khi thiếu giá. Ước lượng alpha và beta trên [-120,-20] phiên, yêu cầu ít nhất 80 cặp return cổ phiếu–thị trường. AR = return cổ phiếu − (alpha + beta × return thị trường). Cộng AR thành CAR cho [-1,+1], [-3,+3], [-5,+5]. Có ba quy tắc căn sự kiện: ngày filing, phiên tiếp theo, và acceptance time.

Giá điều chỉnh cổ phiếu và S&P 500 price index có khác biệt xử lý cổ tức. Yahoo là nguồn công khai phục vụ bài tập, không phải CRSP; báo cáo nêu rõ giới hạn này.

## 4. Dữ liệu kiểm tra tin earnings

Từ metadata SEC đã tải, tìm các filing 8-K có Item 2.02 gần ngày 10-K. Gắn cờ theo cửa sổ baseline [-1,+1], chạy đối chứng bỏ các event có cờ. Cách này không bao phủ mọi earnings press release hay mọi tin ngoài SEC.

## 5. Xem dữ liệu thực tế trong thư mục

| File/thư mục | Nội dung |
|---|---|
| config.json | Mười ticker/CIK, khoảng năm, benchmark và cửa sổ |
| tonecar/data.py | Code tải SEC, từ điển và giá |
| tonecar/text.py | Code trích xuất và đếm từ |
| tonecar/event.py | Code tính AR/CAR |
| tonecar/pipeline.py | Ghép dữ liệu và hồi quy |
| data/raw/sec/ | Raw SEC response và JSON provenance |
| data/raw/market/ | Giá ngày đã tải, trước khi tính return |
| data/external/lm.csv | Từ điển LM nguồn |
| data/filings_manifest.csv | Danh sách filing, accession và URL nguồn |
| data/interim/mda/ | MD&A đã làm sạch cho từng filing |
| data/extraction_audit.csv | Độ dài, đầu/cuối, cách trích xuất và nguồn exhibit |
| data/tone_panel.csv | Số từ và tone đã tính |
| outputs/real/same/car_panel.csv | Panel thực nghiệm baseline |
| outputs/real/same/event_ar.csv | AR từng phiên để tái cộng CAR |
| outputs/real/same/regressions.csv | Hệ số, SE, p-value, CI và N |
| notebooks/final_analysis.ipynb | Tái đếm từ, cộng AR và fit lại baseline offline |

Thư mục outputs/demo chứa dữ liệu mô phỏng để kiểm tra code, được ghi nhãn riêng. Kết luận nghiên cứu và dashboard dùng outputs/real; không lấy dữ liệu mô phỏng thay dữ liệu thật.

## 6. Mẫu mở rộng và biến bổ sung

Delta_tone = tone năm hiện tại − tone năm liền trước của cùng công ty, chỉ cho cặp fiscal year liên tiếp. Không nối qua năm thiếu và không gán năm đầu bằng 0.

Assets, Liabilities và NetIncomeLoss/ProfitLoss lấy từ SEC Company Facts. Ghép đúng accession/kỳ và đơn vị USD; lợi nhuận chỉ dùng kỳ năm. Quy mô là ln(tổng tài sản), liabilities_assets là tổng liabilities/tài sản, ROA là lợi nhuận/tài sản cuối năm. Missing/ambiguous facts giữ thiếu. Mô hình controls có N complete-case riêng. Xem data/fundamentals_panel.csv để kiểm tra tag, kỳ và nguồn.

Báo cáo gốc của mẫu 100 giữ trong archive kết quả; dữ liệu raw vẫn nằm trong data/raw/sec. FinBERT và earnings surprise chưa được đưa vào kết quả mới.
