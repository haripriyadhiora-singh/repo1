from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List

app = FastAPI(title="FastAPI Card Management System")

# ---------------------------
# Pydantic Model
# ---------------------------
class Details(BaseModel):
    name: str
    age: int
    aadhar: str
    legacy_id: int
    card_type: str
    status: str


# ---------------------------
# In-memory Database
# ---------------------------
details_db: List[Details] = [
    Details(
        name="Ravi Kumar",
        age=30,
        aadhar="1234-5678-9012",
        legacy_id=101,
        card_type="Debit",
        status="Active"
    ),
    Details(
        name="Priya Sharma",
        age=28,
        aadhar="2345-6789-0123",
        legacy_id=102,
        card_type="Credit",
        status="Inactive"
    ),
    Details(
        name="Amit Verma",
        age=35,
        aadhar="3456-7890-1234",
        legacy_id=103,
        card_type="Debit",
        status="Active"
    )
]

# ---------------------------
# Routes
# ---------------------------

@app.get("/")
def welcome():
    return {"message": "Welcome to the FastAPI Card Management System"}


@app.get("/details", response_model=List[Details])
def get_all_details():
    return details_db


@app.post("/details", response_model=Details)
def add_details(detail: Details):
    details_db.append(detail)
    return detail


@app.put("/details/{legacy_id}", response_model=Details)
def update_details(legacy_id: int, updated_detail: Details):
    for index, detail in enumerate(details_db):
        if detail.legacy_id == legacy_id:
            details_db[index] = updated_detail
            return updated_detail

    raise HTTPException(status_code=404, detail="Record not found")


@app.delete("/details/{legacy_id}")
def delete_details(legacy_id: int):
    for index, detail in enumerate(details_db):
        if detail.legacy_id == legacy_id:
            details_db.pop(index)
            return {"message": "Record deleted successfully"}

    raise HTTPException(status_code=404, detail="Record not found")
