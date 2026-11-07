import fitz
from fastapi.testclient import TestClient
from app import db,main

def test_merge_selected_pdf_invoices_returns_combined_pdf(tmp_path,monkeypatch):
 monkeypatch.setattr(db,"DB_PATH",tmp_path/"merge.sqlite3")
 monkeypatch.setattr(main,"UPLOADS",tmp_path/"uploads")
 main.UPLOADS.mkdir()
 db.init()
 ids=[]
 for n in range(2):
  doc=fitz.open()
  page=doc.new_page()
  page.insert_text((72,72),f"INVOICE PAGE {n+1}")
  raw=doc.tobytes()
  doc.close()
  source=main.UPLOADS/f"invoice{n+1}.pdf"
  source.write_bytes(raw)
  invoice_id,_=db.save(source.name,f"hash-{n}","pdf",{"filename":source.name,"source_type":"pdf_text","source_path":str(source)})
  ids.append(invoice_id)
 with TestClient(main.app) as client:
  response=client.post("/invoices/merge",json={"ids":ids})
 assert response.status_code==200
 assert response.headers["content-type"].startswith("application/pdf")
 merged=fitz.open(stream=response.content,filetype="pdf")
 assert merged.page_count==2
 assert "INVOICE PAGE 1" in merged[0].get_text()
 assert "INVOICE PAGE 2" in merged[1].get_text()
 merged.close()

def test_merge_rejects_more_than_ten_ids():
 with TestClient(main.app) as client:
  response=client.post("/invoices/merge",json={"ids":list(range(1,12))})
 assert response.status_code==422
