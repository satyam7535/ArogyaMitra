"""
ArogyaMitra — Report Figures and Diagrams Generator
Generates publication-quality charts and architectural diagrams for the final B.Tech report.
All metrics are derived directly from docs/evidence/ artifacts.
"""

import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "docs", "REPORT_FINAL", "figures")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Common styling
plt.rcParams["font.family"] = "sans-serif"
plt.rcParams["font.size"] = 10
plt.rcParams["axes.titlesize"] = 12
plt.rcParams["axes.labelsize"] = 10
plt.rcParams["xtick.labelsize"] = 9
plt.rcParams["ytick.labelsize"] = 9
plt.rcParams["legend.fontsize"] = 9
plt.rcParams["figure.titlesize"] = 13

# ---------------------------------------------------------------------------
# Figure 1: Accuracy vs Symptom Dropout Level
# Source: docs/evidence/model_benchmark.md & tuned_tree_benchmark.md
# ---------------------------------------------------------------------------
def generate_figure1():
    dropouts = ["0% (Clean)", "30% (Robust)", "50% (Extreme)"]
    x = np.arange(len(dropouts))
    width = 0.25

    # Values: BernoulliNB, Tuned LightGBM, Tuned XGBoost
    nb_acc = [1.000, 0.989, 0.919]
    lgb_acc = [0.989, 0.864, 0.683]
    xgb_acc = [0.984, 0.868, 0.720]

    fig, ax = plt.subplots(figsize=(7, 4.5), dpi=300)
    rects1 = ax.bar(x - width, nb_acc, width, label="Bernoulli Naive Bayes v2.0.0 (Deployed)", color="#2b5c8f")
    rects2 = ax.bar(x, lgb_acc, width, label="Tuned LightGBM (Nested CV)", color="#4682b4")
    rects3 = ax.bar(x + width, xgb_acc, width, label="Tuned XGBoost (Nested CV)", color="#87ceeb")

    ax.set_ylabel("Top-1 Accuracy")
    ax.set_title("Figure 1: Model Diagnostic Accuracy Under Symptom Dropout\n(5x3 Repeated Stratified K-Fold CV on 304 Unique Synthetic Rows)")
    ax.set_xticks(x)
    ax.set_xticklabels(dropouts)
    ax.set_ylim(0.5, 1.05)
    ax.legend(loc="lower left", framealpha=0.9)
    ax.grid(axis="y", linestyle="--", alpha=0.5)

    for rects in [rects1, rects2, rects3]:
        for rect in rects:
            height = rect.get_height()
            ax.annotate(f"{height:.3f}",
                        xy=(rect.get_x() + rect.get_width() / 2, height),
                        xytext=(0, 3), textcoords="offset points",
                        ha="center", va="bottom", fontsize=8)

    fig.tight_layout()
    path = os.path.join(OUTPUT_DIR, "fig1_accuracy_vs_dropout.png")
    fig.savefig(path)
    plt.close(fig)
    print(f"[+] Saved: {path}")

# ---------------------------------------------------------------------------
# Figure 2: Expected Calibration Error (ECE) vs Symptom Dropout
# Source: docs/evidence/model_benchmark.md & tuned_tree_benchmark.md
# ---------------------------------------------------------------------------
def generate_figure2():
    dropouts = ["0% (Clean)", "30% (Robust)", "50% (Extreme)"]
    x = np.arange(len(dropouts))

    nb_ece = [0.005, 0.032, 0.072]
    lgb_ece = [0.0098, 0.0975, 0.2019]
    xgb_ece = [0.0826, 0.1983, 0.2118]

    fig, ax = plt.subplots(figsize=(7, 4.5), dpi=300)
    ax.plot(dropouts, nb_ece, "o-", color="#2b5c8f", linewidth=2, label="Bernoulli Naive Bayes v2.0.0")
    ax.plot(dropouts, lgb_ece, "s--", color="#e65100", linewidth=2, label="Tuned LightGBM (Nested CV)")
    ax.plot(dropouts, xgb_ece, "^-.", color="#6a1b9a", linewidth=2, label="Tuned XGBoost (Nested CV)")

    ax.set_ylabel("Expected Calibration Error (ECE - Lower is Better)")
    ax.set_title("Figure 2: Expected Calibration Error Across Missing-Symptom Scenarios\n(Evaluated on Out-of-Fold Splits)")
    ax.set_ylim(0, 0.25)
    ax.legend(loc="upper left", framealpha=0.9)
    ax.grid(True, linestyle="--", alpha=0.5)

    for i, txt in enumerate(nb_ece):
        ax.annotate(f"{txt:.3f}", (dropouts[i], nb_ece[i] + 0.008), ha="center", fontsize=8, color="#2b5c8f")
    for i, txt in enumerate(lgb_ece):
        ax.annotate(f"{txt:.3f}", (dropouts[i], lgb_ece[i] + 0.008), ha="center", fontsize=8, color="#e65100")
    for i, txt in enumerate(xgb_ece):
        ax.annotate(f"{txt:.3f}", (dropouts[i], xgb_ece[i] + 0.008), ha="center", fontsize=8, color="#6a1b9a")

    fig.tight_layout()
    path = os.path.join(OUTPUT_DIR, "fig2_ece_vs_dropout.png")
    fig.savefig(path)
    plt.close(fig)
    print(f"[+] Saved: {path}")

