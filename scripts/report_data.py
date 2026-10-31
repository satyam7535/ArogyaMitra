"""
ArogyaMitra — Report Data and Structured Tables
Contains verified empirical tables, literature review matrices, and appendix datasets.
All metrics are checkable against docs/evidence/.
"""

# Literature Review Summary Table (Chapter 1)
LITERATURE_SUMMARY = [
    {
        "author": "Wallace et al. (2022) [W]",
        "venue": "npj Digital Medicine",
        "method": "Systematic review of 10 studies evaluating 48 digital symptom checkers with QUADAS-2 quality assessment.",
        "findings": "Primary diagnostic accuracy was low (19–37.9%); triage accuracy was higher (48.8–90.1%); results varied widely across checkers for identical vignettes; safety hazards identified.",
        "relevance": "Directly motivates our decision to position the system as clinical decision support rather than diagnosis, our red-flag screening layer, and fail-closed architecture."
    },
    {
        "author": "Niculescu-Mizil & Caruana (2005) [N]",
        "venue": "Proc. ICML",
        "method": "Empirical study of probability calibration across 10 supervised learning algorithms using Platt scaling and isotonic regression.",
        "findings": "Naive Bayes pushes probabilities toward 0 and 1 due to independence assumptions; Platt scaling requires an independent validation set; isotonic regression overfits when data is scarce.",
        "relevance": "Explains why our BernoulliNB model predicts extreme probabilities, why Platt scaling worsened log loss (0.0061 to 0.1643) on 304 rows, and why UI labels confidence as an estimate."
    },
    {
        "author": "Domingos & Pazzani (1997)",
        "venue": "Machine Learning",
        "method": "Theoretical and empirical analysis of Naive Bayes optimality under zero-one loss.",
        "findings": "Naive Bayes remains optimal for classification accuracy even when attribute independence assumptions are strongly violated, provided the ranking margin is preserved.",
        "relevance": "Justifies deploying Bernoulli Naive Bayes for discrete symptom triage despite correlated medical presentations."
    },
    {
        "author": "Ke et al. (2017)",
        "venue": "NeurIPS",
        "method": "Introduced LightGBM with Gradient-based One-Side Sampling (GOSS) and Exclusive Feature Bundling (EFB).",
        "findings": "Achieved up to 20x speedup over standard GBDT on large sparse datasets using histogram-based algorithms and leaf-wise split growth.",
        "relevance": "Served as the comparison tree ensemble in our nested cross-validation benchmark on the 304 unique rows."
    },
    {
        "author": "Ribeiro et al. (2016)",
        "venue": "ACM SIGKDD (LIME)",
        "method": "Local Interpretable Model-agnostic Explanations using perturbed sparse linear surrogates.",
        "findings": "Provides local feature attributions but suffers from sampling stochasticity and high computational overhead.",
        "relevance": "Motivates our rejection of sampling-based surrogates in favor of exact, deterministic Bayesian log-odds feature attributions."
    },
    {
        "author": "Lundberg & Lee (2017)",
        "venue": "NeurIPS (SHAP)",
        "method": "Unified framework for interpreting model predictions using game-theoretic Shapley values.",
        "findings": "Identified efficiency, symmetry, dummy player, and additivity as the unique axiomatic foundation for additive feature importance.",
        "relevance": "Underpins our mathematical derivation of exact additive log-odds, ensuring the sum of symptom attributions equals total class log-evidence."
    },
    {
        "author": "Ji et al. (2023)",
        "venue": "ACM Computing Surveys",
        "method": "Comprehensive survey of hallucination in Large Language Models.",
        "findings": "LLMs frequently fabricate factual entities and clinical claims with high grammatical confidence, requiring strict external grounding.",
        "relevance": "Motivated our architectural restriction: the LLM never classifies diseases and only formats explanations, backed by deterministic fallback templates."
    },
    {
        "author": "Singhal et al. (2023)",
        "venue": "Nature (Med-PaLM)",
        "method": "Domain-specific instruction fine-tuning and evaluation of medical LLMs against physician benchmarks.",
        "findings": "Demonstrates that clinical language models require structured evaluation against physician ground-truth to prevent unsafe advice.",
        "relevance": "Guides our clinical prompt isolation, Pydantic schema validation, and banned drug denylist."
    },
    {
        "author": "Biryukov et al. (2016)",
        "venue": "IEEE EuroS&P (Argon2)",
        "method": "Memory-hard password hashing algorithm resistant to GPU and ASIC brute-force cracking.",
        "findings": "Won the Password Hashing Competition (PHC); optimizes trade-offs between memory hardness, cache-timing resistance, and execution latency.",
        "relevance": "Directly implemented in ArogyaMitra for credential protection (Argon2id with 3 iterations, 64 MB RAM)."
    },
    {
        "author": "Kung & Robinson (1981)",
        "venue": "ACM TODS",
        "method": "Introduced Optimistic Concurrency Control (OCC) using validation phases.",
        "findings": "Avoids locking overhead in read-heavy database transactions by aborting or retrying only upon conflicting writes.",
        "relevance": "Underpins our Mongoose schema concurrency control (`__v`) and atomic conditional updates for concurrent triage responses."
    }
]

