from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from predict_price import get_location_features, predict_price

# Create FastAPI Instance
task_app = FastAPI(
    title="HDB Price Prediction API",
    description="Predict resale prices of HDB flats using LightGBM",
    version="1.0.0",
)

# Define Request Schema using Pydantic BaseModel
class PredictRequest(BaseModel):
    Flat_Type: int          # Categorical code for flat type
    Storey: int             # Floor of the unit
    Floor_Area: float       # Size of the unit in square meters
    Remaining_Lease: float  # Remaining lease years
    CPI: float              # Consumer Price Index at prediction time
    Address: str            # Full address string
    Town: str               # Town name, used for 'Mature' flag (True/False)

# Define Response Schema
class PredictResponse(BaseModel):
    price: float         # Predicted resale price in SGD

# 6. Health-Check Endpoint to keep Container Warm
async def health_check():
    """
    Simple route to check service status.
    Front-end can call this on page load to trigger model loading.
    """
    return {"status": "ok"}

# 7. Prediction endpoint
@task_app.post("/predict", response_model=PredictResponse, tags=["Prediction"])
async def predict_endpoint(request: PredictRequest):
    """
    Handle prediction requests:
    1. Validate input JSON against PredictRequest model.
    2. Compute location features (Distance to MRT/Mall, Pri School within 1km).
    3. Call the LightGBM model to predict log-price and convert to SGD.
    4. Return the rounded price.
    """
    try:
        # Convert Pydantic model to dict for processing
        input_data = request.model_dump()

        # 1) Compute location-based features
        location_feats = get_location_features(input_data["Address"])

        # 2) Aggregate all features for prediction
        features = {
            "Flat_Type": input_data["Flat_Type"],
            "Storey": input_data["Storey"],
            "Floor_Area": input_data["Floor_Area"],
            "Remaining_Lease": input_data["Remaining_Lease"],
            "CPI": input_data["CPI"],
            # The location function returns keys Distance_MRT, Distance_Mall, Within_1km_of_Pri
            **location_feats,
            # 'Mature' flag based on Town membership
            "Mature": input_data["Town"].strip().upper() in [
                "ANG MO KIO","BEDOK","BISHAN","BUKIT MERAH","BUKIT TIMAH",
                "CENTRAL","CLEMENTI","GEYLANG","KALLANG/WHAMPOA","MARINE PARADE",
                "PASIR RIS","QUEENSTOWN","SERANGOON","TAMPINES","TOA PAYOH"
            ]
        }

        # 3) Get prediction from your model
        predicted_price = predict_price(features)

        # 4) Return the result wrapped in PredictResponse
        return PredictResponse(price=predicted_price)

    except Exception as e:
        # If anything goes wrong, return an HTTP 400 with the error message
        raise HTTPException(status_code=400, detail=str(e))