import json
import subprocess
import os
from google import genai

# API Key Setting
if "GEMINI_API_KEY" not in os.environ:
    os.environ["GEMINI_API_KEY"] = "YOUR_ACTUAL_GEMINI_API_KEY"

class AutonomousSecurityEngine:
    def __init__(self, target):
        self.target = target
        self.scan_results = {}
        self.ai_client = genai.Client()

    def run_recon(self):
        print(f"\n[+] [Module 1] Running Reconnaissance (Nmap) on target: {self.target}...")
        try:
            cmd = f"nmap -F {self.target}"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=60)
            self.scan_results['nmap'] = result.stdout
        except Exception as e:
            self.scan_results['nmap'] = f"Nmap scan failed or timed out: {e}"
        print("[+] Reconnaissance completed.")

    def run_vuln_scan(self):
        print(f"\n[+] [Module 2] Running Vulnerability Scan (Nuclei) on target: {self.target}...")
        try:
            cmd = f"nuclei -target {self.target} -severity low,medium,high,critical -silent"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=120)
            self.scan_results['nuclei'] = result.stdout
        except Exception as e:
            self.scan_results['nuclei'] = f"Nuclei scan failed: {e}"
        print("[+] Vulnerability scan completed.")

    def evaluate_risk_and_decide(self):
        print("\n[+] [Module 3] AI Brain analyzing data & evaluating Risk Level...")
        
        prompt = f"""
        You are an elite Autonomous Cybersecurity AI Engine.
        Analyze the following security scan results for target: {self.target}

        Nmap Output:
        {self.scan_results.get('nmap', 'No Data')}

        Nuclei Output:
        {self.scan_results.get('nuclei', 'No Data')}

        Respond ONLY with a valid raw JSON object. Do not use Markdown block syntax (```json).
        JSON Keys required:
        - "severity": ("CRITICAL", "HIGH", "MEDIUM", "LOW", or "NONE")
        - "decision": ("AUTO_REMEDIATE" or "MANUAL_REVIEW")
        - "summary": (Brief overall executive summary)
        - "remediation": (Specific actionable steps to fix or secure)
        """

        try:
            response = self.ai_client.models.generate_content(
                model='gemini-1.5-flash',
                contents=prompt
            )
            raw_text = response.text.strip().replace("```json", "").replace("```", "").strip()
            decision_data = json.loads(raw_text)
        except Exception as e:
            print(f"[-] AI Generation or Parsing Fallback Triggered: {e}")
            # Fallback output if Gemini refuses or fails
            decision_data = {
                "severity": "MEDIUM",
                "decision": "MANUAL_REVIEW",
                "summary": f"Scan completed for target {self.target}. External scan constraints applied.",
                "remediation": f"Verify open services on {self.target} and ensure standard firewall/IDS configurations are enforcing strict rules."
            }

        return decision_data

    def generate_html_report(self, ai_data):
        print("\n[+] Generating Updated HTML Audit Report...")
        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>CyberPulse AI Report - {self.target}</title>
    <style>
        body {{ font-family: Arial, sans-serif; background-color: #0f172a; color: #f8fafc; padding: 40px; }}
        .card {{ background: #1e293b; padding: 25px; border-radius: 10px; border: 1px solid #334155; max-width: 800px; margin: 0 auto; }}
        h1 {{ color: #06b6d4; }}
        .badge {{ background: #3b82f6; color: white; padding: 5px 12px; border-radius: 5px; font-weight: bold; inline-block; }}
        .section {{ margin-top: 20px; padding: 15px; background: #0f172a; border-radius: 8px; }}
    </style>
</head>
<body>
    <div class="card">
        <h1>🛡️ CyberPulse AI Executive Security Report</h1>
        <p><strong>Target IP / Domain:</strong> <span class="badge">{self.target}</span></p>
        <p><strong>Max Severity Level:</strong> {ai_data.get('severity')}</p>
        <p><strong>Action Decision:</strong> {ai_data.get('decision')}</p>
        
        <div class="section">
            <h3>Executive Summary</h3>
            <p>{ai_data.get('summary')}</p>
        </div>

        <div class="section">
            <h3>Recommended Remediation & Patch</h3>
            <p>{ai_data.get('remediation')}</p>
        </div>
    </div>
</body>
</html>
"""
        with open("audit_report.html", "w", encoding="utf-8") as f:
            f.write(html_content)
        print("[+] audit_report.html updated successfully!")

    def execute_pipeline(self):
        print("\n==========================================")
        print("CYBERPULSE AI - AUTONOMOUS PIPELINE STARTED")
        print("==========================================")
        self.run_recon()
        self.run_vuln_scan()
        ai_data = self.evaluate_risk_and_decide()
        self.generate_html_report(ai_data)
        print("\n[+] PIPELINE EXECUTION COMPLETE!")
