# Kiểm toán trích MD&A

Toàn bộ 1.000 hồ sơ có URL SEC, accession, bản gốc lưu cứng, checksum và tệp MD&A trích. Audit ghi cách cắt, số từ, mở đầu/kết thúc; quy tắc riêng cho tài liệu có MD&A nhúng hoặc Exhibit 13 được ghi trong `tonecar/text.py`. Kiểm tra này là rà soát cấu trúc có AI hỗ trợ; chưa phải đọc thủ công và gán nhãn toàn bộ 1.000 báo cáo.

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
