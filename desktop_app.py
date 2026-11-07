"""Windows desktop launcher for HOA DON EX PRO – TAMTH."""
from __future__ import annotations
import os, sys, threading, webbrowser
from pathlib import Path
import tkinter as tk
from tkinter import messagebox

def resource_path(relative: str) -> Path:
    base = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))
    return base / relative

def writable_root() -> Path:
    if getattr(sys, "frozen", False):
        base = Path(os.environ.get("LOCALAPPDATA", str(Path.home()))) / "HoaDonEX_PRO_TAMTH"
        return base
    return Path(__file__).resolve().parent

ROOT = writable_root()
DATA = ROOT / "data"
TEMPLATES = DATA / "templates"
DATA.mkdir(parents=True, exist_ok=True)
TEMPLATES.mkdir(parents=True, exist_ok=True)
os.environ["DATA_DIR"] = str(DATA)
os.environ["DATABASE_PATH"] = str(DATA / "invoices.sqlite3")
os.environ["TEMPLATES_DIR"] = str(TEMPLATES)
os.environ.setdefault("API_KEY", "")
os.environ.setdefault("CORS_ORIGINS", "http://127.0.0.1:8000")

sys.path.insert(0, str(resource_path("backend")))
from app.main import app
from fastapi.staticfiles import StaticFiles
FRONTEND = resource_path("frontend")
if not FRONTEND.exists():
    raise RuntimeError("Không tìm thấy giao diện frontend được đóng gói.")
app.mount("/", StaticFiles(directory=str(FRONTEND), html=True), name="frontend")

import uvicorn

class DesktopApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("HOA DON EX PRO – TAMTH")
        self.root.geometry("440x230")
        self.root.resizable(False, False)
        self.root.protocol("WM_DELETE_WINDOW", self.close)
        tk.Label(self.root, text="HOA DON EX PRO – TAMTH", font=("Segoe UI", 16, "bold")).pack(pady=(22, 8))
        self.status = tk.Label(self.root, text="Đang khởi động bộ xử lý...", font=("Segoe UI", 10))
        self.status.pack(pady=8)
        tk.Button(self.root, text="Mở ứng dụng", width=22, command=self.open_app).pack(pady=6)
        tk.Label(self.root, text="Dữ liệu lưu cục bộ trên máy tính này.\nĐóng cửa sổ này để dừng ứng dụng.", font=("Segoe UI", 9), fg="#555").pack(pady=8)
        self.server = uvicorn.Server(uvicorn.Config(app, host="127.0.0.1", port=8000, log_level="warning"))
        self.thread = threading.Thread(target=self.run_server, daemon=True)
        self.thread.start()
        self.root.after(1400, self.open_app)
        self.root.after(800, self.check_server)

    def run_server(self):
        self.server.run()

    def check_server(self):
        if self.server.started:
            self.status.config(text="● Đang hoạt động tại http://127.0.0.1:8000", fg="green")
        elif self.thread.is_alive():
            self.root.after(800, self.check_server)
        else:
            self.status.config(text="Không thể khởi động bộ xử lý.", fg="red")
            messagebox.showerror("Lỗi khởi động", "Không thể mở bộ xử lý. Vui lòng liên hệ người hỗ trợ.")

    def open_app(self):
        webbrowser.open("http://127.0.0.1:8000/")

    def close(self):
        if messagebox.askyesno("Thoát ứng dụng", "Bạn muốn dừng HOA DON EX PRO – TAMTH?"):
            self.server.should_exit = True
            self.root.destroy()

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    DesktopApp().run()
