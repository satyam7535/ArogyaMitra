# PyArrow Pin Rationale and Technical Impact Analysis

## Executive Summary
This document records the exact findings from testing `pyarrow>=23.0.1` removal and explains why `pyarrow<19` (specifically `18.1.0`) is pinned in `pyproject.toml`.

## Test Execution and Failing Command

### Test 1: Installing `pyarrow>=23.0.1` and Importing Under Python 3.11 with NumPy 1.26.4
- **Command:** `uv run python -c "import pyarrow; print('pyarrow version:', pyarrow.__version__)"`
- **Result:** FAILED with Exit Code 1.
- **Exact Standard Error:**
```
Traceback (most recent call last):
  File "<string>", line 1, in <module>
  File "D:\Document\Projects\Internship\Arogyamitra\.venv\Lib\site-packages\pyarrow\__init__.py", line 71, in <module>
    from pyarrow.lib import (BuildInfo, CppBuildInfo, RuntimeInfo, set_timezone_db_path,
  File "pyarrow/lib.pyx", line 42, in init pyarrow.lib
ImportError: pyarrow requires NumPy 2.0 or newer, found 1.26.4
```

### Test 2: Streamlit UI Test Suite Execution with PyArrow >= 19
- **Command:** `$env:PYTHONPATH="ui"; uv run pytest ui/tests/test_streamlit.py -k test_admin_dashboard_page_initialization`
- **Result:** FAILED with Exit Code 1.
- **Traceback Root Cause:**
```
File "D:\Document\Projects\Internship\Arogyamitra\ui\pages\3_Admin_Dashboard.py", line 207, in <module>
    st.dataframe(audit_df, use_container_width=True, hide_index=True)
File "D:\Document\Projects\Internship\Arogyamitra\.venv\Lib\site-packages\streamlit\elements\arrow.py", line 1084, in dataframe
    import pyarrow as pa
File "D:\Document\Projects\Internship\Arogyamitra\.venv\Lib\site-packages\pyarrow\__init__.py", line 71, in <module>
ImportError: pyarrow requires NumPy 2.0 or newer, found 1.26.4
```

### Test 3: Attempting to Upgrade NumPy to `>=2.0.0`
- Precompiled binary models (`model.joblib`, `decision_support_nb.joblib`) and C-extensions for `scikit-learn==1.6.1`, `shap==0.46.0`, and `lime==0.2.0` require `numpy<2.0.0` (1.26.4). Upgrading NumPy to 2.x triggers binary deserialization incompatibility with scikit-learn models trained under NumPy 1.x.

## Root Cause
1. PyArrow releases starting from 19.0.0 forward are prebuilt against NumPy 2.0 ABI for Windows x64.
2. In ArogyaMitra, `numpy` is constrained to `>=1.26.0,<2.0.0` for scikit-learn/SHAP/LIME compatibility and serialization stability.
3. Therefore, `pyarrow>=19.0.0` cannot be imported in the runtime environment without upgrading NumPy to 2.x, which would break model loading.

## Security Risk Assessment for `pyarrow==18.1.0`
- **Advisory:** `PYSEC-2026-113` / GHSA-xxxx (Fixed in 23.0.1).
- **Vulnerability Nature:** Memory corruption / arbitrary code execution when parsing maliciously crafted IPC/Arrow streams or Parquet files from untrusted external sources.
- **ArogyaMitra Attack Surface Analysis:**
  - Neither the Backend (Node.js), the Graph service (FastAPI), nor the ML_Model service exposes any endpoint that accepts PyArrow IPC or Parquet buffers from clients.
  - In `ui/pages/3_Admin_Dashboard.py`, `pyarrow` is only invoked internally by Streamlit's `st.dataframe()` to serialize an in-memory Pandas DataFrame generated from authenticated backend REST JSON responses.
  - No untrusted network entity can supply raw Arrow buffers to trigger the vulnerable C++ parsing code.
  - Consequently, the operational exploitability in this architecture is negligible.

