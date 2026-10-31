# OWASP ZAP Baseline Scan — Status & Error Notes

**Status**: **NOT RUN**  
**Attempted Command**: `docker pull zaproxy/zap-stable`  
**Raw Command Error Record**: [`docs/evidence/zap_pull_error.txt`](file:///d:/Document/Projects/Internship/Arogyamitra/docs/evidence/zap_pull_error.txt)  

---

## 1. Root Cause Analysis

- The official OWASP ZAP container (`zaproxy/zap-stable`) is ~1.5 GB compressed and requires ~3.5 GB of rootfs image layer storage in containerd.
- Docker Desktop stores the WSL2 virtual disk at `C:\Users\DELL\AppData\Local\Docker\wsl\disk\docker_data.vhdx` on the Windows host Drive C:.
- With Drive C: hovering around 2.3 GB of free physical host space, containerd exhausted local snapshot storage during layer decompression, raising `unexpected EOF` and SIGBUS bbolt metadata panics.

---

## 2. Follow-Up Plan

- Per audit instructions, once the host Docker disk image is relocated from Drive C: to Drive D: (which has >90 GB free), `docker pull zaproxy/zap-stable` can be re-run cleanly along with the full baseline scan script.
- Until Docker storage is relocated to Drive D:, the official ZAP baseline scan remains strictly **NOT RUN**.
