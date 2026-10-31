"""
ArogyaMitra P6.1 Transport Layer Security & MITM Defense Demonstration
Proves:
  1. Cleartext HTTP interception defense: Insecure HTTP requests are rejected at Edge with HTTP 301 Permanent Redirect to HTTPS.
  2. Strict TLS certificate validation: Untrusted / rogue certificates trigger immediate client-side SSLCertVerificationError abort.
  3. Validated TLS connection: Successful encrypted transmission when certificate is authenticated against trusted root.
"""

import datetime
import os
import ssl
import socket
import subprocess
import requests

def get_git_info():
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    status = subprocess.check_output(["git", "status", "--porcelain"], text=True).strip()
    dirty = "DIRTY" if status else "CLEAN"
    date = datetime.datetime.now(datetime.timezone.utc).isoformat()
    return commit, dirty, date

def main():
    commit, dirty, date = get_git_info()
    out = []
    out.append("# EVIDENCE RECORD: P6.1 Transport Security & Man-In-The-Middle (MITM) Defense Demonstration")
    out.append("# COMMAND: python scripts/test_p6_mitm_demo.py")
    out.append(f"# DATE: {date}")
    out.append(f"# COMMIT: {commit}")
    out.append(f"# STATUS: {dirty}")
    out.append("# TARGET: http://localhost:80 -> https://localhost:443 (Edge Nginx Gateway)")
    out.append("# -----------------------------------------------------------------------------------------\n")
    
    # -------------------------------------------------------------------------
    # PART A: Cleartext HTTP Downgrade Interception Defense (HTTP 301 Enforcement)
    # -------------------------------------------------------------------------
    out.append("### PART A: Cleartext HTTP Interception & Downgrade Defense")
    out.append("Sending cleartext HTTP request to http://localhost/api/v1/health (allow_redirects=False)...")
    try:
        r_http = requests.get("http://localhost/api/v1/health", allow_redirects=False, timeout=5)
        out.append(f"Response Status: HTTP {r_http.status_code}")
        out.append(f"Location Header: {r_http.headers.get('Location')}")
        out.append(f"Server Header: {r_http.headers.get('Server')}")
        
        if r_http.status_code == 301 and r_http.headers.get("Location", "").startswith("https://"):
            out.append("Result: PASS - Cleartext HTTP is strictly rejected with HTTP 301 Permanent Redirect to HTTPS.\n")
        else:
            out.append("Result: FAIL - HTTP request was not redirected to HTTPS.\n")
    except Exception as e:
        out.append(f"Result: ERROR - {str(e)}\n")
        
    # -------------------------------------------------------------------------
    # PART B: Strict TLS Certificate Validation (Rejection of Untrusted / Spoofed Cert)
    # -------------------------------------------------------------------------
    out.append("### PART B: TLS Certificate Validation Rejection (MITM / Untrusted CA Defense)")
    out.append("Attempting TLS connection to https://localhost/api/v1/health with strict system CA verification...")
    try:
        r_strict = requests.get("https://localhost/api/v1/health", verify=True, timeout=5)
        out.append(f"Unexpected Success: HTTP {r_strict.status_code} (Certificate was accepted by default store)")
        out.append("Result: FAIL - Self-signed / untrusted edge cert should have been rejected by default CA bundle.\n")
    except requests.exceptions.SSLError as ssl_err:
        out.append("Client TLS Abort Caught: requests.exceptions.SSLError")
        out.append(f"Error Message: {str(ssl_err)}")
        out.append("Result: PASS - Client strictly aborted TLS handshake because gateway cert is not in default public trust store (prevents rogue CA interception).\n")
    except Exception as e:
        out.append(f"Result: ERROR - {type(e).__name__}: {str(e)}\n")
        
    # -------------------------------------------------------------------------
    # PART C: Successful Encrypted Communication with Verified Root of Trust
    # -------------------------------------------------------------------------
    out.append("### PART C: Encrypted Transmission with Validated Certificate Authority")
    cert_path = "deploy/certs/arogyamitra.crt"
    out.append(f"Connecting to https://arogyamitra.local/api/v1/health using trusted root CA ({cert_path})...")
    
    # Run via curl with --resolve and --cacert
    curl_cmd = [
        "curl.exe", "-i", "-s",
        "--resolve", "arogyamitra.local:443:127.0.0.1",
        "--cacert", cert_path,
        "https://arogyamitra.local/api/v1/health"
    ]
    res = subprocess.run(curl_cmd, capture_output=True, text=True, errors="replace")
    out.append(res.stdout.strip())
    
    if "HTTP/1.1 200 OK" in res.stdout and '"status":"healthy"' in res.stdout:
        out.append("\nResult: PASS - Secure encrypted session established when authenticating against trusted root CA.")
    else:
        out.append("\nResult: FAIL - TLS handshake or verification failed.")
        
    report = "\n".join(out)
    print(report)
    with open("docs/evidence/mitm_demo.txt", "w", encoding="utf-8") as f:
        f.write(report)

if __name__ == "__main__":
    main()
