from io import BytesIO
from copy import copy
from datetime import date
from openpyxl import load_workbook
from fastapi import HTTPException
from .config import TEMPLATES
TEMPLATE_FILES={"transfer":"Bang_ke_hoa_don_chuyen_khoan_VND.xlsx","compensation":"Bang_ke_hoa_don_bu_dap_VND.xlsx"}
SHEET_NAMES={"transfer":"Bảng kê hóa đơn","compensation":"Bảng kê hóa đơn GN bù đắp"}
def _date_text(v):
 if not v:return None
 if isinstance(v,date):return v.strftime("%d/%m/%Y")
 try:return date.fromisoformat(str(v)).strftime("%d/%m/%Y")
 except ValueError:raise HTTPException(400,"Ngày hóa đơn phải đúng định dạng YYYY-MM-DD trước khi xuất.")
def _copy_row_style(ws,source_row,target_row):
 if target_row==source_row:return
 for col in range(1,ws.max_column+1):
  src=ws.cell(source_row,col);dst=ws.cell(target_row,col)
  if src.has_style:dst._style=copy(src._style)
  if src.number_format:dst.number_format=src.number_format
  if src.alignment:dst.alignment=copy(src.alignment)
  if src.protection:dst.protection=copy(src.protection)
 if source_row in ws.row_dimensions:ws.row_dimensions[target_row].height=ws.row_dimensions[source_row].height
def export_workbook(items,kind):
 if kind not in TEMPLATE_FILES:raise HTTPException(400,"Loại bảng kê không hợp lệ.")
 template=TEMPLATES/TEMPLATE_FILES[kind]
 if not template.exists():raise HTTPException(400,"Máy chủ chưa được cấu hình mẫu Excel gốc: "+TEMPLATE_FILES[kind])
 from .validate import validate_for_export
 errors=[]
 for item in items:
  ok,missing=validate_for_export(item,kind)
  if not ok:errors.append(f"{item.get('filename','Hồ sơ')}: {', '.join(missing)}")
 if errors:raise HTTPException(422,"Chưa đủ thông tin để xuất bảng kê. "+" | ".join(errors[:8]))
 wb=load_workbook(template);sheet=SHEET_NAMES[kind]
 if sheet not in wb.sheetnames:raise HTTPException(500,"Tên sheet trong mẫu gốc không đúng: "+sheet)
 ws=wb[sheet];first_data_row=3;style_row=3
 for row in range(first_data_row,ws.max_row+1):
  for col in range(1,ws.max_column+1):ws.cell(row,col).value=None
 for i,x in enumerate(items):
  r=first_data_row+i
  if r>style_row:_copy_row_style(ws,style_row,r)
  if kind=="transfer":
   values=[i+1,x.get("buyer_tax_code"),x.get("buyer_name"),x.get("beneficiary_account"),x.get("invoice_form"),x.get("invoice_symbol"),x.get("invoice_number") or x.get("order_reference"),_date_text(x.get("invoice_date")),x.get("total_amount"),x.get("currency"),x.get("item_description"),x.get("financing_amount")]
  else:
   values=[i+1,x.get("tax_code"),x.get("seller_name"),x.get("invoice_form"),x.get("invoice_symbol"),x.get("invoice_number") or x.get("order_reference"),_date_text(x.get("invoice_date")),x.get("total_amount"),x.get("currency"),x.get("item_description"),x.get("financing_amount"),_date_text(x.get("payment_date")),x.get("payment_amount")]
  for col,value in enumerate(values,1):ws.cell(r,col).value=value
 out=BytesIO();wb.save(out);out.seek(0);return out
