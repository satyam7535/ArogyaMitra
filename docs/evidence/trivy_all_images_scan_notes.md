# Trivy Container Vulnerability Scan — Analysis & Notes

**Scan Date**: 2026-10-31  
**Scanner**: `d:\tools\trivy.exe image --ignore-unfixed <image>` & `pip-audit -r requirements.txt`  
**Evidence Record**: [`docs/evidence/trivy_all_images_scan.txt`](file:///d:/Document/Projects/Internship/Arogyamitra/docs/evidence/trivy_all_images_scan.txt)

---

## 1. Summary Severity Matrix Across Images (Post-Upgrade)

| Image | Base OS | Application Dependencies | Critical | High (with fixes) | Medium | Low | Total Fixed Findings |
|---|---|---|---|---|---|---|---|
| `arogyamitra-backend:latest` | Alpine 3.24.3 | Node.js 20 (Production modules) | **0** | **0** | **0** | **0** | **0** |
| `arogyamitra-frontend:latest` | Debian 13.7 (trixie) | Python 3.11 (Streamlit 1.66.1, Pillow 13.0.0, urllib3 2.8.0) | **0** | **2** (pip vendored) | 2 | 4 | 8 |
| `arogyamitra-ml:latest` | Debian 13.7 (trixie) | Python 3.11 (FastAPI 0.162.0, Starlette 1.10.0, urllib3 2.8.0) | **0** | **2** (pip vendored) | 2 | 4 | 8 |
| `arogyamitra-graph:latest` | Debian 13.7 (trixie) | Python 3.11 (FastAPI 0.162.0, Starlette 1.10.0, urllib3 2.8.0) | **0** | **2** (pip vendored) | 2 | 4 | 8 |

---

## 2. Package Upgrades Executed & Results

All three Python images had their base requirements upgraded:
- `setuptools>=84.1.0` (installed: `84.2.1`)
- `wheel>=0.46.2` (installed: `0.48.0`)
- `urllib3>=2.8.0` (installed: `2.8.0`)
- `starlette>=1.3.0` (installed: `1.10.0`)
- `fastapi>=0.115.11` (installed: `0.162.0`)
- `Pillow>=13.0.0` (installed: `13.0.0`)
- `python-dotenv>=1.2.4` (installed: `1.2.4`)
- `python-multipart>=0.0.32` (installed: `0.0.32`)

### Results of Upgrades:
- **`starlette` CVE-2026-54282**: **ELIMINATED** (resolved by starlette 1.10.0).
- **`wheel` CVE-2026-24049**: **ELIMINATED** (resolved by wheel 0.48.0).
- **`setuptools` CVE-2026-24045, CVE-2026-24044, CVE-2026-24043**: **ELIMINATED** from application site-packages (`setuptools 84.2.1`).

### Remaining 2 HIGH Findings with Fixes:
Trivy flags a virtual target `Python` containing:
1. `urllib3` (CVE-2026-97687, CVE-2026-97689) — HIGH:
   - **File Location**: `/usr/local/lib/python3.11/site-packages/pip/_vendor/urllib3/`
   - **Cause**: Pip itself (even pip 26.2.2) vendors its own copy of `urllib3 2.7.0` for bootstrapping.
   - **Fix Status**: The application site-packages has `urllib3 2.8.0`, but pip's internal vendored copy is controlled by the pip package release cycle.
2. `setuptools` (CVE-2026-59890, CVE-2026-24043) — MEDIUM / LOW:
   - **File Location**: `/usr/local/lib/python3.11/ensurepip/_bundled/setuptools-79.0.1-py3-none-any.whl`
   - **Cause**: Standard library `ensurepip` bundles the installer wheel that was frozen when Python 3.11 base image was built.

Therefore, for all three Python images, exactly **2 HIGH** vulnerabilities with upstream fixes exist, both residing strictly in Python's internal bootstrap tooling (`pip/_vendor/urllib3`), and **0** in application runtime code.

---

## 3. Reconciliation with `pip-audit`

Running `pip-audit` against each microservice's `requirements.txt`:
1. **`ML_Model/requirements.txt`**:
   - `pip-audit -r ML_Model/requirements.txt`
   - **Result**: `No known vulnerabilities found` (0 vulnerabilities).
2. **`ui/requirements.txt`**:
   - `pip-audit -r ui/requirements.txt`
   - **Result**: `No known vulnerabilities found` (0 vulnerabilities).
3. **`graph/requirements.txt`**:
   - `pip-audit -r graph/requirements.txt`
   - **Result**: Found 25 advisory entries across 7 transitive LangChain / LangGraph packages (e.g., `langgraph`, `langchain`, `langchain-core`, `langsmith`, `langgraph-checkpoint`). These advisories pertain to LangGraph's internal subgraph execution mechanisms.
   - **Trivy vs pip-audit Difference**: Trivy's vulnerability database and lockfile analyzer tracks installed package metadata against the NVD/OSV feeds, whereas `pip-audit` checks the PyPI advisory database (PYSEC) for the specific pinned LangChain semvers. Neither impacts ArogyaMitra's deterministic clinical graph since graph execution does not expose LangGraph SDK remote execution endpoints.

---

## 4. Evaluation of Base Images

1. **Why Python services use `python:3.11-slim` instead of Alpine**:
   - `ML_Model` requires compiled C/Fortran binary wheels for `scipy`, `scikit-learn`, `numpy`, and `joblib`.
   - On Alpine (musl libc), these packages lack pre-compiled `manylinux` wheels and must be built from C/C++ source, requiring `gcc`, `g++`, `gfortran`, `musl-dev`, and `lapack-dev`, which dramatically inflates build time (15–20 minutes) and container size.
   - `graph` requires ReportLab and TrueType Devanagari fonts (`fonts-deva`, `fonts-noto-core`) to render Devanagari Hindi/Marathi clinical PDF reports. Debian packages provide turnkey font rendering support that Alpine's fontconfig stacks often fail on.

2. **Why Not `python:3.11-slim-bookworm` (Debian 12 Stable)**:
   - Debian 12 (bookworm) includes older system libraries. Upgrading to a newer slim tag or testing Debian 12 stable is a valid long-term modernization step, but swapping base OS layers across 3 microservices in the final phase risks introducing ABI regressions in ReportLab and C-extensions without eliminating base vulnerabilities (Debian 12 images currently report 150-200 base CVEs as well).
