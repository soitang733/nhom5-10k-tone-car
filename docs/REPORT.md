# Giọng điệu báo cáo tài chính và phản ứng thị trường

Nhóm 5 · Đề án 05 Fintech · Mẫu SEC 10-K 2016–2025 · Bản nghiên cứu hoàn chỉnh với code, dữ liệu đã xử lý, notebook và giao diện local.

## Tóm tắt

Nghiên cứu chuyển phần MD&A trong báo cáo 10-K thành các chỉ số giọng điệu và kiểm định mối liên hệ với lợi suất bất thường tích lũy quanh ngày filing. Mẫu mục tiêu 500 báo cáo của 50 doanh nghiệp; mẫu phân tích 500 filings của 50 doanh nghiệp. Baseline CAR [-1,+1] ~ Tone có hệ số -0.05863, SE HC3 0.28599, p = 0.83756, CI 95% [-0.61916; 0.50189]. Kết quả chưa cung cấp bằng chứng thống kê rõ ràng. Thiết kế kiểm định mối liên hệ, không xác định nhân quả.

## Câu hỏi và giả thuyết nghiên cứu

Câu hỏi chính: giọng điệu tài chính trong MD&A có mang thông tin liên quan phản ứng thị trường quanh ngày doanh nghiệp nộp báo cáo 10-K hay không? H1 dự kiến tone cao hơn đi cùng CAR cao hơn. H2 dự kiến tỷ lệ từ tiêu cực cao hơn đi cùng CAR thấp hơn. H3 kiểm định hai phía mối liên hệ giữa tỷ lệ từ bất định và CAR. Cửa sổ chính là [-1,+1]; [-3,+3] và [-5,+5] là kiểm tra độ nhạy.

## Tổng quan tài liệu

Loughran và McDonald (2011) cho thấy lựa chọn từ điển phải phù hợp ngữ cảnh tài chính; các thuật ngữ kế toán có thể bị từ điển tổng quát gán sắc thái không thích hợp. Nghiên cứu này dùng tỷ lệ từ của LM thay vì xem mọi từ mang sắc thái tiêu cực trong ngôn ngữ hàng ngày là tin xấu tài chính.

Tetlock (2007) đặt nền tảng cho nghiên cứu nội dung văn bản và thị trường, nhưng nguồn truyền thông của bài đó khác báo cáo 10-K. Li (2008) nghiên cứu readability và earnings; ở đây readability không được thay thế bằng sentiment. Bodnaruk, Loughran và McDonald (2015) cho thấy văn bản 10-K còn có ứng dụng đo ràng buộc tài chính. Loughran và McDonald (2016) tổng hợp các phương pháp textual analysis trong kế toán và tài chính. MacKinlay (1997) cung cấp khuôn khổ event study dùng để tách lợi suất thực tế khỏi lợi suất kỳ vọng. Đây là adaptation mẫu nhỏ; không tuyên bố tái lập đầy đủ CRSP/Fama–MacBeth của LM (2011).

## Dữ liệu và lựa chọn mẫu

Mẫu có chủ đích mở rộng từ 10 lên 50 công ty; mục tiêu 500 firm-years, thuộc bảy nhóm phân tích trong data/sample_universe.csv. Danh sách được khóa trước kết quả mới; không lựa chọn công ty theo p-value hoặc dấu hệ số. Lấy candidates có report dates 2016–2026, sau đó giữ năm tài chính 2016–2025 và ngày filing không muộn hơn 27/09/2026; năm tài chính lấy từ dei:DocumentFiscalYearFocus hoặc trang bìa. Đây không phải danh mục S&P 500 lịch sử hoặc mẫu ngẫu nhiên; có selection/survivorship bias. Snapshot 100 báo cáo được giữ để đối chiếu trong outputs/archive/baseline_100.

SEC Submissions API cung cấp form, accession, report date, filing date và acceptance time. Chỉ lấy 10-K gốc, giữ filing đầu tiên của cùng report period, lưu candidates và raw response kèm URL, SHA256 và thời gian tải. Client khai báo User-Agent thật, cache và giới hạn 4 request/giây. Dictionary LM 1993–2025 được tải qua link chính thức của Notre Dame SRAF; membership category là giá trị > 0, bỏ các membership đã bị loại (giá trị âm).

Giá Yahoo được điều chỉnh, tải theo khoảng filing thực tế cùng buffer cho estimation; benchmark S&P 500 price index (^GSPC), calendar XNYS. Giá raw giữ nguyên, pct_change không fill forward khi thiếu giá. Không có filing nào bị loại bởi parser hoặc market coverage trong lần chạy này.

## Làm sạch và kiểm tra văn bản

Parser giữ cấu trúc block HTML, bỏ script/style/hidden XBRL header; không xóa mọi table vì một số filing dùng bảng bố cục chứa văn bản. Item 7 kết thúc trước Item 7A hoặc Item 8 với đúng tên mục. Nhận diện ở đầu block tránh nhầm câu tham chiếu trong nội dung và mục lục. WMT 2016–2017 đọc Exhibit 13 được dẫn chiếu chính thức và kết thúc trước Consolidated Statements of Income. JPM/XOM có quy tắc riêng cho MD&A annual report nhúng trong cùng primary document, nhận diện substantive opening và financial-report closing thay vì running header.

Audit lưu offsets, số candidate, độ dài, phương pháp extraction, 300 ký tự đầu/cuối và provenance cho toàn bộ mẫu. Review cấu trúc và snippets đã hoàn tất cho các records được giữ. Đây là audit có trợ giúp AI, không phải nhãn sentiment do con người gán cho từng câu hay xác nhận tuyệt đối parser không sai. Manifest, audit và raw filing cho phép kiểm tra lại mỗi quan sát.

## Phương pháp định lượng

Token chữ cái được chuẩn hóa NFKC và uppercase, giữ token dài ít nhất 2 ký tự, không stemming hoặc bỏ stopwords khỏi mẫu số. Tone = (Positive − Negative)/Total words; NegativeRate = Negative/Total words; UncertaintyRate = Uncertainty/Total words. Từ điển có inflections nên không tự lemmatize.

Lợi suất đơn Ri,t = Pi,t/Pi,t−1 − 1. Market model Ri,t = alpha + beta Rm,t + epsilon ước lượng trên [-120,-20], gồm 101 phiên, yêu cầu ít nhất 80 cặp hợp lệ. ARi,t = Ri,t − (alpha_hat + beta_hat Rm,t). CAR[a,b] là tổng AR gồm hai đầu mút. Trục ngày luôn là trading sessions; thiếu return trong event window thì loại event, không nén ngày.

Baseline căn ngày filing cùng phiên giao dịch; nếu cuối tuần/nghỉ lễ thì phiên kế tiếp. Đối chứng luôn phiên tiếp theo và căn acceptance time so với giờ đóng cửa thực của XNYS, gồm phiên đóng sớm. Hồi quy OLS HC3 gồm tone đơn, thêm hiệu ứng năm, thêm hiệu ứng năm/công ty, negativity/uncertainty, và generic word list. Thêm market-adjusted return, loại event earnings 8-K, và cluster SE theo công ty trong giao diện khám phá.

