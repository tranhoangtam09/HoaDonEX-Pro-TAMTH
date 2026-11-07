from app.extract import number,dateval
from app.validate import validate
def test_number_vietnamese():
 assert number("1.234.567")==1234567
 assert number("1.234.567,89")==1234567.89
def test_date():
 assert dateval("07/11/2026")=="2026-11-07"
def test_validation_flags_missing():
 x=validate({"seller_name":None,"invoice_number":None,"invoice_date":None,"total_amount":None})
 assert not x["is_valid"] and len(x["warnings"])>=4
def test_validation_accepts_consistent():
 x=validate({"seller_name":"ABC","invoice_number":"1","invoice_date":"2026-11-07","subtotal":90,"vat_amount":10,"total_amount":100})
 assert x["is_valid"]
