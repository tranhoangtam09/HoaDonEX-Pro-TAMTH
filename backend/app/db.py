import sqlite3,json
from .config import DB_PATH
def conn():
 DB_PATH.parent.mkdir(parents=True,exist_ok=True);c=sqlite3.connect(DB_PATH);c.row_factory=sqlite3.Row;return c
def init():
 with conn() as c:
  c.execute("""CREATE TABLE IF NOT EXISTS invoices(id INTEGER PRIMARY KEY AUTOINCREMENT,filename TEXT,sha256 TEXT UNIQUE,source_type TEXT,payload TEXT,created_at TEXT DEFAULT CURRENT_TIMESTAMP,updated_at TEXT DEFAULT CURRENT_TIMESTAMP)""")
  c.execute("""CREATE TABLE IF NOT EXISTS audit(id INTEGER PRIMARY KEY,invoice_id INTEGER,action TEXT,detail TEXT,created_at TEXT DEFAULT CURRENT_TIMESTAMP)""")
def save(name,sha,kind,payload):
 with conn() as c:
  cur=c.execute("INSERT OR IGNORE INTO invoices(filename,sha256,source_type,payload) VALUES(?,?,?,?)",(name,sha,kind,json.dumps(payload,ensure_ascii=False)))
  r=c.execute("SELECT id FROM invoices WHERE sha256=?",(sha,)).fetchone()
  if cur.rowcount:c.execute("INSERT INTO audit(invoice_id,action,detail) VALUES(?,?,?)",(r["id"],"created","Uploaded source file"))
  return r["id"],bool(cur.rowcount)
def all():
 with conn() as c:rows=c.execute("SELECT * FROM invoices ORDER BY id DESC").fetchall()
 return [dict(id=r["id"],filename=r["filename"],**json.loads(r["payload"])) for r in rows]
def get(i):
 with conn() as c:r=c.execute("SELECT * FROM invoices WHERE id=?",(i,)).fetchone()
 return None if not r else dict(id=r["id"],filename=r["filename"],**json.loads(r["payload"]))
def update(i,p):
 with conn() as c:
  r=c.execute("SELECT payload FROM invoices WHERE id=?",(i,)).fetchone()
  if not r:return False
  x=json.loads(r["payload"]);x.update(p);x["user_reviewed"]=True
  c.execute("UPDATE invoices SET payload=?,updated_at=CURRENT_TIMESTAMP WHERE id=?",(json.dumps(x,ensure_ascii=False),i))
  c.execute("INSERT INTO audit(invoice_id,action,detail) VALUES(?,?,?)",(i,"edited","User reviewed invoice fields"))
 return True