Breusch–Pagan và condition number được xuất để kiểm tra phương sai thay đổi và ổn định số. CI và p-value HC3 không giải quyết nội sinh hay mọi phụ thuộc trong công ty. Holm p-value hiệu chỉnh các hệ số được báo cáo trong mỗi alignment, không hiệu chỉnh toàn bộ các lựa chọn giao diện. Số công ty nhỏ làm cluster inference yếu; kết quả cluster phải được coi là đối chứng.

## Thống kê mô tả

Tất cả tỷ lệ và lợi suất ở dạng thập phân trong bảng dưới; nhân 100 khi trình bày phần trăm.

| variable | count | mean | std | min | max |
|---|---|---|---|---|---|
| word_count | 500.00000 | 16007.68200 | 12545.35096 | 2001.00000 | 69708.00000 |
| tone | 500.00000 | -0.00550 | 0.00582 | -0.02293 | 0.01242 |
| delta_tone | 450.00000 | 0.00020 | 0.00247 | -0.01626 | 0.01573 |
| negative_rate | 500.00000 | 0.01242 | 0.00458 | 0.00143 | 0.02971 |
| uncertainty_rate | 500.00000 | 0.01542 | 0.00503 | 0.00415 | 0.03033 |
| log_assets | 500.00000 | 25.65301 | 1.27407 | 21.92353 | 29.11827 |
| liabilities_assets | 441.00000 | 0.68190 | 0.18693 | 0.16992 | 1.06082 |
| roa | 500.00000 | 0.08186 | 0.07855 | -0.24787 | 0.65304 |
| car_-1_1 | 500.00000 | -0.00112 | 0.03309 | -0.26365 | 0.15161 |
| car_-3_3 | 500.00000 | 0.00040 | 0.04322 | -0.16049 | 0.20283 |
| car_-5_5 | 500.00000 | 0.00115 | 0.05484 | -0.18046 | 0.19789 |


## Kết quả hồi quy

| outcome | specification | coefficient | se_HC3 | p_value | ci_low | ci_high | n | p_holm_all_reported_tests |
|---|---|---|---|---|---|---|---|---|
| car_-1_1 | tone | -0.05863 | 0.28599 | 0.83756 | -0.61916 | 0.50189 | 500.00000 | 1.00000 |
| car_-1_1 | tone + C(fiscal_year) | -0.04020 | 0.28789 | 0.88893 | -0.60445 | 0.52404 | 500.00000 | 1.00000 |
| car_-1_1 | tone + C(fiscal_year) + C(ticker) | 1.31728 | 1.62175 | 0.41664 | -1.86129 | 4.49585 | 500.00000 | 1.00000 |
| car_-1_1 | tone + log_assets + liabilities_assets + roa + C(fiscal_year) | -0.29220 | 0.45828 | 0.52373 | -1.19041 | 0.60601 | 441.00000 | 1.00000 |
| car_-3_3 | tone | 0.02310 | 0.39806 | 0.95373 | -0.75708 | 0.80328 | 500.00000 | 1.00000 |
| car_-3_3 | tone + C(fiscal_year) | 0.07627 | 0.39694 | 0.84763 | -0.70172 | 0.85426 | 500.00000 | 1.00000 |
| car_-3_3 | tone + C(fiscal_year) + C(ticker) | 0.01632 | 1.20298 | 0.98918 | -2.34148 | 2.37411 | 500.00000 | 1.00000 |
| car_-3_3 | tone + log_assets + liabilities_assets + roa + C(fiscal_year) | -0.55383 | 0.56589 | 0.32774 | -1.66296 | 0.55530 | 441.00000 | 1.00000 |
| car_-5_5 | tone | 0.04761 | 0.49098 | 0.92275 | -0.91469 | 1.00991 | 500.00000 | 1.00000 |
| car_-5_5 | tone + C(fiscal_year) | 0.14183 | 0.48047 | 0.76785 | -0.79988 | 1.08354 | 500.00000 | 1.00000 |
| car_-5_5 | tone + C(fiscal_year) + C(ticker) | 0.43345 | 1.26281 | 0.73142 | -2.04162 | 2.90851 | 500.00000 | 1.00000 |
| car_-5_5 | tone + log_assets + liabilities_assets + roa + C(fiscal_year) | -0.69611 | 0.70440 | 0.32304 | -2.07670 | 0.68449 | 441.00000 | 1.00000 |
| mar_-1_1 | tone | -0.15308 | 0.27651 | 0.57985 | -0.69503 | 0.38888 | 500.00000 | 1.00000 |
| mar_-1_1 | tone + C(fiscal_year) | -0.13719 | 0.27809 | 0.62178 | -0.68223 | 0.40785 | 500.00000 | 1.00000 |
| mar_-1_1 | tone + C(fiscal_year) + C(ticker) | 1.17206 | 1.45981 | 0.42204 | -1.68913 | 4.03324 | 500.00000 | 1.00000 |
| mar_-1_1 | tone + log_assets + liabilities_assets + roa + C(fiscal_year) | -0.42165 | 0.44180 | 0.33988 | -1.28756 | 0.44426 | 441.00000 | 1.00000 |


Baseline có R² 0.00011. Với hệ số b = -0.05863, tăng tone 0.01 liên hệ với thay đổi CAR khoảng -0.05863 điểm phần trăm. CI hệ số tương ứng với thay đổi [-0.61916; 0.50189] điểm phần trăm cho cùng mức tăng tone. Chưa đủ bằng chứng để bác bỏ giả thuyết hệ số tone bằng 0 trong baseline. Đánh giá đồng thời độ lớn, CI, mẫu và độ nhạy; không chọn mô hình theo p-value nhỏ nhất.

## Đối chứng từ điển tổng quát

Word list VADER được dùng theo signs positive/negative, với cùng mẫu số total tokens; không dùng compound score, rules negation hoặc gọi VADER là Harvard General Inquirer. Bảng sau liệt kê các từ VADER gán negative trong khi LM không gán negative và số lượt trong MD&A. Khác biệt lexicon không chứng minh mọi câu chứa từ đó đều trung tính; cần đọc ngữ cảnh. Giao diện cho phép tìm và đọc câu trong filing gốc.

| generic_negative_not_lm_negative | occurrences |
|---|---|
| RISK | 36914 |
| DEBT | 16394 |
| LOWER | 13187 |
| LIABILITIES | 9054 |
| RISKS | 6862 |
| CHARGES | 6138 |
| DEMAND | 4957 |
| GROSS | 4554 |
| NO | 4383 |
| LIABILITY | 3874 |


## Robustness và tin cùng ngày

| alignment | coefficient | p_value | N |
|---|---|---|---|
| same | -0.05863 | 0.83756 | 500 |
| next | 0.02029 | 0.94912 | 500 |
| acceptance | 0.04218 | 0.88773 | 500 |


