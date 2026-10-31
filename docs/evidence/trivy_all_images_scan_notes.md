# Trivy Container Vulnerability Scan — Analysis & Notes

**Scan Date**: 2026-10-31  
**Scanner**: `d:\tools\trivy.exe image --scanners vuln <image>`  
**Evidence Record**: [`docs/evidence/trivy_all_images_scan.txt`](file:///d:/Document/Projects/Internship/Arogyamitra/docs/evidence/trivy_all_images_scan.txt)

---

## 1. Summary Severity Matrix Across Images

| Image | Base OS | Application Dependencies | Critical | High | Medium | Low | Total |
|---|---|---|---|---|---|---|---|
| `arogyamitra-backend:latest` | Alpine 3.24.3 | Node.js (Production modules) | **0** | **0** | **0** | **0** | **0** |
| `arogyamitra-frontend:latest` | Debian 13.7 (trixie) | Python 3.11 (Streamlit UI) | **0** | 41 | 48 | 208 | 297 |
| `arogyamitra-ml:latest` | Debian 13.7 (trixie) | Python 3.11 (FastAPI + Bayes) | **0** | 43 | 51 | 210 | 304 |
| `arogyamitra-graph:latest` | Debian 13.7 (trixie) | Python 3.11 (LangGraph + ReportLab) | **0** | 44 | 53 | 221 | 318 |

---

## 2. `--ignore-unfixed` Findings & Fix Availability

When Trivy is executed with `--ignore-unfixed` on the three Python images:
- **Base OS (Debian 13.7)**: **0 vulnerabilities**. All ~300 OS findings (`apt`, `bash`, `coreutils`, `tar`, `libc-bin`) have **no upstream security patch yet released** by Debian package maintainers for Debian 13 (testing branch).
- **Python Application Packages**: Exactly 8 vulnerabilities have upstream fixes available:
  - **`frontend` (6 HIGH with fixes)**:
    - `setuptools` (CVE-2026-24045, CVE-2026-24044, CVE-2026-24043)
    - `urllib3` (CVE-2026-97687, CVE-2026-97689)
    - `wheel` (CVE-2026-24049)
  - **`ml` (7 HIGH with fixes)**:
    - `setuptools` (CVE-2026-24045, CVE-2026-24044, CVE-2026-24043)
    - `urllib3` (CVE-2026-97687, CVE-2026-97689)
    - `wheel` (CVE-2026-24049)
    - `starlette` (CVE-2026-54282, fixed in starlette >=1.3.0)
  - **`graph` (7 HIGH with fixes)**:
    - `setuptools` (CVE-2026-24045, CVE-2026-24044, CVE-2026-24043)
    - `urllib3` (CVE-2026-97687, CVE-2026-97689)
    - `wheel` (CVE-2026-24049)
    - `starlette` (CVE-2026-54282)

---

## 3. Evaluation of Base Images (Why Not Alpine or Different Slim for Python)

1. **Why Python services use `python:3.11-slim` instead of Alpine**:
   - `ML_Model` requires compiled C/Fortran binary wheels for `scipy`, `scikit-learn`, `numpy`, and `joblib`.
   - On Alpine (musl libc), these packages lack pre-compiled `manylinux` wheels and must be built from C/C++ source, requiring `gcc`, `g++`, `gfortran`, `musl-dev`, and `lapack-dev`, which dramatically inflates build time (15–20 minutes) and container size.
   - `graph` requires ReportLab and TrueType Devanagari fonts (`fonts-deva`, `fonts-noto-core`) to render Devanagari Hindi/Marathi clinical PDF reports. Debian packages provide turnkey font rendering support that Alpine's fontconfig stacks often fail on.

2. **Why Not `python:3.11-slim-bookworm` (Debian 12 Stable)**:
   - Debian 12 (bookworm) includes older system libraries. Upgrading to a newer slim tag or testing Debian 12 stable is a valid long-term modernization step, but swapping base OS layers across 3 microservices in the final phase risks introducing ABI regressions in ReportLab and C-extensions without eliminating base vulnerabilities (Debian 12 images currently report 150-200 base CVEs as well).
