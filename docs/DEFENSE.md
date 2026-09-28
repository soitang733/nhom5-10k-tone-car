# Câu hỏi bảo vệ và gợi ý trả lời

## 1. Vì sao lấy đến 2025 khi đang ở tháng 9/2026?

2025 là năm tài chính đầy đủ gần nhất của thiết kế; nhiều filing 2025 được nộp 2026. Giữ ngày khóa 27/09/2026. Không trộn số liệu năm chưa hoàn tất với báo cáo năm.

## 2. Vì sao dùng MD&A?

MD&A có diễn giải quản trị về hoạt động và tài chính, phù hợp đo ngôn ngữ. Dùng toàn 10-K có thể tăng phần boilerplate và risk factors. Cách chọn section là một quyết định đo lường phải công bố, không đảm bảo kết quả giống LM nguyên bản.

## 3. Tại sao từ điển tổng quát có thể sai?

Ngữ cảnh tài chính khác hội thoại. Đọc bảng bất đồng và một câu trong reader, giải thích nghĩa kế toán trong câu đó. Không khẳng định mọi từ bất đồng đều là lỗi. Đối chứng ở đây là word list VADER, không giả danh Harvard GI.

## 4. Tone khác negativity thế nào?

Tone gộp positive trừ negative trên cùng mẫu số; negativity chỉ đếm nhóm negative. Hai công ty có negativity giống nhau vẫn có tone khác nhau nếu positive khác. Uncertainty là chiều đo riêng.

## 5. CAR khác lợi suất cổ phiếu thế nào?

CAR cộng phần return vượt return dự báo market model. Một cổ phiếu tăng giá vẫn có AR âm nếu mức tăng thấp hơn mức dự báo theo thị trường. CAR không phải buy-and-hold return hoặc lợi nhuận giao dịch sau chi phí.

## 6. Vì sao estimation dừng ở −20?

Khoảng cách giúp giảm ảnh hưởng thông tin gần ngày sự kiện vào mô hình lợi suất kỳ vọng. Đây là lựa chọn thiết kế; kiểm tra độ nhạy khoảng estimation là mở rộng, không đã thực hiện chỉ vì có thể cấu hình.

## 7. Có chứng minh nhân quả không?

Không. Tone có thể tương quan với earnings, rủi ro hoặc đặc điểm công ty; ngày filing cũng có tin khác. FE, HC3 và screening hỗ trợ kiểm tra nhưng không tạo biến thiên ngoại sinh.

## 8. P-value lớn có nghĩa tone không có thông tin?

Không. Nó cho thấy dữ liệu và đặc tả hiện tại chưa đủ để bác bỏ hệ số bằng 0. Đọc CI để đánh giá mức hiệu ứng còn tương thích; sai số đo, mẫu nhỏ và công bố trước filing có thể làm kiểm định yếu.

## 9. Vì sao dùng HC3 và cluster?

HC3 xử lý phương sai thay đổi và leverage; cluster cho phép phụ thuộc trong công ty. Toàn mẫu có 50 cụm; vẫn cần đọc finite-sample correction và độ nhạy theo công ty, đồng thời lưu ý phụ thuộc giữa các công ty trong cùng ngày. Hai SE giải quyết vấn đề khác nhau và cần trình bày giới hạn.

## 10. Năm tài chính khác report_date ra sao?

Fiscal calendar có thể kết thúc đầu tháng 1 năm sau. Đọc DEI rồi lọc fiscal year, thay vì dùng mỗi năm lịch trong report_date. Trường hợp fallback phải giữ cờ để truy nguyên.

## 11. Parser được kiểm tra thế nào?

Kiểm tra heading đầu block, điểm kết thúc Item 7A/8, độ dài, candidates và snippets; JPM/XOM có quy tắc annual report nhúng. Raw checksum và accession cho phép truy ngược. Audit tự động không xác nhận tuyệt đối mọi section đúng hoặc thay thế human labels.

## 12. Tại sao 500 báo cáo có phải 500 công ty độc lập?

Có lặp lại cùng 50 doanh nghiệp; ngành và sự kiện có thể phụ thuộc. Mở rộng thời gian tăng quan sát nhưng không tăng số clusters. Mẫu doanh nghiệp lớn được chọn có survivorship/selection bias.

## 13. Đối chứng earnings đã làm gì?

Gắn cờ 8-K Item 2.02 trong cửa sổ baseline và ước lượng mẫu bỏ cờ. Không bao phủ mọi press release hoặc cửa sổ dài; không tuyên bố đã làm sạch tất cả tin nhiễu.

## 14. Có dùng FinBERT không?

Chưa có kết quả FinBERT trong nghiên cứu này. Repo NLP là nguồn tham khảo hướng mở rộng; baseline thực thi là LM và word list VADER. Không báo cáo mô hình chưa chạy như kết quả.

## 15. Làm sao chứng minh kết quả tái lập?

Chạy notebook để tái đếm từ từ MD&A, cộng AR thành CAR và fit lại baseline; đối chiếu số quan sát, hệ số, SE và CI. Giữ snapshot cùng phiên bản thư viện. Tái tải online có thể khác vì nhà cung cấp sửa giá.

## 16. AI hỗ trợ phần nào?

AI hỗ trợ code, kiểm thử, audit cấu trúc và soạn diễn giải; ghi trong AI_USAGE_LOG. Nhóm phải hiểu công thức, biến, giả định và tự trả lời vấn đáp. Không nhận mã của repo tham khảo hoặc lời văn AI là bằng chứng thực nghiệm của nhóm.

## 17. Vì sao dùng thay đổi tone?

Delta_tone nhắm đến ngôn ngữ thay đổi so với năm liền trước của cùng công ty, có thể giảm ảnh hưởng phong cách viết cố hữu. Đây vẫn là biến đo đếm từ, không đảm bảo thay đổi luôn là tin mới. Năm đầu và năm không có lag liên tiếp bị thiếu delta.

## 18. Fundamentals được lấy để tránh nhìn trước ra sao?

Chọn đúng accession của 10-K, đúng report_date và kỳ năm, thay vì lấy fact mới nhất theo FY. Số được sửa trong một filing sau không được đưa ngược vào sự kiện trước đó. Chỉ tiêu kiểm soát có N riêng do thiếu dữ liệu.

## 19. Tăng mẫu có bảo đảm p nhỏ?

Không. Tăng độ phủ và số công ty có thể làm ước lượng chính xác hơn; một quan hệ thực tế yếu vẫn có thể không rõ. Báo cáo cả baseline, delta, controls và Holm, không chỉ chọn đặc tả có p nhỏ.
