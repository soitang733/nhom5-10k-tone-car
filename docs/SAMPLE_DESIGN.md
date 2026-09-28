# Thiết kế mở rộng mẫu, khóa trước kết quả mới

Giữ giai đoạn 2016–2025 và 10 công ty ban đầu. Bổ sung 40 doanh nghiệp đã niêm yết lâu năm thuộc các nhóm công nghệ, tài chính, y tế, tiêu dùng, công nghiệp, năng lượng và tiện ích. Đây là mẫu có chủ đích, không phải random sample, không phải danh mục S&P 500 lịch sử và có survivorship bias. Ticker/CIK xác nhận từ file company_tickers.json chính thức của SEC; nhãn nhóm là phân loại phục vụ phân tích, không tuyên bố là GICS chính thức.

Mục tiêu 50 công ty × 10 năm = 500 firm-years. Công bố toàn bộ universe trong data/sample_universe.csv trước khi tải các kết quả mới. Không thay công ty vì p-value hoặc hướng CAR; thiếu nguồn, thiếu giá hoặc parser thất bại phải xuất bảng độ phủ và lý do loại. Báo cáo phân biệt mẫu mục tiêu, số văn bản trích được và số event đủ giá.

Primary test giữ CAR[-1,+1] ~ Tone, same-session, HC3 như phiên bản 100. Kiểm định phụ bổ sung delta_tone = tone(t) − tone(t−1), chỉ khi hai fiscal years liên tiếp và cùng công ty đều có văn bản hợp lệ. Không nối qua khoảng thiếu năm. Bổ sung year/firm FE và cluster SE theo công ty làm đối chứng; báo cáo Holm cho nhóm kiểm định xuất. Các năm đầu tiên không có delta trong phạm vi 2016–2025, không tự gán delta=0.

Không cam kết tăng mẫu sẽ tạo p<0,05. Kết quả 100 ban đầu giữ ở outputs/archive/baseline_100 để đối chiếu, không bị xóa. Chưa triển khai FinBERT hoặc earnings surprise trong đợt này; không trình bày các kết quả chưa chạy như đã thực hiện.

## Nối pháp nhân và controls

BLK dùng CIK 0001364742 đến report year 2023, CIK hiện tại cho 2024–2025. DIS dùng CIK 0001001039 đến 2018 và CIK hiện tại từ 2019. Hồ sơ SEC formerNames xác nhận tên công ty cũ và thời điểm đổi pháp nhân. Giữ CIK thực của từng filing, không giả định mã hiện tại có toàn bộ lịch sử. Việc nối theo ticker nhằm phân tích issuer lineage; tái tổ chức/sáp nhập có thể tạo structural break trong tone và fundamentals, được công bố như giới hạn.

Đặc tả phụ bổ sung log_assets, tổng liabilities/assets và ROA (lợi nhuận năm/tài sản cuối năm) từ đúng accession/kỳ của 10-K. Không dùng báo cáo tương lai hoặc lựa chọn controls theo p-value; complete-case N được công bố.

XOM: ticker map hiện hành trỏ sang ExxonMobil Holdings (CIK 2115436), chưa có 10-K trong khoảng mẫu. Giữ báo cáo 2016–2025 của Exxon Mobil CIK 34088, vốn có trong snapshot gốc. Không dùng đăng ký/prospectus của holding mới thay cho báo cáo năm.
