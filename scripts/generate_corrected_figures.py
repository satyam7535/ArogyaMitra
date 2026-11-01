"""
ArogyaMitra — Corrected Figure & Diagram Generator
Generates clean, non-overlapping architectural diagrams and publication figures
strictly matching docs/evidence/ without fabrication or text collisions.
"""

import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
from PIL import Image

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "docs", "REPORT_FINAL", "figures")
UI_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "docs", "evidence", "ui_screenshots")
os.makedirs(OUTPUT_DIR, exist_ok=True)

plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['font.size'] = 9.5
plt.rcParams['axes.titlesize'] = 11
plt.rcParams['axes.labelsize'] = 10
plt.rcParams['xtick.labelsize'] = 9
plt.rcParams['ytick.labelsize'] = 9
plt.rcParams['legend.fontsize'] = 9

# -----------------------------------------------------------------------------
# 1. Merged Performance & Calibration (Figure 4.1: Two Panels)
# Panel A: Top-1 Accuracy across Dropout (0%, 30%, 50%)
# Panel B: Expected Calibration Error (ECE) across Dropout
# Exact numbers from model_benchmark.md:14,31,48 and tuned_tree_benchmark.md:12-17
# -----------------------------------------------------------------------------
def make_fig1_performance_calibration():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4.2), dpi=250)
    
    dropout = np.array([0, 30, 50])
    
    # Accuracy values from evidence
    bnb_acc = [1.000, 0.989, 0.919]
    bnb_acc_err = [0.000, 0.014, 0.023]
    
    lgb_acc = [0.9890, 0.8640, 0.6830]
    lgb_acc_err = [0.0119, 0.0399, 0.0783]
    
    xgb_acc = [0.9836, 0.8683, 0.7203]
    xgb_acc_err = [0.0139, 0.0413, 0.0773]
    
    # ECE values from evidence
    bnb_ece = [0.005, 0.032, 0.072]
    lgb_ece = [0.0098, 0.0975, 0.2019]
    xgb_ece = [0.0826, 0.1983, 0.2118]
    
    # Panel A: Accuracy
    ax1.errorbar(dropout, bnb_acc, yerr=bnb_acc_err, fmt='-o', color='#154360', label='BernoulliNB (Deployed)', lw=2.2, capsize=4, markersize=6)
    ax1.errorbar(dropout, lgb_acc, yerr=lgb_acc_err, fmt='--s', color='#27AE60', label='Tuned LightGBM', lw=1.8, capsize=4, markersize=5)
    ax1.errorbar(dropout, xgb_acc, yerr=xgb_acc_err, fmt=':^', color='#E67E22', label='Tuned XGBoost', lw=1.8, capsize=4, markersize=5)
    
    ax1.set_title('(a) Top-1 Accuracy vs. Symptom Dropout', fontweight='bold', pad=10)
    ax1.set_xlabel('Symptom Dropout Rate (%)')
    ax1.set_ylabel('Top-1 Accuracy')
    ax1.set_xticks([0, 30, 50])
    ax1.set_xticklabels(['0% (Complete)', '30%', '50% (Severe)'])
    ax1.set_ylim(0.60, 1.03)
    ax1.grid(True, linestyle='--', alpha=0.5)
    ax1.legend(loc='lower left', framealpha=0.9)
    
    # Annotate BernoulliNB advantage
    ax1.annotate('BernoulliNB: 0.919\nLightGBM: 0.683', xy=(50, 0.919), xytext=(32, 0.65),
                 arrowprops=dict(facecolor='#154360', shrink=0.08, width=1, headwidth=5),
                 fontsize=8.5, fontweight='bold', color='#154360',
                 bbox=dict(boxstyle='round,pad=0.3', facecolor='#EBF5FB', edgecolor='#AED6F1'))

    # Panel B: ECE
    ax2.plot(dropout, bnb_ece, '-o', color='#154360', label='BernoulliNB (Deployed)', lw=2.2, markersize=6)
    ax2.plot(dropout, lgb_ece, '--s', color='#27AE60', label='Tuned LightGBM', lw=1.8, markersize=5)
    ax2.plot(dropout, xgb_ece, ':^', color='#E67E22', label='Tuned XGBoost', lw=1.8, markersize=5)
    
    ax2.set_title('(b) Expected Calibration Error (ECE)', fontweight='bold', pad=10)
    ax2.set_xlabel('Symptom Dropout Rate (%)')
    ax2.set_ylabel('ECE (Lower is More Reliable)')
    ax2.set_xticks([0, 30, 50])
    ax2.set_xticklabels(['0%', '30%', '50%'])
    ax2.set_ylim(-0.01, 0.25)
    ax2.grid(True, linestyle='--', alpha=0.5)
    ax2.legend(loc='upper left', framealpha=0.9)
    
    plt.tight_layout()
    path = os.path.join(OUTPUT_DIR, "fig1_accuracy_and_ece.png")
    plt.savefig(path, dpi=250)
    plt.close()
    print("Generated:", path)

