# Nhóm 5 · Textual Finance · Streamlit

App đọc snapshot đã kiểm chứng của **100 công ty do người dùng cung cấp**, mỗi công ty có 10 báo cáo 10-K FY2016–2025. Từ HTML gốc SEC và các phụ lục Exhibit 13, dự án trích 1.000 MD&A, tính tone Loughran–McDonald và CAR quanh ngày nộp. Kết quả quan sát và giới hạn được trình bày trong app và báo cáo PDF.

App công khai: https://nhom5-10k-tone-car.streamlit.app/

## Chạy local

```bash
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

Trên Streamlit Community Cloud, dùng repo này, nhánh `main`, entrypoint `app.py`. Phiên bản Python được chọn trong Advanced settings lúc tạo app. Cloud chỉ đọc snapshot; không cần API key và không tải SEC/Yahoo khi khởi động.

`snapshot/` có danh sách gốc 100 công ty, bảng đối chiếu SEC, ba bộ panel/AR/hồi quy theo cách căn ngày, bảng 8-K, phân tích độ nhạy và 1.000 bản trích MD&A. `docs/` chứa báo cáo, nguồn, phương pháp, giới hạn và kiểm toán; `Nhom5_BaoCao.pdf` là bản in. HTML 10-K gốc được giữ trong dự án nghiên cứu local ở `data/raw/sec`, còn app có link trực tiếp tới từng filing SEC để đối chiếu.

Đây là mẫu có chủ đích, không phải replication chính xác dữ liệu CRSP của Loughran–McDonald (2011); các hệ số không chứng minh quan hệ nhân quả.
