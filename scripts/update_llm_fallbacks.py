import re

with open("graph/llm.py", "r", encoding="utf-8") as f:
    content = f.read()

replacement = '''DISEASE_DRAFT_GUIDELINES: dict[str, dict[str, str]] = {
    "Malaria": {
        "en": "Maintain adequate oral hydration with clean boiled water; use mosquito bed nets; monitor oral temperature every 4 hours. No unvetted medication.",
        "hi": "उबला हुआ साफ पानी पिएं; मच्छरदानी का प्रयोग करें; हर 4 घंटे में तापमान की जांच करें। बिना डॉक्टर की सलाह के दवा न लें।",
        "mr": "उकळलेले स्वच्छ पाणी प्या; डास प्रतिबंधक जाळी वापरा; दर 4 तासांनी शरीराचे तापमान तपासा. परस्पर औषधे घेऊ नका.",
        "referral_en": "Refer to Primary Health Centre (PHC) for malaria parasite rapid diagnostic test (RDT) and peripheral blood smear.",
        "referral_hi": "मलेरिया रैपिड टेस्ट (RDT) और रक्त जांच के लिए तत्काल प्राथमिक स्वास्थ्य केंद्र (PHC) रेफर करें।",
        "referral_mr": "मलेरिया रक्ताच्या तपासणीसाठी (RDT) त्वरित प्राथमिक आरोग्य केंद्र (PHC) कडे पाठवा.",
    },
    "Fungal infection": {
        "en": "Keep skin clean and dry; wear loose breathable cotton clothing; do not share towels or personal bedding.",
        "hi": "त्वचा को साफ और सूखा रखें; सूती ढीले कपड़े पहनें; तौलिया या बिस्तर साझा न करें।",
        "mr": "त्वचा स्वच्छ आणि कोरडी ठेवा; सैल सुती कपडे वापरा; टॉवेल किंवा वैयक्तिक वस्तू इतरांना वापरू देऊ नका.",
        "referral_en": "Refer to outpatient clinic or Medical Officer for clinical dermatological evaluation.",
        "referral_hi": "त्वचा संबंधी परामर्श के लिए प्राथमिक स्वास्थ्य केंद्र के डॉक्टर को रेफर करें।",
        "referral_mr": "त्वचारोग तपासणीसाठी प्राथमिक आरोग्य केंद्रातील वैद्यकीय अधिकाऱ्यांकडे पाठवा.",
    },
    "Dengue": {
        "en": "Maintain oral hydration with clean water and ORS; monitor for warning signs (mucosal bleeding, persistent vomiting, severe abdominal pain). Avoid NSAIDs (aspirin/ibuprofen).",
        "hi": "ओआरएस और पर्याप्त तरल पदार्थों का सेवन करें; मसूड़ों से रक्तस्राव या लगातार उल्टी जैसे खतरे के संकेतों पर नजर रखें। एस्पिरिन या ब्रूफेन न लें।",
        "mr": "ओआरएस आणि भरपूर पाणी प्या; हिरड्यांमधून रक्त येणे किंवा उलट्या यांसारख्या गंभीर लक्षणांवर लक्ष ठेवा. ॲस्पिरिन किंवा आयबुप्रोफेन घेऊ नका.",
        "referral_en": "URGENT REFERRAL: Immediate transfer to Community Health Centre / District Hospital for platelet count and hematocrit monitoring.",
        "referral_hi": "अति आवश्यक: प्लेटलेट और रक्त जांच के लिए मरीज को तत्काल सामुदायिक स्वास्थ्य केंद्र या जिला अस्पताल रेफर करें।",
        "referral_mr": "तातडीचा संदर्भ: प्लेटलेट आणि रक्त तपासणीसाठी रुग्णाला तात्काळ ग्रामीण किंवा जिल्हा रुग्णालयात दाखल करा.",
    },
    "Typhoid": {
        "en": "Drink strictly boiled or filtered water; consume freshly cooked, soft foods; wash hands thoroughly with soap before eating.",
        "hi": "केवल उबला या छना हुआ पानी पिएं; ताजा पका हुआ हल्का भोजन करें; भोजन से पूर्व साबुन से हाथ धोएं।",
        "mr": "फक्त उकळलेले पाणी प्या; ताजा आणि हलका आहार घ्या; जेवणापूर्वी हात स्वच्छ धुवा.",
        "referral_en": "Refer to Primary Health Centre for diagnostic blood culture / Widal testing and physician management.",
        "referral_hi": "रक्त परीक्षण और चिकित्सा अधिकारी द्वारा पुष्टि के लिए प्राथमिक स्वास्थ्य केंद्र रेफर करें।",
        "referral_mr": "रक्त तपासणी आणि पुढील उपचारांसाठी प्राथमिक आरोग्य केंद्राकडे पाठवा.",
    },
    "Diabetes": {
        "en": "Monitor fasting and post-prandial blood glucose; maintain foot hygiene and skin integrity; avoid high-glycemic sugary foods; stay hydrated.",
        "hi": "ब्लड शुगर की नियमित जांच कराएं; पैरों की स्वच्छता का ध्यान रखें; मीठे और तले पदार्थों से परहेज करें।",
        "mr": "रक्तातील साखरेची नियमित तपासणी करा; पायांची काळजी घ्या; गोड आणि तळलेले पदार्थ टाळा.",
        "referral_en": "Refer to Medical Officer for HbA1c testing, diabetic complication screening, and formal treatment regimen.",
        "referral_hi": "HbA1c जांच और दीर्घकालिक उपचार योजना के लिए चिकित्सा अधिकारी को रेफर करें।",
        "referral_mr": "HbA1c तपासणी आणि दीर्घकालीन उपचारांसाठी वैद्यकीय अधिकाऱ्यांकडे पाठवा.",
    },
    "Bronchial Asthma": {
        "en": "Avoid smoke, dust, cold drafts, and known allergens; remain calm in an upright sitting posture during tight breathing.",
        "hi": "धूल, धुएं, ठंडी हवा और एलर्जी पैदा करने वाली चीजों से बचें; सांस फूलने पर मरीज को सीधा बैठाएं।",
        "mr": "धूळ, धूर आणि थंड हवेपासून दूर राहा; श्वास घेण्यास त्रास होत असल्यास सरळ बसून राहा.",
        "referral_en": "Refer to Community Health Centre for peak flow assessment and physician evaluation. Emergency transfer if severe dyspnea.",
        "referral_hi": "सांस की गंभीर समस्या होने पर तत्काल निकटतम अस्पताल या सामुदायिक स्वास्थ्य केंद्र रेफर करें।",
        "referral_mr": "गंभीर श्वासविकारासाठी तात्काळ जवळच्या रुग्णालयात किंवा समुदाय आरोग्य केंद्रात दाखल करा.",
    },
    "Hypertension": {
        "en": "Restrict dietary salt and sodium intake; avoid stress, tobacco, and caffeine; take resting blood pressure measurements.",
        "hi": "भोजन में नमक की मात्रा कम करें; तनाव, तंबाकू और धूम्रपान से दूर रहें; शांत अवस्था में रक्तचाप की जांच करें।",
        "mr": "जेवणातील मिठाचे प्रमाण कमी करा; तणाव आणि तंबाखूचे सेवन टाळा; विश्रांतीच्या स्थितीत रक्तदाब तपासा.",
        "referral_en": "Refer to Primary Health Centre for cardiovascular baseline assessment and regular BP tracking.",
        "referral_hi": "नियमित रक्तचाप निगरानी और हृदय स्वास्थ्य परीक्षण हेतु चिकित्सा अधिकारी को रेफर करें।",
        "referral_mr": "नियमित रक्तदाब तपासणी आणि वैद्यकीय सल्ल्यासाठी प्राथमिक आरोग्य केंद्राकडे पाठवा.",
    },
    "Gastroenteritis": {
        "en": "Replenish lost fluids with Oral Rehydration Salts (ORS) solution and boiled water; avoid solid, greasy, or spicy foods initially.",
        "hi": "ओआरएस (ORS) और स्वच्छ उबले पानी के साथ तरल पदार्थों की भरपाई करें; भारी, तैलीय या मसालेदार भोजन से बचें।",
        "mr": "ओआरएस (ORS) आणि स्वच्छ पाण्याने शरीरातील पाण्याची पातळी नियंत्रित ठेवा; पचनास जड अन्न टाळा.",
        "referral_en": "Refer to PHC / sub-centre if vomiting prevents oral intake or dehydration signs (sunken eyes, lethargy) emerge.",
        "referral_hi": "यदि लगातार उल्टी हो या निर्जलीकरण (कमजोरी) के लक्षण दिखें तो तुरंत डॉक्टर को रेफर करें।",
        "referral_mr": "सतत उलट्या किंवा डिहायड्रेशनची लक्षणे आढळल्यास तात्काळ प्राथमिक आरोग्य केंद्रात हलवा.",
    },
    "Heart attack": {
        "en": "[CRITICAL EMERGENCY] Keep patient seated at rest; do not permit walking; loosen tight collar/clothing; maintain calm.",
        "hi": "[गंभीर आपातकाल] मरीज को शांत बैठाकर रखें; चलने न दें; कपड़े ढीले करें; तत्काल एम्बुलेंस बुलाएं।",
        "mr": "[तातडीची आणीबाणी] रुग्णाला पूर्ण विश्रांती द्या; चालण्यास मज्जाव करा; तात्काळ रुग्णवाहिका बोलवा.",
        "referral_en": "CRITICAL EMERGENCY: Immediate 108 ambulance transfer to nearest cardiac-capable tertiary hospital with ECG facility.",
        "referral_hi": "गंभीर आपातकाल: ईसीजी सुविधा वाले निकटतम अस्पताल में 108 एम्बुलेंस द्वारा तत्काल रेफर करें।",
        "referral_mr": "गंभीर आणीबाणी: ईसीजी सुविधा उपलब्ध असलेल्या रुग्णालयात 108 ॲम्ब्युलन्सद्वारे तात्काळ दाखल करा.",
    },
}

def generate_deterministic_fallback(xai_data: dict[str, Any], language: str = "en") -> LLMConclusion:
    """
    Clinically safe, deterministic fallback conclusion generated when LLM
    fails, times out, throws safety errors, or returns malformed JSON.
    Uses per-disease DRAFT guidance across conditions, strictly free of drug prescriptions.
    """
    disease = xai_data.get("primaryDiagnosis") or xai_data.get("disease") or "Undetermined Condition"
    confidence = xai_data.get("confidenceScore", 0)
    if 0 < confidence < 1.0:
        confidence = round(confidence * 100, 1)
    else:
        confidence = round(float(confidence), 1)

    severity = xai_data.get("severityScore", 0)
    symptoms = xai_data.get("matchedSymptoms") or xai_data.get("symptoms") or []
    symptom_str = ", ".join(str(s).replace("_", " ") for s in symptoms) if symptoms else "reported symptoms"
    precautions = xai_data.get("precautions", [])
    precautions_str = "; ".join(precautions) if precautions else "Rest and monitor symptoms closely"

    matched_guide = DISEASE_DRAFT_GUIDELINES.get(disease, {})

    if language == "hi":
        guide_txt = matched_guide.get("hi", f"अनुशंसित सावधानियां: {precautions_str}।")
        referral_txt = matched_guide.get("referral_hi", "विस्तृत जांच और पुष्टि के लिए प्राथमिक स्वास्थ्य केंद्र के डॉक्टर को रेफर करें।")
        return LLMConclusion(
            diagnosis_summary=f"मरीज में {disease} के लक्षण दिखाई दे रहे हैं, जिसकी मॉडल विश्वसनीयता {confidence}% है।",
            confidence_interpretation="मध्यम से उच्च विश्वसनीयता (सांख्यिकीय अनुमान)। योग्य चिकित्सक द्वारा नैदानिक पुष्टि आवश्यक है।",
            severity_assessment=f"गंभीरता स्कोर {severity}। रोगी के महत्वपूर्ण संकेतों की नियमित निगरानी की आवश्यकता है।",
            key_contributing_factors=f"प्रमुख लक्षण: {symptom_str}।",
            recommended_next_steps=f"[प्रारूप - केवल निर्णय समर्थन, कोई दवा खुराक नहीं] {guide_txt}",
            referral_recommendation=referral_txt,
            llmFallback=True,
        )
    elif language == "mr":
        guide_txt = matched_guide.get("mr", f"शिफारस केलेली काळजी: {precautions_str}।")
        referral_txt = matched_guide.get("referral_mr", "तज्ज्ञ डॉक्टरांकडून पुढील वैद्यकीय तपासणीसाठी संदर्भ द्या.")
        return LLMConclusion(
            diagnosis_summary=f"रुग्णामध्ये {disease} ची लक्षणे आढळतात, मॉडेलचा विश्वास {confidence}% आहे.",
            confidence_interpretation="सांख्यिकीय अंदाज. अंतिम निदानासाठी नोंदणीकृत डॉक्टरांचा सल्ला आवश्यक आहे.",
            severity_assessment=f"गंभीरता पातळी: {severity}। रुग्णाच्या प्रकृतीचे नियमित निरीक्षण करा.",
            key_contributing_factors=f"महत्त्वाची लक्षणे: {symptom_str}।",
            recommended_next_steps=f"[प्रारूप - केवळ निर्णय समर्थन, औषधांचे डोस नाहीत] {guide_txt}",
            referral_recommendation=referral_txt,
            llmFallback=True,
        )
    else:
        guide_txt = matched_guide.get("en", f"Standard precautions: {precautions_str}.")
        referral_txt = matched_guide.get("referral_en", "Refer to a medical officer or relevant clinical specialist for formal diagnostic confirmation.")
        return LLMConclusion(
            diagnosis_summary=f"Patient presents clinical indicators consistent with {disease} with a model confidence of {confidence}%.",
            confidence_interpretation="Statistical decision-support estimation. Clinical correlation by a registered medical practitioner is required.",
            severity_assessment=f"Calculated severity score is {severity}. Continuous monitoring of vital signs is recommended.",
            key_contributing_factors=f"Primary presenting symptoms: {symptom_str}.",
            recommended_next_steps=f"[DRAFT - Decision Support Only, not clinically reviewed, no drug dosages] {guide_txt}",
            referral_recommendation=referral_txt,
            llmFallback=True,
        )
'''

pattern = r"def generate_deterministic_fallback\(xai_data: dict\[str, Any\], language: str = \"en\"\) -> LLMConclusion:.*?return LLMConclusion\(.*?\n        \)"
new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)

with open("graph/llm.py", "w", encoding="utf-8") as f:
    f.write(new_content)

print("Updated graph/llm.py successfully.")
