with open('graph/llm.py', 'r', encoding='utf-8') as f:
    text = f.read()

old_block = """    # 2. Strict PII removal (Rule 6: Never send patient names or contact details to the LLM)
    pii_free_data = {
        k: v for k, v in sanitized_xai.items()
        if k not in [
            "patientName",
            "workerName",
            "location",
            "phoneNumber",
            "address",
            "email",
            "contactDetails",
        ]
    }"""

new_block = """    # 2. Strict PII removal (Rule 6: Never send patient names or contact details to the LLM)
    patient_name = str(xai_data.get("patientName", "")).strip()
    worker_name = str(xai_data.get("workerName", "")).strip()

    pii_free_data = {
        k: v for k, v in sanitized_xai.items()
        if k not in [
            "patientName",
            "workerName",
            "location",
            "phoneNumber",
            "address",
            "email",
            "contactDetails",
            "notes",
            "patientNotes",
            "clinicalNotes",
            "patientId",
            "workerId",
        ]
    }

    if patient_name or worker_name:
        def scrub_names(val):
            if isinstance(val, str):
                res = val
                if patient_name and len(patient_name) > 2:
                    res = re.sub(re.escape(patient_name), "[REDACTED_PATIENT]", res, flags=re.IGNORECASE)
                if worker_name and len(worker_name) > 2:
                    res = re.sub(re.escape(worker_name), "[REDACTED_WORKER]", res, flags=re.IGNORECASE)
                return res
            elif isinstance(val, list):
                return [scrub_names(x) for x in val]
            elif isinstance(val, dict):
                return {k: scrub_names(v) for k, v in val.items()}
            return val
        pii_free_data = scrub_names(pii_free_data)"""

# Handle both CRLF and LF
if old_block in text:
    text = text.replace(old_block, new_block)
elif old_block.replace("\r\n", "\n") in text:
    text = text.replace(old_block.replace("\r\n", "\n"), new_block)
else:
    # Try normalized
    text = text.replace(old_block.replace("\n", "\r\n"), new_block.replace("\n", "\r\n"))

with open('graph/llm.py', 'w', encoding='utf-8') as f:
    f.write(text)

print("Updated graph/llm.py with deep PII scrubbing.")
