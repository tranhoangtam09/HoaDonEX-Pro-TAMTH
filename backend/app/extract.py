from pathlib import Path
import re,datetime,fitz,xml.etree.ElementTree as ET
def blank(name,kind):return {"filename":name,"source_type":kind,"seller_name":None,"seller_address":None,"tax_code":None,"invoice_symbol":None,"invoice_number":None,"invoice_date":None,"subtotal":None,"vat_amount":None,"total_amount":None,"currency":"VND","review_note":"Cần kiểm tra đối chiếu bản gốc.","is_valid":False,"warnings":[]}
def dateval(s):
 if not s:return None
 for f in ("%d/%m/%Y","%d-%m-%Y","%Y-%m-%d"):
  try:return datetime.datetime.strptime(s.strip(),f).date().isoformat()
  except ValueError:pass
 return None
def number(v):
 if not v:return None
 s=re.sub(r"[^0-9,.-]","",str(v))
 if "," in s and "." in s:s=s.replace(".","").replace(",",".") if s.rfind(",")>s.rfind(".") else s.replace(",","")
 elif "," in s:s=s.replace(",",".") if len(s.rsplit(",",1)[-1])<=2 else s.replace(",","")
 try:return float(s)
 except ValueError:return None
def xml_extract(data,name):
 root=ET.fromstring(data);d={}
 for e in root.iter():
  k=e.tag.split("}")[-1].lower();v=(e.text or "").strip()
  if v:d.setdefault(k,v)
 def pick(*keys):
  for key in keys:
   for k,v in d.items():
    if key in k:return v
 def amt(*keys):return number(pick(*keys))
 x=blank(name,"xml")
 x.update(seller_name=pick("tenseller","tendonvi","sellername","tennguoiban"),seller_address=pick("diachi","selleraddress"),tax_code=pick("masothue","taxcode","mst"),invoice_symbol=pick("kyhieu","invoiceform"),invoice_number=pick("sohoadon","invoiceno"),invoice_date=dateval(pick("ngayhoadon","ngaylap","issuedate")),subtotal=amt("tongtienchuathue","congtienhang","subtotal"),vat_amount=amt("tongtienthue","tienthue","vatamount"),total_amount=amt("tongthanhtoan","tongtien","totalamount"))
 return x
def pdf_extract(data,name):
 doc=fitz.open(stream=data,filetype="pdf");t="\n".join(p.get_text() for p in doc);x=blank(name,"pdf")
 pats={"tax_code":r"(?:Mã số thuế|MST)\s*[:：]?\s*([0-9-]{10,14})","invoice_number":r"(?:Số hóa đơn|Số HĐ)\s*[:：]?\s*(\d+)","invoice_symbol":r"(?:Ký hiệu|Ký hiệu mẫu số)\s*[:：]?\s*([0-9A-Z/.-]+)","invoice_date":r"(?:Ngày|Date)\s*(?:lập hóa đơn)?\s*[:：]?\s*(\d{1,2}[/-]\d{1,2}[/-]\d{4})"}
 for k,p in pats.items():
  m=re.search(p,t,re.I)
  if m:x[k]=dateval(m.group(1)) if k=="invoice_date" else m.group(1)
 for p,k in [(r"(?:Tên đơn vị bán hàng|Tên người bán|Đơn vị bán hàng)\s*[:：]?\s*([^\n]+)","seller_name"),(r"Địa chỉ\s*[:：]?\s*([^\n]+)","seller_address")]:
  m=re.search(p,t,re.I)
  if m:x[k]=m.group(1).strip()
 for p,k in [(r"(?:Cộng tiền hàng|Tổng tiền chưa thuế)\s*[:：]?\s*([\d.,]+)","subtotal"),(r"(?:Tiền thuế GTGT|Tiền thuế)\s*[:：]?\s*([\d.,]+)","vat_amount"),(r"(?:Tổng cộng tiền thanh toán|Tổng tiền thanh toán|Total)\s*[:：]?\s*([\d.,]+)","total_amount")]:
  m=re.search(p,t,re.I)
  if m:x[k]=number(m.group(1))
 if len(t.strip())<30:x["warnings"].append("PDF scan/ảnh: cần OCR hoặc nhập kiểm tra thủ công.")
 return x
def extract(data,name):
 ext=Path(name).suffix.lower()
 if ext==".xml":return xml_extract(data,name)
 if ext==".pdf":return pdf_extract(data,name)
 x=blank(name,ext[1:]);x["warnings"].append("Tệp ảnh hiện chờ OCR; vui lòng nhập và đối chiếu thủ công.")
 return x
