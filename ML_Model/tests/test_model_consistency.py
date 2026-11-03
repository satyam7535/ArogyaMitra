"""
Consistency verification test: 20 fixed clinical symptom sets.
Validates that calibrated predictions and TreeSHAP attributions remain deterministic.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import pytest

from ML_Model.app import PredictRequest, run_prediction

TWENTY_CLINICAL_SYMPTOM_SETS = [
    {
        "id": 1,
        "disease": "Fungal infection",
        "symptoms": ["itching", "skin_rash", "nodal_skin_eruptions"]
    },
    {
        "id": 2,
        "disease": "Allergy",
        "symptoms": ["continuous_sneezing", "shivering", "chills"]
    },
    {
        "id": 3,
        "disease": "GERD",
        "symptoms": ["stomach_pain", "acidity", "ulcers_on_tongue", "vomiting"]
    },
    {
        "id": 4,
        "disease": "Chronic cholestasis",
        "symptoms": ["itching", "vomiting", "yellowish_skin", "nausea", "loss_of_appetite"]
    },
    {
        "id": 5,
        "disease": "Peptic ulcer diseae",
        "symptoms": ["vomiting", "loss_of_appetite", "abdominal_pain", "passage_of_gases", "internal_itching"]
    },
    {
        "id": 6,
        "disease": "AIDS",
        "symptoms": ["muscle_wasting", "patches_in_throat", "high_fever", "extra_marital_contacts"]
    },
    {
        "id": 7,
        "disease": "Diabetes",
        "symptoms": ["fatigue", "weight_loss", "restlessness", "lethargy", "irregular_sugar_level", "excessive_hunger", "increased_appetite", "polyuria"]
    },
    {
        "id": 8,
        "disease": "Gastroenteritis",
        "symptoms": ["vomiting", "sunken_eyes", "dehydration", "diarrhoea"]
    },
    {
        "id": 9,
        "disease": "Bronchial Asthma",
        "symptoms": ["fatigue", "cough", "high_fever", "breathlessness", "mucoid_sputum"]
    },
    {
        "id": 10,
        "disease": "Hypertension",
        "symptoms": ["headache", "chest_pain", "dizziness", "loss_of_balance", "lack_of_concentration"]
    },
    {
        "id": 11,
        "disease": "Migraine",
        "symptoms": ["acidity", "indigestion", "headache", "blurred_and_distorted_vision", "excessive_hunger"]
    },
    {
        "id": 12,
        "disease": "Cervical spondylosis",
        "symptoms": ["back_pain", "neck_pain", "dizziness", "loss_of_balance"]
    },
    {
        "id": 13,
        "disease": "Paralysis (brain hemorrhage)",
        "symptoms": ["vomiting", "headache", "weakness_of_one_body_side", "altered_sensorium"]
    },
    {
        "id": 14,
        "disease": "Jaundice",
        "symptoms": ["itching", "vomiting", "fatigue", "weight_loss", "high_fever", "yellowish_skin", "dark_urine"]
    },
    {
        "id": 15,
        "disease": "Malaria",
        "symptoms": ["chills", "vomiting", "high_fever", "sweating", "headache", "nausea", "muscle_pain"]
    },
    {
        "id": 16,
        "disease": "Chicken pox",
        "symptoms": ["itching", "skin_rash", "fatigue", "lethargy", "high_fever", "headache", "loss_of_appetite", "mild_fever", "swelled_lymph_nodes"]
    },
    {
        "id": 17,
        "disease": "Dengue",
        "symptoms": ["skin_rash", "chills", "joint_pain", "vomiting", "fatigue", "high_fever", "headache", "nausea", "loss_of_appetite", "pain_behind_the_eyes", "back_pain"]
    },
    {
        "id": 18,
        "disease": "Typhoid",
        "symptoms": ["chills", "vomiting", "fatigue", "high_fever", "headache", "nausea", "constipation", "abdominal_pain", "diarrhoea", "toxic_look_(typhos)"]
    },
    {
        "id": 19,
        "disease": "hepatitis A",
        "symptoms": ["joint_pain", "vomiting", "yellowish_skin", "dark_urine", "nausea", "loss_of_appetite", "abdominal_pain", "diarrhoea", "mild_fever", "yellowing_of_eyes", "muscle_pain"]
    },
    {
        "id": 20,
        "disease": "Hepatitis B",
        "symptoms": ["itching", "fatigue", "lethargy", "yellowish_skin", "dark_urine", "loss_of_appetite", "abdominal_pain", "yellow_urine", "yellowing_of_eyes", "malaise", "receiving_blood_transfusion", "receiving_unsterile_injections"]
    }
]

@pytest.mark.parametrize("case", TWENTY_CLINICAL_SYMPTOM_SETS, ids=[f"set_{c['id']}_{c['disease'].strip()}" for c in TWENTY_CLINICAL_SYMPTOM_SETS])
def test_twenty_fixed_symptom_sets(case):
    req = PredictRequest(symptoms=case["symptoms"])
    res = run_prediction(req)

    assert res["primaryDiagnosis"].strip() == case["disease"].strip(), f"Expected {case['disease']}, got {res['primaryDiagnosis']}"
    assert 0.0 <= res["confidenceScore"] <= 100.0
    assert len(res["topPredictions"]) == 3
    assert len(res["shapExplanation"]) > 0
    assert res["modelUsed"] is not None
