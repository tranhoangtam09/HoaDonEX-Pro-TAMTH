from pathlib import Path
import re,datetime,unicodedata,fitz
from .ocr import image_to_text,pdf_to_text
def blank(name,kind):
 return {"filename":name,"source_type":kind,"seller_name":None,"seller_address":None,"tax_code":None,"buyer_name":None,"buyer_tax_code":None,"buyer_address":None,"beneficiary_account":None,"invoice_form":None,"invoice_symbol":None,"invoice_number":None,"invoice_date":None,"subtotal":None,"vat_amount":None,"total_amount":None,"currency":"VND","item_description":None,"order_reference":None,"financing_amount":None,"payment_date":None,"payment_amount":None,"review_note":"Cần đối chiếu thông tin với hóa đơn gốc.","is_valid":False,"warnings":[],"extraction_method":kind}
def clean(s):return re.sub(r"\\s+"," ",str(s or "")).strip(" :：\\t\\r\\n") or None
def parse_date(s):
 if not s:return None
 s=clean(s);m=re.search(r"(\\d{1,2})\\s*[/.-]\\s*(\\d{1,2})\\s*[/.-]\\s*(\\d{4})",s)
 if not m:m=re.search(r"(?:ngày\\s*)?(\\d{1,2})\\s+tháng\\s+(\\d{1,2})\\s+năm\\s+(\\d{4})",s,re.I)
 if not m:return None
 try:return datetime.date(int(m.group(3)),int(m.group(2)),int(m.group(1))).isoformat()
 except ValueError:return None
def number(v):
 if not v:return None
 s=re.sub(r"[^0-9,.-]","",str(v).replace(" ",""))
 if "," in s and "." in s:s=s.replace(".","").replace(",",".") if s.rfind(",")>s.rfind(".") else s.replace(",","")
 elif "," in s:s=s.replace(",",".") if len(s.rsplit(",",1)[-1]) in (1,2) else s.replace(",","")
 elif s.count(".")>1 or ("." in s and len(s.rsplit(".",1)[-1])==3):s=s.replace(".","")
 try:return int(float(s)) if float(s).is_integer() else float(s)
 except ValueError:return None
def tax_clean(s):
 if not s:return None
 d=re.sub(r"\\D","",s);return d if len(d) in (10,13) else None
def field_after(text,labels):
 for label in labels:
  m=re.search(label+r"[ \\t]*[:：]?[ \\t]*([^\\n\\r]+)",text,re.I)
  if m:
   v=clean(m.group(1))
   if v:return v[:500]
 return None
def split_symbol(raw):
 raw=clean(raw)
 if not raw:return None,None
 raw=re.sub(r"\\s+","",raw);m=re.fullmatch(r"(\\d{1,2})([A-Za-z][A-Za-z0-9/-]{2,})",raw)
 return (m.group(1),m.group(2)) if m else (None,raw)
