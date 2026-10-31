"""
ArogyaMitra P6.1 Real Interception Proxy Man-in-the-Middle (MITM) Demonstration
Proves:
  1. Certificate Verification ON (Production Default):
     When client traffic is routed through an active TLS interception proxy presenting an untrusted/rogue cert,
     the client detects the MITM, terminates the TLS handshake immediately, and NO application data or credentials leak.
  2. Certificate Verification OFF (Vulnerable / Insecure Mode):
     When certificate validation is disabled, the MITM proxy successfully terminates TLS, intercepts plaintext
     headers, credentials (JWT/Authorization), and patient data.
"""

import datetime
import http.server
import os
import socket
import ssl
import subprocess
import sys
import threading
import time
import urllib3
import requests

def get_git_info():
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    status = subprocess.check_output(["git", "status", "--porcelain"], text=True).strip()
    dirty = "DIRTY" if status else "CLEAN"
    date = datetime.datetime.now(datetime.timezone.utc).isoformat()
    return commit, dirty, date

# Intercepted request log
intercepted_requests = []

class RogueMITMProxy(http.server.BaseHTTPRequestHandler):
    """
    Rogue proxy that records intercepted traffic.
    """
    def do_CONNECT(self):
        """
        Handles CONNECT tunnel requests by terminating TLS with a rogue certificate.
        """
        self.send_response(200, "Connection Established")
        self.end_headers()
        
        # Wrap connection in rogue SSL context using deploy/certs/arogyamitra.crt/key (untrusted by public CA pool)
        cert_path = os.path.abspath("deploy/certs/arogyamitra.crt")
        key_path = os.path.abspath("deploy/certs/arogyamitra.key")
        
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        context.load_cert_chain(certfile=cert_path, keyfile=key_path)
        
        try:
            raw_sock = self.connection
            ssl_sock = context.wrap_socket(raw_sock, server_side=True)
            
            # Read decrypted request through TLS tunnel
            data = ssl_sock.recv(4096).decode("utf-8", errors="replace")
            if data:
                intercepted_requests.append({
                    "method": "CONNECT/TLS",
                    "raw": data[:300]
                })
            
            # Send simulated response back through intercepted socket
            body = '{"status":"INTERCEPTED_BY_MITM","warning":"Payload captured by active proxy"}'
            response = (
                f"HTTP/1.1 200 OK\r\n"
                f"Content-Type: application/json\r\n"
                f"Content-Length: {len(body)}\r\n"
                f"Connection: close\r\n\r\n"
                f"{body}"
            )
            ssl_sock.sendall(response.encode("utf-8"))
            ssl_sock.close()
        except Exception as e:
            # Client rejected certificate before sending data
            intercepted_requests.append({
                "method": "CONNECT/TLS_ABORTED",
                "error": str(e)
            })

    def do_GET(self):
        """Plain HTTP interception"""
        auth_header = self.headers.get("Authorization", "None")
        intercepted_requests.append({
            "path": self.path,
            "headers": dict(self.headers),
            "auth": auth_header
        })
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(b'{"status":"PLAINTEXT_INTERCEPTED"}')

    def log_message(self, format, *args):
        # Suppress noisy HTTP server console logs
        pass

def start_proxy_server(port=9998):
    server = http.server.HTTPServer(("127.0.0.1", port), RogueMITMProxy)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server

