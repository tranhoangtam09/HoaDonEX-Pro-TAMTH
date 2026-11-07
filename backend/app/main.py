from fastapi import FastAPI,UploadFile,File,HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel,ConfigDict
from pathlib import Path
from typing import Optional
import hashlib,zipfile,io
from . import db
from .config import MAX_UPLOAD_MB,CORS_ORIGINS
from .extract import extract
from .validate import validate
from .exporter import export_workbook
app=FastAPI(title="HOA DON EX PRO – TAMTH",version="1.1.0")
app.add_middleware(CORSMiddleware,allow_origins=CORS_ORIGINS,allow_methods=["GET","POST","PATCH"],allow_headers=["*"])
ALLOWED={".pdf",".xml",".jpg",".jpeg",".png",".tif",".tiff",".webp"}
@app.on_event("startup")
def startup():db.init()
@app.get("/health")
def health():return {"status":"ok","app":"HOA DON EX PRO – TAMTH","ocr":"optional-paddleocr-vi"}
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
def store(data,name):
 try:x=validate(extract(data,name))
 except RuntimeError as exc:raise HTTPException(503,str(exc))
 except Exception as exc:raise HTTPException(422,f"Không đọc được {name}: {exc}")
 sha=hashlib.sha256(data).hexdigest();i,created=db.save(name,sha,Path(name).suffix.lower(),x)
 return {"id":i,"filename":name,"created":created,**x}
@app.post("/invoices/upload")
async def upload(files:list[UploadFile]=File(...)):
 if not files:raise HTTPException(400,"Chưa chọn tệp.")
 results=[]
 for f in files:
  name=Path(f.filename or "upload").name;data=await f.read()
  if len(data)>MAX_UPLOAD_MB*1024*1024:raise HTTPException(413,f"Tệp {name} vượt giới hạn {MAX_UPLOAD_MB} MB")
  if name.lower().endswith(".zip"):
   try:
    with zipfile.ZipFile(io.BytesIO(data)) as z:
     members=[q for q in z.infolist() if not q.is_dir() and Path(q.filename).suffix.lower() in ALLOWED]
     if len(members)>100:raise HTTPException(413,"ZIP chứa quá nhiều tệp hóa đơn.")
     for q in members:
      if q.file_size<=MAX_UPLOAD_MB*1024*1024:results.append(store(z.read(q),Path(q.filename).name))
   except zipfile.BadZipFile:raise HTTPException(400,"Tệp ZIP không hợp lệ.")
  elif Path(name).suffix.lower() in ALLOWED:results.append(store(data,name))
  else:raise HTTPException(415,"Định dạng không hỗ trợ: "+name)
 return {"created":sum(1 for q in results if q["created"]),"items":results}
@app.post("/export/{kind}")
def export(kind:str):
 rows=db.all()
 if not rows:raise HTTPException(400,"Chưa có hóa đơn để xuất.")
 out=export_workbook(rows,kind);fn="Bang_ke_hoa_don_chuyen_khoan_VND.xlsx" if kind=="transfer" else "Bang_ke_hoa_don_bu_dap_VND.xlsx"
 return StreamingResponse(out,media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",headers={"Content-Disposition":f'attachment; filename="{fn}"'})