# -----------------------------------------------------------------------------
# 2. Dataset Composition (Single clean donut/pie chart)
# -----------------------------------------------------------------------------
def make_fig2_dataset_pie():
    fig, ax = plt.subplots(figsize=(5.5, 3.8), dpi=250)
    
    # 4920 total, 4616 duplicate, 304 unique (data_provenance.txt)
    sizes = [304, 4616]
    labels = ['Unique Clinical Rows\n304 (6.2%)', 'Synthetic Duplicates\n4,616 (93.8%)']
    colors = ['#154360', '#BDC3C7']
    explode = (0.08, 0)
    
    wedges, texts, autotexts = ax.pie(
        sizes, explode=explode, labels=labels, colors=colors,
        autopct='%1.1f%%', pctdistance=0.75, startangle=140,
        wedgeprops=dict(width=0.45, edgecolor='white', linewidth=2)
    )
    
    for t in texts:
        t.set_fontsize(9.5)
        t.set_fontweight('bold')
    for at in autotexts:
        at.set_fontsize(9)
        at.set_color('white')
        at.set_fontweight('bold')
        
    ax.set_title('Dataset Provenance: Raw 4,920 Rows\nvs. 304 Deduplicated Ground-Truth Rows', fontweight='bold', pad=12)
    plt.tight_layout()
    path = os.path.join(OUTPUT_DIR, "fig2_dataset_provenance.png")
    plt.savefig(path, dpi=250)
    plt.close()
    print("Generated:", path)

# -----------------------------------------------------------------------------
# 3. Load Test Results (Throughput & Latency matching load_test_testmode_results.txt)
# -----------------------------------------------------------------------------
def make_fig3_load_test():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(9.5, 3.8), dpi=250)
    
    concurrency = ['C=1\n(Sequential)', 'C=10\n(Moderate)', 'C=50\n(Stress)']
    tput = [10.2, 13.9, 14.7]  # load_test_testmode_results.txt:15-17
    
    # Latencies (load_test_testmode_results.txt:15-17)
    p50 = [79.3, 500.7, 2428.4]
    p90 = [148.9, 1530.1, 5057.2]
    p95 = [190.6, 1952.3, 5862.8]
    p99 = [317.4, 2548.2, 8087.4]
    
    # Panel 1: Throughput
    bars = ax1.bar(concurrency, tput, color=['#2980B9', '#1F618D', '#154360'], width=0.55, edgecolor='black', linewidth=0.8)
    for bar in bars:
        h = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., h + 0.3, f'{h:.1f} r/s', ha='center', va='bottom', fontsize=9, fontweight='bold')
    ax1.set_title('(a) Gateway Throughput (req/s)', fontweight='bold', pad=10)
    ax1.set_ylabel('Throughput (Requests/sec)')
    ax1.set_ylim(0, 18)
    ax1.grid(True, linestyle='--', alpha=0.4, axis='y')
    
    # Panel 2: Latencies
    x = np.arange(len(concurrency))
    w = 0.18
    ax2.bar(x - 1.5*w, p50, width=w, label='p50', color='#5DADE2', edgecolor='black', linewidth=0.6)
    ax2.bar(x - 0.5*w, p90, width=w, label='p90', color='#2E86C1', edgecolor='black', linewidth=0.6)
    ax2.bar(x + 0.5*w, p95, width=w, label='p95', color='#1B4F72', edgecolor='black', linewidth=0.6)
    ax2.bar(x + 1.5*w, p99, width=w, label='p99', color='#112D42', edgecolor='black', linewidth=0.6)
    
    ax2.set_xticks(x)
    ax2.set_xticklabels(concurrency)
    ax2.set_title('(b) Latency Percentiles (ms)', fontweight='bold', pad=10)
    ax2.set_ylabel('Response Time (ms)')
    ax2.grid(True, linestyle='--', alpha=0.4, axis='y')
    ax2.legend(loc='upper left', fontsize=8.5)
    
    plt.tight_layout()
    path = os.path.join(OUTPUT_DIR, "fig3_load_test_results.png")
    plt.savefig(path, dpi=250)
    plt.close()
    print("Generated:", path)

