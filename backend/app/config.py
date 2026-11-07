import os
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()
ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/"data";TEMPLATES=ROOT/"templates";DATA.mkdir(exist_ok=True)
MAX_UPLOAD_MB=int(os.getenv("MAX_UPLOAD_MB","20"))
DB_PATH=Path(os.getenv("DATABASE_PATH",str(DATA/"invoices.sqlite3")))
CORS_ORIGINS=[x.strip() for x in os.getenv("CORS_ORIGINS","http://localhost:5500,http://127.0.0.1:5500").split(",") if x.strip()]