Screening SEC metadata cho 8-K có Item 2.02 trong cửa sổ baseline [-1,+1] gắn cờ 71 events. Mẫu loại các events được gắn cờ còn 429 quan sát; hệ số tone 0.00117, p = 0.99510. Screening không bao phủ mọi earnings press release, tin báo chí, 8-K khác hoặc kỳ vọng thị trường. Đây là kiểm tra confounding có thể tái lập, không khẳng định đã loại mọi sự kiện nhiễu.

Đối chứng cluster theo 50 công ty cho baseline có SE 0.18519, p = 0.75289, CI [-0.43079; 0.31353]. Dùng finite-sample correction và t inference, nhưng ít clusters vẫn là hạn chế. Leave-one-firm-out ước lượng lại sau khi bỏ từng công ty để đánh giá phụ thuộc vào một doanh nghiệp; bảng được lưu ở leave_one_firm_out.csv, không dùng để lựa chọn mẫu có p-value đẹp nhất.

## Diễn giải kinh tế và tài chính

Tone là đặc điểm của ngôn ngữ công bố, không phải phép đo trực tiếp chất lượng doanh nghiệp. Một doanh nghiệp phải mô tả nhiều rủi ro có thể có tone tiêu cực dù kết quả kinh doanh tốt. Nhà đầu tư có thể sử dụng chỉ số này để chọn phần cần đọc kỹ, kết hợp báo cáo định lượng và thời điểm thông tin đã công bố. Ngân hàng có thể dùng như tín hiệu bổ sung trong thẩm định, nhưng không thay thế dòng tiền, đòn bẩy và khả năng trả nợ.

Kết quả không cung cấp cơ sở tự động giao dịch hoặc kết luận tone gây biến động giá. Nếu hệ số không rõ, khả năng thị trường đã tiếp nhận thông tin qua earnings release, sai số đo tone, số quan sát ít và khác biệt công ty đều là các giải thích hợp lý cần nghiên cứu tiếp.

## Giới hạn nghiên cứu

Mẫu doanh nghiệp lớn có selection/survivorship bias. Dictionary 2025 áp dụng báo cáo cũ có look-ahead trong bối cảnh đầu tư thời gian thực. Parser heuristic và page/table artifacts ảnh hưởng mẫu số. Yahoo không thay CRSP; total-return cổ phiếu so với price-index benchmark có khác biệt dividend treatment. Event windows chồng nhau giữa doanh nghiệp và ít clusters gây khó suy luận. Thiếu earnings surprise và human sentence labels làm nghiên cứu mang tính thăm dò. Các giới hạn là phạm vi khoa học của kết quả, không được che bằng dashboard.

## Kết luận

Pipeline hoàn chỉnh lượng hóa MD&A thành biến giọng điệu, truy nguyên từng filing, ước lượng AR/CAR và kiểm định các đặc tả/đối chứng. Kết quả baseline chưa cung cấp bằng chứng thống kê rõ ràng. Đóng góp chính của bài là quy trình tái lập và đánh giá đúng ngữ cảnh từ điển, cùng cách diễn giải kết quả có tính đến bất định. Mở rộng hợp lý gồm sample lớn hơn, benchmark total return và CRSP, controls earnings surprise, kiểm tra thời gian thực, rồi so sánh FinBERT sau baseline.

## Tái lập và liêm chính học thuật

Python 3.12, requirements-lock.txt, notebook đã thực thi, unit/integration tests và lệnh chạy trong README. Demo synthetic được ghi nhãn và không được đưa vào kết quả thật. Nhật ký AI_USAGE_LOG ghi code, kiểm thử, audit có trợ giúp AI và phần diễn giải được AI hỗ trợ. Không nhận kết quả của ba repo tham khảo là kết quả Nhóm 5. Giữ email cấu hình và .env riêng, không đưa vào tài liệu công khai.

## Tài liệu tham khảo

1. Loughran, T., & McDonald, B. (2011). When Is a Liability Not a Liability? Textual Analysis, Dictionaries, and 10-Ks. Journal of Finance, 66(1), 35–65. https://ssrn.com/abstract=1331573
2. Tetlock, P. C. (2007). Giving Content to Investor Sentiment: The Role of Media in the Stock Market. Journal of Finance, 62(3), 1139–1168. https://onlinelibrary.wiley.com/doi/10.1111/j.1540-6261.2007.01232.x
3. Li, F. (2008). Annual report readability, current earnings, and earnings persistence. Journal of Accounting and Economics, 45(2–3), 221–247. https://doi.org/10.1016/j.jacceco.2008.02.003
4. Bodnaruk, A., Loughran, T., & McDonald, B. (2015). Using 10-K Text to Gauge Financial Constraints. Journal of Financial and Quantitative Analysis, 50(4), 623–646. https://ssrn.com/abstract=2331544
5. Loughran, T., & McDonald, B. (2016). Textual Analysis in Accounting and Finance: A Survey. Journal of Accounting Research, 54(4), 1187–1230. https://ssrn.com/abstract=2504147
6. MacKinlay, A. C. (1997). Event Studies in Economics and Finance. Journal of Economic Literature, 35(1), 13–39. https://www.jstor.org/stable/2729691

Nguồn dữ liệu: SEC EDGAR API https://www.sec.gov/search-filings/edgar-application-programming-interfaces và LM dictionary https://sraf.nd.edu/loughranmcdonald-master-dictionary/ . Code tham khảo, thư viện và ngày tra cứu được ghi đầy đủ trong REFERENCES.md.

## Phụ lục A. Độ phủ của mẫu mười năm

Khoảng nghiên cứu là năm tài chính 2016–2025, đủ mười năm. Ngày khóa dữ liệu là 27/09/2026. Một báo cáo năm tài chính 2025 có thể được nộp năm 2026; đây là quan sát hợp lệ vì biến năm tài chính và biến ngày sự kiện phục vụ hai mục đích khác nhau. Giữ khoảng mười năm FY2016–2025 nhất quán; FY2026 nằm ngoài mẫu kể cả với doanh nghiệp đã hoàn tất năm tài chính đó. Mỗi ô dưới đây là số filing thực sự có trong panel baseline, không phải số dự kiến.

| ticker | 2016 | 2017 | 2018 | 2019 | 2020 | 2021 | 2022 | 2023 | 2024 | 2025 |
|---|---|---|---|---|---|---|---|---|---|---|
| AAPL | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 |
| ABBV | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 |
| ABT | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 |
| ADBE | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 |
| AMD | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 |
| AMGN | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 |
| AMZN | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 |
| AXP | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 |
| BAC | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 |
| BLK | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 |
| BMY | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 |
| C | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 |
| CAT | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 |
| COP | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 |
| COST | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 |
| CRM | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 |
| CSCO | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 |
| CVX | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 |
| DIS | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 |
| DUK | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 |
| GOOGL | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 |
| GS | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 |
| HD | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 |
| HON | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 |
| IBM | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 |
| INTC | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 |
| JNJ | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 |
| JPM | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 |
| KO | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 |
| LMT | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 |
| MCD | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 |
| MRK | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 |
| MS | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 |
| MSFT | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 |
| NEE | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 |
| NKE | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 |
| NVDA | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 |
| ORCL | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 |
| PEP | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 |
| PFE | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 |
| PG | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 |
| QCOM | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 |
| SLB | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 |
| TXN | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 |
| UNH | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 |
| UNP | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 |
| UPS | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 |
| WFC | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 |
| WMT | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 |
| XOM | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 |


