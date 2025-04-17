from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Literal
from predict_price import predict_price

app = FastAPI(title="HDB Resale Price Prediction API")


class HDBRequest(BaseModel):
    Flat_Type: int
    Storey: int
    Floor_Area: float
    Remaining_Lease: float
    CPI: float
    Address: str
    Mature: str  # User enters town name (e.g. "BEDOK")


class PredictionResponse(BaseModel):
    predicted_price: int


@app.post("/predict", response_model=PredictionResponse)
def predict(hdb: HDBRequest):
    try:
        user_input = hdb
        price = predict_price(user_input)
        return {"predicted_price": price}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))