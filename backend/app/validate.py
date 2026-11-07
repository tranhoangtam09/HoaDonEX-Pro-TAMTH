import re,datetime
def validate(x):
 w=list(x.get("warnings") or [])
 for k,label in [("seller_name","Tên đơn vị phát hành"),("tax_code","Mã số thuế"),("invoice_form","Ký hiệu mẫu số"),("invoice_symbol","Ký hiệu hóa đơn"),("invoice_number","Số hóa đơn"),("invoice_date","Ngày hóa đơn"),("total_amount","Số tiền hóa đơn")]:
  if x.get(k) in (None,""):w.append("Thiếu trường: "+label)
 tax=x.get("tax_code")
 if tax and not re.fullmatch(r"\d{10}(?:\d{3})?",str(tax)):w.append("Mã số thuế cần kiểm tra định dạng.")
 if x.get("invoice_date"):
  try:datetime.date.fromisoformat(x["invoice_date"])
  except Exception:w.append("Ngày hóa đơn không hợp lệ.")
 a,b,t=x.get("subtotal"),x.get("vat_amount"),x.get("total_amount")
 if None not in (a,b,t) and abs(float(a)+float(b)-float(t))>1:w.append("Tổng tiền không khớp tiền hàng + thuế.")
 x["warnings"]=list(dict.fromkeys(w));x["is_valid"]=not x["warnings"];return x
def validate_for_export(x,kind):
 x=validate(dict(x));required=["seller_name","tax_code","invoice_form","invoice_symbol","invoice_date","total_amount","financing_amount","currency","item_description"]
 if kind=="transfer":required+=["beneficiary_account"]
 missing=[k for k in required if x.get(k) in (None,"")]
 if missing:return False,missing
 if kind=="compensation" and x.get("payment_amount") not in (None,"") and not x.get("payment_date"):return False,["payment_date"]
 return True,[]
