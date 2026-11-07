from fastapi import FastAPI,UploadFile,File,HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel,ConfigDict,Field
from pathlib import Path
from typing import Optional
import hashlib,zipfile,io,hmac,shutil
import fitz
from PIL import Image
from openpyxl import load_workbook
from .config import API_KEY,TEMPLATES,DATA
from . import db
from .config import MAX_UPLOAD_MB,CORS_ORIGINS
from .extract import extract
from .validate import validate
from .exporter import export_workbook
app=FastAPI(title="HOA DON EX PRO – TAMTH",version="1.3.0")
app.add_middleware(CORSMiddleware,allow_origins=CORS_ORIGINS,allow_methods=["GET","POST","PATCH","DELETE"],allow_headers=["*"])
ALLOWED={".pdf",".xml",".jpg",".jpeg",".png",".tif",".tiff",".webp"}
UPLOADS=DATA/"uploads"
@app.middleware("http")
async def require_api_key(request,call_next):
 if API_KEY and request.method != "OPTIONS" and request.url.path not in ("/health","/docs","/openapi.json","/redoc"):
  supplied=request.headers.get("X-API-Key","")
  if not hmac.compare_digest(supplied,API_KEY):
   from fastapi.responses import JSONResponse
   return JSONResponse(status_code=401,content={"detail":"API key không hợp lệ hoặc chưa được nhập."})
 return await call_next(request)

@app.on_event("startup")
def startup():db.init()
@app.get("/health")
def health():return {"status":"ok","app":"HOA DON EX PRO – TAMTH","version":"1.3.0","invoice_count":len(db.all()),"batch_replace":True,"ocr":"optional-paddleocr-vi"}
@app.get("/invoices")
def invoices():return {"items":[validate(x) for x in db.all()]}
@app.get("/invoices/{invoice_id}")
def invoice(invoice_id:int):
 x=db.get(invoice_id)
 if x is None:raise HTTPException(404,"Không tìm thấy hồ sơ")
 return validate(x)
class InvoicePatch(BaseModel):
 model_config=ConfigDict(extra="forbid")
 seller_name:Optional[str]=None;seller_address:Optional[str]=None;tax_code:Optional[str]=None
 buyer_name:Optional[str]=None;buyer_tax_code:Optional[str]=None;buyer_address:Optional[str]=None
 beneficiary_account:Optional[str]=None;invoice_form:Optional[str]=None;invoice_symbol:Optional[str]=None
 invoice_number:Optional[str]=None;invoice_date:Optional[str]=None;subtotal:Optional[float]=None
 vat_amount:Optional[float]=None;total_amount:Optional[float]=None;currency:Optional[str]=None
 item_description:Optional[str]=None;order_reference:Optional[str]=None;financing_amount:Optional[float]=None
 payment_date:Optional[str]=None;payment_amount:Optional[float]=None;review_note:Optional[str]=None
@app.patch("/invoices/{invoice_id}")
def edit(invoice_id:int,p:InvoicePatch):
 if not db.update(invoice_id,p.model_dump(exclude_unset=True)):raise HTTPException(404,"Không tìm thấy hồ sơ")
 return validate(db.get(invoice_id))

def store(data,name,extracted=None):
 try:x=extracted or validate(extract(data,name))
 except RuntimeError as exc:raise HTTPException(503,str(exc))
 except Exception as exc:raise HTTPException(422,f"Không đọc được {name}: {exc}")
 sha=hashlib.sha256(data).hexdigest()
 UPLOADS.mkdir(parents=True,exist_ok=True)
 safe=Path(name).name
 source=UPLOADS/(sha+Path(safe).suffix.lower())
 source.write_bytes(data)
 x["source_path"]=str(source)
 i,created=db.save(safe,sha,Path(safe).suffix.lower(),x)
 return {"id":i,"filename":safe,"created":created,**x}

