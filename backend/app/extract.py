from pathlib import Path
import re,datetime,unicodedata,fitz
from .ocr import image_to_text,pdf_to_text
def blank(name,kind):
 return {"filename":name,"source_type":kind,"seller_name":None,"seller_address":None,"tax_code":None,"buyer_name":None,"buyer_tax_code":None,"buyer_address":None,"beneficiary_account":None,"invoice_form":None,"invoice_symbol":None,"invoice_number":None,"invoice_date":None,"subtotal":None,"vat_amount":None,"total_amount":None,"currency":"VND","item_description":None,"order_reference":None,"financing_amount":None,"payment_date":None,"payment_amount":None,"review_note":"Cần đối chiếu thông tin với hóa đơn gốc.","is_valid":False,"warnings":[],"extraction_method":kind}
def clean(s):return re.sub(r"\s+"," ",str(s or "")).strip(" :：\t\r\n") or None
def parse_date(s):
 if not s:return None
 s=clean(s)
 try:return datetime.date.fromisoformat(s[:10]).isoformat()
 except (ValueError,TypeError):pass
 m=re.search(r"(\d{1,2})\s*[/.-]\s*(\d{1,2})\s*[/.-]\s*(\d{4})",s)
 if not m:m=re.search(r"(?:ngày\s*)?(\d{1,2})\s+tháng\s+(\d{1,2})\s+năm\s+(\d{4})",s,re.I)
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
 d=re.sub(r"\D","",s);return d if len(d) in (10,13) else None
def field_after(text,labels):
 for label in labels:
  m=re.search(label+r"[ \t]*[:：]?[ \t]*([^\n\r]+)",text,re.I)
  if m:
   v=clean(m.group(1))
   if v:return v[:500]
 return None
def split_symbol(raw):
 raw=clean(raw)
 if not raw:return None,None
 raw=re.sub(r"\s+","",raw);m=re.fullmatch(r"(\d{1,2})([A-Za-z][A-Za-z0-9/-]{2,})",raw)
 return (m.group(1),m.group(2)) if m else (None,raw)