# ---------------------------------------------------------------------------
# Figure 3: Dataset Deduplication & Breakdown
# Source: docs/evidence/data_provenance.txt & MODEL_CARD.md
# ---------------------------------------------------------------------------
def generate_figure3():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(8, 4), dpi=300)

    # Pie chart of rows
    labels = ["Unique Ground-Truth Rows\n(304 rows, 6.2%)", "Exact Duplicates Dropped\n(4,616 rows, 93.8%)"]
    sizes = [304, 4616]
    colors = ["#2b5c8f", "#cfd8dc"]
    explode = (0.1, 0)
    ax1.pie(sizes, explode=explode, labels=labels, colors=colors, autopct="%1.1f%%",
            startangle=140, textprops={"fontsize": 8})
    ax1.set_title("Dataset Row Deduplication\n(Total: 4,920 Rows)")

    # Bar chart of dimensions
    dims = ["Raw Rows", "Unique Rows", "Classes", "Symptoms"]
    counts = [4920, 304, 41, 131]
    bar_colors = ["#90a4ae", "#2b5c8f", "#00897b", "#f57c00"]
    bars = ax2.bar(dims, counts, color=bar_colors)
    ax2.set_yscale("log")
    ax2.set_ylabel("Count (Log Scale)")
    ax2.set_title("Key Dataset Dimensions")
    ax2.grid(axis="y", linestyle="--", alpha=0.5)

    for bar in bars:
        h = bar.get_height()
        ax2.annotate(f"{h}",
                     xy=(bar.get_x() + bar.get_width() / 2, h),
                     xytext=(0, 3), textcoords="offset points",
                     ha="center", va="bottom", fontsize=8)

    fig.suptitle("Figure 3: Synthetic Dataset Provenance & Structural Characteristics", fontsize=12)
    fig.tight_layout()
    path = os.path.join(OUTPUT_DIR, "fig3_dataset_breakdown.png")
    fig.savefig(path)
    plt.close(fig)
    print(f"[+] Saved: {path}")

