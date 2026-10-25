import mongoose from "mongoose";
import bcrypt from "bcrypt";

const doctorSchema = new mongoose.Schema({
    name: {
        type: String,
        required: true,
    },
    email: {
        type: String,
        required: true,
        unique: true,
    },  
    phoneNumber: {
        type: String,
        required: true,
        unique: true,
    },
    password: {
        type: String,
        required: true,
    },
    specialization: { 
        type: String, 
        required: true 
    },  // e.g., "Cardiologist"
    isAvailable: { 
        type: Boolean, 
        default: true 
    }, // for second-opinion workflow
    addedBy: { 
        type: mongoose.Schema.Types.ObjectId, 
        ref: "Admin" 
    }, // who added this doctor
}, { timestamps: true });

doctorSchema.pre("save", async function () {
    if (!this.isModified("password")) return;
    this.password = await bcrypt.hash(this.password, 10);
});

export default mongoose.model("Doctor", doctorSchema);