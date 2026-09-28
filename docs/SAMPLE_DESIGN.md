# Thiết kế mẫu 100 công ty

Danh sách đầu vào do người dùng cung cấp trong `companies_100.csv`; bản sao không sửa ở `data/companies_100_input.csv`. Mỗi ticker được ghép CIK SEC, lấy 10-K gốc cho FY2016–2025. Không nối thêm 50 công ty cũ, không đổi công ty theo kết quả hồi quy. Mẫu có chủ đích và thiên lệch sống sót.

| Chỉ tiêu | Số lượng |
| --- | --- |
| Công ty đầu vào | 100 |
| Năm mỗi công ty | 10 |
| Accession phân tích | 1000 |

Xem bảng đối chiếu CIK trong `outputs/qa/company_list_100_validation.csv` và nhãn năm trong manifest.
