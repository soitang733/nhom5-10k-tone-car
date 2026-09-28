# Giọng điệu báo cáo tài chính và phản ứng thị trường

Nhóm 5 · Đề án 05 Fintech · Báo cáo hoàn chỉnh · Dữ liệu SEC 10-K FY2016–FY2025 · Khóa dữ liệu 28/09/2026

## Tóm tắt nghiên cứu

Nghiên cứu dùng chính xác 100 công ty do người dùng cung cấp trong `companies_100.csv`, mỗi công ty mười báo cáo 10-K gốc. Tải và lưu 1.000 tài liệu SEC, trích phần Management's Discussion and Analysis (MD&A), tính tone bằng từ điển Loughran–McDonald (LM), ghép ngày nộp báo cáo với giá điều chỉnh và ước lượng CAR. Mẫu phân tích cuối gồm 1000 báo cáo của 100 công ty. Mô hình nền CAR [-1,+1] ~ tone có hệ số -0.40288, sai số chuẩn HC3 0.22338, p=0.07130, CI 95% [-0.84070; 0.03494]. Kết quả chưa đủ bằng chứng thống kê ở ngưỡng 5% trong baseline. Thiết kế đo mối liên hệ quan sát được; không xác định tác động nhân quả.

## Câu hỏi, giả thuyết và đóng góp

Câu hỏi chính: tỷ lệ từ mang sắc thái tích cực và tiêu cực trong MD&A có liên hệ với lợi suất bất thường của cổ phiếu quanh ngày công bố 10-K hay không? H1: tone cao hơn đi cùng CAR cao hơn. H2: tỷ lệ từ tiêu cực cao hơn đi cùng CAR thấp hơn. H3: tỷ lệ từ bất định có liên hệ hai phía với CAR. Cửa sổ chính [-1,+1] phiên; [-3,+3] và [-5,+5] là đối chứng. Đóng góp thực hành là chuỗi dữ liệu kiểm toán được từ URL SEC và HTML gốc đến văn bản đã trích, điểm tone từng doanh nghiệp–năm, AR từng phiên, CAR và hồi quy.

## Tổng quan tài liệu và phạm vi tái lập

Loughran và McDonald (2011) đặt vấn đề từ điển ngôn ngữ tổng quát dễ gán sai sắc thái cho từ trong tài chính; nghiên cứu này dùng nhóm Positive, Negative và Uncertainty của từ điển LM. Tetlock (2007) gợi ý mối quan hệ giữa ngôn ngữ và thị trường trong bối cảnh tin tức. Li (2008) nghiên cứu tính dễ đọc của báo cáo, là một cấu phần khác tone. MacKinlay (1997) là khuôn khổ event study để xây AR và CAR. Nghiên cứu này là bản triển khai ứng dụng với SEC, dữ liệu giá công khai và 100 công ty có chủ đích, không tuyên bố tái lập dữ liệu CRSP hay mọi bảng trong LM (2011). Ba repo tham khảo trong tài liệu chỉ là nguồn gợi ý cách tổ chức code, không là nguồn dữ liệu kết quả.

## Thiết kế mẫu và truy nguyên nguồn

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

## Thống kê mô tả

Các tỷ lệ và lợi suất ở dạng thập phân; nhân 100 khi diễn giải điểm phần trăm.

| Biến | count | mean | std | min | max |
| --- | --- | --- | --- | --- | --- |
| word_count | 1000.00000 | 11725.62500 | 5846.65913 | 2001.00000 | 41151.00000 |
| tone | 1000.00000 | -0.00564 | 0.00545 | -0.03272 | 0.01375 |
| negative_rate | 1000.00000 | 0.01186 | 0.00520 | 0.00235 | 0.03882 |
| uncertainty_rate | 1000.00000 | 0.01398 | 0.00328 | 0.00716 | 0.02525 |
| car_-1_1 | 1000.00000 | 0.00421 | 0.04150 | -0.14720 | 0.40371 |
| car_-3_3 | 1000.00000 | 0.00456 | 0.05359 | -0.31930 | 0.35063 |
| car_-5_5 | 1000.00000 | 0.00574 | 0.06544 | -0.34394 | 0.36285 |


## Kết quả chính và độ nhạy

