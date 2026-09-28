# Đối chiếu nghiên cứu gốc với dự án

Nguồn đã đọc trực tiếp ngày 28/09/2026. Kết quả từ nghiên cứu khác không được dùng để thay thế kết quả của Nhóm 5.

## Loughran–McDonald (2011)

Bài gốc: 50.115 10-K (1994–2008), 8.341 công ty. Fin-Neg toàn văn: t=-2,64 (Table IV). Riêng MD&A: tỷ lệ từ t=-0,68; tf.idf t=-1,96, sát ngưỡng (Table V). Thiết kế: buy-and-hold excess return [0,3], CRSP, Fama–MacBeth và Newey–West. R² khoảng 2,6%. Không thấy ý nghĩa ở [0,1] (phụ chú 17). Nguồn: https://www.uts.edu.au/globalassets/sites/default/files/adg_cons2015_loughran-mcdonald-je-2011.pdf (trang tạp chí 52–54).

## Tetlock (2007)

Tetlock phân tích chuyên mục Wall Street Journal, không phải MD&A 10-K. Mức bi quan cao dự báo áp lực giảm giá, sau đó có sự đảo chiều; mức bi quan cực đoan đi cùng khối lượng giao dịch cao. Nguồn bài của tác giả: https://www.columbia.edu/~pt2238/papers/Tetlock_Media_Sentiment_JF.pdf ; trang bài báo: https://onlinelibrary.wiley.com/doi/10.1111/j.1540-6261.2007.01232.x . Không suy từ kết quả tin báo chí sang khẳng định 10-K phải có cùng tín hiệu.

## Nghiên cứu thông tin mềm trong earnings announcements

Demers–Vega, Soft Information in Earnings Announcements: News or Noise?, IFDP 951 (2008): dùng thông báo lợi nhuận, thước đo bất ngờ trong net optimism và earnings surprise; độ chắc chắn trong ngôn ngữ còn liên hệ với biến động riêng của cổ phiếu. Nguồn nghiên cứu: https://www.federalreserve.gov/pubs/ifdp/2008/951/ifdp951.htm . Điều này gợi ý phân biệt mức tone, thông tin mới và văn bản được công bố ở thời điểm nào. Delta theo năm của dự án không đồng nhất surprise theo quý trong nghiên cứu này.

## Diễn giải cho Nhóm 5

Dự án có 500 MD&A của 50 công ty, FY2016–2025; baseline dùng (positive−negative)/total words, không phải tỷ lệ Fin-Neg riêng. Baseline hiện hành sau sửa ranh giới p=0.837558; các mô hình delta và controls xem EXPANDED_RESULTS.md. Kết quả không có ý nghĩa thống kê không tự chứng minh parser sai và cũng không chứng minh ngôn ngữ tài chính vô ích. Mẫu có chủ đích doanh nghiệp lớn, phạm vi chương MD&A và dữ liệu giá công khai là các giới hạn.

Nếu triển khai đối chứng sát bài gốc, cần định trước negativity riêng, toàn bộ nội dung 10-K với quy tắc làm sạch thống nhất, cửa sổ [0,3] và cách tính excess return tương ứng. Các đối chứng ấy phải được báo cáo dù không có ý nghĩa, giữ baseline hiện tại và không gọi là tái lập chính xác khi chưa có CRSP/Compustat hoặc cùng mẫu, biến kiểm soát và bộ từ điển lịch sử.