# Section 1.2.2 Comparison with Existing Work Table
COMPARISON_WITH_EXISTING_WORK = [
    {
        "concern": "Low and variable diagnostic accuracy across symptom checkers (primary diagnosis 19–37.9%)",
        "source": "Wallace et al. (2022) [W]",
        "response": "Evaluated top-3 differential diagnoses and dropout robustness across 0%, 30%, and 50% missing symptoms using 5x3 repeated stratified CV.",
        "evidence": "docs/evidence/model_benchmark.md",
        "unvalidated": "Evaluated exclusively on synthetic data (304 unique rows); zero real-patient cohort validation."
    },
    {
        "concern": "Triage and patient safety hazards from incorrect diagnosis alignment (Swiss-cheese failure)",
        "source": "Wallace et al. (2022) [W]",
        "response": "Implemented two-tier triage safety: Decision A red-flag emergency screening, low-confidence escalation (<70%), and fail-closed 503 outage behavior.",
        "evidence": "Backend/src/validators/diseaseClasses.js, docs/evidence/p0_docker_tests.txt",
        "unvalidated": "Red-flag rules remain in DRAFT status pending formal multi-institutional clinician review."
    },
    {
        "concern": "Need for real-world studies, clinical trial evidence, and medical device regulation",
        "source": "Wallace et al. (2022) [W]",
        "response": "Explicitly scoped as an uncertified educational decision-support prototype; added DPDP-aware audit logging and data protection controls.",
        "evidence": "docs/KNOWN_LIMITATIONS.md, docs/PRIVACY.md",
        "unvalidated": "Not certified under CDSCO or MDR 2017; has not undergone prospective clinical trials."
    },
    {
        "concern": "Naive Bayes pushes predicted probabilities toward 0 and 1 due to independence assumptions",
        "source": "Niculescu-Mizil & Caruana (2005) [N]",
        "response": "Rejected false calibration claims; labeled confidence scores as 'estimate, not a clinical probability' in UI; empirical thresholds tuned on held-out data.",
        "evidence": "docs/MODEL_CARD.md, docs/evidence/p3_thresholds_heldout.txt",
        "unvalidated": "Probabilities still saturate near 100% when multiple correlated symptoms match."
    },
    {
        "concern": "Calibration methods require separate calibration data and degrade severely on small datasets",
        "source": "Niculescu-Mizil & Caruana (2005) [N]",
        "response": "Empirically tested Platt scaling on 304 unique rows; verified that log loss worsened from 0.0061 to 0.1643; opted to deploy uncalibrated raw posterior estimates.",
        "evidence": "docs/MODEL_CARD.md, docs/evidence/tuned_tree_benchmark.md",
        "unvalidated": "No large real-world clinical dataset available to train a reliable non-parametric calibration map."
    },
    {
        "concern": "High computational latency and sparse feature representation in tree ensembles",
        "source": "Ke et al. (2017)",
        "response": "Benchmarked LightGBM against BernoulliNB; selected BernoulliNB which executes inference in 1.8 ms via vectorized NumPy operations.",
        "evidence": "docs/evidence/load_test_testmode_results.txt:43",
        "unvalidated": "Only tested on 131 discrete binary features, not continuous lab measurements or vital streams."
    },
    {
        "concern": "Feature attribution instability and stochastic sampling variance in local surrogates (LIME)",
        "source": "Ribeiro et al. (2016), Lundberg & Lee (2017)",
        "response": "Derived exact additive log-odds evidence weights directly from Bernoulli likelihoods, satisfying additivity to machine precision (< 1e-10) without sampling.",
        "evidence": "ML_Model/app.py, docs/evidence/verify_ml.txt",
        "unvalidated": "Feature attributions reflect statistical model log-odds, not causal biological pathophysiology."
    },
    {
        "concern": "Hallucination of diagnoses, dosages, and medical facts in Large Language Models",
        "source": "Ji et al. (2023), Singhal et al. (2023)",
        "response": "Architectural boundary isolation: LLM never predicts the disease class; it only formats pre-computed Bayesian evidence; pre-compiled fallback templates with zero drug dosages.",
        "evidence": "graph/llm.py, docs/evidence/gemini_live_run.txt",
        "unvalidated": "Template library covers only the 41 trained conditions; requires ongoing physician curation."
    }
]

