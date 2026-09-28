# Kiểm tra nhãn năm tài chính

Năm tài chính không đồng nhất với năm ngày kết thúc kỳ báo cáo. Pipeline ưu tiên DocumentFiscalYearFocus và lưu nguồn nhãn, đồng thời kiểm tra các xung đột bằng tài liệu gốc.

- Home Depot: glossary trong các báo cáo cũ định nghĩa fiscal 2016 kết thúc 29/01/2017, fiscal 2017 kết thúc 28/01/2018 và fiscal 2018 kết thúc 03/02/2019. Các báo cáo kết thúc tháng 1–2 trước khi có DEI dùng năm lịch trừ một, thay vì nhãn năm trang bìa. Báo cáo kết thúc 31/01/2016 thuộc fiscal 2015 nên ngoài mẫu.
- Honeywell, accession 0000773840-22-000018: DEI ghi 2020 nhưng trang bìa ghi fiscal year ended December 31, 2021, context kỳ 20210101–20211231. Nhãn được sửa thành 2021 và ghi audited_override trong manifest.
- Salesforce, accession 0001108524-26-000060: DEI ghi 2025 trong khi trang bìa và kỳ báo cáo kết thúc January 31, 2026, năm tài chính 2026. Báo cáo này được loại khỏi mẫu 2016–2025; không giữ thêm chỉ vì nhãn DEI.
- JNJ: các kỳ 52/53 tuần kết thúc đầu tháng 1 được gắn năm tài chính trước nếu không có DEI, theo lịch năm của doanh nghiệp.

Các chỉnh sửa dựa trên nội dung báo cáo và lịch tài chính, được thực hiện trước hồi quy chốt, không dựa trên tone hoặc CAR. Raw HTML và nguồn URL vẫn được giữ nguyên. Kiểm tra một quan sát duy nhất cho mỗi ticker–fiscal_year và xuất danh sách năm còn thiếu; không giải quyết trùng bằng cách chọn quan sát cho p-value tốt hơn.
