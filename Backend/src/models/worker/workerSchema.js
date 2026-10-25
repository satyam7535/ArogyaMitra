import mongoose from "mongoose";
import bcrypt from "bcrypt";
const workerSchema = new mongoose.Schema({
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
    addedBy: {  // who added this worker (location inherited from admin)
        type: mongoose.Schema.Types.ObjectId, 
        ref: "Admin" 
    },
}, { timestamps: true });

workerSchema.pre("save", async function () {
    if (!this.isModified("password")) return;
    this.password = await bcrypt.hash(this.password, 10);
});

export default mongoose.model("Worker", workerSchema);