# HOA DON EX PRO – TAMTH

Ứng dụng xử lý hóa đơn PDF/XML/ảnh, rà soát dữ liệu và xuất hai mẫu bảng kê Excel gốc. Phiên bản triển khai theo kiến trúc **0 đồng phí máy chủ**: giao diện tĩnh trên GitHub Pages; backend, OCR, cơ sở dữ liệu và mẫu Excel chạy trên máy tính Windows của người sử dụng.

## Mô hình sử dụng miễn phí
- Giao diện: GitHub Pages (miễn phí cho repository public).
- Backend: FastAPI chạy tại `http://127.0.0.1:8000` trên máy tính của bạn.
- Cơ sở dữ liệu SQLite và hai mẫu Excel: lưu cục bộ trong `backend/data/`.
- Không cần Render, VPS, server thuê bao hoặc ổ đĩa đám mây trả phí.
- Khi tắt máy hoặc đóng cửa sổ backend, chức năng phân tích/xuất sẽ tạm dừng; website giao diện vẫn truy cập được.

## Cài đặt trên Windows
1. Cài Python 3.11 (đánh dấu **Add Python to PATH** khi cài).
2. Tải repository về máy và giải nén.
3. Chạy `start_windows.bat` trong thư mục gốc. Lần đầu, script tạo môi trường ảo và cài thư viện cần thiết.
4. Cài OCR PaddleOCR theo hướng dẫn hiển thị trong cửa sổ nếu cần đọc PDF scan hoặc ảnh. Việc cài OCR cần kết nối Internet và có thể tải mô hình khá lớn.
5. Giữ cửa sổ backend mở khi sử dụng. Mở website GitHub Pages hoặc mở `frontend/index.html`.
6. Địa chỉ API mặc định là `http://127.0.0.1:8000`; bấm **Lưu kết nối** nếu giao diện chưa tự kết nối.
7. Tại mục **Nạp hai mẫu Excel gốc**, nạp hai workbook mẫu do đơn vị cung cấp.

Tài liệu API: `http://127.0.0.1:8000/docs`.

## Thành phần và chức năng
- PDF có text layer: trích xuất trực tiếp trước, OCR bổ sung khi thiếu trường quan trọng.
- XML hóa đơn: đọc dữ liệu có cấu trúc, gồm người bán, người mua, số/ngày hóa đơn và tổng tiền.
- PDF scan/ảnh JPG, PNG, TIFF, WEBP: OCR tiếng Việt PaddleOCR (cài thêm).
- ZIP: giải nén và tiếp nhận nhiều hóa đơn trong một lần.
- Rà soát, chỉnh sửa thông tin người bán/người mua, MST, số/ngày hóa đơn, tài khoản thụ hưởng, số tiền nhận nợ và thanh toán.
- Xuất Excel theo đúng workbook gốc, giữ sheet hướng dẫn, cấu trúc cột và định dạng.

## Hai mẫu Excel gốc
Nạp hai file mẫu qua giao diện:
- Mẫu chuyển khoản: sheet `Bảng kê hóa đơn`, 12 cột A:L.
- Mẫu bù đắp: sheet `Bảng kê hóa đơn GN bù đắp`, 13 cột A:M.

Các trường tài khoản thụ hưởng, số tiền nhận nợ, ngày thanh toán và số tiền thanh toán không được tự suy ra từ hóa đơn; người dùng cần nhập theo hồ sơ/chứng từ thực tế. Backend kiểm tra cấu trúc mẫu trước khi lưu.

## Triển khai giao diện GitHub Pages
Workflow `.github/workflows/pages.yml` xuất bản thư mục `frontend/` lên GitHub Pages khi có cập nhật nhánh `main`. Nếu Pages chưa được bật tự động, vào **Settings → Pages → Build and deployment → Source: GitHub Actions**. Địa chỉ website dự kiến: `https://tranhoangtam09.github.io/HoaDonEX-Pro-TAMTH/`.

## Dữ liệu và bảo mật
- Hóa đơn và SQLite được lưu trong `backend/data/`; mẫu Excel ở `backend/data/templates/`. Sao lưu thư mục này định kỳ.
- Backend mặc định không bật API key vì chỉ lắng nghe localhost. Không thay host thành `0.0.0.0` hoặc mở cổng router nếu chưa cấu hình xác thực và bảo mật.
- Website Pages chỉ là giao diện; trình duyệt kết nối đến backend localhost. Không có hóa đơn nào được gửi lên GitHub Pages qua kiến trúc này.
- OCR có thể sai. Luôn đối chiếu thông tin với hóa đơn gốc; không có cam kết nhận dạng chính xác 100%.
- Trước khi sử dụng chính thức, cần kiểm thử trên bộ hóa đơn thực tế, xác nhận mẫu Excel và tuân thủ quy định bảo mật dữ liệu của đơn vị.

## Kiểm thử
Từ thư mục `backend`:
```bash
python -m venv .venv
.venv\\Scripts\\activate
pip install -r requirements.txt pytest
pytest -q
node --check ../frontend/app.js
```


## Cập nhật chức năng 1.2
- Khi nạp một lô hóa đơn mới, hệ thống đọc toàn bộ lô trước; nếu đọc thành công mới thay thế danh sách cũ. Nếu lô mới bị lỗi, dữ liệu cũ được giữ nguyên.
- Có thể xóa từng hồ sơ hoặc xóa hàng loạt hồ sơ không nhận dạng đủ tên đơn vị phát hành, số hóa đơn và ngày hóa đơn.
- Chọn tối đa 10 hồ sơ PDF/ảnh để gộp thành một PDF. Thứ tự trang theo thứ tự chọn. XML không thể gộp trực tiếp; cần chuyển XML sang PDF trước.
- Tệp gốc được lưu trong thư mục dữ liệu cục bộ để hỗ trợ gộp PDF. Sao lưu toàn bộ thư mục dữ liệu trước khi chuyển máy hoặc cài lại.
- Giao diện mới có bảng rà soát, bộ đếm chọn hồ sơ và thao tác xóa/gộp. Thời gian OCR phụ thuộc số trang, chất lượng ảnh và cấu hình máy tính.
