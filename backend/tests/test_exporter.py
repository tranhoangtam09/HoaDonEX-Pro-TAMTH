from pathlib import Path
import pytest
from openpyxl import load_workbook
from app.exporter import export_workbook
ROOT=Path(__file__).resolve().parents[1]/"templates"
def base_item():
 return {"filename":"a.pdf","seller_name":"Công ty bán A","tax_code":"1234567890","buyer_name":"Doanh nghiệp mua B","buyer_tax_code":"0987654321","beneficiary_account":"123456","invoice_form":"1","invoice_symbol":"K26TKD","invoice_number":"99","invoice_date":"2026-10-09","total_amount":123000,"currency":"VND","item_description":"Hàng hóa","financing_amount":100000,"is_valid":True}
def test_template_workbooks_have_original_sheet_names_and_widths():
 for name,sheet,cols in [("Bang_ke_hoa_don_chuyen_khoan_VND.xlsx","Bảng kê hóa đơn",12),("Bang_ke_hoa_don_bu_dap_VND.xlsx","Bảng kê hóa đơn GN bù đắp",13)]:
  p=ROOT/name
  if not p.exists():pytest.skip("Original workbook templates provisioned separately")
  wb=load_workbook(p);ws=wb[sheet]
  assert ws.max_column==cols and ws["A2"].value=="STT"
def test_transfer_exact_12_column_mapping():
 if not (ROOT/"Bang_ke_hoa_don_chuyen_khoan_VND.xlsx").exists():pytest.skip("Original workbook template provisioned separately")
 out=export_workbook([base_item()],"transfer");wb=load_workbook(out);ws=wb["Bảng kê hóa đơn"]
 assert [ws.cell(3,c).value for c in range(1,13)]==[1,"0987654321","Doanh nghiệp mua B","123456","1","K26TKD","99","09/10/2026",123000,"VND","Hàng hóa",100000]
 assert wb.sheetnames==["Bảng kê hóa đơn","Hướng dẫn nhập liệu"]
def test_compensation_exact_13_column_mapping_and_no_guessed_payments():
 if not (ROOT/"Bang_ke_hoa_don_bu_dap_VND.xlsx").exists():pytest.skip("Original workbook template provisioned separately")
 x=base_item();x["payment_date"]=None;x["payment_amount"]=None
 out=export_workbook([x],"compensation");wb=load_workbook(out);ws=wb["Bảng kê hóa đơn GN bù đắp"]
 assert [ws.cell(3,c).value for c in range(1,14)]==[1,"1234567890","Công ty bán A","1","K26TKD","99","09/10/2026",123000,"VND","Hàng hóa",100000,None,None]
 assert wb.sheetnames==["Bảng kê hóa đơn GN bù đắp","Hướng dẫn nhập liệu"]

def test_transfer_export_allows_missing_fields_and_leaves_cells_blank():
 if not (ROOT/"Bang_ke_hoa_don_chuyen_khoan_VND.xlsx").exists():pytest.skip("Original workbook template provisioned separately")
 x=base_item()
 x["buyer_name"]=None
 x["buyer_tax_code"]=None
 x["beneficiary_account"]=None
 x["invoice_number"]=None
 x["invoice_date"]=None
 x["total_amount"]=None
 x["financing_amount"]=None
 out=export_workbook([x],"transfer")
 wb=load_workbook(out);ws=wb["Bảng kê hóa đơn"]
 assert ws["A3"].value==1
 assert ws["B3"].value is None
 assert ws["C3"].value is None
 assert ws["D3"].value is None
 assert ws["G3"].value is None
 assert ws["H3"].value is None
 assert ws["I3"].value is None
 assert ws["L3"].value is None

def test_compensation_export_allows_missing_payment_and_invoice_fields():
 if not (ROOT/"Bang_ke_hoa_don_bu_dap_VND.xlsx").exists():pytest.skip("Original workbook template provisioned separately")
 x=base_item()
 x["seller_name"]=None
 x["tax_code"]=None
 x["invoice_number"]=None
 x["invoice_date"]=None
 x["total_amount"]=None
 x["financing_amount"]=None
 x["payment_date"]=None
 x["payment_amount"]=None
 out=export_workbook([x],"compensation")
 wb=load_workbook(out);ws=wb["Bảng kê hóa đơn GN bù đắp"]
 assert ws["A3"].value==1
 for cell in ("B3","C3","F3","G3","H3","K3","L3","M3"):
  assert ws[cell].value is None
