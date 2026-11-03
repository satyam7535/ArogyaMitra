"""
ArogyaMitra — Publication Figures & Architecture Diagram Generator
Generates clean, non-overlapping architectural diagrams, LaTeX equation snippets,
and empirical evaluation charts matching docs/evidence/ exactly.
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
# 0. Clean LaTeX Equation Snippets
# -----------------------------------------------------------------------------
def make_equations():
    eqs = [
        ("eq3_1_likelihood.png", r"$P(\mathbf{x} \mid Y = c) = \prod_{j=1}^{D} P(X_j = x_j \mid Y = c) = \prod_{j=1}^{D} \theta_{c, j}^{x_j} (1 - \theta_{c, j})^{1 - x_j}$", (6.5, 0.75)),
        ("eq3_2_laplace.png", r"$\hat{\theta}_{c, j} = \frac{N_{c, j} + \alpha}{N_c + 2\alpha}$", (3.2, 0.75)),
        ("eq3_3_log_posterior.png", r"$\ln P(Y = c \mid \mathbf{x}) = \ln P(Y = c) + \sum_{j=1}^{D} \left[ x_j \ln \hat{\theta}_{c, j} + (1 - x_j) \ln(1 - \hat{\theta}_{c, j}) \right] - \ln P(\mathbf{x})$", (7.2, 0.85)),
        ("eq3_4_additive_attribution.png", r"$w_{c, j}(x_j) = x_j \ln\left( \frac{\hat{\theta}_{c, j}}{\bar{\theta}_j} \right) + (1 - x_j) \ln\left( \frac{1 - \hat{\theta}_{c, j}}{1 - \bar{\theta}_j} \right)$", (5.8, 0.8)),
    ]
    for fname, latex_str, figsize in eqs:
        fig, ax = plt.subplots(figsize=figsize, dpi=300)
        ax.axis("off")
        ax.text(0.5, 0.5, latex_str, fontsize=12, ha="center", va="center", color="#154360")
        fig.tight_layout()
        out_path = os.path.join(OUTPUT_DIR, fname)
        fig.savefig(out_path, bbox_inches="tight", transparent=False, facecolor="#F8F9FA")
        plt.close(fig)
        print("Generated equation:", out_path)

# -----------------------------------------------------------------------------
# 1. Dataset Composition (Figure 4.1: Single clean donut chart)
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
# 2. Performance & Calibration (Figure 4.2: Two Panels, no overlapping boxes)
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
    ax1.set_ylim(0.60, 1.05)
    ax1.grid(True, linestyle='--', alpha=0.5)
    ax1.legend(loc='lower left', framealpha=0.9)
    
    # Clean label placed away from lines
    ax1.text(32, 0.95, 'BernoulliNB: 0.919\nLightGBM: 0.683',
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
# 3. Load Test Results (Figure 4.3)
# -----------------------------------------------------------------------------
def make_fig3_load_test():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(9.5, 3.8), dpi=250)
    
    concurrency = ['C=1\n(Sequential)', 'C=10\n(Moderate)', 'C=50\n(Stress)']
    tput = [10.2, 13.9, 14.7]
    
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
# 4. List Latency Optimization (Figure 4.4: Legend moved so it does not cover bar)
# -----------------------------------------------------------------------------
def make_fig4_list_opt():
    fig, ax = plt.subplots(figsize=(6.8, 3.8), dpi=250)
    
    metrics = ['p50 Latency', 'p90 Latency', 'p95 Latency', 'p99 Latency']
    before = [193.0, 349.8, 460.5, 660.6]
    after = [76.2, 117.9, 130.3, 152.0]
    
    x = np.arange(len(metrics))
    w = 0.35
    
    rects1 = ax.bar(x - w/2, before, w, label='Before (Full Scan)', color='#E74C3C', edgecolor='black', linewidth=0.8)
    rects2 = ax.bar(x + w/2, after, w, label='After (Paginated + Projected)', color='#27AE60', edgecolor='black', linewidth=0.8)
    
    improvements = ['-60.5%', '-66.3%', '-71.7%', '-77.0%']
    for i in range(len(metrics)):
        ax.text(x[i] + w/2, after[i] + 15, improvements[i], ha='center', va='bottom', fontsize=8.5, fontweight='bold', color='#1E8449')
        
    ax.set_xticks(x)
    ax.set_xticklabels(metrics, fontweight='bold')
    ax.set_ylabel('Latency (ms)')
    ax.set_title('Worker List Endpoint Latency (C=1):\nBefore vs. After Combined Pagination & Projection', fontweight='bold', pad=12)
    ax.set_ylim(0, 850)
    ax.grid(True, linestyle='--', alpha=0.4, axis='y')
    # Legend placed at top-left away from tall p99 Before bar (at x=3)
    ax.legend(loc='upper left', framealpha=0.9)
    
    plt.tight_layout()
    path = os.path.join(OUTPUT_DIR, "fig4_list_latency_before_after.png")
    plt.savefig(path, dpi=250)
    plt.close()
    print("Generated:", path)

# -----------------------------------------------------------------------------
# 5. Architecture & Container Diagram (Figure 3.1: No Diagram title, TLS 1.2/1.3, enlarged text)
# -----------------------------------------------------------------------------
def make_diag1_architecture():
    fig, ax = plt.subplots(figsize=(8.2, 4.6), dpi=250)
    ax.axis('off')
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    
    # Outer Client Area
    ax.add_patch(patches.Rectangle((2, 5), 20, 90, facecolor='#EAECEE', edgecolor='#BDC3C7', linestyle='--', linewidth=1.5))
    ax.text(12, 91, 'CLIENT ZONE', ha='center', va='center', fontweight='bold', color='#5D6D7E', fontsize=10)
    
    # Client Browser Box
    ax.add_patch(patches.Rectangle((4, 40), 16, 25, facecolor='#FFFFFF', edgecolor='#2980B9', linewidth=1.5))
    ax.text(12, 55, 'Frontline User\nBrowser', ha='center', va='center', fontweight='bold', color='#154360', fontsize=9.5)
    ax.text(12, 45, 'HTTPS / TLS 1.2-1.3', ha='center', va='center', color='#7F8C8D', fontsize=8)
    
    # Internal Docker Bridge Perimeter
    ax.add_patch(patches.Rectangle((28, 5), 70, 90, facecolor='#F4F6F7', edgecolor='#154360', linewidth=2))
    ax.text(63, 91, 'PRIVATE DOCKER BRIDGE NETWORK (arogya-net)', ha='center', va='center', fontweight='bold', color='#154360', fontsize=10.5)
    
    # 1. Nginx Reverse Proxy (Ingress)
    ax.add_patch(patches.Rectangle((32, 40), 15, 25, facecolor='#D4EFDF', edgecolor='#27AE60', linewidth=1.5))
    ax.text(39.5, 56, 'Nginx Gateway', ha='center', va='center', fontweight='bold', color='#1E8449', fontsize=9.5)
    ax.text(39.5, 48, 'Port 443 (Host)\nTLS 1.2 / 1.3 Strict\nHSTS & Rate Limit', ha='center', va='center', color='#27AE60', fontsize=8)
    
    # Arrow Client -> Nginx
    ax.annotate('', xy=(32, 52.5), xytext=(20, 52.5), arrowprops=dict(facecolor='#154360', edgecolor='#154360', width=1.5, headwidth=6))
    ax.text(26, 56, 'HTTPS:443', ha='center', va='bottom', fontsize=8, fontweight='bold', color='#154360')
    
    # 2. UI Service (Streamlit)
    ax.add_patch(patches.Rectangle((53, 65), 18, 18, facecolor='#FCF3CF', edgecolor='#F39C12', linewidth=1.2))
    ax.text(62, 76, 'UI Service (Streamlit)', ha='center', va='center', fontweight='bold', color='#B9770E', fontsize=9)
    ax.text(62, 69, 'Port 8501 (Internal)\nWorker/Doctor/Admin', ha='center', va='center', color='#7D6608', fontsize=8)
    
    # 3. Core Backend API Gateway (Node.js 22)
    ax.add_patch(patches.Rectangle((53, 38), 18, 22, facecolor='#E8F8F5', edgecolor='#1ABC9C', linewidth=1.5))
    ax.text(62, 52, 'Core Backend API\n(Express / Node.js 22)', ha='center', va='center', fontweight='bold', color='#117A65', fontsize=9)
    ax.text(62, 42, 'Port 5000 (Internal)\nAuth / Red-Flags / OCC', ha='center', va='center', color='#16A085', fontsize=8)
    
    # 4. ML Engine (FastAPI)
    ax.add_patch(patches.Rectangle((77, 55), 18, 18, facecolor='#EBF5FB', edgecolor='#2980B9', linewidth=1.2))
    ax.text(86, 66, 'ML Engine (FastAPI)', ha='center', va='center', fontweight='bold', color='#1F618D', fontsize=9)
    ax.text(86, 59, 'Port 8000 (Internal)\nBernoulliNB v2.0.0', ha='center', va='center', color='#2874A6', fontsize=8)
    
    # 5. Graph Narrative (FastAPI)
    ax.add_patch(patches.Rectangle((77, 32), 18, 18, facecolor='#FADBD8', edgecolor='#E74C3C', linewidth=1.2))
    ax.text(86, 43, 'Graph Service (LangGraph)', ha='center', va='center', fontweight='bold', color='#922B21', fontsize=9)
    ax.text(86, 36, 'Port 8001 (Internal)\n10s/20s Cap + Fallback', ha='center', va='center', color='#B03A2E', fontsize=8)
    
    # 6. MongoDB Database (Internal only, with mongo-data volume)
    ax.add_patch(patches.Rectangle((53, 10), 18, 20, facecolor='#EAEDED', edgecolor='#34495E', linewidth=1.5))
    ax.text(62, 23, 'MongoDB 7.0 Persistence', ha='center', va='center', fontweight='bold', color='#2C3E50', fontsize=9)
    ax.text(62, 15, 'Port 27017 (NO HOST PORT)\nVolume: mongo-data', ha='center', va='center', color='#566573', fontsize=8)
    
    # Connecting Arrows inside bridge
    ax.annotate('', xy=(53, 74), xytext=(47, 57), arrowprops=dict(facecolor='#27AE60', edgecolor='#27AE60', width=1, headwidth=4))
    ax.annotate('', xy=(53, 49), xytext=(47, 49), arrowprops=dict(facecolor='#27AE60', edgecolor='#27AE60', width=1, headwidth=4))
    ax.annotate('', xy=(77, 63), xytext=(71, 52), arrowprops=dict(facecolor='#1ABC9C', edgecolor='#1ABC9C', width=1, headwidth=4))
    ax.annotate('', xy=(77, 40), xytext=(71, 46), arrowprops=dict(facecolor='#1ABC9C', edgecolor='#1ABC9C', width=1, headwidth=4))
    ax.annotate('', xy=(62, 30), xytext=(62, 38), arrowprops=dict(facecolor='#1ABC9C', edgecolor='#1ABC9C', width=1, headwidth=4))
    
    plt.tight_layout()
    path = os.path.join(OUTPUT_DIR, "diag1_architecture_trust_boundaries.png")
    plt.savefig(path, dpi=250)
    plt.close()
    print("Generated:", path)

# -----------------------------------------------------------------------------
# 6. Lifecycle & State Machine (Figure 3.2: Clean Left-to-Right Flow)
# Flow: Draft -> Analyzing -> Analyzed -> {Accepted | Escalated -> Reviewed -> Closed}
# With Red-Flag 409 Block path clearly shown!
# -----------------------------------------------------------------------------
def make_diag3_state_machine():
    fig, ax = plt.subplots(figsize=(8.2, 4.4), dpi=250)
    ax.axis('off')
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    
    # 1. DRAFT
    ax.add_patch(patches.Rectangle((2, 48), 13, 20, facecolor='#EAECEE', edgecolor='#7F8C8D', linewidth=1.5))
    ax.text(8.5, 60, 'DRAFT', ha='center', va='center', fontweight='bold', color='#2C3E50', fontsize=9)
    ax.text(8.5, 52, 'Demographics\n& 131 Vocab', ha='center', va='center', color='#5D6D7E', fontsize=7.5)
    
    # Arrow 1 -> 2
    ax.annotate('', xy=(19, 58), xytext=(15, 58), arrowprops=dict(facecolor='#2C3E50', width=1, headwidth=4))
    
    # 2. ANALYZING
    ax.add_patch(patches.Rectangle((19, 48), 14, 20, facecolor='#EBF5FB', edgecolor='#2980B9', linewidth=1.5))
    ax.text(26, 60, 'ANALYZING', ha='center', va='center', fontweight='bold', color='#154360', fontsize=9)
    ax.text(26, 52, 'Queue Job\n& Red Flags', ha='center', va='center', color='#2874A6', fontsize=7.5)
    
    # Arrow 2 -> 3
    ax.annotate('', xy=(37, 58), xytext=(33, 58), arrowprops=dict(facecolor='#2C3E50', width=1, headwidth=4))
    
    # 3. ANALYZED
    ax.add_patch(patches.Rectangle((37, 48), 14, 20, facecolor='#E8F8F5', edgecolor='#1ABC9C', linewidth=1.5))
    ax.text(44, 60, 'ANALYZED', ha='center', va='center', fontweight='bold', color='#117A65', fontsize=9)
    ax.text(44, 52, 'ML Top-3\n+ Attributions', ha='center', va='center', color='#16A085', fontsize=7.5)
    
    # Branching from ANALYZED:
    # Path A: Normal Case -> ACCEPTED
    ax.annotate('', xy=(58, 76), xytext=(51, 64), arrowprops=dict(facecolor='#27AE60', width=1.2, headwidth=4))
    ax.text(54, 73, 'No Red Flag\nAccept', ha='right', va='bottom', fontsize=7.5, fontweight='bold', color='#27AE60')
    
    ax.add_patch(patches.Rectangle((58, 68), 16, 18, facecolor='#D4EFDF', edgecolor='#27AE60', linewidth=1.5))
    ax.text(66, 79, 'ACCEPTED', ha='center', va='center', fontweight='bold', color='#1E8449', fontsize=9)
    ax.text(66, 72, 'Worker Signs Off\n(Routine Care)', ha='center', va='center', color='#27AE60', fontsize=7.5)
    
    # Path B: Red-Flag Emergency -> 409 Intercept -> Forced ESCALATED
    ax.add_patch(patches.Rectangle((35, 12), 24, 22, facecolor='#FDEDEC', edgecolor='#E74C3C', linewidth=1.5, linestyle='--'))
    ax.text(47, 28, 'RED-FLAG TRIGGER', ha='center', va='center', fontweight='bold', color='#922B21', fontsize=8.5)
    ax.text(47, 19, 'Emergency Symptom Detected\nAccept Blocked (HTTP 409)', ha='center', va='center', color='#C0392B', fontsize=7.5)
    
    ax.annotate('', xy=(44, 34), xytext=(44, 48), arrowprops=dict(facecolor='#C0392B', width=1.2, headwidth=4))
    ax.text(45, 41, 'Cardiac / Neuro\nEmergency', ha='left', va='center', fontsize=7, color='#C0392B', fontweight='bold')
    
    # Red flag forces escalation
    ax.annotate('', xy=(58, 45), xytext=(47, 34), arrowprops=dict(facecolor='#C0392B', width=1.2, headwidth=4))
    
    # Normal Escalation arrow from ANALYZED
    ax.annotate('', xy=(58, 50), xytext=(51, 54), arrowprops=dict(facecolor='#E67E22', width=1.2, headwidth=4))
    ax.text(55, 54, 'Escalate', ha='left', va='bottom', fontsize=7.5, fontweight='bold', color='#E67E22')
    
    # 4. ESCALATED
    ax.add_patch(patches.Rectangle((58, 38), 16, 20, facecolor='#FCF3CF', edgecolor='#F39C12', linewidth=1.5))
    ax.text(66, 50, 'ESCALATED', ha='center', va='center', fontweight='bold', color='#B9770E', fontsize=9)
    ax.text(66, 42, 'Dispatched to\nPhysician Queue', ha='center', va='center', color='#7D6608', fontsize=7.5)
    
    # Arrow 4 -> 5
    ax.annotate('', xy=(78, 48), xytext=(74, 48), arrowprops=dict(facecolor='#2C3E50', width=1.2, headwidth=4))
    ax.text(76, 51, 'MD Review', ha='center', va='bottom', fontsize=7, color='#2C3E50')
    
    # 5. REVIEWED
    ax.add_patch(patches.Rectangle((78, 38), 18, 20, facecolor='#E8F8F5', edgecolor='#1ABC9C', linewidth=1.5))
    ax.text(87, 50, 'REVIEWED', ha='center', va='center', fontweight='bold', color='#117A65', fontsize=9)
    ax.text(87, 42, 'Doctor Diagnosis\n& Rx Signed (__v)', ha='center', va='center', color='#16A085', fontsize=7.5)
    
    # Arrow 5 -> 6
    ax.annotate('', xy=(87, 24), xytext=(87, 38), arrowprops=dict(facecolor='#27AE60', width=1.2, headwidth=4))
    ax.text(88, 31, 'Worker Confirms', ha='left', va='center', fontsize=7, color='#27AE60')
    
    # 6. CLOSED
    ax.add_patch(patches.Rectangle((78, 8), 18, 16, facecolor='#D4EFDF', edgecolor='#27AE60', linewidth=1.5))
    ax.text(87, 18, 'CLOSED', ha='center', va='center', fontweight='bold', color='#1E8449', fontsize=9)
    ax.text(87, 12, 'Consultation Complete', ha='center', va='center', color='#27AE60', fontsize=7.5)
    
    plt.tight_layout()
    path = os.path.join(OUTPUT_DIR, "diag3_state_machine.png")
    plt.savefig(path, dpi=250)
    plt.close()
    print("Generated:", path)

# -----------------------------------------------------------------------------
# 7. LLM Timeout Hierarchy (Figure 3.3: Widen boxes so text fits inside)
# -----------------------------------------------------------------------------
def make_diag5_timeout():
    fig, ax = plt.subplots(figsize=(7.8, 3.6), dpi=250)
    ax.axis('off')
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    
    levels = [
        ("Nginx Edge Reverse Proxy", "proxy_read_timeout = 90s (External connection barrier)", 76, 68, "#154360", "#EBF5FB"),
        ("Backend Axios Client Timeout", "timeout = 30s (Backend HTTP client -> Graph Microservice)", 52, 68, "#1B4F72", "#E8F8F5"),
        ("LangGraph Narrative Hard Cap", "asyncio.wait_for = 20s (Bounded cap across all cascade attempts)", 28, 68, "#2471A3", "#FCF3CF"),
        ("Per-Attempt Gemini API Timeout", "timeout = 10s per individual candidate model call", 4, 68, "#B03A2E", "#FADBD8"),
    ]
    
    for title, detail, y_pos, bar_width, border_col, bg_col in levels:
        ax.add_patch(patches.Rectangle((4, y_pos), bar_width, 19, facecolor=bg_col, edgecolor=border_col, linewidth=1.5))
        ax.text(6, y_pos + 12.5, title, fontweight='bold', color=border_col, fontsize=9.5)
        ax.text(6, y_pos + 5, detail, color='#2C3E50', fontsize=8)
        
    # Annotate Fallback Guarantee Box
    ax.add_patch(patches.Rectangle((75, 4), 22, 91, facecolor='#FDEDEC', edgecolor='#C0392B', linestyle='--', linewidth=1.5))
    ax.text(86, 88, 'FAIL-SAFE', ha='center', va='center', fontweight='bold', color='#922B21', fontsize=9.5)
    ax.text(86, 82, 'GUARANTEE', ha='center', va='center', fontweight='bold', color='#922B21', fontsize=9.5)
    desc = (
        "If total elapsed\ntime reaches 20s\nor all models\nreturn 429 / 404:\n\n"
        "INSTANT\nFALLBACK\n\n"
        "Deterministically\nrenders local\npre-compiled\nclinical templates."
    )
    ax.text(86, 46, desc, ha='center', va='center', color='#78281F', fontsize=7.8)
    
    plt.tight_layout()
    path = os.path.join(OUTPUT_DIR, "diag5_llm_timeout_hierarchy.png")
    plt.savefig(path, dpi=250)
    plt.close()
    print("Generated:", path)

# -----------------------------------------------------------------------------
# 8. Verified End-to-End Clinical Workflow Panels (Figure 3.4: Clean 2x3 Grid)
# -----------------------------------------------------------------------------
def make_ui_workflow_panels():
    panel_specs = [
        ("01_worker_result.png", "(a) Frontline Worker Intake & ML Differential"),
        ("04_redflag_block.png", "(b) Red-Flag Accept Intercept (HTTP 409 Safety Gate)"),
        ("06_worker_list_escalated.png", "(c) Frontline Worker Escalated Case Queue"),
        ("08_doctor_response.png", "(d) Medical Officer Clinical Second Opinion"),
        ("09_worker_reviewed.png", "(e) Frontline Worker Verified 'Reviewed' Status"),
        ("admin_dashboard_real.png", "(f) System Admin Live Telemetry & Audit Trail"),
    ]
    
    loaded_images = []
    for fname, label in panel_specs:
        p = os.path.join(UI_DIR, fname)
        if os.path.exists(p):
            loaded_images.append((Image.open(p), label))
        else:
            print(f"Warning: Screenshot {fname} not found!")
            
    if len(loaded_images) == 6:
        w = 900
        h = 520
        # 3 rows, 2 cols (max 2 per row)
        composite = Image.new('RGB', (w*2 + 40, h*3 + 90), (255, 255, 255))
        
        fig, axes = plt.subplots(3, 2, figsize=(9.0, 10.5), dpi=250)
        axes = axes.flatten()
        
        for i, (img, label) in enumerate(loaded_images):
            axes[i].imshow(img)
            axes[i].axis("off")
            axes[i].set_title(label, fontsize=8.5, weight="bold", color="#154360", pad=4)
            
        fig.tight_layout(pad=1.2)
        out_path = os.path.join(OUTPUT_DIR, "fig_clinical_workflow_panels.png")
        fig.savefig(out_path, bbox_inches="tight")
        plt.close(fig)
        print("Generated clean Figure 3.4 composite:", out_path)
    else:
        print(f"Expected 6 panel images, found {len(loaded_images)}. Skipping composite.")

if __name__ == "__main__":
    print("Generating publication-quality figures, diagrams, and equations...")
    make_equations()
    make_fig2_dataset_pie()
    make_fig1_performance_calibration()
    make_fig3_load_test()
    make_fig4_list_opt()
    make_diag1_architecture()
    make_diag3_state_machine()
    make_diag5_timeout()
    make_ui_workflow_panels()
    print("All figures generated successfully!")
