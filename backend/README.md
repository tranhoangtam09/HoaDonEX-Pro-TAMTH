# Backend FastAPI + PaddleOCR Vietnamese

Install requirements.txt and requirements-ocr.txt, then run uvicorn app.main:app --reload.

PDF text layers are extracted first. PaddleOCR Vietnamese (lang=vi) is used for scanned PDFs, images, or incomplete text extraction. OCR initializes lazily; the first run may download model weights.

## Original workbook templates
Provision these two original Excel files through the frontend panel "Nạp hai mẫu Excel gốc":
- Bang_ke_hoa_don_chuyen_khoan_VND.xlsx (sheet Bảng kê hóa đơn, 12 columns)
- Bang_ke_hoa_don_bu_dap_VND.xlsx (sheet Bảng kê hóa đơn GN bù đắp, 13 columns)

The backend validates the sheet name, header row 2 and column count, then stores the workbook on the persistent disk.

Transfer mapping A:L: STT, buyer/beneficiary tax ID, buyer/beneficiary name, beneficiary account, invoice form, invoice symbol, invoice number/order reference, invoice date, invoice amount, currency, item/purpose, financing amount.

Compensation mapping A:M: STT, seller/issuer tax ID, seller/issuer name, invoice form, invoice symbol, invoice number/order reference, invoice date, invoice amount, currency, item/purpose, financing amount, payment date, payment amount.

The financing amount, beneficiary bank account and payment details are never inferred from invoice total. They are entered and reviewed manually. Export retains the original workbook, instructions sheet and formatting.

## Security
Set API_KEY in the hosting environment. The frontend asks the operator to enter it. This shared key is only a basic access gate, not per-user authentication. Use HTTPS, persistent storage and appropriate retention/access controls before real financial documents are processed.
