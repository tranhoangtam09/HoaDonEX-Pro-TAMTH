# HOA DON EX PRO – TAMTH

Ứng dụng độc lập hỗ trợ nhập hóa đơn điện tử/tệp scan, trích xuất dữ liệu, rà soát thủ công và xuất bảng kê Excel.

## Thành phần
- `frontend/`: giao diện web tĩnh, triển khai GitHub Pages/Cloudflare Pages.
- `backend/`: API FastAPI, xử lý PDF/XML/ảnh/ZIP, SQLite, xuất Excel.
- `backend/templates/`: đặt hai mẫu Excel trống đã làm sạch dữ liệu:
  - `Bang_ke_hoa_don_chuyen_khoan_VND.xlsx`
  - `Bang_ke_hoa_don_bu_dap_VND.xlsx`

## Chạy backend (Python 3.11+)
```bash
cd backend
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```
API: `http://127.0.0.1:8000`; tài liệu: `/docs`.

## Chạy giao diện
Mở `frontend/index.html`, vào Cấu hình và nhập URL API (mặc định `http://127.0.0.1:8000`).

## Lưu ý
Không cam kết trích xuất chính xác 100%. Người dùng phải kiểm tra các trường trước khi xuất. Mẫu Excel và hóa đơn thực không được đưa vào repo công khai. Trước khi dùng dữ liệu nghiệp vụ thật, hãy triển khai backend có HTTPS, xác thực, giới hạn dung lượng/tần suất, quét mã độc, chính sách lưu/xóa dữ liệu và kiểm thử thực tế.