# -----------------------------------------------------------------------------
# 4. List Latency Optimization Before vs After (load_test_profiling_notes.md:44-48)
# -----------------------------------------------------------------------------
def make_fig4_list_opt():
    fig, ax = plt.subplots(figsize=(6.5, 3.6), dpi=250)
    
    metrics = ['p50 Latency', 'p90 Latency', 'p95 Latency', 'p99 Latency']
    before = [193.0, 349.8, 460.5, 660.6]  # load_test_profiling_notes.md:44
    after = [76.2, 117.9, 130.3, 152.0]    # load_test_profiling_notes.md:45
    
    x = np.arange(len(metrics))
    w = 0.35
    
    rects1 = ax.bar(x - w/2, before, w, label='Before (Full Scan)', color='#E74C3C', edgecolor='black', linewidth=0.8)
    rects2 = ax.bar(x + w/2, after, w, label='After (Paginated + Projected)', color='#27AE60', edgecolor='black', linewidth=0.8)
    
    # Annotate improvements
    improvements = ['-60.5%', '-66.3%', '-71.7%', '-77.0%']
    for i in range(len(metrics)):
        ax.text(x[i] + w/2, after[i] + 15, improvements[i], ha='center', va='bottom', fontsize=8.5, fontweight='bold', color='#1E8449')
        
    ax.set_xticks(x)
    ax.set_xticklabels(metrics, fontweight='bold')
    ax.set_ylabel('Latency (ms)')
    ax.set_title('Worker List Endpoint Latency (C=1):\nBefore vs. After Combined Pagination & Projection', fontweight='bold', pad=12)
    ax.set_ylim(0, 750)
    ax.grid(True, linestyle='--', alpha=0.4, axis='y')
    ax.legend(loc='upper right')
    
    plt.tight_layout()
    path = os.path.join(OUTPUT_DIR, "fig4_list_latency_before_after.png")
    plt.savefig(path, dpi=250)
    plt.close()
    print("Generated:", path)