| fiscal_year | N | tone_mean | tone_sd | CAR_mean |
|---|---|---|---|---|
| 2016 | 50 | -0.006922 | 0.005547 | 0.001716 |
| 2017 | 50 | -0.006022 | 0.005431 | 0.001694 |
| 2018 | 50 | -0.005286 | 0.005544 | -0.002767 |
| 2019 | 50 | -0.005333 | 0.005887 | 0.006424 |
| 2020 | 50 | -0.005987 | 0.005802 | -0.000153 |
| 2021 | 50 | -0.004629 | 0.005613 | 0.003438 |
| 2022 | 50 | -0.005326 | 0.006183 | -0.005143 |
| 2023 | 50 | -0.005275 | 0.006326 | -0.002443 |
| 2024 | 50 | -0.00509 | 0.006081 | -0.003388 |
| 2025 | 50 | -0.005143 | 0.005943 | -0.010539 |


Bảng theo năm giúp nhận diện thay đổi thành phần mẫu và bối cảnh thị trường. Trung bình CAR theo năm là thống kê mô tả của các sự kiện được chọn, không phải lợi suất năm của danh mục. Chênh lệch giữa hai năm có thể xuất phát từ timing filing, mức biến động thị trường, cách diễn đạt hoặc tin kinh doanh. Mười năm quan sát làm tăng chiều thời gian nhưng có 50 công ty; số công ty độc lập không tăng tương ứng với số báo cáo. Vì vậy, không được diễn giải 500 báo cáo như 500 doanh nghiệp độc lập.

Một doanh nghiệp có thể có năm tài chính kết thúc tháng 6, tháng 9 hoặc đầu tháng 1. Việc chỉ cắt report_date ở ngày 31/12 dễ loại sai hoặc gắn nhầm năm. Pipeline mở rộng khoảng candidates thêm một năm, đọc DocumentFiscalYearFocus, rồi mới áp dụng tiêu chuẩn năm tài chính. Các trường hợp không tìm được DEI được đánh dấu fallback trong manifest, để người đọc có thể kiểm tra nhãn năm từ trang bìa. Giữ accession làm khóa giúp phân biệt báo cáo khi ticker hoặc cách đặt tên file thay đổi.

## Phụ lục B. Cách đọc các bảng kết quả

Hệ số tone đo mức thay đổi CAR dạng thập phân khi tone tăng một đơn vị. Vì tone thường có độ lớn nhỏ, tăng một đơn vị không phải kịch bản kinh tế hợp lý. Báo cáo dùng mức tăng 0,01 và một độ lệch chuẩn. Với độ lệch chuẩn tone bằng 0.005822, hệ số baseline -0.058633 tương ứng CAR thay đổi -0.0341 điểm phần trăm khi tone tăng một độ lệch chuẩn. Khoảng tin cậy tương ứng là [-0.3605; 0.2922] điểm phần trăm. Đây là thay đổi dự báo có điều kiện trong đặc tả đơn, không phải lợi nhuận có thể thực hiện bằng chiến lược giao dịch.

P-value trả lời mức tương thích giữa dữ liệu và giả thuyết hệ số bằng 0 dưới mô hình suy luận đã chọn. Nó không phải xác suất giả thuyết không đúng, cũng không đo xác suất dự án thành công. Nếu khoảng tin cậy chứa 0, kết luận đúng là chưa đủ bằng chứng bác bỏ hệ số bằng 0 ở mức tương ứng. Không suy ra tone hoàn toàn vô dụng; một mẫu nhỏ, sai số đo lường hoặc công bố thông tin sớm có thể làm kiểm định ít lực. Ngược lại, một hệ số có p nhỏ vẫn có thể phản ánh yếu tố bị bỏ sót.

R² của hồi quy CAR trên tone cho biết phần biến thiên CAR được giải thích trong mẫu bởi các biến của đặc tả. Nó không đo độ chính xác phân loại sentiment và không thay thế kiểm định ngoài mẫu. Thêm hiệu ứng năm/công ty có thể tăng R² một cách cơ học do thêm biến. Khi so sánh, cần đọc đồng thời N, bậc tự do, hệ số tone và sai số chuẩn; không chỉ chọn mô hình có R² cao nhất.

Trong đặc tả có hiệu ứng công ty, hệ số tone dựa nhiều hơn vào biến động tone bên trong cùng doanh nghiệp qua thời gian. Đặc tả đơn kết hợp cả khác biệt giữa công ty và thay đổi theo năm. Nếu hai hệ số khác nhau, nguyên nhân có thể là phong cách viết cố hữu, cơ cấu ngành hoặc đặc điểm doanh nghiệp tương quan với tone. Hiệu ứng năm kiểm soát một thành phần chung của từng năm, nhưng không thay thế kiểm soát cụ thể earnings surprise, thay đổi đòn bẩy hoặc tin pháp lý của từng công ty.

HC3 điều chỉnh sai số chuẩn đối với phương sai thay đổi và quan sát có leverage. Nó không loại bỏ tương quan chuỗi trong cùng công ty. Cluster theo ticker cho phép dạng phụ thuộc trong cụm, với 50 cụm trong toàn mẫu; cần finite-sample correction và kiểm tra phụ thuộc giữa các công ty trong cùng ngày. Hai cách tính SE được trình bày như đối chứng. Leave-one-firm-out kiểm tra xem dấu/độ lớn hệ số có phụ thuộc một công ty hay không; từng lần bỏ công ty không phải một mô hình độc lập để tìm p-value thuận lợi.

## Phụ lục C. Vì sao ngày filing cần kiểm tra độ nhạy

Ngày SEC nhận filing là mốc có thể xác định công khai và tái lập. Tuy nhiên, báo cáo tài chính có thể đã được thông báo trong earnings release trước ngày nộp 10-K. CAR quanh filing vì vậy đo phần thông tin và phản ứng gắn với thời điểm filing, không đo toàn bộ tác động của kết quả năm. Chọn cửa sổ dài hơn có thể bắt phản ứng chậm, đồng thời đưa thêm tin không liên quan vào lợi suất.

Quy tắc same dùng phiên của ngày filing nếu là phiên giao dịch. Quy tắc next luôn chuyển sang phiên kế tiếp. Quy tắc acceptance đọc thời điểm nộp, chuyển múi giờ New York và so với giờ đóng cửa thực tế của XNYS; filing sau đóng cửa được chuyển sang phiên kế tiếp. Ngày nghỉ và phiên đóng cửa sớm đều theo lịch giao dịch. Không dùng ngày lịch thay cho ngày giao dịch, không nén trục thời gian khi mất giá.

