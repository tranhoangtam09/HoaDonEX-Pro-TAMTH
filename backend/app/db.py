import sqlite3,json
from .config import DB_PATH

def conn():
 DB_PATH.parent.mkdir(parents=True,exist_ok=True)
 c=sqlite3.connect(DB_PATH);c.row_factory=sqlite3.Row
 return c

def init():
 with conn() as c:
  c.execute("""CREATE TABLE IF NOT EXISTS invoices(id INTEGER PRIMARY KEY AUTOINCREMENT,filename TEXT,sha256 TEXT UNIQUE,source_type TEXT,payload TEXT,created_at TEXT DEFAULT CURRENT_TIMESTAMP,updated_at TEXT DEFAULT CURRENT_TIMESTAMP)""")
  c.execute("""CREATE TABLE IF NOT EXISTS audit(id INTEGER PRIMARY KEY,invoice_id INTEGER,action TEXT,detail TEXT,created_at TEXT DEFAULT CURRENT_TIMESTAMP)""")

def _record(row):
 payload=json.loads(row["payload"])
 payload["id"]=row["id"]
 payload["filename"]=row["filename"]
 return payload

def save(name,sha,kind,payload):
 payload=dict(payload)
 payload.pop("id",None)
 payload["filename"]=name
 with conn() as c:
  cur=c.execute("INSERT OR IGNORE INTO invoices(filename,sha256,source_type,payload) VALUES(?,?,?,?)",(name,sha,kind,json.dumps(payload,ensure_ascii=False)))
  r=c.execute("SELECT id FROM invoices WHERE sha256=?",(sha,)).fetchone()
  if cur.rowcount:c.execute("INSERT INTO audit(invoice_id,action,detail) VALUES(?,?,?)",(r["id"],"created","Uploaded source file"))
  return r["id"],bool(cur.rowcount)

def clear_all():
 with conn() as c:
  c.execute("DELETE FROM audit")
  c.execute("DELETE FROM invoices")

def delete_one(i):
 with conn() as c:
  c.execute("DELETE FROM audit WHERE invoice_id=?",(i,))
  cur=c.execute("DELETE FROM invoices WHERE id=?",(i,))
  return cur.rowcount>0

def delete_unrecognized():
 with conn() as c:
  rows=c.execute("SELECT id,payload FROM invoices").fetchall()
  ids=[]
  for r in rows:
   p=json.loads(r["payload"])
   if not p.get("seller_name") or not p.get("invoice_number") or not p.get("invoice_date"):
    ids.append(r["id"])
  if ids:
   c.executemany("DELETE FROM audit WHERE invoice_id=?",[(i,) for i in ids])
   c.executemany("DELETE FROM invoices WHERE id=?",[(i,) for i in ids])
  return len(ids)

def all():
 with conn() as c:rows=c.execute("SELECT * FROM invoices ORDER BY id DESC").fetchall()
 return [_record(r) for r in rows]

def get(i):
 with conn() as c:r=c.execute("SELECT * FROM invoices WHERE id=?",(i,)).fetchone()
 return None if not r else _record(r)

def update(i,p):
 with conn() as c:
  r=c.execute("SELECT payload FROM invoices WHERE id=?",(i,)).fetchone()
  if not r:return False
  x=json.loads(r["payload"]);x.update(p);x["user_reviewed"]=True
  c.execute("UPDATE invoices SET payload=?,updated_at=CURRENT_TIMESTAMP WHERE id=?",(json.dumps(x,ensure_ascii=False),i))
  c.execute("INSERT INTO audit(invoice_id,action,detail) VALUES(?,?,?)",(i,"edited","User reviewed invoice fields"))
 return True
