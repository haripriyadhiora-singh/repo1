from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from datetime import date

app = FastAPI()

# -----------------------------
# Models
# -----------------------------

class Patient(BaseModel):
    id: int
    name: str
    age: int
    insurance_company: str


class Policy(BaseModel):
    id: int
    patient_id: int
    policy_number: str
    coverage_amount: float
    valid_till: date


class Claim(BaseModel):
    id: int
    patient_id: int
    policy_id: int
    hospital_name: str
    treatment_details: str
    claim_amount: float
    status: str = "Pending"
    settlement_amount: float = 0


# -----------------------------
# In-Memory Database
# -----------------------------

patients: List[Patient] = []
policies: List[Policy] = []
claims: List[Claim] = []


# -----------------------------
# Patient APIs
# -----------------------------

@app.post("/patients")
def add_patient(patient: Patient):
    patients.append(patient)
    return {"message": "Patient added", "data": patient}


@app.get("/patients")
def get_patients():
    return patients


# -----------------------------
# Policy APIs
# -----------------------------

@app.post("/policies")
def add_policy(policy: Policy):
    policies.append(policy)
    return {"message": "Policy added", "data": policy}


@app.get("/policies")
def get_policies():
    return policies


# -----------------------------
# Claim APIs
# -----------------------------

@app.post("/claims")
def submit_claim(claim: Claim):
    claims.append(claim)
    return {"message": "Claim submitted", "data": claim}


@app.put("/claims/approve/{claim_id}")
def approve_claim(claim_id: int):
    for claim in claims:
        if claim.id == claim_id:
            claim.status = "Approved"
            return {"message": "Claim approved", "data": claim}
    raise HTTPException(status_code=404, detail="Claim not found")


@app.put("/claims/reject/{claim_id}")
def reject_claim(claim_id: int):
    for claim in claims:
        if claim.id == claim_id:
            claim.status = "Rejected"
            return {"message": "Claim rejected", "data": claim}
    raise HTTPException(status_code=404, detail="Claim not found")


@app.put("/claims/settle/{claim_id}")
def settle_claim(claim_id: int):
    for claim in claims:
        if claim.id == claim_id:

            if claim.status != "Approved":
                raise HTTPException(status_code=400, detail="Claim must be approved first")

            # Find policy
            policy = next((p for p in policies if p.id == claim.policy_id), None)

            if not policy:
                raise HTTPException(status_code=404, detail="Policy not found")

            if policy.valid_till < date.today():
                raise HTTPException(status_code=400, detail="Policy expired")

            # Settlement logic
            settlement = min(claim.claim_amount, policy.coverage_amount)
            claim.settlement_amount = settlement
            claim.status = "Settled"

            return {
                "message": "Claim settled successfully",
                "settlement_amount": settlement,
                "data": claim
            }

    raise HTTPException(status_code=404, detail="Claim not found")


@app.get("/claims")
def get_claims():
    return claims
