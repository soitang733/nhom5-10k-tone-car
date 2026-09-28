# Nhật ký sử dụng AI — Nhóm 5

Ngày 27–28/09/2026, Codex hỗ trợ đọc đặc tả người dùng, xây pipeline Python, tải và lưu dữ liệu công khai, trích MD&A, tính tone/CAR, kiểm thử, viết báo cáo và app. Người dùng cung cấp danh sách chính xác 100 công ty trong `companies_100.csv` và thông tin liên hệ cho SEC User-Agent. Ba repo GitHub được dùng để tham khảo cách tổ chức và phương pháp, không là nguồn dữ liệu hoặc kết quả định lượng.

AI rà soát các lỗi bố cục 10-K/Exhibit 13 của CCL, CAH, DE, FCX, FDX, LVS, MELI, MLM, NUE và một số issuer khác; sửa nhãn năm tài khóa 52/53 tuần và DEI lỗi thời; chạy lại mẫu đúng 100 công ty FY2016–FY2025. Dữ liệu gốc, URL, accession, ngày tải và SHA-256 được lưu để đối chiếu. Audit cấu trúc gồm tiêu đề, ranh giới, số token và đoạn đầu/cuối; **không phải gán nhãn thủ công toàn văn của con người**.

AI tính và kiểm tra các bảng hồi quy, đối chứng lịch ngày, 8-K Item 2.02, biến tài chính cùng accession, loại bảng số và hiệu chỉnh Holm. Các phương pháp đối chứng được công bố cùng baseline, không chọn theo p-value. Kết quả là quan hệ quan sát được, không chứng minh nhân quả hay hiệu quả giao dịch.

Người nộp bài cần tự đọc các filing mẫu, hiểu phương trình và giới hạn, kiểm tra lại báo cáo cuối, rồi trả lời trực tiếp câu hỏi phản biện. Mọi diễn giải có lỗi còn lại thuộc trách nhiệm nhóm.
