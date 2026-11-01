"""
ArogyaMitra — Report Data and Structured Tables
Contains verified empirical tables, literature review matrices, and appendix datasets.
All metrics are strictly checkable against docs/evidence/.
"""

# Literature Review Summary Table (Chapter 1) — 6 Key Seminal Papers (Item 18)
LITERATURE_SUMMARY = [
    {
        "cite_num": "[1]",
        "author": "Wallace et al. (2022)",
        "venue": "npj Digital Medicine",
        "method": "Systematic review of 10 studies evaluating digital symptom checkers using QUADAS-2.",
        "findings": "Primary diagnostic accuracy was low (19–37.9%); triage accuracy was 48.8–90.1%; results varied across checkers; Swiss-cheese error alignment poses patient safety hazards.",
        "relevance": "Directly motivates positioning ArogyaMitra as decision support rather than diagnosis, adding deterministic red flags, and fail-closed design."
    },
    {
        "cite_num": "[2]",
        "author": "Niculescu-Mizil & Caruana (2005)",
        "venue": "Proc. ICML",
        "method": "Empirical study of probability calibration across 10 supervised learning algorithms.",
        "findings": "Naive Bayes pushes probabilities toward 0 and 1 due to independence assumptions; Isotonic regression performs worse than Platt scaling when data is scarce.",
        "relevance": "Explains why BernoulliNB outputs extreme posteriors; justifies labeling scores as uncalibrated estimates. Our Platt scaling trial was an independent experiment."
    },
    {
        "cite_num": "[3]",
        "author": "Domingos & Pazzani (1997)",
        "venue": "Machine Learning",
        "method": "Theoretical and empirical analysis of Naive Bayes optimality under zero-one loss.",
        "findings": "Naive Bayes remains optimal for classification accuracy even when attribute independence is violated, provided ranking order is preserved.",
        "relevance": "Justifies deploying Bernoulli Naive Bayes for discrete symptom triage despite correlated clinical presentations."
    },
    {
        "cite_num": "[4]",
        "author": "Ke et al. (2017)",
        "venue": "NeurIPS",
        "method": "Introduced LightGBM with Gradient-based One-Side Sampling and Exclusive Feature Bundling.",
        "findings": "Achieved significant speedup over standard GBDT on large sparse datasets using histogram-based algorithms.",
        "relevance": "Served as the comparative tree ensemble in our nested cross-validation benchmark on the 304 unique rows."
    },
    {
        "cite_num": "[5]",
        "author": "Lundberg & Lee (2017)",
        "venue": "NeurIPS (SHAP)",
        "method": "Unified framework for interpreting model predictions using game-theoretic Shapley values.",
        "findings": "Identified efficiency, symmetry, dummy player, and additivity as the unique axiomatic foundation for additive feature importance.",
        "relevance": "Underpins our mathematical derivation of exact additive log-odds, ensuring symptom attributions sum to class log-evidence without sampling."
    },
    {
        "cite_num": "[6]",
        "author": "Ji et al. (2023)",
        "venue": "ACM Computing Surveys",
        "method": "Comprehensive survey of hallucination in Large Language Models.",
        "findings": "LLMs frequently fabricate factual entities and clinical claims with grammatical confidence, requiring external grounding.",
        "relevance": "Motivated our architectural restriction: the LLM never classifies diseases and only formats explanations, backed by deterministic fallback templates."
    }
]