def parse_invoice_text(text,name,source_type):
 x=blank(name,source_type);t=text.replace("\u00a0"," ")
 sym=field_after(t,[r"Ký hiệu(?: hóa đơn)?"]);invno=field_after(t,[r"Số hóa đơn",r"Số\s*HĐ"])
 if not invno:
  m=re.search(r"(?m)^\s*Số\s*[:：]\s*([^\n\r]+)",t,re.I)
  if m:invno=clean(m.group(1))
 if not sym:
  m=re.search(r"(?:^|\n)\s*(\d{1,2}[A-Z][A-Z0-9/-]{3,})\s*(?:\n|$)",t)
  if m:sym=m.group(1)
 if not invno or not re.search(r"\d",invno):
  m=re.search(r"(?:^|\n)\s*(\d{3,})\s*(?:\n|$)",t)
  if m:invno=m.group(1)
 x["invoice_form"],x["invoice_symbol"]=split_symbol(sym)
 x["invoice_number"]=(re.sub(r"\D","",invno) or None) if invno else None
 m=re.search(r"(?:Ngày\s*)?\d{1,2}\s+tháng\s+\d{1,2}\s+năm\s+\d{4}",t,re.I) or re.search(r"(?:Ngày|Date)\s*[:：]?\s*\d{1,2}[/.-]\d{1,2}[/.-]\d{4}",t,re.I)
 x["invoice_date"]=parse_date(m.group(0)) if m else None
 seller=field_after(t,[r"Đơn vị bán hàng"])
 if not seller or seller.lower() in ("địa chỉ","mã số thuế"):
  head=t.split("Họ tên người mua hàng")[0];candidates=re.findall(r"(?:CÔNG TY|DOANH NGHIỆP|HỘ KINH DOANH)[^\n]{3,160}",head,re.I)
  seller=clean(candidates[0]) if candidates else None
  if seller:
   lines=head.splitlines()
   for idx,line in enumerate(lines):
    if seller in line and idx+1<len(lines) and re.match(r"\s*(?:DẦU KHÍ|THƯƠNG MẠI|ĐỒNG THÁP)",lines[idx+1],re.I):seller=clean(seller+" "+lines[idx+1]);break
 x["seller_name"]=seller
 m=re.search(r"(?:MST|Mã số thuế)\s*[:：]?\s*([0-9\s.-]{10,22})",t,re.I)
 if m:x["tax_code"]=tax_clean(m.group(1))
 buyer=t.split("Họ tên người mua hàng",1)[1] if "Họ tên người mua hàng" in t else ""
 x["buyer_name"]=field_after(buyer,[r"Tên đơn vị",r"Người mua hàng"])
 if not x["buyer_name"]:
  m=re.search(r"(?im)^\s*Tên đơn vị\s*[:：]?\s*\n\s*([^\n\r]+)",buyer)
  if m:x["buyer_name"]=clean(m.group(1))
 x["buyer_tax_code"]=tax_clean(field_after(buyer,[r"Mã số thuế",r"MST"]) or "")
 x["seller_address"]=field_after(t,[r"Địa chỉ"]);x["buyer_address"]=field_after(buyer,[r"Địa chỉ"])
 for p,k in [(r"(?:III\.?\s*)?Tổng cộng tiền thanh toán\s*[:：]?\s*([\d.,]+)","total_amount"),(r"(?:I\s*)?Cộng tiền hàng hóa, dịch vụ\s*[:：]?\s*([\d.,]+)","subtotal"),(r"(?:Tiền thuế GTGT|Thuế GTGT)\s*[:：]?\s*([\d.,]+)","vat_amount")]:
  m=re.search(p,t,re.I)
  if m:x[k]=number(m.group(1))
 m=re.search(r"(?:TÊN HÀNG HÓA,?\s*DỊCH VỤ|HÀNG HÓA,?\s*DỊCH VỤ).*?(?:STT)?\s*1\s+([^\n]+)",t,re.I|re.S)
 if m:x["item_description"]=clean(m.group(1))
 m=re.search(r"(?:Đơn đặt hàng|Hợp đồng|Đơn hàng)\s*[:#]?\s*([^\)\n]+)",t,re.I)
 if m:x["order_reference"]=clean(m.group(1))
 if not x["invoice_form"] or not x["invoice_symbol"]:x["warnings"].append("Chưa tách được ký hiệu mẫu số và ký hiệu hóa đơn.")
 return x

def _pdf_blocks(page):
 return sorted([(b[1],b[0],b[3],clean(b[4])) for b in page.get_text("blocks") if len(b)>4 and clean(b[4])],key=lambda z:(z[0],z[1]))
def _amount_near_label(blocks,labels):
 for y,x0,y1,txt in blocks:
  if any(label in txt.lower() for label in labels):
   vals=re.findall(r"(?<!\\d)(\\d{1,3}(?:[.,]\\d{3})+|\\d+)(?!\\d)",txt)
   vals=[v for v in vals if len(re.sub(r"\\D","",v))>=4]
   if vals:return number(vals[0])
   near=[(abs(by-y),btxt) for by,bx,by1,btxt in blocks if abs(by-y)<=5 and btxt!=txt]
   for _,other in sorted(near):
    vals=re.findall(r"(?<!\\d)(\\d{1,3}(?:[.,]\\d{3})+|\\d+)(?!\\d)",other)
    vals=[v for v in vals if len(re.sub(r"\\D","",v))>=4]
    if vals:return number(vals[0])
 return None
