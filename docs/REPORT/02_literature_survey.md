# Chapter 2: Literature Survey & Related Work

## 2.1 Primary Healthcare in Developing Nations

Primary healthcare delivery in low- and middle-income countries (LMICs) relies heavily on community-based healthcare extension programs. In India, over 1 million Accredited Social Health Activists (ASHAs) provide frontline maternal and communicable disease surveillance. Studies by Patel et al. (2018) and the National Health Mission (NHM) emphasize that diagnostic error rates at the primary health center (PHC) level exceed 28%, predominantly driven by atypical presentations of common endemic conditions (e.g., Dengue, Malaria, Typhoid, Hepatitis).

## 2.2 Machine Learning in Symptom-Based Triage

Early computer-aided diagnostic systems, such as MYCIN (Shortliffe, 1976) and INTERNIST-I (Miller et al., 1982), utilized rule-based expert systems that failed to scale due to rigid combinatorial state explosions. 

With the emergence of statistical learning, researchers turned to probabilistic models (Naïve Bayes) and tree ensembles. However, recent surveys (Rajpurkar et al., 2022; Wiens et al., 2019) identify widespread methodological flaws in healthcare ML literature:
1. **Shortcut Learning & Data Leakage**: Many disease classification papers evaluate models on synthetically expanded datasets where identical symptom rows are replicated thousands of times. When standard $k$-fold splits are applied without row deduplication, identical samples appear in both partitions, creating misleading 100% accuracy metrics.
2. **Confidence Miscalibration**: Decision tree models produce uncalibrated probability estimates (Guo et al., 2017). A decision tree leaf with Gini purity of 1.0 will output a pseudo-confidence of 100%, even when the sample representation is minimal. In clinical settings, overconfident misdiagnoses have severe patient safety implications.

## 2.3 Explainable AI (XAI) in Clinical Decision Support

The "black-box" nature of modern machine learning creates critical adoption barriers among healthcare professionals (Amann et al., 2020). 
- **LIME (Local Interpretable Model-agnostic Explanations)** (Ribeiro et al., 2016): Fits local surrogate linear models by sampling perturbations around an instance. However, LIME lacks mathematical consistency and produces non-deterministic attributions that vary between identical runs on the same input vector.
- **SHAP (SHapley Additive exPlanations)** (Lundberg & Lee, 2017): Based on cooperative game theory, Shapley values provide the unique attribution formulation satisfying four fundamental axioms: *Efficiency*, *Symmetry*, *Dummy Player*, and *Additivity*. The **TreeSHAP** algorithm optimizes calculation time from exponential $O(2^M)$ to polynomial $O(TLD^2)$, making real-time, deterministic feature attribution feasible for tree ensembles.

## 2.4 Cryptographic Privacy & Healthcare Regulations

Healthcare data is subject to stringent legal protections globally (HIPAA, GDPR) and nationally in India under the **Digital Personal Data Protection Act (DPDP Act 2023)**. 
- Traditional web frameworks frequently store patient demographics in cleartext databases or rely exclusively on disk encryption (Transparent Data Encryption). However, TDE provides no defense against application-level SQL/NoSQL injection vulnerabilities or rogue database administrators.
- Field-level encryption using Authenticated Encryption with Associated Data (AEAD), specifically **AES-256-GCM** (Dworkin, NIST SP 800-38D), provides both confidentiality and tamper-evident authentication.
- Authentication mechanisms have shifted from CPU-hard algorithms (PBKDF2) and fixed-memory algorithms (bcrypt) to memory-hard schemes such as **Argon2id** (RFC 9106), which mitigate GPU/ASIC brute-force dictionary attacks.

## 2.5 Comparative Analysis & System Positioning

| Feature / Dimension | Standard Academic Prototypes | Commercial Telehealth Tools | ArogyaMitra (This Work) |
| :--- | :--- | :--- | :--- |
| **Dataset Hygiene** | Raw 4,920 rows (Unchecked Leakage) | Proprietary / Closed | Deduplicated 304 rows, 5x3 Repeated Stratified CV |
| **Probability Calibration** | Raw Softmax / Leaf Purity | Heuristic scores | Post-hoc Sigmoid/Platt Scaling (ECE 0.0384) |
| **Explainability** | None or Noisy LIME | Static decision trees | Axiomatic TreeSHAP Attribution Charts |
| **Data Protection** | Cleartext MongoDB | Cloud TDE | Field-Level AES-256-GCM + Argon2id |
| **Multi-Tenancy** | Single database / Single tenant | Centralized SaaS | Scoped Multi-Tenant with Anti-Enumeration 404s |
| **Clinical Fallback** | Hard fail on API error | Degraded UI | Deterministic Clinical Rule-Based Fallback |
| **Language Support** | English only | 1-2 Languages | Vernacular (English, Hindi, Marathi) |
