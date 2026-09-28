# Audit trích xuất hoàn chỉnh

Manifest 500 filing; tách được 500 sections. Review đầu/cuối và ranh giới block được ghi tại data/research_audit.csv.

| extraction_method | filings |
|---|---|
| disjoint_Item7_C_excluding_capital_and_risk_factors | 10 |
| embedded_annual_report_BAC | 10 |
| embedded_annual_report_CVX | 10 |
| embedded_annual_report_JPM | 10 |
| embedded_annual_report_XOM | 10 |
| incorporated_Exhibit_13_IBM | 10 |
| incorporated_Exhibit_13_PFE | 4 |
| incorporated_Exhibit_13_WFC | 10 |
| incorporated_Exhibit_13_WMT | 2 |
| issuer_heading_boundaries_HON | 6 |
| issuer_heading_boundaries_INTC | 9 |
| issuer_heading_boundaries_MCD | 7 |
| issuer_heading_boundaries_MS | 9 |
| item7_block_heading | 393 |

JPM/XOM: Item 7 chính thức dẫn chiếu annual report nhúng cùng tài liệu. Parser dùng opening substantive, bỏ mục lục và chạy tới closing heading trước phần financial reporting. Mỗi section có trích đoạn đầu/cuối và số token để kiểm tra độc lập; kiểm tra tự động không tương đương đọc thủ công toàn văn. Giữ SHA256 raw và URL SEC để kiểm tra lại.

Audit có trợ giúp AI tập trung ranh giới, snippets và nguồn; không nhận là human annotation từng câu hoặc chứng minh tuyệt đối parser không sai. Page headers và tables được giữ trong baseline; đây là hạn chế đo lường đã công bố.
