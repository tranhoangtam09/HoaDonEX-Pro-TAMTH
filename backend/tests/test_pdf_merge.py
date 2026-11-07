import asyncio
import fitz
import pytest
from pydantic import ValidationError
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
 response=main.merge_invoices(main.MergeRequest(ids=ids))
 async def collect():
  chunks=[]
  async for chunk in response.body_iterator:chunks.append(chunk)
  return b"".join(chunks)
 output=asyncio.run(collect())
 assert response.media_type=="application/pdf"
 merged=fitz.open(stream=output,filetype="pdf")
 assert merged.page_count==2
 assert "INVOICE PAGE 1" in merged[0].get_text()
 assert "INVOICE PAGE 2" in merged[1].get_text()
 merged.close()

def test_merge_rejects_more_than_ten_ids():
 with pytest.raises(ValidationError):
  main.MergeRequest(ids=list(range(1,12)))
