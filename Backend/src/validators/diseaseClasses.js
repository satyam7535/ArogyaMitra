/**
 * ArogyaMitra — Trained Clinical Disease Classes (v2.0.0)
 * Canonical list of 41 classes from the trained Bernoulli Naive Bayes model.
 * Used for strict boundary validation: any prediction outside this vocabulary is rejected with 503 MODEL_UNAVAILABLE.
 */

export const TRAINED_DISEASE_CLASSES = Object.freeze([
  "(vertigo) Paroymsal  Positional Vertigo",
  "AIDS",
  "Acne",
  "Alcoholic hepatitis",
  "Allergy",
  "Arthritis",
  "Bronchial Asthma",
  "Cervical spondylosis",
  "Chicken pox",
  "Chronic cholestasis",
  "Common Cold",
  "Dengue",
  "Diabetes",
  "Dimorphic hemorrhoids(piles)",
  "Drug Reaction",
  "Fungal infection",
  "GERD",
  "Gastroenteritis",
  "Heart attack",
  "Hepatitis B",
  "Hepatitis C",
  "Hepatitis D",
  "Hepatitis E",
  "Hypertension",
  "Hyperthyroidism",
  "Hypoglycemia",
  "Hypothyroidism",
  "Impetigo",
  "Jaundice",
  "Malaria",
  "Migraine",
  "Osteoarthristis",
  "Paralysis (brain hemorrhage)",
  "Peptic ulcer diseae",
  "Pneumonia",
  "Psoriasis",
  "Tuberculosis",
  "Typhoid",
  "Urinary tract infection",
  "Varicose veins",
  "hepatitis A",
]);

export const isValidDiseaseClass = (disease) => {
  if (!disease || typeof disease !== "string") return false;
  return TRAINED_DISEASE_CLASSES.includes(disease.trim());
};

export const validatePredictionBoundary = (mlResult) => {
  if (!mlResult || typeof mlResult !== "object") {
    return { valid: false, reason: "ML result is not an object" };
  }

  const disease = mlResult.disease || mlResult.primaryDiagnosis;
  if (!isValidDiseaseClass(disease)) {
    return {
      valid: false,
      reason: `Predicted class '${disease}' is not in the 41 trained model classes`,
    };
  }

  const confidence = Number(mlResult.confidence ?? mlResult.confidenceScore);
  if (isNaN(confidence) || confidence < 0) {
    return { valid: false, reason: `Invalid confidence score: ${confidence}` };
  }

  if (Array.isArray(mlResult.topPredictions) && mlResult.topPredictions.length > 0) {
    for (const pred of mlResult.topPredictions) {
      if (!isValidDiseaseClass(pred.disease)) {
        return {
          valid: false,
          reason: `Differential prediction '${pred.disease}' is not in trained classes`,
        };
      }
    }
  }

  return { valid: true };
};

