from app.extract import number,parse_date,parse_invoice_text
from app.validate import validate,validate_for_export
def test_number_vietnamese():
 assert number("1.234.567")==1234567
 assert number("1.234.567,89")==1234567.89
def test_vietnamese_date():
 assert parse_date("07/11/2026")=="2026-11-07"
 assert parse_date("Ngày 14 tháng 10 năm 2026")=="2026-10-14"
def test_split_invoice_symbol_and_form():
 x=parse_invoice_text("1K26TKD\n16573\nNgày 14 tháng 10 năm 2026","sample.pdf","pdf_text")
 assert x["invoice_form"]=="1" and x["invoice_symbol"]=="K26TKD" and x["invoice_number"]=="16573"
def test_validation_flags_missing():
 x=validate({"seller_name":None,"tax_code":None,"invoice_form":None,"invoice_symbol":None,"invoice_number":None,"invoice_date":None,"total_amount":None})
 assert not x["is_valid"] and len(x["warnings"])>=7
def test_financing_amount_is_never_inferred():
 x={"filename":"a.pdf","seller_name":"A","tax_code":"1234567890","invoice_form":"1","invoice_symbol":"K26TKD","invoice_number":"1","invoice_date":"2026-11-07","total_amount":100000,"currency":"VND","item_description":"Fuel"}
 ok,missing=validate_for_export(x,"compensation")
 assert ok and "financing_amount" in missing
