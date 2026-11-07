import re,datetime

def validate(x):
 w=list(x.get("warnings") or [])
 if x.get("user_reviewed"):
  # Recompute extraction/validation warnings after the operator has corrected fields.
  stale=("OCR","Chưa cài OCR","Chưa tách được ký hiệu","Thiếu trường:","cần kiểm tra định dạng","không hợp lệ","Tổng tiền không khớp")
  w=[m for m in w if not any(token.lower() in m.lower() for token in stale)]
 for k,label in [("seller_name","Tên đơn vị phát hành"),("tax_code","Mã số thuế"),("invoice_form","Ký hiệu mẫu số"),("invoice_symbol","Ký hiệu hóa đơn"),("invoice_number","Số hóa đơn"),("invoice_date","Ngày hóa đơn"),("total_amount","Số tiền hóa đơn")]:
  if x.get(k) in (None,""):w.append("Thiếu trường: "+label)
 for key,label in [("tax_code","Mã số thuế đơn vị phát hành"),("buyer_tax_code","Mã số thuế đơn vị thụ hưởng")]:
  tax=x.get(key)
  if tax and not re.fullmatch(r"\d{10}(?:\d{3})?",str(tax)):w.append(label+" cần kiểm tra định dạng.")
 for key,label in [("invoice_date","Ngày hóa đơn"),("payment_date","Ngày đã thanh toán")]:
  if x.get(key):
   try:datetime.date.fromisoformat(str(x[key]))
   except Exception:w.append(label+" không hợp lệ.")
 a,b,t=x.get("subtotal"),x.get("vat_amount"),x.get("total_amount")
 if None not in (a,b,t) and abs(float(a)+float(b)-float(t))>1:w.append("Tổng tiền không khớp tiền hàng + thuế.")
 x["warnings"]=list(dict.fromkeys(w));x["is_valid"]=not x["warnings"]
 return x

def validate_for_export(x,kind):
 """Exports are permissive: missing fields are warnings, never export blockers."""
 if kind not in ("transfer","compensation"):
  return False,["Loại bảng kê không hợp lệ."]
 x=validate(dict(x))
 required=(
  ["buyer_name","buyer_tax_code","beneficiary_account","invoice_form","invoice_symbol","invoice_number","invoice_date","total_amount","financing_amount","currency","item_description"]
  if kind=="transfer" else
  ["seller_name","tax_code","invoice_form","invoice_symbol","invoice_number","invoice_date","total_amount","financing_amount","currency","item_description","payment_date","payment_amount"]
 )
 missing=[k for k in required if x.get(k) in (None,"")]
 return True,missing
