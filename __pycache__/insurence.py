const express = require("express");
const mongoose = require("mongoose");

const app = express();
app.use(express.json());

/* ===========================
   DATABASE CONNECTION
=========================== */
mongoose.connect("mongodb://127.0.0.1:27017/hospitalInsurance")
.then(() => console.log("MongoDB Connected"))
.catch(err => console.log(err));

/* ===========================
   SCHEMAS
=========================== */

// Patient Schema
const patientSchema = new mongoose.Schema({
    name: String,
    age: Number,
    insuranceCompany: String
});
const Patient = mongoose.model("Patient", patientSchema);

// Policy Schema
const policySchema = new mongoose.Schema({
    patientId: {
        type: mongoose.Schema.Types.ObjectId,
        ref: "Patient"
    },
    policyNumber: String,
    coverageAmount: Number,
    premiumAmount: Number,
    validTill: Date
});
const Policy = mongoose.model("Policy", policySchema);

// Claim Schema
const claimSchema = new mongoose.Schema({
    patientId: {
        type: mongoose.Schema.Types.ObjectId,
        ref: "Patient"
    },
    policyId: {
        type: mongoose.Schema.Types.ObjectId,
        ref: "Policy"
    },
    hospitalName: String,
    treatmentDetails: String,
    claimAmount: Number,
    status: {
        type: String,
        enum: ["Pending", "Approved", "Rejected", "Settled"],
        default: "Pending"
    },
    settlementAmount: {
        type: Number,
        default: 0
    }
});
const Claim = mongoose.model("Claim", claimSchema);

/* ===========================
   PATIENT ROUTES
=========================== */

// Add Patient
app.post("/patients", async (req, res) => {
    try {
        const patient = new Patient(req.body);
        await patient.save();
        res.status(201).json(patient);
    } catch (err) {
        res.status(400).json({ error: err.message });
    }
});

// Get All Patients
app.get("/patients", async (req, res) => {
    const patients = await Patient.find();
    res.json(patients);
});

/* ===========================
   POLICY ROUTES
=========================== */

// Add Policy
app.post("/policies", async (req, res) => {
    try {
        const policy = new Policy(req.body);
        await policy.save();
        res.status(201).json(policy);
    } catch (err) {
        res.status(400).json({ error: err.message });
    }
});

// Get Policies
app.get("/policies", async (req, res) => {
    const policies = await Policy.find().populate("patientId");
    res.json(policies);
});

/* ===========================
   CLAIM ROUTES
=========================== */

// Submit Claim
app.post("/claims", async (req, res) => {
    try {
        const claim = new Claim(req.body);
        await claim.save();
        res.status(201).json(claim);
    } catch (err) {
        res.status(400).json({ error: err.message });
    }
});

// Approve Claim
app.put("/claims/approve/:id", async (req, res) => {
    const claim = await Claim.findById(req.params.id);
    if (!claim) return res.status(404).json({ message: "Claim not found" });

    claim.status = "Approved";
    await claim.save();

    res.json({ message: "Claim Approved", claim });
});

// Reject Claim
app.put("/claims/reject/:id", async (req, res) => {
    const claim = await Claim.findById(req.params.id);
    if (!claim) return res.status(404).json({ message: "Claim not found" });

    claim.status = "Rejected";
    await claim.save();

    res.json({ message: "Claim Rejected", claim });
});

// Settle Claim (With Coverage Check)
app.put("/claims/settle/:id", async (req, res) => {
    const claim = await Claim.findById(req.params.id);
    if (!claim) return res.status(404).json({ message: "Claim not found" });

    if (claim.status !== "Approved") {
        return res.status(400).json({ message: "Claim must be approved first" });
    }

    const policy = await Policy.findById(claim.policyId);
    if (!policy) return res.status(404).json({ message: "Policy not found" });

    // Check policy validity
    if (new Date(policy.validTill) < new Date()) {
        return res.status(400).json({ message: "Policy expired" });
    }

    // Settlement calculation
    const settlement = Math.min(claim.claimAmount, policy.coverageAmount);

    claim.status = "Settled";
    claim.settlementAmount = settlement;
    await claim.save();

    res.json({
        message: "Claim Settled Successfully",
        settlementAmount: settlement,
        claim
    });
});

// Get All Claims
app.get("/claims", async (req, res) => {
    const claims = await Claim.find()
        .populate("patientId")
        .populate("policyId");

    res.json(claims);
});

/* ===========================
   SERVER START
=========================== */

app.listen(5000, () => {
    console.log("Server running on port 5000");
});
