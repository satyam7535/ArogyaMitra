import mongoose from "mongoose";

const patientSchema = new mongoose.Schema({
    name: {
        type: String,
        required: true,
    },
    age: {
        type: Number,
        required: true,
    },
    gender: {
        type: String,
        enum: ["male", "female", "other"],
        required: true,
    },
    phoneNumber: {
        type: String,
    },
    address: {
        type: String,
    },
    medicalHistory: {
        type: String, // free-text for any pre-existing conditions
    },
    registeredBy: {
        type: mongoose.Schema.Types.ObjectId,
        ref: "Worker",
        required: true,
    }, // the worker who registered this patient
}, { timestamps: true });

export default mongoose.model("Patient", patientSchema);
