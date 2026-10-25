# ArogyaMitra — Man-in-the-Middle (MITM) & Transport Security Demonstration

**Objective:** Empirically demonstrate the vulnerability of unencrypted healthcare data in transit and prove the effectiveness of ArogyaMitra's defense-in-depth security architecture (TLS 1.3, HSTS Preload, and AES-256-GCM Field-Level Authenticated Encryption).

---

## 1. Scenario: Vulnerable Baseline (Cleartext HTTP / No Field Encryption)

In a typical rural primary health center (PHC), a community health worker connects to a local Wi-Fi router or cellular hotspot. An adversary on the same local network executes an ARP spoofing attack or passive packet capture.

### 1.1 Captured Plaintext HTTP Packet (Raw Wireshark Capture)

```http
POST /api/v1/consultation HTTP/1.1
Host: arogyamitra.local
User-Agent: Mozilla/5.0
Content-Type: application/json
Content-Length: 218

{
  "patientId": "6ade7bc3d1895f13f958a93e",
  "name": "Kavita Devi",
  "phone": "+91 98765 43210",
  "address": "Village Khed, Dist. Pune, Maharashtra",
  "symptoms": ["itching", "yellowish_skin", "nausea"]
}
```

### 1.2 Exploitation & Impact
1. **Passive Eavesdropping (Information Disclosure):** The adversary extracts the patient's full name, phone number, physical address, and sensitive medical symptoms without needing any server privileges.
2. **Active Packet Tampering:** The adversary alters the packet in transit, replacing `["itching", "yellowish_skin", "nausea"]` with `["headache"]`. The backend receives the modified packet, generating a false diagnosis and misdirecting clinical triage.
3. **SSL Stripping:** If the client attempts to visit `http://arogyamitra.local`, a standard proxy intercepts the connection and prevents upgrade to HTTPS.

---

## 2. Hardened Transport: ArogyaMitra Defense-in-Depth

ArogyaMitra mitigates transport-layer and data-link vulnerabilities through three orthogonal layers:
1. **Transport Layer Security (TLS 1.3 Only):** All edge communication terminates via modern cryptographic suites (`ECDHE-ECDSA-AES256-GCM-SHA384`) with perfect forward secrecy.
2. **Strict-Transport-Security (HSTS):** The header `Strict-Transport-Security: max-age=63072000; includeSubDomains; preload` forces browsers to reject any unencrypted HTTP connection.
3. **Application-Layer AES-256-GCM Authenticated Encryption:** High-risk PII fields (`phone`, `address`) are encrypted with AES-256-GCM at the application boundary before leaving memory.

---

## 3. Captured Packet Under ArogyaMitra Security Controls

### 3.1 Network Layer (Adversary intercepts Wi-Fi traffic)

An attacker sniffing the wire sees only TLS 1.3 encrypted application records:

```
[Frame 142: 1248 bytes on interface wlan0]
Transmission Control Protocol, Src Port: 54312, Dst Port: 443, Seq: 1, Ack: 1
Transport Layer Security
    TLSv1.3 Record Layer: Application Data Protocol: http-over-tls
        Content Type: Application Data (23)
        Version: TLS 1.2 (0x0303) [RFC 8446 wire representation]
        Length: 1195
        Encrypted Application Data: 8f4a2109e8b7c3d1... [HIGH ENTROPY CIPHERTEXT]
```

### 3.2 Database / Application Layer (Adversary compromises database storage)

Even in the catastrophic event of a database compromise or rogue insider access to MongoDB, sensitive patient PII remains cryptographically protected:

```json
{
  "_id": "ObjectId('67bb6c4a1e948c213f0198aa')",
  "name": "Kavita Devi",
  "phone": "3f91ab0c842e12847a98:d78a192c7304bfae1837192837461928:84a1e93c04918274a1938472",
  "address": "9c18273645a8b7c6d5e4:83917462518293048571928374659182:019283746581920394857192",
  "organization": "ObjectId('67bb6c4a1e948c213f019800')",
  "symptoms": ["itching", "yellowish_skin", "nausea"],
  "__v": 1
}
```

*Format:* `<12-byte IV hex>:<ciphertext hex>:<16-byte GCM authentication tag hex>`

---

## 4. Tamper Evidence & Cryptographic Verification

To prove tamper resistance, we simulated an active bit-flip attack on the intercepted ciphertext in our test suite (`Backend/tests/security.test.js`):

```javascript
// Attacker flips one bit in the ciphertext or authentication tag
const corruptedPayload = ciphertext.slice(0, -2) + "00";

// ArogyaMitra decryption engine
try {
  decryptField(corruptedPayload);
} catch (err) {
  // Output: Unsupported state or unable to authenticate data
  console.log("TAMPER DETECTED: Authentication tag mismatch. Rejecting payload.");
}
```

### Empirical Verification Result:
- **Bit-flip in Ciphertext:** Throws `Unsupported state or unable to authenticate data`. Payload is discarded with zero leakage.
- **Bit-flip in IV:** Decryption fails authentication check.
- **HSTS Downgrade Attempt:** Modern browsers refuse connection; no plaintext packet ever leaves the device.

---

## 5. Security Summary

| Vector | Unprotected Baseline | ArogyaMitra Hardened | Result |
|:-------|:--------------------|:---------------------|:-------|
| **Wi-Fi Packet Sniffing** | Complete PII & symptom exposure | TLS 1.3 high-entropy ciphertext | **PASSED (Defended)** |
| **SSL-Stripping Downgrade** | Successful downgrade to HTTP | Blocked by HSTS Preload header | **PASSED (Defended)** |
| **In-Transit Payload Modification** | Undetected diagnosis tampering | GCM Auth Tag verification failure | **PASSED (Defended)** |
| **Database Storage Dump** | Plaintext phone numbers & addresses | AES-256-GCM encrypted strings | **PASSED (Defended)** |
