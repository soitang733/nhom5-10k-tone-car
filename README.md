# Nhóm 5 · Textual Finance · Streamlit

Dashboard đọc snapshot **dữ liệu thật** SEC 10-K của 50 doanh nghiệp, FY2016–2025. Tone được tính từ từ điển Loughran–McDonald; CAR dùng market model. Dữ liệu đã sửa 14 phạm vi MD&A bị chọn nhầm. Kết quả chính hiện chưa có ý nghĩa thống kê ở mức 5%.

## Chạy local

```bash
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

## Đưa lên Streamlit Community Cloud

Repo GitHub chứa chính thư mục này ở gốc. Trên [share.streamlit.io](https://share.streamlit.io/), chọn repo, nhánh `main` và entrypoint `app.py`. Python 3.12. App không dùng API key hoặc file `.env`; mọi phân tích trên Cloud đọc snapshot cố định, **không tự tải SEC/Yahoo**. Mỗi filing có link đến tài liệu SEC gốc. Chỉ nhóm nghiên cứu cập nhật snapshot từ pipeline có kiểm tra trong dự án gốc.

`snapshot/` gồm ba panel/AR/hồi quy theo alignment, 500 bản trích MD&A và file kiểm chứng. `docs/` chứa báo cáo/phương pháp/giới hạn; PDF 20 trang nằm ở gốc. Raw HTML SEC không được sao chép lên repo Streamlit để giảm dung lượng; xem file trực tiếp qua link SEC ở tab Khám phá báo cáo. Các file văn bản MD&A là bản trích đã xử lý, không phải HTML gốc.

Nguồn công trình so sánh và các giới hạn về chọn mẫu, dữ liệu giá và earnings surprise được nêu trong `docs/REFERENCES.md` và `docs/LIMITATIONS_REMEDIATION.md`. App không nhận đây là replication chính xác Loughran–McDonald (2011).