# ---------------------------------------------------------------------------
# Figure 4: Load Test Latency Percentiles & Throughput
# Source: docs/evidence/load_test_testmode_results.txt
# ---------------------------------------------------------------------------
def generate_figure4():
    tiers = ["C = 1", "C = 10", "C = 50"]
    x = np.arange(len(tiers))
    width = 0.18

    # Latencies in ms
    p50 = [79.3, 500.7, 2428.4]
    p90 = [148.9, 1530.1, 5057.2]
    p95 = [190.6, 1952.3, 5862.8]
    p99 = [317.4, 2548.2, 8087.4]
    throughput = [10.2, 13.9, 14.7]

    fig, ax1 = plt.subplots(figsize=(8, 4.8), dpi=300)

    rects1 = ax1.bar(x - 1.5*width, p50, width, label="p50 Latency", color="#4caf50")
    rects2 = ax1.bar(x - 0.5*width, p90, width, label="p90 Latency", color="#2196f3")
    rects3 = ax1.bar(x + 0.5*width, p95, width, label="p95 Latency", color="#ff9800")
    rects4 = ax1.bar(x + 1.5*width, p99, width, label="p99 Latency", color="#f44336")

    ax1.set_ylabel("Latency (ms)")
    ax1.set_xlabel("Concurrency Tier (Users)")
    ax1.set_title("Figure 4: Load Test Latency Percentiles and Throughput Across Concurrency\n(200 Requests / Endpoint / Level, 2,400 Total Benchmark Requests)")
    ax1.set_xticks(x)
    ax1.set_xticklabels(tiers)
    ax1.set_ylim(0, 9500)
    ax1.grid(axis="y", linestyle="--", alpha=0.5)

    # Line plot for throughput on twin axis
    ax2 = ax1.twinx()
    line = ax2.plot(x, throughput, "k-o", linewidth=2.5, markersize=8, label="Throughput (req/s)")
    ax2.set_ylabel("Throughput (req/s)", color="black")
    ax2.set_ylim(0, 20)

    # Combine legends
    handles1, labels1 = ax1.get_legend_handles_labels()
    handles2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(handles1 + handles2, labels1 + labels2, loc="upper left", framealpha=0.9)

    fig.tight_layout()
    path = os.path.join(OUTPUT_DIR, "fig4_load_test_latency_throughput.png")
    fig.savefig(path)
    plt.close(fig)
    print(f"[+] Saved: {path}")

# ---------------------------------------------------------------------------
# Figure 5: Test Suite Distribution
# Source: docs/evidence/verify_all.txt, verify_backend.txt, verify_ml.txt, verify_graph.txt, verify_ui.txt
# ---------------------------------------------------------------------------
def generate_figure5():
    labels = ["Backend API & Security\n(231 tests, 72.0%)",
              "ML Microservice\n(55 tests, 17.1%)",
              "LangGraph Reasoning\n(26 tests, 8.1%)",
              "Streamlit UI AppTest\n(9 tests, 2.8%)"]
    sizes = [231, 55, 26, 10]
    colors = ["#2b5c8f", "#00897b", "#f57c00", "#7e57c2"]
    explode = (0.05, 0.05, 0.05, 0.05)

    fig, ax = plt.subplots(figsize=(6.5, 4.5), dpi=300)
    wedges, texts, autotexts = ax.pie(sizes, explode=explode, labels=labels, colors=colors, autopct="%1.1f%%",
                                      startangle=140, textprops={"fontsize": 9})
    for at in autotexts:
        at.set_color("white")
        at.set_weight("bold")
        at.set_fontsize(8)

    ax.set_title("Figure 5: Automated Prototype Test Suite Breakdown\n(322 Verified Unit & Integration Tests, 100% Passing)", fontsize=11)
    fig.tight_layout()
    path = os.path.join(OUTPUT_DIR, "fig5_test_suite_composition.png")
    fig.savefig(path)
    plt.close(fig)
    print(f"[+] Saved: {path}")

# ---------------------------------------------------------------------------
# Figure 6: Worker List Latency Before vs After Optimization
# Source: docs/evidence/load_test_profiling_notes.md
# ---------------------------------------------------------------------------
def generate_figure6():
    tiers = ["C = 1", "C = 10", "C = 50"]
    x = np.arange(len(tiers))
    width = 0.2

    # Before (full scan unpaginated) vs After (paginated limit=20 + lean projection)
    before_p50 = [193.0, 1120.0, 3850.0]
    after_p50 = [76.2, 417.7, 2295.1]
    before_p99 = [660.6, 2150.0, 9420.0]
    after_p99 = [152.0, 1255.3, 7047.0]

    fig, ax = plt.subplots(figsize=(7.5, 4.5), dpi=300)
    ax.bar(x - 1.5*width, before_p50, width, label="Before: p50 Latency", color="#e57373")
    ax.bar(x - 0.5*width, after_p50, width, label="After: p50 Latency (60.5% Speedup at C=1)", color="#81c784")
    ax.bar(x + 0.5*width, before_p99, width, label="Before: p99 Latency", color="#d32f2f")
    ax.bar(x + 1.5*width, after_p99, width, label="After: p99 Latency (77.0% Speedup at C=1)", color="#388e3c")

    ax.set_ylabel("Latency (ms)")
    ax.set_xlabel("Concurrency Tier")
    ax.set_title("Figure 6: Consultation List Endpoint Latency (GET /consultation/my)\nBefore vs. After Server-Side Pagination & Lean Projection")
    ax.set_xticks(x)
    ax.set_xticklabels(tiers)
    ax.legend(loc="upper left", framealpha=0.9, fontsize=8)
    ax.grid(axis="y", linestyle="--", alpha=0.5)

    fig.tight_layout()
    path = os.path.join(OUTPUT_DIR, "fig6_list_latency_before_after.png")
    fig.savefig(path)
    plt.close(fig)
    print(f"[+] Saved: {path}")