# -----------------------------------------------------------------------------
# 5. Architecture & Container Diagram (diag1 with MongoDB clearly included)
# -----------------------------------------------------------------------------
def make_diag1_architecture():
    fig, ax = plt.subplots(figsize=(8.0, 4.4), dpi=250)
    ax.axis('off')
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    
    # Outer Client Area
    ax.add_patch(patches.Rectangle((2, 5), 20, 90, facecolor='#EAECEE', edgecolor='#BDC3C7', linestyle='--', linewidth=1.5))
    ax.text(12, 91, 'CLIENT ZONE', ha='center', va='center', fontweight='bold', color='#5D6D7E', fontsize=9.5)
    
    # Client Browser Box
    ax.add_patch(patches.Rectangle((4, 40), 16, 25, facecolor='#FFFFFF', edgecolor='#2980B9', linewidth=1.5))
    ax.text(12, 55, 'Frontline User\nBrowser', ha='center', va='center', fontweight='bold', color='#154360', fontsize=9)
    ax.text(12, 45, 'HTTPS / TLS 1.2-1.3', ha='center', va='center', color='#7F8C8D', fontsize=7.5)
    
    # Internal Docker Bridge Perimeter
    ax.add_patch(patches.Rectangle((28, 5), 70, 90, facecolor='#F4F6F7', edgecolor='#154360', linewidth=2))
    ax.text(63, 91, 'PRIVATE DOCKER BRIDGE NETWORK (arogya-net)', ha='center', va='center', fontweight='bold', color='#154360', fontsize=10)
    
    # 1. Nginx Reverse Proxy (Ingress)
    ax.add_patch(patches.Rectangle((32, 40), 14, 25, facecolor='#D4EFDF', edgecolor='#27AE60', linewidth=1.5))
    ax.text(39, 56, 'Nginx Gateway', ha='center', va='center', fontweight='bold', color='#1E8449', fontsize=9)
    ax.text(39, 48, 'Port 443 (Host)\nTLS Termination', ha='center', va='center', color='#27AE60', fontsize=7.5)
    
    # Arrow Client -> Nginx
    ax.annotate('', xy=(32, 52.5), xytext=(20, 52.5), arrowprops=dict(facecolor='#154360', edgecolor='#154360', width=1.5, headwidth=6))
    ax.text(26, 56, 'HTTPS:443', ha='center', va='bottom', fontsize=7.5, fontweight='bold', color='#154360')
    
    # 2. UI Service (Streamlit)
    ax.add_patch(patches.Rectangle((52, 65), 18, 18, facecolor='#FCF3CF', edgecolor='#F39C12', linewidth=1.2))
    ax.text(61, 76, 'UI Service (Streamlit)', ha='center', va='center', fontweight='bold', color='#B9770E', fontsize=8.5)
    ax.text(61, 69, 'Port 8501 (Internal)', ha='center', va='center', color='#7D6608', fontsize=7.5)
    
    # 3. Core Backend API Gateway (Node.js)
    ax.add_patch(patches.Rectangle((52, 38), 18, 22, facecolor='#E8F8F5', edgecolor='#1ABC9C', linewidth=1.5))
    ax.text(61, 52, 'Core Backend API\n(Express / Node.js 20)', ha='center', va='center', fontweight='bold', color='#117A65', fontsize=8.5)
    ax.text(61, 42, 'Port 5000 (Internal)\nAuth / Red-Flags / AES', ha='center', va='center', color='#16A085', fontsize=7.5)
    
    # 4. ML Engine (FastAPI)
    ax.add_patch(patches.Rectangle((76, 55), 18, 16, facecolor='#EBF5FB', edgecolor='#2980B9', linewidth=1.2))
    ax.text(85, 65, 'ML Engine (FastAPI)', ha='center', va='center', fontweight='bold', color='#1F618D', fontsize=8.5)
    ax.text(85, 59, 'Port 8000 (Internal)\nBernoulliNB (1.8 ms)', ha='center', va='center', color='#2874A6', fontsize=7.5)
    
    # 5. Graph Narrative (FastAPI)
    ax.add_patch(patches.Rectangle((76, 32), 18, 16, facecolor='#FADBD8', edgecolor='#E74C3C', linewidth=1.2))
    ax.text(85, 42, 'Graph Service (LangGraph)', ha='center', va='center', fontweight='bold', color='#922B21', fontsize=8.5)
    ax.text(85, 36, 'Port 8001 (Internal)\n10s/20s Cap + Fallback', ha='center', va='center', color='#B03A2E', fontsize=7.5)
    
    # 6. MongoDB Database (Internal only, with mongo-data volume)
    ax.add_patch(patches.Rectangle((52, 10), 18, 20, facecolor='#EAEDED', edgecolor='#34495E', linewidth=1.5))
    ax.text(61, 23, 'MongoDB 7.0 Persistence', ha='center', va='center', fontweight='bold', color='#2C3E50', fontsize=8.5)
    ax.text(61, 15, 'Port 27017 (NO HOST PORT)\nVolume: mongo-data', ha='center', va='center', color='#566573', fontsize=7.5)
    
    # Connecting Arrows inside bridge
    # Nginx -> UI
    ax.annotate('', xy=(52, 74), xytext=(46, 57), arrowprops=dict(facecolor='#27AE60', edgecolor='#27AE60', width=1, headwidth=4))
    # Nginx -> Backend
    ax.annotate('', xy=(52, 49), xytext=(46, 49), arrowprops=dict(facecolor='#27AE60', edgecolor='#27AE60', width=1, headwidth=4))
    # Backend -> ML
    ax.annotate('', xy=(76, 63), xytext=(70, 52), arrowprops=dict(facecolor='#1ABC9C', edgecolor='#1ABC9C', width=1, headwidth=4))
    # Backend -> Graph
    ax.annotate('', xy=(76, 40), xytext=(70, 46), arrowprops=dict(facecolor='#1ABC9C', edgecolor='#1ABC9C', width=1, headwidth=4))
    # Backend -> MongoDB
    ax.annotate('', xy=(61, 30), xytext=(61, 38), arrowprops=dict(facecolor='#1ABC9C', edgecolor='#1ABC9C', width=1, headwidth=4))
    
    plt.tight_layout()
    path = os.path.join(OUTPUT_DIR, "diag1_architecture_trust_boundaries.png")
    plt.savefig(path, dpi=250)
    plt.close()
    print("Generated:", path)