| outcome | specification | coefficient | se_HC3 | p_value | ci_low | ci_high | n | p_holm_all_reported_tests |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| car_-1_1 | tone | -0.40288 | 0.22338 | 0.07130 | -0.84070 | 0.03494 | 1000.00000 | 1.00000 |
| car_-1_1 | tone + C(fiscal_year) | -0.43391 | 0.22513 | 0.05393 | -0.87515 | 0.00734 | 1000.00000 | 1.00000 |
| car_-1_1 | tone + C(fiscal_year) + C(ticker) | -0.59605 | 0.63379 | 0.34698 | -1.83825 | 0.64615 | 1000.00000 | 1.00000 |
| car_-1_1 | tone + log_assets + liabilities_assets + roa + C(fiscal_year) | -0.74541 | 0.27793 | 0.00732 | -1.29015 | -0.20068 | 794.00000 | 0.32199 |
| car_-3_3 | tone | -0.56458 | 0.28384 | 0.04669 | -1.12089 | -0.00827 | 1000.00000 | 1.00000 |
| car_-3_3 | tone + C(fiscal_year) | -0.57236 | 0.28326 | 0.04332 | -1.12754 | -0.01717 | 1000.00000 | 1.00000 |
| car_-3_3 | tone + C(fiscal_year) + C(ticker) | -0.31909 | 0.90942 | 0.72568 | -2.10152 | 1.46334 | 1000.00000 | 1.00000 |
| car_-3_3 | tone + log_assets + liabilities_assets + roa + C(fiscal_year) | -0.88857 | 0.33806 | 0.00858 | -1.55116 | -0.22599 | 794.00000 | 0.36884 |
| car_-5_5 | tone | -0.56145 | 0.35450 | 0.11324 | -1.25626 | 0.13335 | 1000.00000 | 1.00000 |
| car_-5_5 | tone + C(fiscal_year) | -0.59777 | 0.35373 | 0.09104 | -1.29106 | 0.09551 | 1000.00000 | 1.00000 |
| car_-5_5 | tone + C(fiscal_year) + C(ticker) | -1.02485 | 1.13283 | 0.36563 | -3.24515 | 1.19546 | 1000.00000 | 1.00000 |
| car_-5_5 | tone + log_assets + liabilities_assets + roa + C(fiscal_year) | -0.90634 | 0.40629 | 0.02570 | -1.70266 | -0.11002 | 794.00000 | 0.97651 |
| mar_-1_1 | tone | -0.32037 | 0.22715 | 0.15842 | -0.76557 | 0.12483 | 1000.00000 | 1.00000 |
| mar_-1_1 | tone + C(fiscal_year) | -0.34000 | 0.22915 | 0.13787 | -0.78912 | 0.10912 | 1000.00000 | 1.00000 |
| mar_-1_1 | tone + C(fiscal_year) + C(ticker) | -0.51905 | 0.64256 | 0.41921 | -1.77844 | 0.74034 | 1000.00000 | 1.00000 |
| mar_-1_1 | tone + log_assets + liabilities_assets + roa + C(fiscal_year) | -0.64789 | 0.28513 | 0.02307 | -1.20673 | -0.08905 | 794.00000 | 0.92281 |


Ba cách căn ngày cho cùng mô hình nền:

| Căn ngày | N | Hệ số | p HC3 | CI thấp | CI cao |
| --- | --- | --- | --- | --- | --- |
| same | 1000 | -0.40288 | 0.07130 | -0.84070 | 0.03494 |
| next | 1000 | -0.21843 | 0.30636 | -0.63697 | 0.20011 |
| acceptance | 1000 | -0.24790 | 0.25581 | -0.67548 | 0.17967 |


Hệ số b=-0.40288 có nghĩa tăng tone 0,01 đi cùng CAR thay đổi xấp xỉ -0.40288 điểm phần trăm trong mẫu, không phải dự báo giao dịch. Kiểm định cluster theo doanh nghiệp cho b=-0.40288, SE=0.23655, p=0.09167, CI [-0.87224; 0.06648]. 229 báo cáo có 8-K Item 2.02 gần cửa sổ sự kiện; bảng `excluding_8k202.csv` cho ước lượng sau loại chúng. Screening này không nhận diện mọi tin tức cùng ngày. Phép loại từng doanh nghiệp và 18 kiểm định độ nhạy nằm trong output để người đọc đối chiếu dấu, độ lớn và khoảng tin cậy.

## Diễn giải kinh tế và giới hạn

Tone mô tả ngôn ngữ công bố, không đo trực tiếp chất lượng doanh nghiệp. Doanh nghiệp có nhiều rủi ro phải mô tả có thể dùng nhiều từ tiêu cực dù hoạt động tốt. Nhà đầu tư và ngân hàng có thể dùng tone như tín hiệu ưu tiên đọc, kết hợp dòng tiền, đòn bẩy và bối cảnh công bố. Không dùng kết quả quan sát này để khẳng định tone gây biến động giá hay tạo chiến lược giao dịch có lãi. Các nguồn nhiễu gồm earnings release cùng ngày, lựa chọn thời điểm công bố, thay đổi chế độ thị trường, benchmark là chỉ số giá trong khi cổ phiếu dùng adjusted price, thay đổi nghĩa của từ và văn bản bảng. Số công ty đủ 10 năm tạo survivorship bias. Audit cấu trúc có trợ giúp AI và hash nguồn, chưa có gán nhãn thủ công toàn văn hay kiểm tra CRSP độc lập.

## Tính tái lập và trách nhiệm sử dụng AI

Code đọc `config.json`, tải SEC với User-Agent nhóm, cache raw kèm metadata, tải từ điển LM chính thức, giá và companyfacts, sau đó tính lại toàn bộ. Không có dữ liệu giả trong kết quả thực nghiệm. Các URL SEC, accession, SHA-256, văn bản trích, lỗi bị loại, bảng giá và script đều được giữ để tái kiểm. AI hỗ trợ viết code, chuẩn hóa và rà soát ranh giới; số liệu đến từ nguồn đã lưu và được tính bằng Python. Người trình bày cần tự giải thích dữ liệu, phương trình, cờ 8-K, CI, Holm và giới hạn khi bảo vệ.

## Tài liệu tham khảo

Loughran, T. & McDonald, B. (2011), “When Is a Liability Not a Liability? Textual Analysis, Dictionaries, and 10-Ks”, Journal of Finance. [Notre Dame SRAF](https://sraf.nd.edu/loughranmcdonald-master-dictionary/). Tetlock, P. (2007), “Giving Content to Investor Sentiment”, Journal of Finance. Li, F. (2008), “Annual Report Readability, Current Earnings, and Earnings Persistence”, Journal of Accounting and Economics. MacKinlay, A. (1997), “Event Studies in Economics and Finance”, Journal of Economic Literature. Dữ liệu: [SEC EDGAR](https://www.sec.gov/edgar/search/), [SEC API](https://www.sec.gov/search-filings/edgar-application-programming-interfaces), [XNAS/XNYS calendar package](https://github.com/gerrymanoim/exchange_calendars), [Yahoo Finance](https://finance.yahoo.com/).
