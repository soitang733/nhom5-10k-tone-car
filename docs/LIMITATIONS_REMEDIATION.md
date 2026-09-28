# Giới hạn và cách khắc phục

Tone mô tả ngôn ngữ công bố, không đo trực tiếp chất lượng doanh nghiệp. Doanh nghiệp có nhiều rủi ro phải mô tả có thể dùng nhiều từ tiêu cực dù hoạt động tốt. Nhà đầu tư và ngân hàng có thể dùng tone như tín hiệu ưu tiên đọc, kết hợp dòng tiền, đòn bẩy và bối cảnh công bố. Không dùng kết quả quan sát này để khẳng định tone gây biến động giá hay tạo chiến lược giao dịch có lãi. Các nguồn nhiễu gồm earnings release cùng ngày, lựa chọn thời điểm công bố, thay đổi chế độ thị trường, benchmark là chỉ số giá trong khi cổ phiếu dùng adjusted price, thay đổi nghĩa của từ và văn bản bảng. Số công ty đủ 10 năm tạo survivorship bias. Audit cấu trúc có trợ giúp AI và hash nguồn, chưa có gán nhãn thủ công toàn văn hay kiểm tra CRSP độc lập.


Đối chứng định lượng gồm 18 kiểm định định trước, Holm trên toàn bộ họ, căn ngày sự kiện ba cách, loại 8-K 2.02, cluster theo công ty và leave-one-firm-out. Bảng số loại khỏi MD&A chỉ ở bản sensitivity. Kết quả baseline không bị thay theo p-value.

| alignment | specification | coefficient | p_cluster | p_holm | N |
| --- | --- | --- | --- | --- | --- |
| same | baseline_tone | -0.40288 | 0.09167 | 1.00000 | 1000 |
| same | numeric_tables_removed_tone | -0.43780 | 0.09623 | 1.00000 | 1000 |
| same | numeric_tables_removed_delta | -0.81423 | 0.20618 | 1.00000 | 900 |
| same | negativity_car | 0.03975 | 0.84081 | 1.00000 | 1000 |
| same | negativity_bhar | 0.03864 | 0.87197 | 1.00000 | 1000 |
| same | clean_negativity_bhar | 0.00791 | 0.97385 | 1.00000 | 1000 |
| next | baseline_tone | -0.21843 | 0.39230 | 1.00000 | 1000 |
| next | numeric_tables_removed_tone | -0.22185 | 0.42031 | 1.00000 | 1000 |
| next | numeric_tables_removed_delta | -0.37561 | 0.47739 | 1.00000 | 900 |
| next | negativity_car | 0.01103 | 0.95675 | 1.00000 | 1000 |
| next | negativity_bhar | -0.04393 | 0.81381 | 1.00000 | 1000 |
| next | clean_negativity_bhar | -0.04721 | 0.80268 | 1.00000 | 1000 |
| acceptance | baseline_tone | -0.24790 | 0.34249 | 1.00000 | 1000 |
| acceptance | numeric_tables_removed_tone | -0.27203 | 0.34228 | 1.00000 | 1000 |
| acceptance | numeric_tables_removed_delta | -0.89379 | 0.16406 | 1.00000 | 900 |
| acceptance | negativity_car | -0.09476 | 0.65222 | 1.00000 | 1000 |
| acceptance | negativity_bhar | -0.00394 | 0.98637 | 1.00000 | 1000 |
| acceptance | clean_negativity_bhar | -0.00377 | 0.98694 | 1.00000 | 1000 |