# Section 1.2.2 Comparison with Existing Work Table
COMPARISON_WITH_EXISTING_WORK = [
    {
        "concern": "Low and variable diagnostic accuracy across symptom checkers (primary diagnosis 19–37.9%)",
        "source": "Wallace et al. (2022) [1]",
        "response": "Evaluated top-3 differential diagnoses and dropout robustness across 0%, 30%, and 50% missing symptoms using 5x3 repeated stratified CV.",
        "evidence": "docs/evidence/model_benchmark.md:21-23",
        "unvalidated": "Evaluated on synthetic data (304 unique rows); zero real-patient cohort validation."
    },
    {
        "concern": "Triage and patient safety hazards from incorrect diagnosis alignment (Swiss-cheese failure)",
        "source": "Wallace et al. (2022) [1]",
        "response": "Implemented two-tier triage safety: Decision A red-flag emergency screening, low-confidence escalation (<70%), and fail-closed HTTP 503 outage behavior.",
        "evidence": "config/red_flags.yaml, docs/evidence/p0_docker_tests.txt",
        "unvalidated": "Red-flag rules remain in DRAFT status pending formal institutional clinical review."
    },
    {
        "concern": "Need for real-world studies, clinical trial evidence, and medical device regulation",
        "source": "Wallace et al. (2022) [1]",
        "response": "Explicitly scoped as an uncertified educational decision-support prototype; added DPDP-aware audit logging and data protection controls.",
        "evidence": "docs/KNOWN_LIMITATIONS.md",
        "unvalidated": "Not certified under CDSCO or MDR 2017; has not undergone prospective clinical trials."
    },
    {
        "concern": "Naive Bayes pushes predicted probabilities toward 0 and 1 due to independence assumptions",
        "source": "Niculescu-Mizil & Caruana (2005) [2]",
        "response": "Labeled confidence scores as 'estimate, not a clinical probability' in UI; empirical thresholds tuned on held-out data.",
        "evidence": "docs/MODEL_CARD.md:65-69, docs/evidence/p3_thresholds_heldout.txt",
        "unvalidated": "Confidence scores still saturate near 100% when multiple correlated symptoms match."
    },
    {
        "concern": "Calibration methods require separate calibration data and may degrade on small datasets",
        "source": "Niculescu-Mizil & Caruana (2005) [2]",
        "response": "Empirically tested Platt scaling on 304 unique rows; verified log loss worsened from 0.0061 to 0.1643; deployed uncalibrated raw posterior estimates.",
        "evidence": "docs/MODEL_CARD.md:67",
        "unvalidated": "No large real-world clinical dataset available to train a reliable non-parametric calibration map."
    },
    {
        "concern": "Feature attribution instability and stochastic sampling variance in local surrogates (LIME)",
        "source": "Lundberg & Lee (2017) [5]",
        "response": "Derived exact additive log-odds evidence weights directly from Bernoulli likelihoods, satisfying additivity without sampling.",
        "evidence": "ML_Model/app.py, docs/evidence/verify_ml.txt",
        "unvalidated": "Feature attributions reflect statistical model log-odds, not causal biological pathophysiology."
    },
    {
        "concern": "Hallucination of diagnoses, dosages, and medical facts in Large Language Models",
        "source": "Ji et al. (2023) [6]",
        "response": "Architectural boundary isolation: LLM never predicts the disease class; it only formats pre-computed evidence; fallback templates with zero drug dosages.",
        "evidence": "graph/llm.py, docs/evidence/gemini_live_run.txt",
        "unvalidated": "Template library covers only the 41 trained conditions; requires ongoing physician curation."
    }
]

