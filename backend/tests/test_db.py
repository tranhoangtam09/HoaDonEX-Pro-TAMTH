from app import db

def test_invoice_records_can_be_listed_and_loaded_without_duplicate_filename(tmp_path,monkeypatch):
 monkeypatch.setattr(db,"DB_PATH",tmp_path/"test.sqlite3")
 db.init()
 payload={"filename":"invoice.pdf","seller_name":"Công ty A","total_amount":123}
 invoice_id,created=db.save("invoice.pdf","sha256-unique","pdf",payload)
 assert created is True
 assert db.get(invoice_id)["filename"]=="invoice.pdf"
 assert db.all()[0]["filename"]=="invoice.pdf"
 duplicate_id,created_again=db.save("different-name.pdf","sha256-unique","pdf",{"filename":"different-name.pdf"})
 assert duplicate_id==invoice_id and created_again is False
 assert len(db.all())==1
