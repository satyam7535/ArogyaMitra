"""
ArogyaMitra P5.2 Rate Limiter Verification
Tests production rate limiting at both Edge Nginx and Express API boundaries.
Shows HTTP 429 Too Many Requests and Retry-After header under sustained load.
"""
import subprocess
import json
import datetime
import urllib3
import requests

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def get_git_info():
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    status = subprocess.check_output(["git", "status", "--porcelain"], text=True).strip()
    dirty = "DIRTY" if status else "CLEAN"
    date = datetime.datetime.now(datetime.timezone.utc).isoformat()
    return commit, dirty, date

def main():
    commit, dirty, date = get_git_info()
    out = []
    out.append("# EVIDENCE RECORD: P5.2 Production Rate Limiter Verification")
    out.append("# COMMAND: python scripts/test_p5_rate_limit.py")
    out.append(f"# DATE: {date}")
    out.append(f"# COMMIT: {commit}")
    out.append(f"# STATUS: {dirty}")
    out.append("# -------------------------------------------------------------")
    out.append("### 1. Ingress HTTPS Rate Limiter Test (POST https://localhost/api/v1/worker/login)")
    out.append("Testing 20 sequential authentication requests against rate-limited worker login...")
    
    url = "https://localhost/api/v1/worker/login"
    payload = {"email": "worker.primary@arogyamitra.gov.in", "password": "incorrect_password_for_ratelimit_test"}
    headers = {"Content-Type": "application/json"}
    
    rate_limited_observed = False
    
    for i in range(1, 21):
        try:
            r = requests.post(url, json=payload, headers=headers, verify=False, timeout=5)
            status = r.status_code
            retry_after = r.headers.get("Retry-After") or r.headers.get("retry-after")
            reset_time = r.headers.get("RateLimit-Reset") or r.headers.get("ratelimit-reset")
            limit = r.headers.get("RateLimit-Limit") or r.headers.get("ratelimit-limit")
            remaining = r.headers.get("RateLimit-Remaining") or r.headers.get("ratelimit-remaining")
            
            line = f"Request {i:02d}: HTTP {status} | Retry-After: {retry_after} | Limit: {limit} | Remaining: {remaining} | Reset: {reset_time}"
            out.append(line)
            
            if status == 429:
                rate_limited_observed = True
                if i == 16:
                    out.append("\n--- HTTP 429 RESPONSE HEADERS ---")
                    for k, v in r.headers.items():
                        out.append(f"{k}: {v}")
                    out.append("\n--- HTTP 429 RESPONSE BODY ---")
                    out.append(r.text)
                    out.append("---------------------------------\n")
        except Exception as e:
            out.append(f"Request {i:02d}: ERROR - {str(e)}")
            
    out.append(f"\nVerification Result: Rate Limit 429 Observed = {rate_limited_observed}")
    
    # Also verify curl command raw output directly
    out.append("\n### 2. Direct curl Probe Capturing Raw HTTP/1.1 429 Protocol Output")
    curl_cmd = [
        "curl.exe", "-k", "-i", "-s", "-X", "POST",
        "https://localhost/api/v1/worker/login",
        "-H", "Content-Type: application/json",
        "-d", json.dumps(payload)
    ]
    curl_res = subprocess.run(curl_cmd, capture_output=True, text=True, errors="replace")
    out.append(curl_res.stdout)
    
    report = "\n".join(out)
    print(report)
    with open("docs/evidence/rate_limit_429.txt", "w", encoding="utf-8") as f:
        f.write(report)

if __name__ == "__main__":
    main()