Screening 8-K Item 2.02 nhận diện một nguồn nhiễu cụ thể: công bố kết quả hoạt động hoặc tình hình tài chính. Cờ được lập từ metadata SEC và đối chiếu cửa sổ baseline. Việc loại cờ không bảo đảm mẫu sạch mọi tin; earnings có thể xuất hiện trong press release, hội nghị hoặc nguồn ngoài SEC. Cờ baseline cũng không đồng nghĩa đã sàng lọc toàn bộ cửa sổ dài hơn. Nếu phân tích mở rộng, phải xây cờ riêng cho từng cửa sổ và alignment, không tái sử dụng cờ [-1,+1] như thể bao phủ mọi tình huống.

## Phụ lục D. Đo tone và vấn đề ngữ cảnh

Từ điển LM chuyên biệt giảm nhầm lẫn do ngôn ngữ tài chính. Một từ kế toán có vẻ tiêu cực trong hội thoại chưa chắc là tín hiệu tin xấu trong báo cáo. Tuy nhiên, đếm từ vẫn không hiểu đầy đủ phủ định, điều kiện hoặc người chịu rủi ro. Câu nói công ty không còn chịu một rủi ro có thể vẫn chứa từ negative. Một đoạn cảnh báo tuân thủ bắt buộc có thể làm negativity tăng mà không phản ánh biến động cơ bản mới.

Mẫu số là toàn bộ token chữ cái hợp lệ của MD&A đã trích xuất. Nếu bỏ stopwords khỏi mẫu số, tỷ lệ sẽ đổi dù số negative không đổi; đó là một chỉ số khác và phải nêu rõ. Không stemming giúp so khớp đúng các inflections trong từ điển. Các bảng chứa số vẫn được giữ vì nhiều filing dùng HTML table làm bố cục văn bản; token số không nằm trong mẫu số, nhưng nhãn chữ trong bảng vẫn có thể được đếm. Running headers và cụm lặp có thể tạo sai số đo lường.

VADER được sử dụng như word list tổng quát đối chứng, không phải Harvard General Inquirer và không phải toàn bộ thuật toán VADER compound. Hai bộ từ điển dùng cùng token và mẫu số để so sánh mức đo lường. Bảng các từ bất đồng giúp người đọc chọn câu để đọc trong MD&A. Tần suất bất đồng không tự chứng minh từ điển nào đúng ở từng câu; muốn đánh giá độ chính xác cần tập nhãn con người, hướng dẫn annotation và thước đo đồng thuận.

FinBERT là hướng mở rộng sau baseline. Có thể chia MD&A thành câu/đoạn, tính xác suất sentiment và tổng hợp theo tài liệu, nhưng cần công bố mô hình, giới hạn token, cách chia đoạn và trọng số. Để so sánh có ý nghĩa phải dùng cùng sample, cùng event windows và không điều chỉnh phương pháp sau khi nhìn thấy kết quả. Dự án hiện tại không báo cáo kết quả FinBERT chưa chạy như bằng chứng thực nghiệm.

## Phụ lục E. Kiểm soát chất lượng và khả năng tái lập

Chuỗi kiểm tra bắt đầu từ provenance: accession, URL chính thức, ngày tải và SHA256 của raw filing. Tiếp theo là kiểm tra ranh giới Item 7, độ dài token, đoạn đầu/cuối và phương pháp extraction. Tại tầng thị trường, kiểm tra số quan sát estimation, độ phủ event window và biến động benchmark. Tại tầng thống kê, kiểm tra hạng ma trận, bậc tự do, sai số chuẩn và giá trị thiếu. Một lỗi ở tầng trước có thể làm kết luận tầng sau sai dù hồi quy vẫn chạy.

Notebook đã đóng gói tái đếm LM từ MD&A, cộng AR thành CAR cho ba cửa sổ rồi fit lại baseline. Đây là kiểm tra độc lập giữa dữ liệu văn bản, bảng AR và bảng hồi quy; không chỉ in lại bảng kết quả. Tái tải dữ liệu online là bước khác và có thể thay đổi do nhà cung cấp điều chỉnh dữ liệu lịch sử. Vì vậy nên giữ snapshot dữ liệu đã xử lý cùng phiên bản package và checksum khi nộp bài.

Giao diện là công cụ đọc dữ liệu, không tạo thêm bằng chứng chỉ vì có biểu đồ. Khi dùng bộ lọc, phải đọc rõ mô hình và N của mẫu đang chọn. Một năm với mười công ty không đủ cho mọi đặc tả có nhiều dummy; chương trình từ chối các mô hình thiếu bậc tự do hoặc hạng không đầy đủ thay vì trả hệ số khó hiểu. Kết luận tổng quan luôn gắn với toàn mẫu và cửa sổ được ghi rõ.

## Phụ lục F. Hàm ý thực tiễn và nghiên cứu tiếp theo

Với nhà đầu tư, tone có thể hỗ trợ sàng lọc tài liệu cần đọc: negative hoặc uncertainty tăng đột ngột là lý do xem thay đổi nội dung, không phải tín hiệu bán tự động. Cần đối chiếu earnings release, guidance, dòng tiền và ngày tin đã xuất hiện. Một giao dịch triển khai sau công bố còn chịu chi phí, độ trễ và khả năng thông tin đã được phản ánh vào giá; event study này chưa backtest các yếu tố đó.

Với ngân hàng, thông tin định tính có thể bổ sung hồ sơ thẩm định. Người phân tích nên đọc các câu chứa rủi ro, so với lịch sử công ty và kiểm tra tính trọng yếu. Tone không thay thế năng lực trả nợ, giá trị tài sản bảo đảm hoặc dòng tiền dự kiến. Các thay đổi boilerplate do quy định cần được phân biệt với rủi ro kinh doanh mới.

Mở rộng tiếp theo nên ưu tiên tăng số công ty và cân bằng ngành, thêm earnings surprise và fundamentals có thời điểm công bố rõ ràng, sử dụng benchmark total return nhất quán và đối chiếu dữ liệu CRSP khi có quyền truy cập. Sau đó xây tập audit có nhãn con người cho parser và sentiment. Với mục tiêu dự báo, chia train/test theo thời gian, dùng từ điển khả dụng tại thời điểm đó và đánh giá ngoài mẫu trước khi rút ra hàm ý giao dịch.

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
## Phụ lục H. Kiểm tra nhãn năm tài chính

Năm tài chính không đồng nhất với năm ngày kết thúc kỳ báo cáo. Pipeline ưu tiên DocumentFiscalYearFocus và lưu nguồn nhãn, đồng thời kiểm tra các xung đột bằng tài liệu gốc.

- Home Depot: glossary trong các báo cáo cũ định nghĩa fiscal 2016 kết thúc 29/01/2017, fiscal 2017 kết thúc 28/01/2018 và fiscal 2018 kết thúc 03/02/2019. Các báo cáo kết thúc tháng 1–2 trước khi có DEI dùng năm lịch trừ một, thay vì nhãn năm trang bìa. Báo cáo kết thúc 31/01/2016 thuộc fiscal 2015 nên ngoài mẫu.
- Honeywell, accession 0000773840-22-000018: DEI ghi 2020 nhưng trang bìa ghi fiscal year ended December 31, 2021, context kỳ 20210101–20211231. Nhãn được sửa thành 2021 và ghi audited_override trong manifest.
- Salesforce, accession 0001108524-26-000060: DEI ghi 2025 trong khi trang bìa và kỳ báo cáo kết thúc January 31, 2026, năm tài chính 2026. Báo cáo này được loại khỏi mẫu 2016–2025; không giữ thêm chỉ vì nhãn DEI.
- JNJ: các kỳ 52/53 tuần kết thúc đầu tháng 1 được gắn năm tài chính trước nếu không có DEI, theo lịch năm của doanh nghiệp.

