from app.extract import _parse_pdf_layout, blank

class FakePage:
    def __init__(self, blocks): self.blocks=blocks
    def get_text(self, mode): return self.blocks

class FakeDocument:
    def __init__(self, pages): self.pages=pages
    def __iter__(self): return iter(self.pages)
    def __getitem__(self, index): return self.pages[index]
    def __len__(self): return len(self.pages)
    def close(self): pass

def block(y,x,text):
    return (x,y,x+500,y+12,text,0,0)

def install_fake_pdf(monkeypatch, two_pages=False):
    page1=FakePage([
        block(36,130,"CÔNG TY TNHH THƯƠNG MẠI - DỊCH VỤ - SẢN XUẤT NGỌC TRAI"),
        block(53,130,"4200410988 Mã số thuế"),
        block(121,50,"Đơn vị bán hàng: CHI NHÁNH CÔNG TY TNHH THƯƠNG MẠI-DỊCH VỤ-SẢN XUẤT"),
        block(136,297,"NGỌC TRAI"),
        block(153,50,"4200410988-001 Mã số thuế Địa chỉ"),
        block(212,207,"Ký hiệu (Sign): 1C26TNT"),
        block(230,390,"Số (No): 00001036"),
        block(266,126,"Ngày 06 tháng 07 năm 2026"),
        block(317,50,"CÔNG TY TNHH MỘT THÀNH VIÊN TÔM GIỐNG HOÀNG LỘC Tên đơn vị"),
        block(334,50,"1900563381 Mã số thuế"),
        block(450,70,"Air Switch 100 pcs/50 bags/ctn GÓI 10,000 220.370 2.203.704 1"),
    ])
    if two_pages:
        page2=FakePage([
            block(530,245,"Cộng tiền hàng: 180.777.500"),
            block(547,55,"Thuế suất GTGT: KCT 0 Tiền thuế GTGT"),
            block(564,245,"180.777.500 Tổng tiền thanh toán"),
        ])
        pages=[page1,page2]
    else:
        pages=[page1,FakePage([
            block(530,245,"Cộng tiền hàng: 2.203.704"),
            block(547,55,"Thuế suất GTGT: 8 % 176.296 Tiền thuế GTGT"),
            block(564,245,"2.380.000 Tổng tiền thanh toán"),
        ])]
    monkeypatch.setattr("app.extract.fitz.open",lambda *args,**kwargs:FakeDocument(pages))

def test_meinvoice_branch_uses_branch_tax_id_not_parent_tax_id(monkeypatch):
    install_fake_pdf(monkeypatch)
    parsed=_parse_pdf_layout(b"test",blank("branch.pdf","pdf_text"))
    assert parsed["seller_name"]=="CHI NHÁNH CÔNG TY TNHH THƯƠNG MẠI-DỊCH VỤ-SẢN XUẤT NGỌC TRAI"
    assert parsed["tax_code"]=="4200410988001"
    assert parsed["buyer_name"]=="CÔNG TY TNHH MỘT THÀNH VIÊN TÔM GIỐNG HOÀNG LỘC"
    assert parsed["buyer_tax_code"]=="1900563381"
    assert parsed["invoice_symbol"]=="C26TNT"
    assert parsed["invoice_number"]=="00001036"
    assert parsed["invoice_date"]=="2026-07-06"
    assert parsed["total_amount"]==2380000
    assert parsed["subtotal"]==2203704
    assert parsed["vat_amount"]==176296

def test_meinvoice_two_page_total_is_read_from_page_two_and_zero_vat_is_preserved(monkeypatch):
    install_fake_pdf(monkeypatch,two_pages=True)
    parsed=_parse_pdf_layout(b"test",blank("two_pages.pdf","pdf_text"))
    assert parsed["invoice_number"]=="00001036"
    assert parsed["total_amount"]==180777500
    assert parsed["subtotal"]==180777500
    assert parsed["vat_amount"]==0
