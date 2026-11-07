import datetime
import fitz
from app.extract import _parse_pdf_layout, blank

def build_meinvoice_branch_pdf(two_pages=False, tax_zero=False):
    doc=fitz.open()
    p=doc.new_page(width=620,height=820)
    lines=[
        (36,130,"CÔNG TY TNHH THƯƠNG MẠI - DỊCH VỤ - SẢN XUẤT NGỌC TRAI"),
        (53,130,"MST: 4200410988"),
        (121,50,"Đơn vị bán hàng: CHI NHÁNH CÔNG TY TNHH THƯƠNG MẠI-DỊCH VỤ-SẢN XUẤT"),
        (136,297,"NGỌC TRAI"),
        (153,50,"Mã số thuế: 4200410988-001"),
        (212,207,"Ký hiệu: 1C26TNT"),
        (230,390,"Số: 00001036"),
        (266,126,"Ngày 06 tháng 07 năm 2026"),
        (317,50,"CÔNG TY TNHH MỘT THÀNH VIÊN TÔM GIỐNG HOÀNG LỘC Tên đơn vị"),
        (334,50,"Mã số thuế: 1900563381"),
        (450,70,"Air Switch 100 pcs/50 bags/ctn GÓI 10,000 220.370 2.203.704 1"),
    ]
    for y,x,text in lines:p.insert_text((x,y),text,fontsize=9)
    if two_pages:
        p2=doc.new_page(width=620,height=820)
        p2.insert_text((245,530),"Cộng tiền hàng: 180.777.500",fontsize=10)
        p2.insert_text((55,547),"Thuế suất GTGT: KCT 0 Tiền thuế GTGT",fontsize=10)
        p2.insert_text((245,564),"180.777.500 Tổng tiền thanh toán",fontsize=10)
    else:
        p.insert_text((245,530),"Cộng tiền hàng: 2.203.704",fontsize=10)
        p.insert_text((55,547),"Thuế suất GTGT: 8 % 176.296 Tiền thuế GTGT",fontsize=10)
        p.insert_text((245,564),"2.380.000 Tổng tiền thanh toán",fontsize=10)
    raw=doc.tobytes()
    doc.close()
    return raw

def test_meinvoice_branch_uses_branch_tax_id_not_parent_tax_id():
    x=blank("branch.pdf","pdf_text")
    parsed=_parse_pdf_layout(build_meinvoice_branch_pdf(),x)
    assert parsed["seller_name"]=="CHI NHÁNH CÔNG TY TNHH THƯƠNG MẠI-DỊCH VỤ-SẢN XUẤT NGỌC TRAI"
    assert parsed["tax_code"]=="4200410988001"
    assert parsed["buyer_name"]=="CÔNG TY TNHH MỘT THÀNH VIÊN TÔM GIỐNG HOÀNG LỘC"
    assert parsed["buyer_tax_code"]=="1900563381"
    assert parsed["invoice_symbol"]=="C26TNT"
    assert parsed["invoice_number"]=="00001036"
    assert parsed["invoice_date"]=="2026-07-06"
    assert parsed["total_amount"]==2380000

def test_meinvoice_two_page_total_is_read_from_page_two_and_zero_vat_is_preserved():
    x=blank("two_pages.pdf","pdf_text")
    parsed=_parse_pdf_layout(build_meinvoice_branch_pdf(two_pages=True,tax_zero=True),x)
    assert parsed["invoice_number"]=="00001036"
    assert parsed["total_amount"]==180777500
    assert parsed["subtotal"]==180777500
    assert parsed["vat_amount"]==0
