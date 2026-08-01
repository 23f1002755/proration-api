from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request Model
class ChargeRequest(BaseModel):
    old_price: float
    new_price: float
    days_remaining: int
    days_in_actual_month: int
    spec: str

# Response Model
class ChargeResponse(BaseModel):
    charge: float

@app.get("/")
def root():
    return {"message": "Proration API Running"}

@app.post("/charge", response_model=ChargeResponse)
def calculate(req: ChargeRequest):

    difference = req.new_price - req.old_price

    if req.spec == "v1":
        charge = difference * (req.days_remaining / 30)

    elif req.spec == "v2":
        charge = difference * (
            req.days_remaining / req.days_in_actual_month
        )

    else:
        charge = 0

    return {
        "charge": round(charge, 2)
    }