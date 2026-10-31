# Chapter 5: Conclusion & Future Scope

## 5.1 Project Contributions & Summary

This work developed **ArogyaMitra**, a privacy-first, AI-assisted primary healthcare decision support prototype designed for primary healthcare environments.

### Key Technical Contributions:
1. **Resolution of Dataset Leakage**: Discovered and addressed a 93.8% row duplication flaw in benchmark symptom data, establishing an un-leaked evaluation pipeline using 5x3 Repeated Stratified K-Fold CV and symptom-dropout augmentation.
2. **Diagnostic Modeling & Exact Bayesian Attribution**: Evaluated candidate tree ensembles and Naive Bayes on the deduplicated dataset; deployed Bernoulli Naive Bayes with exact additive Bayesian log-odds feature attributions (the data is synthetic with 304 unique rows and the model is uncalibrated).
3. **Clinical Explainability**: Integrated exact additive Bayesian log-odds feature attributions, providing deterministic, mathematically rigorous feature weights to frontline clinicians.
4. **Defense-in-Depth Cryptography**: Implemented field-level AES-256-GCM encryption for patient PII, Argon2id password hashing, and anti-enumeration multi-tenancy complying with India's DPDP Act 2023.
5. **High-Throughput Asynchronous Concurrency**: Built an in-memory asynchronous job queue with worker concurrency limits, achieving 0.00% request failure across 2,400 empirical benchmark requests across concurrency tiers of 1, 10, and 50 users (200 requests per endpoint per level).
6. **Unified Multilingual Workstation**: Developed a streamlined Streamlit interface supporting English, Hindi, and Marathi, backed by bilingual ReportLab PDF generation and automated headless testing.

---

## 5.2 Limitations

1. **Synthetic Symptom Representation**: The data is synthetic with 304 unique rows across 41 disease classes; the underlying dataset maps discrete categorical symptoms rather than continuous physiological vitals (e.g., continuous SpO2 waveforms or ECG streams).
2. **Language Tokenizer Constraints**: Deep medical terminology in regional Devanagari dialects (Marathi, Hindi) occasionally requires transliteration when standard Unicode fonts lack specialized medical glyphs.
3. **Hardware Storage Constraints on Development Host**: Local Docker containerization was constrained by host system drive space limitations, requiring microservices to run in decoupled local virtual environments.

---

## 5.3 Future Directions

1. **Ayushman Bharat Digital Mission (ABDM) Integration**: Seamless federation with India's national health stack via Ayushman Bharat Health Account (ABHA) IDs for federated Electronic Health Record (EHR) retrieval.
2. **Federated Multi-PHC Learning**: Training edge tree ensembles across regional health centers without centralizing raw patient PII, using privacy-preserving federated aggregation.
3. **Offline-First Mobile PWA**: Developing a Progressive Web App (PWA) client with local SQLite vector indexing to enable full offline triage in remote geographical areas lacking cellular connectivity.
4. **Multimodal Clinical Input**: Integrating computer vision modules for dermatological lesion assessment and voice-to-text transcription in local Indian dialects.
