import os
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()
ROOT=Path(__file__).resolve().parents[1]
DATA=Path(os.getenv("DATA_DIR",str(ROOT/"data")));DATA.mkdir(parents=True,exist_ok=True)
TEMPLATES=Path(os.getenv("TEMPLATES_DIR",str(DATA/"templates")))
MAX_UPLOAD_MB=int(os.getenv("MAX_UPLOAD_MB","20"))
API_KEY=os.getenv("API_KEY","")
DB_PATH=Path(os.getenv("DATABASE_PATH",str(DATA/"invoices.sqlite3")))
DEFAULT_ORIGINS="http://localhost:5500,http://127.0.0.1:5500,https://tranhoangtam09.github.io"
CORS_ORIGINS=[x.strip() for x in os.getenv("CORS_ORIGINS",DEFAULT_ORIGINS).split(",") if x.strip()]