# -----------------------------------------------------------------------------
# 6. State Machine (diag3 redrawn cleanly without overlapping text)
# -----------------------------------------------------------------------------
def make_diag3_state_machine():
    fig, ax = plt.subplots(figsize=(7.5, 4.0), dpi=250)
    ax.axis('off')
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    
    # State 1: PENDING_INTAKE
    ax.add_patch(patches.Rectangle((3, 40), 18, 24, facecolor='#EBF5FB', edgecolor='#2980B9', linewidth=1.5))
    ax.text(12, 55, 'PENDING_INTAKE', ha='center', va='center', fontweight='bold', color='#154360', fontsize=8.5)
    ax.text(12, 46, 'Patient symptoms\ncollected (131 vocab)', ha='center', va='center', color='#5D6D7E', fontsize=7.5)
    
    # Arrow 1 -> 2
    ax.annotate('', xy=(28, 52), xytext=(21, 52), arrowprops=dict(facecolor='#154360', edgecolor='#154360', width=1, headwidth=4))
    ax.text(24.5, 54, 'Submit', ha='center', va='bottom', fontsize=7.5, color='#154360')
    
    # State 2: RED-FLAG GATE
    ax.add_patch(patches.Rectangle((28, 38), 20, 28, facecolor='#FDEDEC', edgecolor='#E74C3C', linewidth=1.5))
    ax.text(38, 56, 'Decision A:\nRed-Flag Screening', ha='center', va='center', fontweight='bold', color='#922B21', fontsize=8.5)
    ax.text(38, 44, 'Matches 7 emergency\nsymptoms?', ha='center', va='center', color='#78281F', fontsize=7.5)
    
    # Emergency Branch Upwards
    ax.annotate('', xy=(38, 80), xytext=(38, 66), arrowprops=dict(facecolor='#C0392B', edgecolor='#C0392B', width=1.5, headwidth=5))
    ax.text(39, 72, 'YES (Emergency)', ha='left', va='center', fontsize=7.5, fontweight='bold', color='#C0392B')
    
    ax.add_patch(patches.Rectangle((25, 80), 26, 16, facecolor='#C0392B', edgecolor='#78281F', linewidth=1.5))
    ax.text(38, 88, 'EMERGENCY TRIAGE', ha='center', va='center', fontweight='bold', color='#FFFFFF', fontsize=9)
    ax.text(38, 83, 'Immediate Ambulance Transfer', ha='center', va='center', color='#FADBD8', fontsize=7.5)
    
    # Normal Path -> State 3 (ML + LLM)
    ax.annotate('', xy=(55, 52), xytext=(48, 52), arrowprops=dict(facecolor='#27AE60', edgecolor='#27AE60', width=1, headwidth=4))
    ax.text(51.5, 54, 'NO', ha='center', va='bottom', fontsize=7.5, fontweight='bold', color='#27AE60')
    
    ax.add_patch(patches.Rectangle((55, 38), 20, 28, facecolor='#E8F8F5', edgecolor='#1ABC9C', linewidth=1.5))
    ax.text(65, 56, 'Decision B:\nWorker Review', ha='center', va='center', fontweight='bold', color='#117A65', fontsize=8.5)
    ax.text(65, 45, 'BernoulliNB Top-3\n+ LLM Narrative', ha='center', va='center', color='#16A085', fontsize=7.5)
    
    # Accept Branch -> COMPLETED
    ax.annotate('', xy=(82, 65), xytext=(75, 56), arrowprops=dict(facecolor='#27AE60', edgecolor='#27AE60', width=1, headwidth=4))
    ax.text(78, 63, 'Accept', ha='right', va='bottom', fontsize=7.5, color='#27AE60', fontweight='bold')
    
    ax.add_patch(patches.Rectangle((82, 58), 16, 20, facecolor='#D4EFDF', edgecolor='#27AE60', linewidth=1.5))
    ax.text(90, 70, 'ACCEPTED', ha='center', va='center', fontweight='bold', color='#1E8449', fontsize=8.5)
    ax.text(90, 63, 'Worker logs sign-off;\nOutpatient guidance', ha='center', va='center', color='#27AE60', fontsize=7)
    
    # Escalate Branch -> ESCALATED
    ax.annotate('', xy=(82, 35), xytext=(75, 45), arrowprops=dict(facecolor='#E67E22', edgecolor='#E67E22', width=1, headwidth=4))
    ax.text(78, 38, 'Escalate', ha='right', va='top', fontsize=7.5, color='#E67E22', fontweight='bold')
    
    ax.add_patch(patches.Rectangle((82, 22), 16, 22, facecolor='#FDEBD0', edgecolor='#E67E22', linewidth=1.5))
    ax.text(90, 35, 'ESCALATED', ha='center', va='center', fontweight='bold', color='#A04000', fontsize=8.5)
    ax.text(90, 28, '[PENDING FIX ROUND]\nDoctor review queue', ha='center', va='center', color='#BA4A00', fontsize=7)
    
    plt.tight_layout()
    path = os.path.join(OUTPUT_DIR, "diag3_state_machine.png")
    plt.savefig(path, dpi=250)
    plt.close()
    print("Generated:", path)

