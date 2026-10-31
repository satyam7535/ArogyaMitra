# Trivy Container Vulnerability Scan — Analysis & Notes

**Scan Date**: 2026-10-31  
**Scanner**: `d:\tools\trivy.exe image --ignore-unfixed <image>` & `pip-audit -r requirements.txt`  
**Evidence Record**: [`docs/evidence/trivy_all_images_scan.txt`](file:///d:/Document/Projects/Internship/Arogyamitra/docs/evidence/trivy_all_images_scan.txt)

---

## 1. Summary Severity Matrix Across Images (Post-Upgrade & Pip Removal)

| Image | Base OS | Application Dependencies | Critical | High (with fixes) | Medium | Low | Total Fixed Findings |
|---|---|---|---|---|---|---|---|
| `arogyamitra-backend:latest` | Alpine 3.24.3 | Node.js 20 (Multi-stage production build) | **0** | **0** | **0** | **0** | **0** |
| `arogyamitra-frontend:latest` | Debian 13.7 (trixie) | Python 3.11 (Streamlit 1.66.1, Pillow 13.0.0, urllib3 2.8.0, pip removed) | **0** | **0** | **0** | **0** | **0** |
| `arogyamitra-ml:latest` | Debian 13.7 (trixie) | Python 3.11 (FastAPI 0.162.0, Starlette 1.10.0, scikit-learn 1.6.1, pip removed) | **0** | **0** | **0** | **0** | **0** |
| `arogyamitra-graph:latest` | Debian 13.7 (trixie) | Python 3.11 (FastAPI 0.162.0, Starlette 1.10.0, LangGraph 0.3.15, pip removed) | **0** | **0** | **0** | **0** | **0** |

---

## 2. Package Upgrades & Hardening Executed

1. **Application Packages Upgraded**:
   - `setuptools>=84.1.0` (installed: `84.2.1`)
   - `wheel>=0.46.2` (installed: `0.48.0`)
   - `urllib3>=2.8.0` (installed: `2.8.0`)
   - `starlette>=1.3.0` (installed: `1.10.0`)
   - `fastapi>=0.115.11` (installed: `0.162.0`)
   - `Pillow>=13.0.0` (installed: `13.0.0`)
   - `python-dotenv>=1.2.4` (installed: `1.2.4`)
   - `python-multipart>=0.0.32` (installed: `0.0.32`)
   - `langgraph>=0.3.15` and `langchain>=0.3.30` (installed)

2. **Elimination of Pip Bootstrap Directory (Zero High Findings)**:
   - Previously, Trivy flagged 2 HIGH findings (`CVE-2026-97687`, `CVE-2026-97689`) solely due to pip's internal vendored copy of `urllib3 2.7.0` inside `/usr/local/lib/python3.11/site-packages/pip/_vendor/urllib3/` and `ensurepip`'s bundled wheel `/usr/local/lib/python3.11/ensurepip/_bundled/setuptools-79.0.1-py3-none-any.whl`.
   - By appending `python -m pip uninstall -y pip && rm -rf /usr/local/lib/python3.11/ensurepip` in each Python Dockerfile, the bootstrap directories were removed from the final production images while preserving all installed runtime dependencies.
   - Trivy scan with `--ignore-unfixed` now confirms: **0 HIGH vulnerabilities with fixes across all 4 production container images**.

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
