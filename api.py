import os
import uuid
import requests
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import FileResponse, RedirectResponse

app = FastAPI()

# Fetch keys directly from Environment Variables
CHAPA_SECRET_KEY = os.getenv("CHAPA_SECRET_KEY")
BASE_URL = os.getenv("RENDER_EXTERNAL_URL", "https://cyberpulse-ai-dwxt.onrender.com")

@app.get("/")
def read_root():
    if os.path.exists("index.html"):
        return FileResponse("index.html")
    return {"message": "CyberPulse AI API is Running"}

@app.get("/audit_report.html")
def get_report():
    if os.path.exists("audit_report.html"):
        return FileResponse("audit_report.html")
    return {"error": "Report not found"}

@app.get("/undefined")
def fix_undefined():
    return FileResponse("index.html")

# 1. Initiating Payment with Chapa Gateway
@app.post("/scan")
async def initiate_scan_payment(request: Request):
    try:
        body = await request.json()
        email = body.get("email")
        target = body.get("target")

        if not email or not target:
            raise HTTPException(status_code=400, detail="Email and Target are required.")

        tx_ref = f"cyberpulse-{uuid.uuid4().hex[:8]}"

        payload = {
            "amount": "100",  # ETB 100
            "currency": "ETB",
            "email": email,
            "first_name": "Customer",
            "last_name": "User",
            "tx_ref": tx_ref,
            "callback_url": f"{BASE_URL}/verify-payment/{tx_ref}",
            "return_url": f"{BASE_URL}/audit_report.html?tx_ref={tx_ref}",
            "customization": {
                "title": "CyberPulse AI Audit",
                "description": f"Security Scan Payment for {target}"
            }
        }

        headers = {
            "Authorization": f"Bearer {CHAPA_SECRET_KEY}",
            "Content-Type": "application/json"
        }

        chapa_response = requests.post("https://api.chapa.co/v1/transaction/initialize", json=payload, headers=headers)
        res_data = chapa_response.json()

        if res_data.get("status") == "success":
            return {"status": "success", "checkout_url": res_data["data"]["checkout_url"]}
        else:
            # Fallback direct access if API error
            return {"status": "success", "checkout_url": f"/audit_report.html?target={target}"}

    except Exception:
        return {"status": "success", "checkout_url": f"/audit_report.html?target={target}"}

# 2. Verify Payment Route
@app.get("/verify-payment/{tx_ref}")
def verify_payment(tx_ref: str):
    headers = {"Authorization": f"Bearer {CHAPA_SECRET_KEY}"}
    response = requests.get(f"https://api.chapa.co/v1/transaction/verify/{tx_ref}", headers=headers)
    res_data = response.json()

    if res_data.get("status") == "success":
        return RedirectResponse(url="/audit_report.html?status=paid")
    else:
        return RedirectResponse(url="/?error=payment_failed")
