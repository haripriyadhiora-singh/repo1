from fastapi import FastAPI

app = FastAPI()


def pre_authorization(treatment_covered: bool, waiting_period_completed: bool):
    if treatment_covered and waiting_period_completed:
        return "Approved"
    return "Rejected"


def settlement_process(claim_type: str, verification_passed: bool):
    if not verification_passed:
        return "Rejected"

    if claim_type == "Cashless":
        return "Settled: Insurer paid hospital directly"
    else:
        return "Settled: Amount transferred to patient"


def appeal_process(review_passed: bool):
    if review_passed:
        return "Approved After Appeal"
    return "Final Rejection"


@app.get("/")
def home():
    return {"message": "Health Insurance API Running"}


@app.get("/claim")
def claim_process(
    policy_active: bool = True,
    hospital_in_network: bool = True,
    treatment_covered: bool = True,
    waiting_period_completed: bool = True,
    verification_passed: bool = True,
    review_passed: bool = True
):
    if not policy_active:
        return {"result": "Claim Rejected: Policy Not Active"}

    if hospital_in_network:
        claim_type = "Cashless"
        approval = pre_authorization(treatment_covered, waiting_period_completed)

        if approval == "Rejected":
            return {"result": "Cashless Denied – Switch to Reimbursement"}
    else:
        claim_type = "Reimbursement"

    settlement = settlement_process(claim_type, verification_passed)

    if settlement == "Rejected":
        settlement = appeal_process(review_passed)

    return {"result": settlement}