Các chỉnh sửa dựa trên nội dung báo cáo và lịch tài chính, được thực hiện trước hồi quy chốt, không dựa trên tone hoặc CAR. Raw HTML và nguồn URL vẫn được giữ nguyên. Kiểm tra một quan sát duy nhất cho mỗi ticker–fiscal_year và xuất danh sách năm còn thiếu; không giải quyết trùng bằng cách chọn quan sát cho p-value tốt hơn.


Phạm vi đo văn bản: parser sử dụng chương MD&A chính. Citi và Honeywell có các phần rời nhau; các chương xen giữa ngoài phạm vi được loại. Intel dùng chương MD&A và phần Critical Accounting khi nằm sau Properties; không sao chép toàn bộ ghi chú kế toán và mọi đoạn dẫn chiếu pháp lý trong cross-reference. Đây là giới hạn đo lường cần lưu ý khi tái lập, không được nhận là toàn bộ nội dung được pháp lý dẫn chiếu vào Item 7. URL, checksum và snippets đầu/cuối của từng đoạn được lưu để kiểm tra độc lập.


## Phụ lục I. Rà soát xử lý dữ liệu

### Cập nhật ranh giới sau rà soát mở rộng

Phần dưới lưu lịch sử kiểm tra dấu nháy trước sửa ranh giới. Rà soát sau đó phát hiện thêm 14 bản trích sai phạm vi; đã sửa và tính lại kết quả. Các số baseline và mức thay đổi tone trong phần lịch sử không phải kết quả hiện hành. Xem LIMITATIONS_REMEDIATION.md và REPORT.md để dùng kết quả mới. Kiểm tra 500/500 token tái lập chỉ chứng minh tính nhất quán của code; nó đã không phát hiện lỗi ngữ nghĩa chọn chương.

### Lịch sử kiểm tra dấu nháy

### Hiện tượng trong ảnh

Các số 155,041, 52, ký hiệu $ và % là ô bảng tài chính trong Apple FY2016/FY2017. Khi chuyển HTML thành text, mỗi p/div/tr/td tạo dấu xuống dòng; các thẻ lồng nhau tạo nhiều dòng trống. CSS pre-wrap giữ nguyên chúng nên trông như mất chữ hoặc giãn trắng rất lớn. File gốc và nội dung trích vẫn có chữ và số.

Chế độ đọc hiện gộp khoảng trắng và chia đoạn vừa đọc, không xóa từ hoặc số, không đổi thứ tự. Nút Giữ xuống dòng bản trích cho phép đối chiếu bản lưu; Xem file gốc đã lưu trên máy mở HTML đúng bố cục. Kiểm thử hai báo cáo trong ảnh xác nhận chuỗi chữ sau chuẩn hóa khoảng trắng giữ nguyên, tìm từ và màn hình nhỏ hoạt động.

### Lỗi kỹ thuật phát hiện và sửa

Rà lại trước sửa cho thấy 494/500 báo cáo có token giống hệt khi trích lại; 6 báo cáo khác chuỗi token do xử lý dấu nháy cũ và một nhãn It em. Năm báo cáo thay đổi tone, lớn nhất 0,000187143 ở COP FY2018; đây tương đương 0,0187143 điểm phần trăm của chỉ số tone, không phải CAR. Một báo cáo chỉ đổi cách biểu diễn token, không đổi điểm số.

Đã thống nhất dấu nháy thẳng, nháy cong và mã Windows cũ trước tokenization. Từ có dấu nháy bên trong vẫn là một token, ví dụ we're, management's; chỉ ghép từ điển khi toàn token khớp. Các cách mã hóa cùng một từ cho kết quả giống nhau. Không tự gán sentiment cho từ sở hữu không có trong dictionary. Frontend highlight dùng cùng quy tắc nhận diện dấu nháy.

Đã trích lại toàn bộ 500 MD&A từ nguồn raw đã lưu, rồi tính lại LM, generic word-list, delta tone và các hồi quy. Số, $, % không nằm trong mẫu số token chữ cái; nhãn chữ trong bảng vẫn nằm trong baseline. Baseline chưa loại toàn bộ bảng hoặc boilerplate, đây là giới hạn đo lường và khác biệt với bài gốc, không được gọi là replication chính xác.

### Kiểm tra sau sửa

- 500 báo cáo được đếm lại: positive/negative/uncertainty, mẫu số và tone khớp panel.
- 500/500 báo cáo có chuỗi token giống khi trích lại độc lập bằng code hiện hành.
- SHA256 của 500 báo cáo gốc khớp panel; nguồn Exhibit 13 có checksum riêng.
- Ba alignment: mỗi alignment 500 sự kiện và 5.500 dòng AR. Không trùng event–relative_day; đủ ngày -5 đến +5; expected return = alpha + beta × market return; AR và ba cửa sổ CAR khớp, sai số dưới 1e-12.
- Chuỗi cập nhật mẫu giữ 50 công ty và FY2016–2025. Snapshot trước sửa giữ tại outputs/archive/pre_text_audit_500 để kiểm tra thay đổi.

Chuẩn hóa dấu nháy ảnh hưởng tone của 137/500 báo cáo; mức thay đổi tuyệt đối lớn nhất 0.00023842. CAR và giá đầu vào không thay đổi. Baseline trước sửa: b=-0.067932, p=0.806095; sau sửa: b=-0.067826, p=0.806694. Kết luận không có bằng chứng thống kê rõ ở mức 5% vẫn giữ.

### Những điều kiểm tra này chưa chứng minh

Trích lại giống code hiện hành xác nhận khả năng tái lập, không tự xác nhận ranh giới MD&A chính xác tuyệt đối. Có review cấu trúc và snippets, chưa có human annotation toàn bộ 500 tài liệu. Tables, page headers, câu boilerplate, khác biệt bố cục và phần dẫn chiếu có thể ảnh hưởng phép đo. Yahoo không thay CRSP; earnings surprise chưa được kiểm soát đầy đủ. Cần công bố các giới hạn thay vì dùng p-value để quyết định dữ liệu đúng hay sai.

Minh chứng: outputs/qa/text_processing_checks.json, text_reextraction_audit.csv, tokenizer_correction_comparison.csv và reader_checks.json.


## Phụ lục J. Đối chiếu nghiên cứu gốc

Nguồn đã đọc trực tiếp ngày 28/09/2026. Kết quả từ nghiên cứu khác không được dùng để thay thế kết quả của Nhóm 5.

### Loughran–McDonald (2011)

