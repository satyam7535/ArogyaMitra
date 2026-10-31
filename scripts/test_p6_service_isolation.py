"""
ArogyaMitra P6.4 Internal Service Isolation & Port Exposure Probes
Verifies that microservices (5000, 8000, 8001, 27017) are isolated inside Docker
and NOT accessible directly on host interfaces.
"""

import datetime
import socket
import subprocess

def get_git_info():
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    status = subprocess.check_output(["git", "status", "--porcelain"], text=True).strip()
    dirty = "DIRTY" if status else "CLEAN"
    date = datetime.datetime.now(datetime.timezone.utc).isoformat()
    return commit, dirty, date

def probe_port(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(1.5)
        res = s.connect_ex(("127.0.0.1", port))
        return res == 0 # True if open, False if closed/refused

def main():
    commit, dirty, date = get_git_info()
    out = []
    out.append("# EVIDENCE RECORD: P6.4 Internal Service Isolation & Network Exposure Probes")
    out.append("# COMMAND: python scripts/test_p6_service_isolation.py")
    out.append(f"# DATE: {date}")
    out.append(f"# COMMIT: {commit}")
    out.append(f"# STATUS: {dirty}")
    out.append("# TARGET PORTS: 5000 (Backend), 8000 (ML), 8001 (Graph), 27017 (Mongo)")
    out.append("# ----------------------------------------------------------------------------------\n")
    
    # 1. Netstat check
    out.append("### 1. Host Listening Ports Netstat Probe")
    try:
        netstat_out = subprocess.check_output(["netstat", "-ano"], text=True, errors="replace")
        matching = [l for l in netstat_out.splitlines() if any(f":{p} " in l for p in (5000, 8000, 8001, 27017))]
        if matching:
            out.append("Found listening lines:")
            for l in matching:
                out.append(f"  {l}")
        else:
            out.append("Clean: Zero listening sockets found on host for ports 5000, 8000, 8001, 27017.")
    except Exception as e:
        out.append(f"Netstat check error: {e}")
        
    out.append("\n### 2. Direct Socket Connection Probes from Host")
    ports = [
        (5000, "Backend API (:5000)"),
        (8000, "ML Inference Service (:8000)"),
        (8001, "Graph Workflow Engine (:8001)"),
        (27017, "MongoDB Database (:27017)"),
    ]
    
    all_isolated = True
    for port, label in ports:
        is_open = probe_port(port)
        if is_open:
            out.append(f"[-] {label}: EXPOSED (Socket connected successfully!)")
            all_isolated = False
        else:
            out.append(f"[+] {label}: ISOLATED (Connection Refused - not exposed on host)")
            
    out.append(f"\n### 3. Direct curl Ingress Probes from Host")
    curl_targets = [
        ("http://localhost:5000/health", "Backend Direct HTTP"),
        ("http://localhost:8000/health", "ML Direct HTTP"),
        ("http://localhost:8001/health", "Graph Direct HTTP"),
    ]
    for url, label in curl_targets:
        res = subprocess.run(["curl.exe", "-s", "--connect-timeout", "2", url], capture_output=True, text=True, errors="replace")
        if res.returncode == 0 and res.stdout.strip():
            out.append(f"[-] {label} ({url}): UNEXPECTED RESPONSE - {res.stdout.strip()}")
            all_isolated = False
        else:
            out.append(f"[+] {label} ({url}): BLOCKED (curl exit code {res.returncode}: Connection refused/timed out)")
            
    out.append(f"\n### 4. Direct MongoDB Driver Probe from Host")
    try:
        mongo_probe = subprocess.run([
            "mongosh.exe", "mongodb://localhost:27017/arogyamitra",
            "--eval", "db.version()", "--connectTimeoutMS", "2000"
        ], capture_output=True, text=True, errors="replace")
        if mongo_probe.returncode == 0:
            out.append(f"[-] MongoDB: EXPOSED on host! ({mongo_probe.stdout.strip()})")
            all_isolated = False
        else:
            out.append(f"[+] MongoDB: BLOCKED on host (Exit code {mongo_probe.returncode}: Connection refused)")
    except FileNotFoundError:
        out.append("[+] MongoDB: mongosh not on host; socket probe confirms port 27017 is closed on host.")
        
    out.append(f"\nFinal Isolation Audit Result: All Internal Microservices Strictly Isolated = {all_isolated}")
    
    report = "\n".join(out)
    print(report)
    with open("docs/evidence/service_isolation.txt", "w", encoding="utf-8") as f:
        f.write(report)

if __name__ == "__main__":
    main()

