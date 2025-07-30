from fastapi import FastAPI, File, UploadFile
from PyPDF2 import PdfReader
import re

app = FastAPI()

def extract_data_from_pdf(file):
    reader = PdfReader(file)
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"

    # Regex-based extraction
    data = {
        "BillOfLadingNumber": re.search(r"(Bill of Lading|B/L No)\s*[:\-]?\s*(\S+)", text, re.IGNORECASE),
        "Shipper": re.search(r"Shipper\s*[:\-]?\s*(.+?)(?=Consignee|Notify|$)", text, re.IGNORECASE | re.DOTALL),
        "Consignee": re.search(r"Consignee\s*[:\-]?\s*(.+?)(?=Notify|$)", text, re.IGNORECASE | re.DOTALL),
        "NotifyParty": re.search(r"Notify\s*Party\s*[:\-]?\s*(.+?)(?=$)", text, re.IGNORECASE | re.DOTALL)
    }

    return {
        "BillOfLadingNumber": data["BillOfLadingNumber"].group(2) if data["BillOfLadingNumber"] else "",
        "Shipper": data["Shipper"].group(1).strip() if data["Shipper"] else "",
        "Consignee": data["Consignee"].group(1).strip() if data["Consignee"] else "",
        "NotifyParty": data["NotifyParty"].group(1).strip() if data["NotifyParty"] else ""
    }

@app.post("/extract")
async def extract(file: UploadFile = File(...)):
    result = extract_data_from_pdf(file.file)
    return result
