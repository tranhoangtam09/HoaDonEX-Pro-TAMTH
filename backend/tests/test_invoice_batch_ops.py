from app import db

def test_clear_all_replaces_previous_batch(tmp_path,monkeypatch):
 monkeypatch.setattr(db,"DB_PATH",tmp_path/"replace.sqlite3")
 db.init()
 db.save("old.pdf","old-hash","pdf",{"seller_name":"Old","invoice_number":"1","invoice_date":"2026-01-01"})
 assert len(db.all())==1
 db.clear_all()
 assert db.all()==[]
 db.save("new.pdf","new-hash","pdf",{"seller_name":"New"})
 assert [x["filename"] for x in db.all()]==["new.pdf"]

def test_delete_unrecognized_only_removes_incomplete_records(tmp_path,monkeypatch):
 monkeypatch.setattr(db,"DB_PATH",tmp_path/"delete.sqlite3")
 db.init()
 db.save("missing.pdf","missing-hash","pdf",{"seller_name":None,"invoice_number":None,"invoice_date":None})
 db.save("complete.pdf","complete-hash","pdf",{"seller_name":"Seller","invoice_number":"123","invoice_date":"2026-10-01"})
 assert db.delete_unrecognized()==1
 assert [x["filename"] for x in db.all()]==["complete.pdf"]

def test_delete_one_removes_selected_record(tmp_path,monkeypatch):
 monkeypatch.setattr(db,"DB_PATH",tmp_path/"one.sqlite3")
 db.init()
 invoice_id,_=db.save("one.pdf","one-hash","pdf",{"seller_name":"Seller"})
 assert db.delete_one(invoice_id) is True
 assert db.get(invoice_id) is None
 assert db.delete_one(invoice_id) is False

def test_replace_batch_is_atomic_and_resets_old_batch_ids(tmp_path,monkeypatch):
 monkeypatch.setattr(db,"DB_PATH",tmp_path/"atomic.sqlite3")
 db.init()
 old_id,_=db.save("old.pdf","old-sha","pdf",{"seller_name":"Old"})
 new_ids=db.replace_batch([
  ("new-a.pdf","new-sha-a","pdf",{"seller_name":"New A"}),
  ("new-b.pdf","new-sha-b","pdf",{"seller_name":"New B"})
 ])
 assert old_id not in new_ids
 assert new_ids==[1,2]
 assert [x["filename"] for x in db.all()]==["new-b.pdf","new-a.pdf"]
