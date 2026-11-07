"""Optional Vietnamese OCR adapter using PaddleOCR 2.x."""
from __future__ import annotations
import io
from functools import lru_cache
import fitz
from PIL import Image,ImageOps,ImageEnhance,ImageFilter
@lru_cache(maxsize=1)
def engine():
 try:
  from paddleocr import PaddleOCR
 except Exception as exc:
  raise RuntimeError("Chưa cài OCR tiếng Việt. Cài backend/requirements-ocr.txt trên máy chủ.") from exc
 return PaddleOCR(use_angle_cls=True,lang="vi",show_log=False,use_gpu=False)
def preprocess(image):
 image=ImageOps.exif_transpose(image).convert("L")
 if image.width<1800:
  scale=min(2.5,1800/max(1,image.width))
  image=image.resize((int(image.width*scale),int(image.height*scale)),Image.Resampling.LANCZOS)
 return ImageEnhance.Contrast(image).enhance(1.7).filter(ImageFilter.SHARPEN).convert("RGB")
def _recognize(image):
 import numpy as np
 result=engine().ocr(np.array(preprocess(image)),cls=True);lines=[]
 if result:
  for page in result:
   if page:
    for item in page:
     try:
      txt=str(item[1][0]).strip()
      if txt:lines.append(txt)
     except (IndexError,TypeError):continue
 return lines
def image_to_text(data):
 with Image.open(io.BytesIO(data)) as im:return "\n".join(_recognize(im))
def pdf_to_text(data,max_pages=10):
 doc=fitz.open(stream=data,filetype="pdf");lines=[]
 try:
  for page in doc[:max_pages]:
   pix=page.get_pixmap(matrix=fitz.Matrix(3,3),alpha=False)
   lines.extend(_recognize(Image.frombytes("RGB",[pix.width,pix.height],pix.samples)))
 finally:doc.close()
 return "\n".join(lines)
