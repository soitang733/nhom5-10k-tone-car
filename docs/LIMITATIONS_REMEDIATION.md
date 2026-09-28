# Khắc phục hạn chế và phân tích đối chứng

Ngày cập nhật: 28/09/2026. Đây là bản hiện hành sau sửa ranh giới MD&A. Toàn bộ dữ liệu thật gồm 500 báo cáo, 50 công ty, FY2016–2025. Baseline giữ định nghĩa Tone = positive_rate - negative_rate và CAR market model [-1,+1]. Sửa lỗi dữ liệu là cập nhật baseline; các phương pháp mới được báo cáo riêng, không lựa chọn theo p-value.

## 1. Lỗi chọn phạm vi đã khắc phục

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

## 2. Đối chứng loại bảng số liệu

Không xóa mọi table vì báo cáo SEC cũ dùng table để dàn trang cả chương. Quy tắc leaf-numeric-v1 chỉ loại bảng không chứa bảng con, có ít nhất hai hàng, ít nhất sáu ô có nội dung, ít nhất bốn ô số và tỷ lệ ô số từ 35%. Ô số chứa chữ số nhưng không chứa chuỗi chữ cái dài từ ba ký tự. Bảng chứa tiêu đề Item 7/8, Management Discussion hoặc Consolidated Statements được giữ. Bảng có bất kỳ ô văn dài trên 60 token cũng được giữ để bảo vệ thuyết minh.

Đặt marker quanh bảng ứng viên, trích lại MD&A, bỏ marker rồi so sánh toàn bộ token với baseline trước khi xóa phần bảng. Điều kiện này xác nhận không đổi ranh giới chương. Nếu marker làm hỏng nhận diện heading, giữ bản trích ban đầu thay vì chấp nhận phạm vi khác; có 5 trường hợp bảo vệ như vậy. Quy tắc bảo thủ có thể giữ lại một số bảng, không được gọi là văn bản prose-only hoặc loại sạch mọi bảng.

Đã xử lý 500 báo cáo; 488 báo cáo có bảng số được loại; tổng 11069 bảng và 506,606 token chữ bị loại. Trung vị tỷ lệ token bị loại trên toàn mẫu: 5.16%. Không dùng giá trị p để điều chỉnh các ngưỡng. Bản text đối chứng ở data/interim/mda_numeric_tables_removed; panel và bảng kê snippets từng bảng ở outputs/limitations. Baseline và raw giữ riêng, không ghi đè bằng text đối chứng. Rà snippets có trợ giúp AI trên 12 bảng: sáu bảng nhiều token bị loại nhất và sáu bảng chọn ngẫu nhiên seed=5, lưu table_snippet_review_sample.csv. Mẫu này có nhãn tài chính, tên sản phẩm và dòng giải thích ngắn trong ô; vì vậy đối chứng loại cả nội dung chữ của bảng số, không phải chỉ loại chữ số. Đây không phải human annotation mọi bảng.

## 3. Đối chứng phương pháp

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

## 4. Hạn chế còn lại và phạm vi kết luận

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

## 5. Tái lập và kiểm chứng

Chạy scripts/repair_referenced_mda.py để sửa nguồn khi dùng snapshot cũ; pipeline mới tự chặn nguồn nhầm và chuyển Exhibit 13. Chạy scripts/address_limitations.py để xây text đối chứng và 18 hồi quy. Chạy scripts/publish_limitations.py sau khi các kết quả đã hoàn tất. Kiểm thử mới bảo vệ bảng dàn trang và ô văn dài, chặn IBM cross-reference, giữ phần Chevron income discussion và kiểm tra compounding. Mẫu và ngưỡng được ấn định bằng cấu trúc văn bản, không bằng dấu hoặc ý nghĩa thống kê của kết quả.

Nguồn đối chiếu và khác biệt methodology xem LITERATURE_COMPARISON.md; dữ liệu SEC từng filing có URL trong manifest. Không coi checksum hoặc chạy lại cùng parser là bằng chứng tuyệt đối rằng parser hiểu đúng tài liệu.
