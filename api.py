from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, HTMLResponse
from pydantic import BaseModel
from main import AutonomousSecurityEngine
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import os

app = FastAPI(title="CyberPulse AI Production Engine")

class ScanRequest(BaseModel):
    email: str
    target: str

def send_email_report(to_email: str, target: str, report_file: str):
    sender_email = "simegnewfetene68@gmail.com"  # የራስህ Gmail
    sender_password = "izyihfbasdsisdmq" # የ16 ዲጂት App Password

    msg = MIMEMultipart()
    msg['From'] = f"CyberPulse AI <{sender_email}>"
    msg['To'] = to_email
    msg['Subject'] = f"🛡️ Executive AI Security Report - Target: {target}"

    body = f"Greetings,\n\nYour automated AI Security Audit for target {target} has been successfully executed.\nPlease find attached your full Executive Security Audit Report.\n\nBest regards,\nCyberPulse AI Security Engine"
    msg.attach(MIMEText(body, 'plain'))

    try:
        if os.path.exists(report_file):
            with open(report_file, "rb") as attachment:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(attachment.read())
                encoders.encode_base64(part)
                part.add_header('Content-Disposition', f'attachment; filename="CyberPulse_Audit_Report.html"')
                msg.attach(part)

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, to_email, msg.as_string())
        server.quit()
        print(f"✅ REAL EMAIL DISPATCHED: Security Audit Report successfully sent to {to_email}!")
        return True
    except Exception as e:
        print(f"[-] Real Email Dispatching Failed: {e}")
        return False

@app.get("/", response_class=HTMLResponse)
def serve_landing_page():
    if os.path.exists("index.html"):
        with open("index.html", "r", encoding="utf-8") as f:
            return f.read()
    return "<h1>index.html not found</h1>"

@app.post("/api/scan-request")
def handle_scan_request(req: ScanRequest):
    try:
        print(f"\n[+] New Scan Request Received for IP: {req.target} | Email: {req.email}")
        
        # 1. AI Pipeline ማስኬድ
        engine = AutonomousSecurityEngine(req.target)
        engine.execute_pipeline()
        
        # 2. እውነተኛ ኢሜይል መላክ
        send_email_report(req.email, req.target, "audit_report.html")
        
        return {
            "status": "SUCCESS",
            "message": "AI Security Audit completed and sent directly to your email inbox!",
            "target": req.target,
            "report_url": "/report"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/report")
def get_report():
    report_path = "audit_report.html"
    if os.path.exists(report_path):
        return FileResponse(report_path, media_type="text/html")
    return {"error": "No audit report found."}