@app.post("/invoices/upload")
async def upload(files:list[UploadFile]=File(...)):
 if not files:raise HTTPException(400,"Chưa chọn tệp.")
 # Parse every source first. Do not touch the current batch until all files are readable.
 staged=[]
 for f in files:
  name=Path(f.filename or "upload").name;data=await f.read()
  if len(data)>MAX_UPLOAD_MB*1024*1024:raise HTTPException(413,f"Tệp {name} vượt giới hạn {MAX_UPLOAD_MB} MB")
  if name.lower().endswith(".zip"):
   try:
    with zipfile.ZipFile(io.BytesIO(data)) as z:
     members=[q for q in z.infolist() if not q.is_dir() and Path(q.filename).suffix.lower() in ALLOWED]
     if len(members)>100:raise HTTPException(413,"ZIP chứa quá nhiều tệp hóa đơn.")
     for q in members:
      if q.file_size>MAX_UPLOAD_MB*1024*1024:raise HTTPException(413,f"Tệp {q.filename} trong ZIP vượt giới hạn.")
      blob=z.read(q);member_name=Path(q.filename).name
      staged.append((blob,member_name,validate(extract(blob,member_name))))
   except zipfile.BadZipFile:raise HTTPException(400,"Tệp ZIP không hợp lệ.")
  elif Path(name).suffix.lower() in ALLOWED:
   staged.append((data,name,validate(extract(data,name))))
  else:raise HTTPException(415,"Định dạng không hỗ trợ: "+name)
 if not staged:raise HTTPException(400,"Không tìm thấy hóa đơn hợp lệ trong tệp đã chọn.")
 # Persist source files first; then atomically replace database rows in one SQLite transaction.
 UPLOADS.mkdir(parents=True,exist_ok=True)
 records=[]
 for blob,name,x in staged:
  sha=hashlib.sha256(blob).hexdigest()
  source=UPLOADS/(sha+Path(name).suffix.lower())
  try:source.write_bytes(blob)
  except OSError as exc:raise HTTPException(507,f"Không lưu được tệp gốc {name}: {exc}")
  x["source_path"]=str(source)
  records.append((name,sha,Path(name).suffix.lower(),x))
 ids=db.replace_batch(records)
 results=[]
 for (blob,name,x),invoice_id in zip(staged,ids):
  results.append({"id":invoice_id,"filename":name,**x})
 return {"replaced":True,"removed_previous":True,"created":len(results),"items":results,"batch_count":len(results),"message":f"Đã thay thế toàn bộ dữ liệu cũ bằng {len(results)} hóa đơn mới."}

@app.delete("/invoices/unrecognized")
def delete_unrecognized():
 count=db.delete_unrecognized()
 return {"deleted":count,"message":f"Đã xóa {count} hóa đơn không nhận diện đủ thông tin."}

@app.delete("/invoices/{invoice_id}")
def delete_invoice(invoice_id:int):
 if not db.delete_one(invoice_id):raise HTTPException(404,"Không tìm thấy hồ sơ")
 return {"deleted":True,"id":invoice_id}

class MergeRequest(BaseModel):
 ids:list[int]=Field(min_length=1,max_length=10)

@app.post("/invoices/merge")
def merge_invoices(req:MergeRequest):
 if len(set(req.ids))!=len(req.ids):raise HTTPException(400,"Danh sách chọn có hóa đơn trùng lặp.")
 merged=fitz.open()
 try:
  for invoice_id in req.ids:
   x=db.get(invoice_id)
   if not x:raise HTTPException(404,f"Không tìm thấy hóa đơn ID {invoice_id}.")
   source=Path(x.get("source_path") or "")
   if not source.is_file():raise HTTPException(422,f"Không còn tệp gốc của {x.get('filename','hóa đơn')}. Vui lòng nạp lại hóa đơn.")
   ext=source.suffix.lower()
   if ext==".pdf":
    with fitz.open(source) as part:merged.insert_pdf(part)
   elif ext in (".jpg",".jpeg",".png",".tif",".tiff",".webp"):
    try:
     with Image.open(source) as im:
      frames=[]
      try:
       while True:
        frames.append(im.copy().convert("RGB"))
        im.seek(im.tell()+1)
      except EOFError:pass
      for frame in frames:
       buf=io.BytesIO();frame.save(buf,format="PDF",resolution=150);buf.seek(0)
       with fitz.open(stream=buf.getvalue(),filetype="pdf") as part:merged.insert_pdf(part)
    except Exception as exc:raise HTTPException(422,f"Không chuyển được ảnh {x.get('filename')}: {exc}")
   else:
    raise HTTPException(415,f"Không thể gộp trực tiếp định dạng {ext or 'không xác định'}. Hãy chuyển XML sang PDF hoặc chọn PDF/ảnh.")
  if not merged.page_count:raise HTTPException(400,"Không có trang PDF để gộp.")
  output=merged.tobytes(garbage=4,deflate=True)
 finally:merged.close()
 return StreamingResponse(io.BytesIO(output),media_type="application/pdf",headers={"Content-Disposition":'attachment; filename="HoaDon_Gop_TAMTH.pdf"'})