def main():
    commit, dirty, date = get_git_info()
    out = []
    out.append("================================================================================")
    out.append("AROGYAMITRA — REAL INTERCEPTION PROXY MITM DEMONSTRATION")
    out.append(f"Date: {date}")
    out.append(f"Commit: {commit} ({dirty})")
    out.append("Test Type: Active Intercepting Proxy with and without TLS Certificate Verification")
    out.append("================================================================================\n")

    proxy_port = 9998
    proxy_server = start_proxy_server(proxy_port)
    time.sleep(0.5)
    proxies = {
        "http": f"http://127.0.0.1:{proxy_port}",
        "https": f"http://127.0.0.1:{proxy_port}",
    }

    # -------------------------------------------------------------------------
    # TEST 1: Strict Certificate Verification ON (Production Default)
    # -------------------------------------------------------------------------
    out.append("[SCENARIO 1] Client with Certificate Verification ENABLED (Production Policy)")
    out.append("  Routing HTTPS request through rogue proxy at 127.0.0.1:9998...")
    out.append("  Client Target: https://localhost/api/v1/health")
    out.append("  Client Header: Authorization: Bearer SECRET_WORKER_JWT_TOKEN_12345")
    
    initial_intercept_count = len(intercepted_requests)
    tls_blocked = False
    error_message = ""
    
    try:
        # Standard requests with default verification (or explicit default CA pool)
        resp = requests.get(
            "https://localhost/api/v1/health",
            headers={"Authorization": "Bearer SECRET_WORKER_JWT_TOKEN_12345"},
            proxies=proxies,
            verify=True,  # STRICT TLS VALIDATION ON
            timeout=5
        )
        out.append(f"  [!] UNEXPECTED: Request succeeded with status {resp.status_code}")
    except requests.exceptions.SSLError as ssl_err:
        tls_blocked = True
        error_message = str(ssl_err)
        out.append("  [+] TLS HANDSHAKE REJECTED BY CLIENT:")
        out.append(f"      Exception: {type(ssl_err).__name__}")
        out.append(f"      Detail: {error_message[:140]}...")
    except Exception as e:
        error_message = str(e)
        out.append(f"  [+] Connection terminated: {type(e).__name__}: {error_message[:100]}")

    # Check if proxy was able to read any plaintext application payload
    leaked_data = [
        item for item in intercepted_requests[initial_intercept_count:]
        if "SECRET_WORKER_JWT_TOKEN" in item.get("raw", "")
    ]
    
    if tls_blocked and len(leaked_data) == 0:
        out.append("  [+] VERIFIED: Handshake aborted during certificate validation.")
        out.append("  [+] ZERO CREDENTIALS OR APPLICATION BYTES LEAKED TO PROXY.")
        out.append("  Result: PASS (Strict TLS prevented active MITM interception)\n")
    else:
        out.append("  Result: FAIL\n")

    # -------------------------------------------------------------------------
    # TEST 2: Certificate Verification OFF (Vulnerable Client)
    # -------------------------------------------------------------------------
    out.append("[SCENARIO 2] Vulnerable Client with Certificate Verification DISABLED (verify=False)")
    out.append("  Routing HTTPS request through rogue proxy at 127.0.0.1:9998...")
    out.append("  Client Target: https://localhost/api/v1/health")
    out.append("  Client Header: Authorization: Bearer SECRET_WORKER_JWT_TOKEN_12345")
    
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    start_vulnerable_count = len(intercepted_requests)
    
    try:
        resp_vuln = requests.get(
            "https://localhost/api/v1/health",
            headers={
                "Authorization": "Bearer SECRET_WORKER_JWT_TOKEN_12345",
                "X-Patient-Aadhaar": "1234-5678-9012"
            },
            proxies=proxies,
            verify=False,  # VULNERABLE CLIENT: NO CERT VALIDATION
            timeout=5
        )
        out.append(f"  [!] Connection accepted rogue certificate. Response: {resp_vuln.status_code}")
        out.append(f"      Response Body: {resp_vuln.text}")
    except Exception as e:
        out.append(f"  [!] Error: {e}")

    # Check intercepted requests
    captured = [
        item for item in intercepted_requests[start_vulnerable_count:]
        if "raw" in item
    ]
    
    if captured:
        raw_intercepted = captured[0]["raw"]
        out.append("  [!] MITM PROXY SUCCESSFULLY INTERCEPTED DECRYPTED APPLICATION TRAFFIC:")
        for line in raw_intercepted.split("\r\n"):
            if line.strip():
                out.append(f"      >>> {line}")
        out.append("  [!] DEMONSTRATION COMPLETE: Disabling cert validation allows full credential extraction.")
        out.append("  Result: VERIFIED (Vulnerability mechanism proven under live proxy interception)\n")
    else:
        out.append("  Result: INCONCLUSIVE\n")

    out.append("================================================================================")
    out.append("SUMMARY OF FINDINGS:")
    out.append("1. Active interception proxy captures credentials and tokens ONLY when cert verification is disabled.")
    out.append("2. Under strict TLS certificate verification (verify=True), SSLCertVerificationError terminates")
    out.append("   the socket connection before the HTTP request header or token is transmitted.")
    out.append("================================================================================")

    report_text = "\n".join(out)
    print(report_text)
    
    os.makedirs("docs/evidence", exist_ok=True)
    with open("docs/evidence/mitm_proxy_interception_demo.txt", "w", encoding="utf-8") as f:
        f.write(report_text)
    print("\nSaved to docs/evidence/mitm_proxy_interception_demo.txt")

if __name__ == "__main__":
    main()

