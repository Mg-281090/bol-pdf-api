from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
import fitz  # PyMuPDF
import re

app = FastAPI()

@app.post("/extract")
async def extract_bol_data(file: UploadFile = File(...)):
    try:
        content = await file.read()

        # Load PDF
        pdf = fitz.open(stream=content, filetype="pdf")
        text = ""
        for page in pdf:
            text += page.get_text("text")

        # Extract fields using regex
        bol_number = re.search(r"(BILL OF LADING\s*NUMBER|B/L NO\.?)[:\s]*([A-Z0-9\-]+)", text, re.IGNORECASE)
        shipper = re.search(r"SHIPPER[:\s]*(.*?)(?=CONSIGNEE|NOTIFY|$)", text, re.IGNORECASE | re.DOTALL)
        consignee = re.search(r"CONSIGNEE[:\s]*(.*?)(?=NOTIFY|$)", text, re.IGNORECASE | re.DOTALL)
        notify_party = re.search(r"NOTIFY\s*PARTY[:\s]*(.*?)(?=$)", text, re.IGNORECASE | re.DOTALL)

        return JSONResponse(content={
            "BillOfLadingNumber": bol_number.group(2).strip() if bol_number else "",
            "Shipper": shipper.group(1).strip() if shipper else "",
            "Consignee": consignee.group(1).strip() if consignee else "",
            "NotifyParty": notify_party.group(1).strip() if notify_party else ""
        })

    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=400)
