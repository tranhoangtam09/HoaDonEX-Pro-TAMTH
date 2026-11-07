from fastapi import FastAPI,UploadFile,File,HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from pathlib import Path
import hashlib,zipfile,io
from . import db
from .config import MAX_UPLOAD_MB,CORS_ORIGINS
from .extract import extract
from .validate import validate
from .exporter import make
app=FastAPI(title="HOA DON EX PRO – TAMTH",version="1.0.0")
app.add_middleware(CORSMiddleware,allow_origins=CORS_ORIGINS,allow_methods=["GET","POST","PATCH"],allow_headers=["*"])
@app.on_event("startup")
def startup():db.init()
@app.get("/health")
def health():return {"status":"ok","app":"HOA DON EX PRO – TAMTH"}
@app.get("/invoices")
def invoices():return {"items":[validate(x) for x in db.all()]}
@app.get("/invoices/{i}")
def invoice(i:int):
 x=db.get(i)
 if x is None:raise HTTPException(404,"Không tìm thấy hồ sơ")
 return validate(x)
class Patch(BaseModel):
 model_config={"extra":"forbid"}
 seller_name:str|None=None;seller_address:str|None=None;tax_code:str|None=None;invoice_symbol:str|None=None;invoice_number:str|None=None;invoice_date:str|None=None;subtotal:float|None=None;vat_amount:float|None=None;total_amount:float|None=None;review_note:str|None=None
@app.patch("/invoices/{i}")
def edit(i:int,p:Patch):
 if not db.update(i,p.model_dump(exclude_unset=True)):raise HTTPException(404,"Không tìm thấy hồ sơ")
 return validate(db.get(i))
def store(data,name):
 x=validate(extract(data,name));sha=hashlib.sha256(data).hexdigest();i,created=db.save(name,sha,Path(name).suffix.lower(),x)
 return {"id":i,"filename":name,"created":created,**x}
@app.post("/invoices/upload")
async def upload(files:list[UploadFile]=File(...)):
 out=[]
 for f in files:
  data=await f.read()
  if len(data)>MAX_UPLOAD_MB*1024*1024:raise HTTPException(413,f"Tệp vượt giới hạn {MAX_UPLOAD_MB} MB")
  name=Path(f.filename or "upload").name
  if name.lower().endswith(".zip"):
   try:
    with zipfile.ZipFile(io.BytesIO(data)) as z:
     for q in z.infolist():
      if q.is_dir() or q.file_size>MAX_UPLOAD_MB*1024*1024:continue
      if Path(q.filename).suffix.lower() in (".pdf",".xml",".jpg",".jpeg",".png"):out.append(store(z.read(q),Path(q.filename).name))
   except zipfile.BadZipFile:raise HTTPException(400,"ZIP không hợp lệ")
  elif Path(name).suffix.lower() in (".pdf",".xml",".jpg",".jpeg",".png"):out.append(store(data,name))
  else:raise HTTPException(415,"Định dạng không hỗ trợ: "+name)
 return {"created":sum(q["created"] for q in out),"items":out}
@app.post("/export/{kind}")
def export(kind:str):
 rows=db.all()
 if not rows:raise HTTPException(400,"Chưa có hóa đơn")
 b=make(rows,kind);name="Bang_ke_chuyen_khoan_VND.xlsx" if kind=="transfer" else "Bang_ke_bu_dap_VND.xlsx"
 return StreamingResponse(b,media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",headers={"Content-Disposition":f'attachment; filename="{name}"'})