def parse_invoice_text(text,name,source_type):
 x=blank(name,source_type);t=text.replace("\\u00a0"," ")
 sym=field_after(t,[r"Ký hiệu(?: hóa đơn)?"]);invno=field_after(t,[r"Số hóa đơn",r"Số\\s*HĐ",r"Số"])
 if not sym:
  m=re.search(r"(?:^|\\n)\\s*(\\d{1,2}[A-Z][A-Z0-9/-]{3,})\\s*(?:\\n|$)",t)
  if m:sym=m.group(1)
 if not invno or not re.search(r"\\d",invno):
  m=re.search(r"(?:^|\\n)\\s*(\\d{3,})\\s*(?:\\n|$)",t)
  if m:invno=m.group(1)
 x["invoice_form"],x["invoice_symbol"]=split_symbol(sym)
 x["invoice_number"]=(re.sub(r"\\D","",invno) or None) if invno else None
 m=re.search(r"(?:Ngày\\s*)?\\d{1,2}\\s+tháng\\s+\\d{1,2}\\s+năm\\s+\\d{4}",t,re.I) or re.search(r"(?:Ngày|Date)\\s*[:：]?\\s*\\d{1,2}[/.-]\\d{1,2}[/.-]\\d{4}",t,re.I)
 x["invoice_date"]=parse_date(m.group(0)) if m else None
 seller=field_after(t,[r"Đơn vị bán hàng"])
 if not seller or seller.lower() in ("địa chỉ","mã số thuế"):
  head=t.split("Họ tên người mua hàng")[0];candidates=re.findall(r"(?:CÔNG TY|DOANH NGHIỆP|HỘ KINH DOANH)[^\\n]{3,160}",head,re.I)
  seller=clean(candidates[0]) if candidates else None
  if seller:
   lines=head.splitlines()
   for idx,line in enumerate(lines):
    if seller in line and idx+1<len(lines) and re.match(r"\\s*(?:DẦU KHÍ|THƯƠNG MẠI|ĐỒNG THÁP)",lines[idx+1],re.I):seller=clean(seller+" "+lines[idx+1]);break
 x["seller_name"]=seller
 m=re.search(r"(?:MST|Mã số thuế)\\s*[:：]?\\s*([0-9\\s.-]{10,22})",t,re.I)
 if m:x["tax_code"]=tax_clean(m.group(1))
 buyer=t.split("Họ tên người mua hàng",1)[1] if "Họ tên người mua hàng" in t else ""
 x["buyer_name"]=field_after(buyer,[r"Tên đơn vị",r"Người mua hàng"])
 x["buyer_tax_code"]=tax_clean(field_after(buyer,[r"Mã số thuế",r"MST"]) or "")
 x["seller_address"]=field_after(t,[r"Địa chỉ"]);x["buyer_address"]=field_after(buyer,[r"Địa chỉ"])
 for p,k in [(r"(?:III\\.?\\s*)?Tổng cộng tiền thanh toán\\s*[:：]?\\s*([\\d.,]+)","total_amount"),(r"(?:I\\s*)?Cộng tiền hàng hóa, dịch vụ\\s*[:：]?\\s*([\\d.,]+)","subtotal"),(r"(?:Tiền thuế GTGT|Thuế GTGT)\\s*[:：]?\\s*([\\d.,]+)","vat_amount")]:
  m=re.search(p,t,re.I)
  if m:x[k]=number(m.group(1))
 m=re.search(r"(?:TÊN HÀNG HÓA,?\\s*DỊCH VỤ|HÀNG HÓA,?\\s*DỊCH VỤ).*?(?:STT)?\\s*1\\s+([^\\n]+)",t,re.I|re.S)
 if m:x["item_description"]=clean(m.group(1))
 m=re.search(r"(?:Đơn đặt hàng|Hợp đồng|Đơn hàng)\\s*[:#]?\\s*([^\\)\\n]+)",t,re.I)
 if m:x["order_reference"]=clean(m.group(1))
 if not x["invoice_form"] or not x["invoice_symbol"]:x["warnings"].append("Chưa tách được ký hiệu mẫu số và ký hiệu hóa đơn.")
 return x
def extract(data,name):
 ext=Path(name).suffix.lower()
 if ext==".xml":
  import xml.etree.ElementTree as ET
  root=ET.fromstring(data);vals={}
  for e in root.iter():
   k=unicodedata.normalize("NFD",e.tag.split("}")[-1].lower()).encode("ascii","ignore").decode();v=clean(e.text)
   if v:vals.setdefault(k,v)
  def pick(*keys):
   for key in keys:
    for k,v in vals.items():
     if key in k:return v
  x=parse_invoice_text("\\n".join(f"{k}: {v}" for k,v in vals.items()),name,"xml")
  x.update(seller_name=pick("tendonvi","tennguoiban","sellername") or x["seller_name"],tax_code=tax_clean(pick("masothue","taxcode","mst") or "") or x["tax_code"],invoice_number=pick("sohoadon","invoiceno") or x["invoice_number"])
  return x
 if ext==".pdf":
  doc=fitz.open(stream=data,filetype="pdf");text="\\n".join(p.get_text("text") for p in doc);doc.close()
  x=parse_invoice_text(text,name,"pdf_text");critical=("seller_name","tax_code","invoice_form","invoice_symbol","invoice_number","invoice_date","total_amount")
  if len(re.sub(r"\\s","",text))<80 or any(not x.get(k) for k in critical):
   try:
    ot=pdf_to_text(data);ox=parse_invoice_text(ot,name,"paddleocr_vi")
    for k in critical+("seller_address","item_description","order_reference"):
     if not x.get(k) and ox.get(k):x[k]=ox[k]
    x["extraction_method"]="pdf_text+paddleocr_vi" if text.strip() else "paddleocr_vi";x["raw_text"]=(text+"\\n--- OCR ---\\n"+ot)[:30000];x["warnings"].append("Có sử dụng OCR bổ sung; cần đối chiếu ảnh gốc.")
   except RuntimeError as exc:x["raw_text"]=text[:30000];x["warnings"].append(str(exc))
  else:x["raw_text"]=text[:30000]
  return x
 if ext in (".jpg",".jpeg",".png",".tif",".tiff",".webp"):
  try:ot=image_to_text(data)
  except RuntimeError as exc:
   x=blank(name,"image");x["warnings"].append(str(exc));return x
  x=parse_invoice_text(ot,name,"paddleocr_vi");x["raw_text"]=ot[:30000];x["warnings"].append("Dữ liệu được nhận dạng bằng OCR; cần đối chiếu ảnh gốc.");return x
 raise ValueError("Định dạng tệp không được hỗ trợ")
