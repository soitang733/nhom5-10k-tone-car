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

Mã tái lập nằm trong `tonecar/`, `scripts/`, `tests/` và `notebooks/`. `companies_100_input.csv` là đúng danh sách đầu vào của nhóm, `config.json` cố định thiết kế mẫu, còn `requirements-research.txt` chứa các phụ thuộc cho pipeline nghiên cứu. Các tệp HTML SEC gốc dung lượng khoảng 4,5 GiB được lưu ở máy nghiên cứu và không đưa vào repo; bảng manifest trong `snapshot/` cho URL, accession và dấu vết để kiểm tra từng filing. Chạy `python -m pytest -q tests` và `python scripts/smoke_streamlit_100.py` để kiểm tra repo công khai.

Đây là mẫu có chủ đích, không phải replication chính xác dữ liệu CRSP của Loughran–McDonald (2011); các hệ số không chứng minh quan hệ nhân quả.
