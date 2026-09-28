# Nguồn dữ liệu và cách tải

Danh sách gốc `data/companies_100_input.csv` có SHA-256 lưu trong snapshot metadata. Bảng kiểm `outputs/qa/company_list_100_validation.csv` đối chiếu ticker và CIK với SEC. Danh sách được cố định theo file người dùng đưa, không lựa theo p-value. SEC Submissions API cho form, accession, report date, filing date và acceptance time. Client đọc cả file lịch sử, giữ form 10-K đầu tiên cho từng kỳ, bỏ 10-K/A; ngày nộp không sau 28/09/2026. Bản HTML hoặc phụ lục Exhibit 13 thật được lưu cứng vào `data/raw/sec` dưới tên băm URL kèm JSON provenance, URL và SHA-256. Hồ sơ Apple FY2025 trong mẫu là bản năm kết thúc 27/09/2025, không phải dữ liệu tự dựng.

Mười năm tài khóa 2016–2025 được gán từ DEI và kỳ trên bìa, có đối chiếu các trường hợp năm tài khóa kết thúc tháng 1–2 và DEI lỗi thời. `data/filings_manifest.csv` ghi nguồn quyết định nhãn năm; mỗi cặp ticker–năm đúng một accession. Mẫu có chủ đích gồm các công ty tồn tại và có dữ liệu đủ 10 năm, nên có thiên lệch sống sót và không đại diện ngẫu nhiên cho toàn thị trường.


Tệp HTML gốc và Exhibit 13 được lưu trong `data/raw/sec/*.raw`, metadata cùng basename `.json`. Bảng sau xử lý nằm ở `data/tone_panel.csv` và `outputs/real/{same,next,acceptance}/car_panel.csv`. Từ điển LM ở `data/external/lm.csv`; giá có raw cache. `data/filings_manifest.csv` cho phép mở từng URL SEC và đối chiếu hash.