# Appendix A: Engineering Challenges and Architectural Fixes
APPENDIX_A_CHALLENGES = [
    {
        "problem": "Identical Canned Prediction & Mock Fallback (P0 Defect)",
        "found": "Health worker testing showed every symptom input produced an identical 88.5% confidence prediction for 'Infectious Gastroenteritis'.",
        "fix": "Traced to in-process import failure inside container falling back to legacy mock. Rewrote UI to route strictly through backend API `POST /api/v1/consultation/triage`; removed all mock fallbacks; enforced fail-closed HTTP 503 MODEL_UNAVAILABLE on ML outage.",
        "evidence": "docs/evidence/p0_root_cause.txt, p0_docker_tests.txt"
    },
    {
        "problem": "Massive Dataset Duplication & Evaluative Leakage",
        "found": "Automated data provenance analysis on raw Kaggle dataset (4,920 rows) revealed identical symptom vectors across splits.",
        "fix": "Discovered 4,616 exact duplicate rows (93.8% duplication). Dropped duplicates to 304 unique ground-truth rows (~7.4 per class); instituted 5x3 Repeated Stratified K-Fold CV with in-fold symptom dropout to eliminate evaluation leakage.",
        "evidence": "docs/evidence/data_provenance.txt, MODEL_CARD.md"
    },
    {
        "problem": "Hardcoded Cryptographic Fallback Keys in Source Code",
        "found": "Gitleaks audit and static analysis detected fallback encryption keys embedded in `src/utils/cryptoUtils.js` and `dataEncryption.js`.",
        "fix": "Removed all hardcoded fallback keys from source repository; updated gitleaks baseline with written rationales; implemented production startup guard `encryption_key_exit.test.js` verifying process exits with code 1 if ENCRYPTION_KEY is unset.",
        "evidence": "docs/evidence/gitleaks_report.txt, Backend/tests/encryption_key_exit.test.js"
    },
    {
        "problem": "Unevidenced Accuracy Figures in Initial Report Draft",
        "found": "Fact-checking audit found numbers (99.67%, 95.39%, 83.22%, F1 0.9512, ECE 0.0384, Brier 0.0121) lacked supporting evidence files.",
        "fix": "Removed unevidenced draft figures from report text; reconciled all performance claims with traceable nested CV benchmarks in `model_benchmark.md` and `tuned_tree_benchmark.md`.",
        "evidence": "docs/evidence/model_benchmark.md, tuned_tree_benchmark.md, COMPLETION_LEDGER.md"
    },
    {
        "problem": "Unrealistic Load Test Stack & Concurrency Bottlenecks",
        "found": "Early load test issued requests against production rate limiters, recording 429s as normal behavior while list endpoint had high latency.",
        "fix": "Created dedicated `docker-compose.test.yml` with test-only limits (`ALLOW_LOAD_TEST=true`, `LLM_ENABLED=false`); pre-created pending consultations; optimized worker list with server-side pagination and projection.",
        "evidence": "docs/evidence/load_test_testmode_results.txt, load_test_profiling_notes.md"
    },
    {
        "problem": "Garbled LLM Output from Substring Confidence Rewriting",
        "found": "Naive in-place regex replacement of confidence terms ('certain', 'high') mangled valid clinical words like 'certainly' or 'ascertain'.",
        "fix": "Replaced regex replacement with whole-phrase boundary matching; on detection of banned confidence terms, triggers one LLM regeneration; if still failing, falls back cleanly to deterministic clinical template.",
        "evidence": "scripts/test_confidence_word_filter.py, docs/evidence/p2_guardrails_tests.txt"
    },
    {
        "problem": "Gemini Model Deprecation & API Quota Exhaustion",
        "found": "Gemini 1.5 Flash returned 404 model not found; free-tier API quota exhausted after 20 daily calls returning HTTP 429.",
        "fix": "Implemented dynamic ordered cascade `LLM_MODELS = ['gemini-3.8-flash', 'gemini-3-flash-preview', 'gemini-2.5-flash']`; added 10s per-attempt timeout and 20s overall cap; engaged deterministic safe template on exhaustion.",
        "evidence": "docs/evidence/gemini_live_run.txt, scripts/test_llm_timeouts_and_429.py"
    },
    {
        "problem": "Container Vulnerabilities in Base Docker Images",
        "found": "Trivy container security scans reported Critical and High vulnerabilities in Python and Node.js images.",
        "fix": "Implemented multi-stage Docker build for backend stripping npm CLI; uninstalled pip and ensurepip from runtime stages of Python images; upgraded critical packages; achieved zero fixable Critical/High with `--ignore-unfixed`.",
        "evidence": "docs/evidence/trivy_all_images_scan.txt, trivy_all_images_scan_notes.md"
    },
    {
        "problem": "Worker List Endpoint Latency Degradation",
        "found": "Load test showed worker consultation history dominating latency under sequential and concurrent load.",
        "fix": "Added server-side pagination (`page`, `limit`, default 20) and lean Mongoose projection; combined optimization reduced C=1 p50 latency from 193.0 ms to 76.2 ms (60.5% faster) and p99 from 660.6 ms to 152.0 ms (77.0% faster). Cause not isolated.",
        "evidence": "docs/evidence/load_test_profiling_notes.md:44-48, load_test_testmode_results.txt"
    },
    {
        "problem": "Session Expiry & Second-Opinion Escalation Lifecycle",
        "found": "Frontline workers experienced silent token expiration, while clinician escalation saving and review workflows required dedicated integration.",
        "fix": "Implemented explicit 401 session expiry banners and `refresh_session_token` handling in `ui/utils/api_client.py`, and established end-to-end multi-role consultation persistence in `Backend/src/controller/consultation.controller.js` connecting worker escalation, physician review queue with OCC updates, and worker reviewed status inspection.",
        "evidence": "ui/utils/api_client.py, Backend/src/controller/consultation.controller.js, docs/evidence/playwright_report.txt"
    }
]
