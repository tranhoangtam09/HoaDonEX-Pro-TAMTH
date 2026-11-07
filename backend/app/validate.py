import re,datetime
def validate(x):
 w=list(x.get("warnings") or [])
 for k in ("seller_name","invoice_number","invoice_date","total_amount"):
  if x.get(k) in (None,""):w.append("Thiếu trường bắt buộc: "+k)
 tax=x.get("tax_code")
 if tax and not re.fullmatch(r"\d{10}(?:-\d{3})?",str(tax)):w.append("Mã số thuế cần kiểm tra.")
 if x.get("invoice_date"):
  try:datetime.date.fromisoformat(x["invoice_date"])
  except Exception:w.append("Ngày hóa đơn không hợp lệ.")
 a,b,t=x.get("subtotal"),x.get("vat_amount"),x.get("total_amount")
 if None not in (a,b,t) and abs(float(a)+float(b)-float(t))>1:w.append("Tổng tiền không khớp tiền hàng + thuế.")
 x["warnings"]=list(dict.fromkeys(w));x["is_valid"]=not x["warnings"];return x
