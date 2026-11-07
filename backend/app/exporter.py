from io import BytesIO
from .config import TEMPLATES
from openpyxl import load_workbook
from fastapi import HTTPException
FILES={"transfer":"Bang_ke_hoa_don_chuyen_khoan_VND.xlsx","compensation":"Bang_ke_hoa_don_bu_dap_VND.xlsx"}
ALIASES={"tên đơn vị phát hành hóa đơn":"seller_name","tên đơn vị phát hành":"seller_name","tên người bán":"seller_name","mã số thuế":"tax_code","số hóa đơn":"invoice_number","ký hiệu hóa đơn":"invoice_symbol","ngày hóa đơn":"invoice_date","địa chỉ":"seller_address","số tiền hóa đơn":"total_amount","tổng tiền thanh toán":"total_amount","tiền trước thuế":"subtotal","tiền thuế":"vat_amount"}
def make(items,kind):
 if kind not in FILES:raise HTTPException(400,"Loại bảng kê không hợp lệ")
 p=TEMPLATES/FILES[kind]
 if not p.exists():raise HTTPException(400,"Thiếu mẫu Excel: "+p.name+" (đặt mẫu trống vào backend/templates/)")
 bad=[x["filename"] for x in items if not x.get("is_valid")]
 if bad:raise HTTPException(400,"Hồ sơ cần rà soát trước khi xuất: "+", ".join(bad[:5]))
 wb=load_workbook(p);ws=wb.active;heads={str(c.value).strip().lower():c.column for row in ws.iter_rows(min_row=1,max_row=min(15,ws.max_row)) for c in row if c.value};cols={}
 for h,col in heads.items():
  for alias,k in ALIASES.items():
   if alias in h:cols[k]=col
 if not cols:raise HTTPException(400,"Không nhận diện được tiêu đề cột trong mẫu Excel; cần map đúng mẫu.")
 for ri,x in enumerate(items,max(ws.max_row+1,2)):
  for k,col in cols.items():ws.cell(ri,col).value=x.get(k)
 b=BytesIO();wb.save(b);b.seek(0);return b