# ---------------------------------------------------------------------------
# Diagrams 1 - 7: Generated Architectural Visualizations
# ---------------------------------------------------------------------------
def generate_diagrams():
    # Diagram 1: Architecture with Trust Boundaries
    fig, ax = plt.subplots(figsize=(8, 4.5), dpi=300)
    ax.axis("off")
    # Draw trust boundary boxes
    rect1 = plt.Rectangle((0.02, 0.05), 0.96, 0.9, fill=True, color="#f5f7fa", ec="#b0bec5", lw=1.5, linestyle="--")
    ax.add_patch(rect1)
    ax.text(0.04, 0.9, "Docker Bridge Network (arogya-network) — Private RFC 1918 Address Space", fontsize=10, weight="bold", color="#37474f")

    # Ingress box
    ax.add_patch(plt.Rectangle((0.05, 0.35), 0.2, 0.45, color="#e3f2fd", ec="#1e88e5", lw=2))
    ax.text(0.15, 0.65, "Nginx Proxy\n(arogya-proxy)\n:80 -> 301\n:443 TLS 1.3", ha="center", va="center", weight="bold", fontsize=9)

    # UI box
    ax.add_patch(plt.Rectangle((0.32, 0.55), 0.28, 0.3, color="#f3e5f5", ec="#8e24aa", lw=2))
    ax.text(0.46, 0.7, "Streamlit Web UI\n(arogya-frontend :8501)\nWorker/Doctor/Admin Portals", ha="center", va="center", weight="bold", fontsize=9)

    # Backend Gateway
    ax.add_patch(plt.Rectangle((0.32, 0.12), 0.28, 0.35, color="#e8f5e9", ec="#43a047", lw=2))
    ax.text(0.46, 0.3, "Express 5 Backend\n(arogya-backend :5000)\nAuth, Crypto, Job Queue", ha="center", va="center", weight="bold", fontsize=9)

    # ML Microservice
    ax.add_patch(plt.Rectangle((0.68, 0.55), 0.26, 0.3, color="#fff3e0", ec="#fb8c00", lw=2))
    ax.text(0.81, 0.7, "ML Microservice\n(arogya-ml :8000)\nFastAPI / BernoulliNB", ha="center", va="center", weight="bold", fontsize=9)

    # Graph Microservice
    ax.add_patch(plt.Rectangle((0.68, 0.12), 0.26, 0.35, color="#fbe9e7", ec="#d84315", lw=2))
    ax.text(0.81, 0.3, "LangGraph Pipeline\n(arogya-graph :8001)\nGemini / ReportLab", ha="center", va="center", weight="bold", fontsize=9)

    # Connecting arrows
    ax.annotate("", xy=(0.32, 0.7), xytext=(0.25, 0.65), arrowprops=dict(arrowstyle="->", lw=1.5, color="#1565c0"))
    ax.annotate("", xy=(0.32, 0.3), xytext=(0.25, 0.45), arrowprops=dict(arrowstyle="->", lw=1.5, color="#1565c0"))
    ax.annotate("", xy=(0.46, 0.47), xytext=(0.46, 0.55), arrowprops=dict(arrowstyle="<->", lw=1.5, color="#4a148c"))
    ax.annotate("", xy=(0.68, 0.7), xytext=(0.60, 0.35), arrowprops=dict(arrowstyle="<->", lw=1.5, color="#2e7d32"))
    ax.annotate("", xy=(0.68, 0.3), xytext=(0.60, 0.25), arrowprops=dict(arrowstyle="<->", lw=1.5, color="#2e7d32"))

    ax.set_title("Diagram 1: ArogyaMitra Container Network Architecture & Trust Boundaries", fontsize=11, weight="bold")
    path = os.path.join(OUTPUT_DIR, "diag1_architecture_trust_boundaries.png")
    fig.savefig(path)
    plt.close(fig)
    print(f"[+] Saved: {path}")

    # Diagram 3: Consultation State Machine
    fig, ax = plt.subplots(figsize=(8, 4), dpi=300)
    ax.axis("off")
    # States
    states = [
        ("DRAFT\n(Intake)", 0.1, 0.5, "#e0e0e0"),
        ("ANALYZING\n(Job Queue)", 0.32, 0.5, "#bbdefb"),
        ("ANALYZED\n(Triage Ready)", 0.55, 0.5, "#c8e6c9"),
        ("ACCEPTED\n(Frontline Care)", 0.82, 0.75, "#a5d6a7"),
        ("ESCALATED\n(MD Review)", 0.82, 0.25, "#ffcc80"),
    ]
    for name, cx, cy, col in states:
        ax.add_patch(plt.Rectangle((cx - 0.08, cy - 0.15), 0.16, 0.3, color=col, ec="#37474f", lw=1.5))
        ax.text(cx, cy, name, ha="center", va="center", weight="bold", fontsize=8.5)

    # Transitions
    ax.annotate("Worker Saves", xy=(0.24, 0.5), xytext=(0.18, 0.5), arrowprops=dict(arrowstyle="->", lw=1.5))
    ax.annotate("ML Inference", xy=(0.47, 0.5), xytext=(0.40, 0.5), arrowprops=dict(arrowstyle="->", lw=1.5))
    ax.annotate("Decision B: Normal\n(Accept Allowed)", xy=(0.74, 0.75), xytext=(0.63, 0.55), arrowprops=dict(arrowstyle="->", lw=1.5, color="#2e7d32"))
    ax.annotate("Decision B: Red Flag\nor Doctor Escalation", xy=(0.74, 0.25), xytext=(0.63, 0.45), arrowprops=dict(arrowstyle="->", lw=1.5, color="#c62828"))

    ax.set_title("Diagram 3: Consultation Lifecycle & Triage State Transitions", fontsize=11, weight="bold")
    path = os.path.join(OUTPUT_DIR, "diag3_state_machine.png")
    fig.savefig(path)
    plt.close(fig)
    print(f"[+] Saved: {path}")

    # Diagram 5: LLM Timeout Hierarchy
    fig, ax = plt.subplots(figsize=(7.5, 3.5), dpi=300)
    ax.axis("off")
    # Concentric or nested hierarchy bars
    levels = [
        ("Nginx Ingress proxy_read_timeout (90 seconds)", 0.05, 0.75, 0.9, 0.18, "#bbdefb", "#1976d2"),
        ("Backend Axios Timeout to Graph Service (30 seconds)", 0.12, 0.52, 0.76, 0.18, "#c8e6c9", "#388e3c"),
        ("LangGraph asyncio.wait_for Hard Cap (20 seconds)", 0.20, 0.29, 0.60, 0.18, "#ffe0b2", "#f57c00"),
        ("Per-Attempt Gemini Call Timeout (10 seconds)", 0.28, 0.06, 0.44, 0.18, "#ffcdd2", "#d32f2f"),
    ]
    for title, x, y, w, h, bg, border in levels:
        ax.add_patch(plt.Rectangle((x, y), w, h, color=bg, ec=border, lw=2))
        ax.text(x + w/2, y + h/2, title, ha="center", va="center", weight="bold", fontsize=9, color="#212121")

    ax.set_title("Diagram 5: Fail-Safe LLM Timeout Hierarchy (Deterministic Safety Bounds)", fontsize=11, weight="bold")
    path = os.path.join(OUTPUT_DIR, "diag5_llm_timeout_hierarchy.png")
    fig.savefig(path)
    plt.close(fig)
    print(f"[+] Saved: {path}")

    # Diagram 2: End-to-End Workflow Sequence
    fig, ax = plt.subplots(figsize=(8, 4.2), dpi=300)
    ax.axis("off")
    steps = [
        "1. Worker logs in & inputs symptoms at Streamlit UI (:8501)",
        "2. UI forwards authenticated JSON over HTTPS to Nginx (:443)",
        "3. Nginx verifies TLS 1.3, applies rate-limits, routes to Backend (:5000)",
        "4. Express validates Zod schema, decrypts patient AES-256 PII, creates Consultation",
        "5. Express pushes analysis job to async queue, dispatches to ML (:8000)",
        "6. ML calculates BernoulliNB probabilities & exact log-odds attributions in 1.8ms",
        "7. Graph Service (:8001) coordinates prompt-guarded LLM synthesis (Gemini / Fallback)",
        "8. ReportLab renders bilingual Devanagari Hindi/Marathi PDF in 63.0ms",
        "9. Worker reviews triage: Decision B normal Accept OR Escalate to Doctor",
        "10. Doctor logs in, reviews queue, signs clinical second opinion",
    ]
    for i, s in enumerate(steps):
        bg = "#e3f2fd" if i % 2 == 0 else "#f5f5f5"
        ax.add_patch(plt.Rectangle((0.02, 0.88 - i*0.09), 0.96, 0.075, color=bg, ec="#90caf9", lw=1))
        ax.text(0.05, 0.915 - i*0.09, s, va="center", fontsize=8.5, color="#263238")
    ax.set_title("Diagram 2: End-to-End Clinical Consultation & Triage Execution Flow", fontsize=11, weight="bold")
    path = os.path.join(OUTPUT_DIR, "diag2_workflow_sequence.png")
    fig.savefig(path)
    plt.close(fig)
    print(f"[+] Saved: {path}")

    # Diagram 4: Security Layers and Threat Model
    fig, ax = plt.subplots(figsize=(8, 4), dpi=300)
    ax.axis("off")
    sec_layers = [
        ("Layer 1: Network Boundary", "TLS 1.3 Termination, HSTS (max-age=63072000), HTTP->HTTPS 301, IP Rate Limiting (100 req/min)", "#e1f5fe"),
        ("Layer 2: Gateway & Auth", "Argon2id Memory-Hard Password Hashing (3 iter, 64MB RAM), Rotating JWT, CSRF, Helmet, Strict Zod", "#e8f5e9"),
        ("Layer 3: Cryptographic Storage", "Field-Level AES-256-GCM Authenticated Encryption with Random 96-bit IV & 128-bit Auth Tag per Field", "#fff8e1"),
        ("Layer 4: Access Control & Privacy", "Multi-Tenant Fiduciary Organization Scoping, Anti-Enumeration 404s, DPDP Two-Party Deletion Approval", "#f3e5f5"),
        ("Layer 5: AI Guardrails & Integrity", "XML Prompt Boundary Isolation, Forbidden Drug Denylist, Whole-Phrase Confidence Filter, Fail-Closed 503", "#ffebee"),
    ]
    for i, (title, desc, col) in enumerate(sec_layers):
        ax.add_patch(plt.Rectangle((0.03, 0.82 - i*0.19), 0.94, 0.16, color=col, ec="#546e7a", lw=1.5))
        ax.text(0.06, 0.92 - i*0.19, title, weight="bold", fontsize=9.5, color="#1a237e")
        ax.text(0.06, 0.86 - i*0.19, desc, fontsize=8.5, color="#37474f")
    ax.set_title("Diagram 4: ArogyaMitra Defense-in-Depth Cryptographic & Architectural Security Layers", fontsize=11, weight="bold")
    path = os.path.join(OUTPUT_DIR, "diag4_security_layers.png")
    fig.savefig(path)
    plt.close(fig)
    print(f"[+] Saved: {path}")

    # Diagram 6: Docker Network and Volume Layout
    fig, ax = plt.subplots(figsize=(8, 4.2), dpi=300)
    ax.axis("off")
    ax.add_patch(plt.Rectangle((0.02, 0.05), 0.96, 0.9, color="#fafafa", ec="#78909c", lw=1.5, linestyle="--"))
    ax.text(0.05, 0.9, "Bridge Network: arogyamitra_arogya-network (Isolated Docker Subnet)", fontsize=10, weight="bold")

    containers = [
        ("arogya-proxy\n(nginx:1.27-alpine)\nPorts: 80, 443", 0.06, 0.45, 0.22, 0.35, "#bbdefb"),
        ("arogya-frontend\n(Streamlit UI)\nPort: 8501 (internal)", 0.36, 0.52, 0.25, 0.32, "#e1bee7"),
        ("arogya-backend\n(Express Node.js)\nPort: 5000 (internal)", 0.36, 0.12, 0.25, 0.32, "#c8e6c9"),
        ("arogya-ml\n(FastAPI / ML)\nPort: 8000 (internal)", 0.69, 0.52, 0.25, 0.32, "#ffe0b2"),
        ("arogya-graph\n(FastAPI / Graph)\nPort: 8001 (internal)", 0.69, 0.12, 0.25, 0.32, "#ffcdd2"),
    ]
    for cname, cx, cy, cw, ch, ccol in containers:
        ax.add_patch(plt.Rectangle((cx, cy), cw, ch, color=ccol, ec="#37474f", lw=1.5))
        ax.text(cx + cw/2, cy + ch/2, cname, ha="center", va="center", fontsize=8, weight="bold")

    # Volume
    ax.add_patch(plt.Rectangle((0.06, 0.12), 0.22, 0.25, color="#cfd8dc", ec="#455a64", lw=1.5))
    ax.text(0.17, 0.245, "Named Volume:\narogyamitra_mongo_data\n(Encrypted Persistent Disk)", ha="center", va="center", fontsize=7.5, weight="bold")

    ax.set_title("Diagram 6: Docker Container Network Topology & Persistent Volume Configuration", fontsize=11, weight="bold")
    path = os.path.join(OUTPUT_DIR, "diag6_docker_network_volume.png")
    fig.savefig(path)
    plt.close(fig)
    print(f"[+] Saved: {path}")

    # Diagram 7: MITM Interception
    fig, (ax_unsec, ax_sec) = plt.subplots(1, 2, figsize=(8, 4), dpi=300)
    ax_unsec.axis("off")
    ax_sec.axis("off")

    ax_unsec.set_title("Insecure Cleartext (HTTP :80)\nAttacker Sniffs Credentials & PHI", color="#b71c1c", fontsize=9.5, weight="bold")
    ax_unsec.add_patch(plt.Rectangle((0.05, 0.1), 0.9, 0.8, color="#ffebee", ec="#c62828", lw=2))
    raw_packet = (
        "POST /api/v1/worker/login HTTP/1.1\n"
        "Host: localhost\n"
        "Content-Type: application/json\n\n"
        "{\n"
        "  \"email\": \"worker@arogyamitra...\",\n"
        "  \"password\": \"Worker@Arogya2026!\"\n"
        "}\n\n"
        "STATUS: COMPROMISED (Plaintext Leaked)"
    )
    ax_unsec.text(0.1, 0.5, raw_packet, family="monospace", fontsize=7.5, va="center", color="#b71c1c")

    ax_sec.set_title("Secured Ingress (HTTPS :443)\nTLS 1.3 Asymmetric Handshake", color="#1b5e20", fontsize=9.5, weight="bold")
    ax_sec.add_patch(plt.Rectangle((0.05, 0.1), 0.9, 0.8, color="#e8f5e9", ec="#2e7d32", lw=2))
    enc_packet = (
        "TLSv1.3 Record Layer: Encrypted Application Data\n"
        "Cipher: TLS_AES_256_GCM_SHA384\n"
        "Payload (128 bytes):\n"
        "  7b a4 19 f2 cc 8b 11 09\n"
        "  4f 6e da bb 01 9a 33 ff\n"
        "  92 41 8c bd 09 1a ee ff\n"
        "  ... [Indistinguishable from Random]\n\n"
        "STATUS: SECURED (Eavesdropping Blocked)"
    )
    ax_sec.text(0.1, 0.5, enc_packet, family="monospace", fontsize=7.5, va="center", color="#1b5e20")

    fig.suptitle("Diagram 7: Man-in-the-Middle (MITM) Interception Analysis: Cleartext vs. TLS 1.3", fontsize=11, weight="bold")
    fig.tight_layout()
    path = os.path.join(OUTPUT_DIR, "diag7_mitm_interception.png")
    fig.savefig(path)
    plt.close(fig)
    print(f"[+] Saved: {path}")

if __name__ == "__main__":
    generate_figure1()
    generate_figure2()
    generate_figure3()
    generate_figure4()
    generate_figure5()
    generate_figure6()
    generate_diagrams()
    print("All report figures and diagrams generated successfully.")
