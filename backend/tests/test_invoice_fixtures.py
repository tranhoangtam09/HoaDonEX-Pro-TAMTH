from pathlib import Path
from app.extract import parse_invoice_text,extract
SAMPLE="""1K26TKD
16573
Ký hiệu:
Số:
CÔNG TY CỔ PHẦN THƯƠNG MẠI
DẦU KHÍ ĐỒNG THÁP
Địa chỉ: Số 472 Nguyễn Huệ, phường Mỹ Trà, tỉnh Đồng Tháp, Việt Nam
MST:1400147351
HÓA ĐƠN
Ngày 14 tháng 10 năm 2026
Đơn vị bán hàng:
Họ tên người mua hàng:
Tên đơn vị:
DOANH NGHIỆP TƯ NHÂN KIM TIẾN
Mã số thuế: 1 9 0 0 3 2 5 7 7 1
TÊN HÀNG HÓA, DỊCH VỤ
STT
1 Dầu Điêzen 0,05S Mức 2
(Đơn đặt hàng 83/2026)
I Cộng tiền hàng hóa, dịch vụ: 165.720.000
III. Tổng cộng tiền thanh toán: 165.720.000
"""
def test_realistic_invoice_text():
 x=parse_invoice_text(SAMPLE,"sample.pdf","pdf_text")
 assert x["seller_name"]=="CÔNG TY CỔ PHẦN THƯƠNG MẠI DẦU KHÍ ĐỒNG THÁP"
 assert x["tax_code"]=="1400147351" and x["invoice_number"]=="16573"
 assert x["invoice_date"]=="2026-10-14" and x["total_amount"]==165720000
 assert x["invoice_form"]=="1" and x["invoice_symbol"]=="K26TKD" and x["order_reference"]=="83/2026"
def test_actual_pdf_regression_set_if_present():
 fixtures=Path(__file__).resolve().parents[2]/"fixtures"
 expected={"2026100916460.pdf":("16460","2026-10-09",169320000),"2026101416573(1).pdf":("16573","2026-10-14",165720000),"2026101616689.pdf":("16689","2026-10-16",154320000)}
 for name,(num,day,total) in expected.items():
  p=fixtures/name
  if not p.exists():continue
  x=extract(p.read_bytes(),name)
  assert x["tax_code"]=="1400147351" and x["invoice_number"]==num and x["invoice_date"]==day and x["total_amount"]==total
