# HOA DON EX PRO – TAMTH

Ứng dụng độc lập xử lý hóa đơn PDF/XML/ảnh, rà soát dữ liệu và xuất đúng hai mẫu bảng kê Excel gốc.

## Thành phần
- frontend/: giao diện web tiếng Việt, có cấu hình API và nạp hai mẫu Excel.
- backend/: FastAPI, SQLite, trích xuất PDF/XML, OCR tiếng Việt PaddleOCR.
- backend/templates/: thư mục mẫu mặc định; trên máy chủ có thể đặt mẫu tại TEMPLATES_DIR.

## Chạy thử cục bộ
Từ thư mục backend:
```bash
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
pip install -r requirements-ocr.txt
uvicorn app.main:app --reload
```
Mở frontend/index.html bằng trình duyệt và cấu hình URL API. Tài liệu API ở /docs.

## OCR và nhận dạng
PDF có text layer được trích xuất trước. Nếu thiếu trường trọng yếu hoặc là PDF scan, backend chuyển sang PaddleOCR với mã ngôn ngữ vi; ảnh JPG/PNG cũng được xử lý qua OCR. OCR chỉ là bước nhận dạng, không phải xác minh pháp lý; người dùng phải kiểm tra ảnh gốc.

## Hai mẫu Excel gốc
Trong giao diện có mục “Nạp hai mẫu Excel gốc”. Nạp đúng hai file:
- Bang_ke_hoa_don_chuyen_khoan_VND.xlsx
- Bang_ke_hoa_don_bu_dap_VND.xlsx

Backend xác thực sheet, hàng tiêu đề và số cột trước khi lưu vào ổ đĩa bền vững.
- Chuyển khoản: sheet “Bảng kê hóa đơn”, 12 cột A:L.
- Bù đắp: sheet “Bảng kê hóa đơn GN bù đắp”, 13 cột A:M.

Các cột số tiền nhận nợ, tài khoản thụ hưởng, ngày thanh toán và số tiền đã thanh toán không được tự suy ra từ tổng tiền hóa đơn. Người dùng phải nhập đúng theo hồ sơ tín dụng/chứng từ thanh toán. Bản xuất giữ nguyên workbook, sheet hướng dẫn, định dạng và cấu trúc mẫu.

## Triển khai trực tuyến
- Backend: Render Blueprint từ render.yaml; dịch vụ cần ổ đĩa bền vững để giữ SQLite và hai mẫu Excel.
- Frontend: GitHub Pages qua workflow .github/workflows/pages.yml.
- API_KEY được Render tạo tự động; nhập key vào phần Cấu hình API của frontend. Không đưa key vào mã nguồn.

Lần đầu chạy OCR có thể tải mô hình nhận dạng nên cần thời gian và bộ nhớ. Cần kiểm thử tải thực tế trước khi dùng quy trình nghiệp vụ thường xuyên.

## Giới hạn và an toàn
Không cam kết chính xác 100%. Chưa có xác minh dữ liệu với cơ quan thuế, chữ ký số hay ngân hàng. API key dùng chung là lớp bảo vệ cơ bản, không thay thế đăng nhập phân quyền từng người dùng. Không tải hóa đơn thật lên môi trường công khai khi chưa kiểm tra HTTPS, quyền truy cập, chính sách lưu/xóa, sao lưu và tuân thủ bảo mật nội bộ.