Bài gốc: 50.115 10-K (1994–2008), 8.341 công ty. Fin-Neg toàn văn: t=-2,64 (Table IV). Riêng MD&A: tỷ lệ từ t=-0,68; tf.idf t=-1,96, sát ngưỡng (Table V). Thiết kế: buy-and-hold excess return [0,3], CRSP, Fama–MacBeth và Newey–West. R² khoảng 2,6%. Không thấy ý nghĩa ở [0,1] (phụ chú 17). Nguồn: https://www.uts.edu.au/globalassets/sites/default/files/adg_cons2015_loughran-mcdonald-je-2011.pdf (trang tạp chí 52–54).

### Tetlock (2007)

Tetlock phân tích chuyên mục Wall Street Journal, không phải MD&A 10-K. Mức bi quan cao dự báo áp lực giảm giá, sau đó có sự đảo chiều; mức bi quan cực đoan đi cùng khối lượng giao dịch cao. Nguồn bài của tác giả: https://www.columbia.edu/~pt2238/papers/Tetlock_Media_Sentiment_JF.pdf ; trang bài báo: https://onlinelibrary.wiley.com/doi/10.1111/j.1540-6261.2007.01232.x . Không suy từ kết quả tin báo chí sang khẳng định 10-K phải có cùng tín hiệu.

### Nghiên cứu thông tin mềm trong earnings announcements

Demers–Vega, Soft Information in Earnings Announcements: News or Noise?, IFDP 951 (2008): dùng thông báo lợi nhuận, thước đo bất ngờ trong net optimism và earnings surprise; độ chắc chắn trong ngôn ngữ còn liên hệ với biến động riêng của cổ phiếu. Nguồn nghiên cứu: https://www.federalreserve.gov/pubs/ifdp/2008/951/ifdp951.htm . Điều này gợi ý phân biệt mức tone, thông tin mới và văn bản được công bố ở thời điểm nào. Delta theo năm của dự án không đồng nhất surprise theo quý trong nghiên cứu này.

### Diễn giải cho Nhóm 5

Dự án có 500 MD&A của 50 công ty, FY2016–2025; baseline dùng (positive−negative)/total words, không phải tỷ lệ Fin-Neg riêng. Baseline hiện hành sau sửa ranh giới p=0.837558; các mô hình delta và controls xem EXPANDED_RESULTS.md. Kết quả không có ý nghĩa thống kê không tự chứng minh parser sai và cũng không chứng minh ngôn ngữ tài chính vô ích. Mẫu có chủ đích doanh nghiệp lớn, phạm vi chương MD&A và dữ liệu giá công khai là các giới hạn.

Nếu triển khai đối chứng sát bài gốc, cần định trước negativity riêng, toàn bộ nội dung 10-K với quy tắc làm sạch thống nhất, cửa sổ [0,3] và cách tính excess return tương ứng. Các đối chứng ấy phải được báo cáo dù không có ý nghĩa, giữ baseline hiện tại và không gọi là tái lập chính xác khi chưa có CRSP/Compustat hoặc cùng mẫu, biến kiểm soát và bộ từ điển lịch sử.


## Phụ lục K. Khắc phục hạn chế và đối chứng

Ngày cập nhật: 28/09/2026. Đây là bản hiện hành sau sửa ranh giới MD&A. Toàn bộ dữ liệu thật gồm 500 báo cáo, 50 công ty, FY2016–2025. Baseline giữ định nghĩa Tone = positive_rate - negative_rate và CAR market model [-1,+1]. Sửa lỗi dữ liệu là cập nhật baseline; các phương pháp mới được báo cáo riêng, không lựa chọn theo p-value.

### 1. Lỗi chọn phạm vi đã khắc phục

Kiểm tra tái trích, checksum và phép đếm từ không đủ để chứng minh đã chọn đúng chương. Rà soát đầu/cuối theo nhóm bố cục phát hiện 14 bản bị chọn nhầm: CVX 2016–2025, IBM 2016–2018 và PFE 2019. Parser cũ có thể nhận mục lục/đoạn dẫn chiếu làm opening rồi chạy vào chương khác; ngưỡng số từ vẫn đạt nên kiểm tra kỹ thuật cũ cho qua.

Chevron chứa MD&A thực chất trong chính HTML 10-K: chọn tiêu đề theo sau bởi Key Financial Results, cho phép nhãn Financial Table of Contents ở bố cục mới; kết thúc trước Management's Responsibility/Report of Independent. Giữ phần thảo luận Consolidated Statement of Income bên trong MD&A để tránh cắt sớm. IBM và Pfizer dẫn chiếu annual report: tải Exhibit 13 theo bảng hồ sơ của SEC, lưu raw, URL và SHA256 riêng, rồi trích chương Management Discussion/Financial Review. Chặn opening dạng management discussion overview-pages và information required ... incorporated by reference.

| ticker | fiscal_year | old_words | new_words |
|---|---|---|---|
| CVX | 2016 | 16232 | 11134 |
| CVX | 2017 | 15914 | 10977 |
| CVX | 2018 | 14974 | 10931 |
| CVX | 2019 | 14876 | 10553 |
| CVX | 2020 | 16425 | 12048 |
| CVX | 2021 | 16801 | 11867 |
| CVX | 2022 | 17508 | 12768 |
| CVX | 2023 | 19566 | 12655 |
| CVX | 2024 | 19575 | 13453 |
| CVX | 2025 | 19635 | 13102 |
| IBM | 2016 | 6162 | 32002 |
| IBM | 2017 | 6370 | 29663 |
| IBM | 2018 | 5856 | 29497 |
| PFE | 2019 | 1018 | 39279 |


Tone, delta tone, hồi quy, notebook và báo cáo được tính lại; giá và AR/CAR không đổi. Nguồn gốc trước sửa giữ tại outputs/archive/pre_boundary_repair_500, bao gồm panel, audit và bản text cũ. Minh chứng từng sửa: outputs/qa/boundary_repairs.csv. Rà soát có trợ giúp AI đã đọc snippets đầu/cuối của 14 bản sửa, không phải human annotation toàn văn.

Baseline hiện hành HC3: b=-0.058633, p=0.837558, CI95%=[-0.619158; 0.501892], N=500. Hệ số dùng tỷ lệ thập phân; để diễn giải mức tăng tone 1 điểm phần trăm, nhân b với 0,01 trước khi đổi return sang phần trăm.

### 2. Đối chứng loại bảng số liệu

Không xóa mọi table vì báo cáo SEC cũ dùng table để dàn trang cả chương. Quy tắc leaf-numeric-v1 chỉ loại bảng không chứa bảng con, có ít nhất hai hàng, ít nhất sáu ô có nội dung, ít nhất bốn ô số và tỷ lệ ô số từ 35%. Ô số chứa chữ số nhưng không chứa chuỗi chữ cái dài từ ba ký tự. Bảng chứa tiêu đề Item 7/8, Management Discussion hoặc Consolidated Statements được giữ. Bảng có bất kỳ ô văn dài trên 60 token cũng được giữ để bảo vệ thuyết minh.

