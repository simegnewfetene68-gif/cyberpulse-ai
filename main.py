import os
from fastapi import FastAPI, Request
from fastapi.responses import FileResponse

app = FastAPI()
@app.post("/scan")
async def handle_scan(request: Request):
    return {"status": "success", "message": "Scan initiated"}
@app.get("/undefined")
def fix_undefined():
    return FileResponse("index.html")

@app.get("/")
@app.get("/undefined")
@app.get("/index.html")
def read_root():
    if os.path.exists("index.html"):
        return FileResponse("index.html")
    return {"status": "CyberPulse AI API is running"}

@app.api_route("/api/scan-request", methods=["GET", "POST"])
async def scan_request(request: Request):
    try:
        data = await request.json()
    except Exception:
        data = {}
    return {
        "status": "success",
        "message": "Scan initiated successfully",
        "data": data
    }
@app.get("/audit_report.html")
def get_report():
    if os.path.exists("audit_report.html"):
        return FileResponse("audit_report.html")
    return {"error": "Report not found"}