# Appendix A: Engineering Challenges and Architectural Fixes
APPENDIX_A_CHALLENGES = [
    {
        "problem": "Identical Canned Prediction & Mock Fallback (P0 Defect)",
        "found": "Health worker testing showed every symptom input produced an identical 88.5% confidence prediction for 'Infectious Gastroenteritis'.",
        "fix": "Traced to in-process import failure inside container falling back to legacy mock. Rewrote UI to route strictly through backend API `POST /api/v1/consultation/triage`; eliminated all mock fallbacks; enforced fail-closed HTTP 503 MODEL_UNAVAILABLE on ML outage.",
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
        "fix": "Completely excised unevidenced draft figures from report text; reconciled all performance claims with traceable nested CV benchmarks in `model_benchmark.md` and `tuned_tree_benchmark.md`.",
        "evidence": "docs/evidence/model_benchmark.md, tuned_tree_benchmark.md, COMPLETION_LEDGER.md"
    },
    {
        "problem": "Unrealistic Load Test Stack & Concurrency Bottlenecks",
        "found": "Early load test issued requests against production rate limiters, recording 429s as normal behavior while list endpoint had 2.4s p99 latency.",
        "fix": "Created dedicated `docker-compose.test.yml` with test-only limits (`ALLOW_LOAD_TEST=true`, `LLM_ENABLED=false`); pre-created pending consultations; optimized worker list with server-side pagination and projection (60.5% p50 latency speedup).",
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
        "fix": "Implemented dynamic ordered cascade `LLM_MODELS = ['gemini-2.5-flash', 'gemini-3.5-flash', 'gemini-3-flash-preview']`; added 10s per-attempt timeout and 20s overall cap; engaged deterministic safe template on exhaustion.",
        "evidence": "docs/evidence/gemini_live_run.txt, scripts/test_llm_timeouts_and_429.py"
    },
    {
        "problem": "Container Vulnerabilities in Base Docker Images",
        "found": "Trivy container security scans reported Critical and High vulnerabilities in Python and Node.js images.",
        "fix": "Implemented multi-stage Docker build for backend stripping npm CLI; uninstalled pip and ensurepip from runtime stages of Python images; upgraded critical packages; reduced fixable vulnerabilities to 0 with `--ignore-unfixed`.",
        "evidence": "docs/evidence/trivy_all_images_scan.txt, trivy_all_images_scan_notes.md"
    },
    {
        "problem": "Worker List Endpoint Latency Degradation",
        "found": "Load test at 50 concurrent users showed `GET /consultation/my` taking 7.0s p99 due to full collection scan and JSON transfer of all patient records.",
        "fix": "Added server-side pagination (`page`, `limit`, default 20) and lean Mongoose projection excluding heavy internal audit vectors; reduced C=1 p50 latency from 193 ms to 76.2 ms (60.5% speedup) and p99 from 660.6 ms to 152.0 ms (77.0% speedup).",
        "evidence": "docs/evidence/load_test_profiling_notes.md, load_test_testmode_results.txt"
    },
    {
        "problem": "Silent Auth Failure / Session Expiry in Streamlit UI",
        "found": "When JWT access token expired after 15 minutes, UI failed silently or crashed without clear guidance to health worker.",
        "fix": "Added explicit 401 interceptor in `ui/utils/api_client.py` displaying prominent warning: 'Your session has expired. Please log in again to continue.'; sanitized state without data loss.",
        "evidence": "ui/utils/api_client.py, docs/evidence/verify_ui.txt"
    }
]