def _parse_pdf_layout(data,x):
 try:
  doc=fitz.open(stream=data,filetype="pdf")
  if not doc:return x
  blocks=_pdf_blocks(doc[0])
  header=[b[3] for b in blocks if re.search(r"ký hiệu|\\(sign\\)|\\bSố\\b|\\(no\\)",b[3],re.I)]
  header_text="\\n".join(header+[b[3] for b in blocks if re.search(r"\\b\\d{1,2}[A-Z][A-Z0-9/-]{2,}\\b|\\b\\d{5,}\\b",b[3]) and 160<=b[0]<=280])
  sm=re.search(r"\\b(\\d{1,2}[A-Z][A-Z0-9/-]{2,})\\b",header_text,re.I)
  nm=re.search(r"(?<!\\d)(\\d{5,})(?!\\d)",header_text)
  if sm:x["invoice_form"],x["invoice_symbol"]=split_symbol(sm.group(1))
  if nm:x["invoice_number"]=nm.group(1)
  seller_idx=next((i for i,b in enumerate(blocks) if re.search(r"đơn vị bán hàng",b[3],re.I)),None)
  if seller_idx is not None:
   label_block=blocks[seller_idx][3]
   tail=re.split(r"đơn vị bán hàng\\s*[:：]?",label_block,flags=re.I,maxsplit=1)
   parts=[clean(tail[-1])] if tail and clean(tail[-1]) else []
   base_y=blocks[seller_idx][0]
   for by,bx,by1,bt in blocks[seller_idx+1:]:
    if by-base_y>48:break
    if re.search(r"mã số thuế|địa chỉ|số tài khoản|hóa đơn giá trị|mã cqt",bt,re.I):break
    if re.fullmatch(r"[A-ZÀ-Ỹ0-9 .,&/-]{2,}",bt,re.I):parts.append(bt)
   seller=clean(" ".join(p for p in parts if p))
   if seller:x["seller_name"]=seller
   for by,bx,by1,bt in blocks[seller_idx+1:]:
    if by-base_y>65:break
    if re.search(r"mã số thuế|tax code",bt,re.I):
     mt=re.search(r"(?<!\\d)(\\d{10}(?:-\\d{3})?)(?!\\d)",bt)
     if mt:x["tax_code"]=tax_clean(mt.group(1));break
  else:
   for _,_,_,bt in blocks[:8]:
    if re.search(r"^(?:CÔNG TY|DOANH NGHIỆP|HỘ KINH DOANH)",bt,re.I):
     x["seller_name"]=bt;break
   for _,_,_,bt in blocks[:12]:
    mt=re.search(r"(?<!\\d)(\\d{10}(?:-\\d{3})?)(?!\\d)",bt)
    if mt:x["tax_code"]=tax_clean(mt.group(1));break
  for labels,key in [(["tổng tiền thanh toán","total amount"],"total_amount"),(["cộng tiền hàng","total before vat"],"subtotal"),(["tiền thuế gtgt","vat amount"],"vat_amount")]:
   value=_amount_near_label(blocks,labels)
   if value is not None:x[key]=value
  start=next((i for i,b in enumerate(blocks) if "tên hàng hóa" in b[3].lower() or "name of goods" in b[3].lower()),None)
  if start is not None:
   goods=[]
   for by,bx,by1,bt in blocks[start+1:]:
    if re.search(r"cộng tiền hàng|total before vat|thuế suất|vat rate",bt,re.I):break
    if re.search(r"\\b\\d{1,3}(?:[.,]\\d{3})+\\b",bt) and not re.search(r"tên hàng|đơn vị tính|số lượng|đơn giá|thành tiền|^a$|^b$|^c$",bt,re.I):goods.append(bt)
   if goods:x["item_description"]="; ".join(goods)[:500]
  doc.close()
 except Exception:
  return x
 return x