Đặt marker quanh bảng ứng viên, trích lại MD&A, bỏ marker rồi so sánh toàn bộ token với baseline trước khi xóa phần bảng. Điều kiện này xác nhận không đổi ranh giới chương. Nếu marker làm hỏng nhận diện heading, giữ bản trích ban đầu thay vì chấp nhận phạm vi khác; có 5 trường hợp bảo vệ như vậy. Quy tắc bảo thủ có thể giữ lại một số bảng, không được gọi là văn bản prose-only hoặc loại sạch mọi bảng.

Đã xử lý 500 báo cáo; 488 báo cáo có bảng số được loại; tổng 11069 bảng và 506,606 token chữ bị loại. Trung vị tỷ lệ token bị loại trên toàn mẫu: 5.16%. Không dùng giá trị p để điều chỉnh các ngưỡng. Bản text đối chứng ở data/interim/mda_numeric_tables_removed; panel và bảng kê snippets từng bảng ở outputs/limitations. Baseline và raw giữ riêng, không ghi đè bằng text đối chứng. Rà snippets có trợ giúp AI trên 12 bảng: sáu bảng nhiều token bị loại nhất và sáu bảng chọn ngẫu nhiên seed=5, lưu table_snippet_review_sample.csv. Mẫu này có nhãn tài chính, tên sản phẩm và dòng giải thích ngắn trong ô; vì vậy đối chứng loại cả nội dung chữ của bảng số, không phải chỉ loại chữ số. Đây không phải human annotation mọi bảng.

### 3. Đối chứng phương pháp

Thêm negativity = negative_count / word_count để tách tác động từ tiêu cực khỏi net tone. Thêm buy-and-hold excess return [0,3] = tích(1 + return cổ phiếu) - tích(1 + return chỉ số). Đây không phải tổng AR market model. Mỗi sự kiện có đúng bốn phiên 0,1,2,3. Cổ phiếu và benchmark vẫn là Yahoo adjusted prices và S&P500 price index, chưa thay bằng CRSP value-weighted total-return benchmark.

Sáu đặc tả trên mỗi alignment same, next, acceptance: tone baseline/CAR; tone loại bảng/CAR; delta tone loại bảng/CAR; negativity baseline/CAR; negativity baseline/BHAR; negativity loại bảng/BHAR. Delta chỉ tính hai năm liền kề cùng doanh nghiệp; N=450. Toàn mẫu N=500 có 50 cụm doanh nghiệp. Dùng SE cluster theo ticker, hiệu chỉnh mẫu hữu hạn và t-distribution; p_Holm hiệu chỉnh chung cả 18 kiểm định. p baseline HC3 ở mục 1 và p cluster trong bảng có thể khác vì cách ước lượng bất định khác nhau.

| specification | coefficient | se_cluster | p_cluster | p_holm | N |
|---|---|---|---|---|---|
| baseline_tone | -0.05863 | 0.18519 | 0.75289 | 1.00000 | 500 |
| numeric_tables_removed_tone | -0.10978 | 0.17969 | 0.54407 | 1.00000 | 500 |
| numeric_tables_removed_delta | 1.62099 | 1.66976 | 0.33642 | 1.00000 | 450 |
| negativity_car | -0.05657 | 0.31280 | 0.85722 | 1.00000 | 500 |
| negativity_bhar | 0.12992 | 0.28714 | 0.65294 | 1.00000 | 500 |
| clean_negativity_bhar | 0.19216 | 0.29945 | 0.52405 | 1.00000 | 500 |


Kết quả đầy đủ cả ba alignment được công bố trong outputs/limitations/sensitivity_models.csv, không chỉ mô hình có p nhỏ nhất. Số kiểm định qua mức 5% sau Holm: 0/18. Chưa đủ bằng chứng không có nghĩa tone vô ích hoặc doanh nghiệp không cung cấp thông tin; chỉ giới hạn kết luận trong mẫu, phép đo và mô hình đã kiểm tra.

### 4. Hạn chế còn lại và phạm vi kết luận

| Hạn chế | Xử lý hiện tại | Điều chưa thể khẳng định |
|---|---|---|
| Nhầm chương do dẫn chiếu/mục lục | Sửa 14 bản, chặn cross-reference, cập nhật toàn bộ score | Chưa xác nhận từng câu trong cả 500 bản bằng người đọc độc lập |
| Từ nhãn bảng ảnh hưởng tone | Có đối chứng loại bảng số bảo thủ, giữ text gốc | Còn bảng phức tạp, page header và boilerplate |
| Net tone gộp hai loại từ | Thêm negativity riêng và delta tone | Chưa có trọng số TF-IDF tương đương bài gốc hoặc FinBERT có human labels |
| Khác outcome/window | Thêm BH excess return [0,3], ba alignment | Chưa replication chính xác Loughran–McDonald |
| Quan sát lặp cùng công ty, nhiều kiểm định | Firm-cluster SE và Holm toàn bộ đối chứng | Không tự xử lý mọi phụ thuộc chéo hoặc nội sinh |
| Earnings announcement và thông tin đồng thời | Đã screening 8-K Item 2.02, controls tài chính | Chưa có analyst consensus để tính earnings surprise |
| Mẫu chỉ 50 công ty lớn hiện còn hoạt động | Danh sách và chọn mẫu được công khai, 10 năm | Không đại diện toàn bộ thị trường; còn survivorship bias |
| Yahoo và price-index benchmark | Cache, checksum, kiểm tra công thức và dữ liệu thật | Chưa có delisting return/CRSP total return hoặc tái dựng universe lịch sử |

Không thể xóa những giới hạn nguồn dữ liệu bằng cách đổi lời văn hoặc đổi mô hình cho p < 0,05. Để xử lý survivorship cần universe lịch sử gồm doanh nghiệp hủy niêm yết và dữ liệu return tương ứng. Để kiểm soát earnings surprise cần consensus có thời điểm đo trước sự kiện. Để đánh giá sentiment theo ngữ cảnh cần gán nhãn độc lập và tập đánh giá tách khỏi huấn luyện. Các việc này chưa được thực hiện trong bản hiện tại.

### 5. Tái lập và kiểm chứng

Chạy scripts/repair_referenced_mda.py để sửa nguồn khi dùng snapshot cũ; pipeline mới tự chặn nguồn nhầm và chuyển Exhibit 13. Chạy scripts/address_limitations.py để xây text đối chứng và 18 hồi quy. Chạy scripts/publish_limitations.py sau khi các kết quả đã hoàn tất. Kiểm thử mới bảo vệ bảng dàn trang và ô văn dài, chặn IBM cross-reference, giữ phần Chevron income discussion và kiểm tra compounding. Mẫu và ngưỡng được ấn định bằng cấu trúc văn bản, không bằng dấu hoặc ý nghĩa thống kê của kết quả.

Nguồn đối chiếu và khác biệt methodology xem LITERATURE_COMPARISON.md; dữ liệu SEC từng filing có URL trong manifest. Không coi checksum hoặc chạy lại cùng parser là bằng chứng tuyệt đối rằng parser hiểu đúng tài liệu.
