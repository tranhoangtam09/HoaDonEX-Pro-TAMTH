# Backend
Install `pip install -r requirements.txt`, then run `uvicorn app.main:app --reload`.

OCR dependencies are optional. Current image files are flagged for manual review; OCR is not yet wired into the extraction pipeline. XML/PDF field mappings are heuristic and must be customized for each invoice provider. Excel export requires sanitized approved templates in `templates/` and header mapping validation against those exact workbooks.