def extract(data,name):
 ext=Path(name).suffix.lower()
 if ext==".xml":
  import xml.etree.ElementTree as ET
  root=ET.fromstring(data)
  def tag(e):return re.sub(r"[^a-z0-9]","",unicodedata.normalize("NFD",e.tag.split("}")[-1].lower()).encode("ascii","ignore").decode())
  def section(*names):
   targets=set(names)
   return next((e for e in root.iter() if tag(e) in targets),None)
  def val(node,*names):
   if node is None:return None
   targets=set(names)
   for e in node.iter():
    if e is not node and tag(e) in targets:
     v=clean(e.text)
     if v:return v
   return None
  common=section("ttchung","thongtinchung")
  seller=section("nban","nguoiban","seller")
  buyer=section("nmua","nguoimua","buyer")
  totals=section("ttoan","thanhtoan","payment")
  goods=section("dshhdvu","danhsachhanghoadichvu","items")
  x=blank(name,"xml")
  x.update(
   seller_name=val(seller,"ten","tendonvi","tennguoiban","sellername"),
   tax_code=tax_clean(val(seller,"mst","masothue","taxcode") or ""),
   seller_address=val(seller,"dchi","diachi","address"),
   buyer_name=val(buyer,"ten","tendonvi","tennguoimua","buyername"),
   buyer_tax_code=tax_clean(val(buyer,"mst","masothue","taxcode") or ""),
   buyer_address=val(buyer,"dchi","diachi","address"),
   invoice_form=val(common,"khmshdon","mauso","invoiceform"),
   invoice_symbol=val(common,"khhdon","kyhieu","invoicesymbol"),
   invoice_number=val(common,"shdon","sohoadon","invoiceno"),
   invoice_date=parse_date(val(common,"nlap","ngaylap","invoicedate") or ""),
   currency=val(common,"dvtte","loaitien","currency") or "VND",
   total_amount=number(val(totals,"tgttoan","tongcongthanhtoan","totalamount")),
   subtotal=number(val(totals,"tgtcthue","tienhangtruoc thue","subtotal")),
   vat_amount=number(val(totals,"tgtthue","tienthue","vatamount")),
   item_description=val(goods,"thhdvu","tenhanghoa","itemname")
  )
  if not x["seller_name"] or not x["tax_code"]:x["warnings"].append("XML không có đủ thông tin đơn vị phát hành; cần kiểm tra cấu trúc nhà cung cấp.")
  if not x["invoice_number"] or not x["invoice_date"]:x["warnings"].append("XML không có đủ số/ngày hóa đơn.")
  return x
 if ext==".pdf":
  doc=fitz.open(stream=data,filetype="pdf");text="\n".join(p.get_text("text") for p in doc);doc.close()
  x=parse_invoice_text(text,name,"pdf_text")
  x=_parse_pdf_layout(data,x)
  critical=("seller_name","tax_code","buyer_name","buyer_tax_code","invoice_form","invoice_symbol","invoice_number","invoice_date","total_amount")
  if len(re.sub(r"\s","",text))<80 or any(not x.get(k) for k in critical):
   try:
    ot=pdf_to_text(data);ox=parse_invoice_text(ot,name,"paddleocr_vi")
    for k in critical+("seller_address","item_description","order_reference"):
     if not x.get(k) and ox.get(k):x[k]=ox[k]
    x["extraction_method"]="pdf_text+paddleocr_vi" if text.strip() else "paddleocr_vi";x["raw_text"]=(text+"\n--- OCR ---\n"+ot)[:30000];x["warnings"].append("Có sử dụng OCR bổ sung; cần đối chiếu ảnh gốc.")
   except RuntimeError as exc:x["raw_text"]=text[:30000];x["warnings"].append(str(exc))
  else:x["raw_text"]=text[:30000]
  return x
 if ext in (".jpg",".jpeg",".png",".tif",".tiff",".webp"):
  try:ot=image_to_text(data)
  except RuntimeError as exc:
   x=blank(name,"image");x["warnings"].append(str(exc));return x
  x=parse_invoice_text(ot,name,"paddleocr_vi");x["raw_text"]=ot[:30000];x["warnings"].append("Dữ liệu được nhận dạng bằng OCR; cần đối chiếu ảnh gốc.");return x
 raise ValueError("Định dạng tệp không được hỗ trợ")
