FROM python:3.11-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1
RUN apt-get update && apt-get install -y --no-install-recommends libgomp1 libglib2.0-0 libgl1 libsm6 libxext6 libxrender1 && rm -rf /var/lib/apt/lists/*
WORKDIR /opt/app/backend
COPY backend/requirements-ocr.txt ./requirements-ocr.txt
COPY backend/requirements.txt ./requirements.txt
RUN pip install --upgrade pip && pip install -r requirements-ocr.txt
COPY backend/ ./
RUN mkdir -p /var/data/templates
ENV DATABASE_PATH=/var/data/invoices.sqlite3
ENV TEMPLATES_DIR=/var/data/templates
EXPOSE 8000
CMD ["uvicorn","app.main:app","--host","0.0.0.0","--port","8000"]