# -----------------------------------------------------------------------------
# 7. LLM Timeout Hierarchy (diag5 redrawn cleanly with wrapped text)
# -----------------------------------------------------------------------------
def make_diag5_timeout():
    fig, ax = plt.subplots(figsize=(7.5, 3.4), dpi=250)
    ax.axis('off')
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    
    levels = [
        ("Nginx Edge Reverse Proxy", "proxy_read_timeout = 90s", 78, "#154360", "#EBF5FB"),
        ("Backend HTTP Client Timeout", "timeout = 30s (Backend -> Graph call)", 54, "#1B4F72", "#E8F8F5"),
        ("LangGraph Narrative Hard Cap", "asyncio.wait_for = 20s (Across all models)", 30, "#2471A3", "#FCF3CF"),
        ("Per-Attempt LLM Model Timeout", "timeout = 10s per Gemini API attempt", 6, "#B03A2E", "#FADBD8"),
    ]
    
    for title, detail, y_pos, border_col, bg_col in levels:
        # Outer bar
        bar_width = 80 - (78 - y_pos)*0.6
        ax.add_patch(patches.Rectangle((10, y_pos), bar_width, 18, facecolor=bg_col, edgecolor=border_col, linewidth=1.5))
        ax.text(12, y_pos + 12, title, fontweight='bold', color=border_col, fontsize=9)
        ax.text(12, y_pos + 5, detail, color='#2C3E50', fontsize=8)
        
    # Annotate Fallback Guarantee
    ax.add_patch(patches.Rectangle((68, 6), 28, 42, facecolor='#FDEDEC', edgecolor='#C0392B', linestyle='--', linewidth=1.2))
    ax.text(82, 38, 'FAIL-SAFE GUARANTEE', ha='center', va='center', fontweight='bold', color='#922B21', fontsize=8)
    ax.text(82, 24, 'If total elapsed >= 20s\nor all models 429/404:\nINSTANT FALLBACK\nto deterministic\nclinical template.', ha='center', va='center', color='#78281F', fontsize=7.2)
    
    plt.tight_layout()
    path = os.path.join(OUTPUT_DIR, "diag5_llm_timeout_hierarchy.png")
    plt.savefig(path, dpi=250)
    plt.close()
    print("Generated:", path)

# -----------------------------------------------------------------------------
# 8. Combined UI Panels (One clean composite image)
# -----------------------------------------------------------------------------
def make_ui_composite():
    p1 = os.path.join(UI_DIR, "01_worker_result.png")
    p2 = os.path.join(UI_DIR, "04_redflag_block.png")
    p11 = os.path.join(UI_DIR, "07_doctor_queue_real.png")
    p9 = os.path.join(UI_DIR, "09_worker_reviewed.png")
    
    if all(os.path.exists(p) for p in [p1, p2, p11, p9]):
        im1 = Image.open(p1)
        im2 = Image.open(p2)
        im3 = Image.open(p11)
        im4 = Image.open(p9)
        
        # Resize to common width
        w = 1000
        h = 600
        im1_r = im1.resize((w, h))
        im2_r = im2.resize((w, h))
        im3_r = im3.resize((w, h))
        im4_r = im4.resize((w, h))
        
        # 2x2 grid
        composite = Image.new('RGB', (w*2 + 30, h*2 + 70), (255, 255, 255))
        composite.paste(im1_r, (10, 30))
        composite.paste(im2_r, (w + 20, 30))
        composite.paste(im3_r, (10, h + 50))
        composite.paste(im4_r, (w + 20, h + 50))
        
        out_path = os.path.join(OUTPUT_DIR, "fig5_ui_panels_combined.png")
        composite.save(out_path, quality=90)
        print("Generated UI composite:", out_path)
    else:
        print("One or more UI screenshots not found; skipping composite.")

if __name__ == "__main__":
    print("Generating corrected publication figures and diagrams...")
    make_fig1_performance_calibration()
    make_fig2_dataset_pie()
    make_fig3_load_test()
    make_fig4_list_opt()
    make_diag1_architecture()
    make_diag3_state_machine()
    make_diag5_timeout()
    make_ui_composite()
    print("All figures generated successfully!")
