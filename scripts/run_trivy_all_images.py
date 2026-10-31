#!/usr/bin/env python3
"""
Trivy Image Vulnerability Scanner for ArogyaMitra Stack
Scans all 4 application images:
  1. arogyamitra-backend:latest
  2. arogyamitra-frontend:latest
  3. arogyamitra-ml:latest
  4. arogyamitra-graph:latest

Produces summary and raw severity breakdown (CRITICAL, HIGH, MEDIUM, LOW)
distinguishing Base OS from bundled language packages (npm, pip).
Saves output to docs/evidence/trivy_all_images_scan.txt.
"""

import json
import subprocess
import sys
import os

IMAGES = [
    "arogyamitra-backend:latest",
    "arogyamitra-frontend:latest",
    "arogyamitra-ml:latest",
    "arogyamitra-graph:latest",
]

TRIVY_BIN = r"d:\tools\trivy.exe"

def scan_image(img):
    print(f"\n=======================================================")
    print(f"Scanning image: {img}")
    print(f"=======================================================")
    cmd = [TRIVY_BIN, "image", "--format", "json", "--scanners", "vuln", img]
    try:
        proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding="utf-8", errors="replace", timeout=300)
        if proc.returncode != 0:
            print(f"Error scanning {img}: {proc.stderr[:400]}")
            return None
        return json.loads(proc.stdout)
    except Exception as e:
        print(f"Exception during scan of {img}: {e}")
        return None

def analyze_report(img, data):
    results = data.get("Results", [])
    print(f"\nImage Report: {img}")
    print(f"Schema Version: {data.get('SchemaVersion')}")
    print(f"Artifact Name: {data.get('ArtifactName')}")
    
    total_findings = 0
    by_severity = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0, "UNKNOWN": 0}
    by_target = {}

    for res in results:
        target = res.get("Target", "unknown")
        target_class = res.get("Class", "unknown")
        target_type = res.get("Type", "unknown")
        vulns = res.get("Vulnerabilities", [])
        
        target_key = f"{target} ({target_type})"
        by_target[target_key] = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0, "UNKNOWN": 0, "details": []}
        
        for v in vulns:
            sev = v.get("Severity", "UNKNOWN").upper()
            if sev not in by_severity:
                sev = "UNKNOWN"
            by_severity[sev] += 1
            by_target[target_key][sev] += 1
            total_findings += 1
            by_target[target_key]["details"].append({
                "id": v.get("VulnerabilityID"),
                "pkg": v.get("PkgName"),
                "installed": v.get("InstalledVersion"),
                "fixed": v.get("FixedVersion", "None"),
                "severity": sev,
                "title": v.get("Title", "")[:80]
            })

    print(f"Total Vulnerabilities: {total_findings}")
    print(f"Summary by Severity: {by_severity}")
    print(f"\nBreakdown by Target / Component:")
    for target_key, counts in by_target.items():
        sub_total = sum(counts[s] for s in ["CRITICAL", "HIGH", "MEDIUM", "LOW", "UNKNOWN"])
        if sub_total > 0:
            print(f"  - {target_key}: Total {sub_total} (CRIT: {counts['CRITICAL']}, HIGH: {counts['HIGH']}, MED: {counts['MEDIUM']}, LOW: {counts['LOW']})")
            for d in counts["details"][:10]: # Print top 10
                print(f"      * [{d['severity']}] {d['id']} {d['pkg']} ({d['installed']} -> fixed: {d['fixed']})")
            if len(counts["details"]) > 10:
                print(f"      * ... and {len(counts['details']) - 10} more")

    return {
        "image": img,
        "total": total_findings,
        "by_severity": by_severity,
        "targets": by_target
    }

def main():
    all_summaries = []
    log_lines = []
    
    # redirect print
    class Logger:
        def __init__(self, orig):
            self.orig = orig
            self.lines = []
        def write(self, s):
            self.orig.write(s)
            self.lines.append(s)
        def flush(self):
            self.orig.flush()

    logger = Logger(sys.stdout)
    sys.stdout = logger

    print("# ArogyaMitra — Trivy Container Image Security Audit")
    print(f"# Tool: {TRIVY_BIN}")
    print("# Scope: All 4 production stack application images")

    for img in IMAGES:
        raw = scan_image(img)
        if raw:
            summary = analyze_report(img, raw)
            all_summaries.append(summary)

    print("\n=======================================================")
    print("FINAL SUMMARY COMPARISON TABLE")
    print("=======================================================")
    print(f"{'Image':<32} | {'Total':<6} | {'CRITICAL':<8} | {'HIGH':<6} | {'MEDIUM':<6} | {'LOW':<5}")
    print("-" * 72)
    for s in all_summaries:
        b = s["by_severity"]
        print(f"{s['image']:<32} | {s['total']:<6} | {b['CRITICAL']:<8} | {b['HIGH']:<6} | {b['MEDIUM']:<6} | {b['LOW']:<5}")

    sys.stdout = logger.orig
    full_output = "".join(logger.lines)
    
    out_path = os.path.join("docs", "evidence", "trivy_all_images_scan.txt")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(full_output)
    print(f"\nSaved raw evidence to {out_path}")

if __name__ == "__main__":
    main()
