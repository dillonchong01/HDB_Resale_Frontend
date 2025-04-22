from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from predict_price import predict_price

# Create FastAPI Instance
task_app = FastAPI(
    title="HDB Price Prediction API",
    description="Predict resale prices of HDB flats using LightGBM",
    version="1.0.0",
)

# Define Request Schema using Pydantic BaseModel
class PredictRequest(BaseModel):
    Flat_Type: str          # Flat type str
    Storey: int             # Floor of the unit
    Floor_Area: float       # Size of the unit in square meters
    Remaining_Lease: float  # Remaining lease years
    RPI: float              # Consumer Price Index at prediction time
    Address: str            # Full address string
    Town: str               # Town name, used for 'Mature' flag (True/False)

# Define Response Schema
class PredictResponse(BaseModel):
    price: float         # Predicted resale price in SGD

# 6. Health-Check Endpoint to keep Container Warm
@task_app.get("/health")
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

        # Get prediction from your model
        predicted_price = predict_price(input_data)

        # Return the result wrapped in PredictResponse
        return PredictResponse(price=predicted_price)

    except Exception as e:
        # If anything goes wrong, return an HTTP 400 with the error message
        raise HTTPException(status_code=400, detail=str(e))