@app.get("/templates/status")
def template_status():
 return {"transfer":(TEMPLATES/"Bang_ke_hoa_don_chuyen_khoan_VND.xlsx").exists(),"compensation":(TEMPLATES/"Bang_ke_hoa_don_bu_dap_VND.xlsx").exists()}

@app.post("/templates/{kind}")
async def upload_template(kind:str,file:UploadFile=File(...)):
 expected={"transfer":("Bang_ke_hoa_don_chuyen_khoan_VND.xlsx","Bảng kê hóa đơn",12),"compensation":("Bang_ke_hoa_don_bu_dap_VND.xlsx","Bảng kê hóa đơn GN bù đắp",13)}
 if kind not in expected:raise HTTPException(400,"Loại mẫu Excel không hợp lệ.")
 filename,sheet_name,columns=expected[kind]
 data=await file.read()
 if len(data)>10*1024*1024:raise HTTPException(413,"Mẫu Excel vượt quá 10 MB.")
 try:
  wb=load_workbook(io.BytesIO(data),read_only=True,data_only=False)
  if sheet_name not in wb.sheetnames:raise HTTPException(422,"Không đúng tên sheet của mẫu gốc: "+sheet_name)
  ws=wb[sheet_name]
  if ws.max_column!=columns or str(ws["A2"].value or "").strip()!="STT":raise HTTPException(422,"Cấu trúc mẫu Excel không đúng số cột hoặc tiêu đề dòng 2.")
  headers=[" ".join(str(ws.cell(2,c).value or "").lower().replace(chr(10)," ").split()) for c in range(1,columns+1)]
  required_headers={"transfer":["mã số thuế đơn vị thụ hưởng","tên đơn vị thụ hưởng","số tài khoản thụ hưởng","ký hiệu mẫu số","ký hiệu hóa đơn","ngày hóa đơn","số tiền nhận nợ"],"compensation":["mã số thuế đơn vị phát hành","tên đơn vị phát hành","ký hiệu mẫu số","ký hiệu hóa đơn","ngày hóa đơn","số tiền nhận nợ","ngày đã thanh toán","số tiền đã thanh toán"]}[kind]
  if not all(any(token in h for h in headers) for token in required_headers):raise HTTPException(422,"Tiêu đề cột không khớp mẫu Excel gốc đã thống nhất.")
 except HTTPException:raise
 except Exception as exc:raise HTTPException(422,"Không đọc được file Excel: "+str(exc))
 TEMPLATES.mkdir(parents=True,exist_ok=True)
 (TEMPLATES/filename).write_bytes(data)
 return {"ok":True,"kind":kind,"filename":filename,"sheet":sheet_name,"columns":columns}

@app.post("/export/{kind}")
def export(kind:str):
 rows=db.all()
 if not rows:raise HTTPException(400,"Chưa có hóa đơn để xuất.")
 out=export_workbook(rows,kind);fn="Bang_ke_hoa_don_chuyen_khoan_VND.xlsx" if kind=="transfer" else "Bang_ke_hoa_don_bu_dap_VND.xlsx"
 return StreamingResponse(out,media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",headers={"Content-Disposition":f'attachment; filename="{fn}"'})
