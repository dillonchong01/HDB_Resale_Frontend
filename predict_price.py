import numpy as np
import pandas as pd
import lightgbm as lgb
from pathlib import Path
from typing import Dict, Any
from data_transformation.feature_engineering import authenticate, get_distance, nearest_loc
from data_transformation.coordinate_api_caller import get_lat_long


# Config
MODEL_PATH = Path("models/lgbm_model.txt")
HDB_FEATURE_PATH = Path("datasets/HDB_Features.csv")
MRT_COORD_PATH = Path("datasets/coordinates/MRT_LatLong.csv")
MALL_COORD_PATH = Path("datasets/coordinates/Mall_LatLong.csv")
SCHOOL_COORD_PATH = Path("datasets/coordinates/School_LatLong.csv")
MATURE_ESTATES = [
    "ANG MO KIO", "BEDOK", "BISHAN", "BUKIT MERAH", "BUKIT TIMAH", "CENTRAL", "CLEMENTI",
    "GEYLANG", "KALLANG/WHAMPOA", "MARINE PARADE", "PASIR RIS", "QUEENSTOWN", "SERANGOON",
    "TAMPINES", "TOA PAYOH"
]

# Get Location Features
def get_location_features(address: str) -> Dict[str, Any]:
    """
    Determines location-based features based on user input of address

    Args:
        address (str): Full address string

    Returns:
        Dictionary with keys: Distance_MRT, Distance_Mall, Within_1km_of_Pri, Mature
    """
    # If HDB already exists in our HDB Feature Dataset, extract location values from there
    if HDB_FEATURE_PATH.exists():
        hdb_features = pd.read_csv(HDB_FEATURE_PATH)
        matched = hdb_features[hdb_features["Address"] == address.strip().upper()]
        if not matched.empty:
            return {
                "Distance_MRT": matched.iloc[0]["Distance_MRT"],
                "Distance_Mall": matched.iloc[0]["Distance_Mall"],
                "Within_1km_of_Pri": matched.iloc[0]["Within_1km_of_Pri"]
            }
    api_token = authenticate()
    df = get_lat_long([address], api_token)
    hdb_lat = df['Lat'][0]
    hdb_long = df['Long'][0]

    mrts = pd.read_csv(MRT_COORD_PATH)
    malls = pd.read_csv(MALL_COORD_PATH)
    schools = pd.read_csv(SCHOOL_COORD_PATH)

    # Get Distance to Nearest MRT
    _, mrt_lat, mrt_long, _ = nearest_loc(hdb_lat, hdb_long, mrts)
    mrt_dist = get_distance(hdb_lat, hdb_long, mrt_lat, mrt_long, api_token)
    # Get Distance to Nearest Mall
    _, mall_lat, mall_long, _ = nearest_loc(hdb_lat, hdb_long, malls)
    mall_dist = get_distance(hdb_lat, hdb_long, mall_lat, mall_long, api_token)
    # Return True if there is oversubscribed Primary School within 1km
    _, _, _, school_1km = nearest_loc(hdb_lat, hdb_long, schools)

    return {
        "Distance_MRT": mrt_dist,
        "Distance_Mall": mall_dist,
        "Within_1km_of_Pri": school_1km
    }

def predict_price(input_features: Dict[str, Any]) -> float:
    """
    Predicts the resale price of an HDB flat using a trained LightGBM model.

    Args:
        input_features (Dict[str, Any]): Dictionary containing the following keys:
            - 'Flat_Type': Categorical type of the flat (encoded as integer)
            - 'Storey': Floor level of the unit
            - 'Floor_Area': Size of the unit in square meters
            - 'Remaining_Lease': Remaining lease in years
            - 'CPI': Consumer Price Index at the time of transaction
            - 'Address': Full address string used to derive location features
            - 'Mature': Town name (used to check if estate is in mature list)

    Returns:
        float: Predicted resale price in SGD (rounded to 2 decimal places)
    """
    if not MODEL_PATH.exists():
        raise FileNotFoundError(f"Trained model not found at {MODEL_PATH}")
    
    # Load Model
    model = lgb.Booster(model_file=str(MODEL_PATH))

    # Get Location Features
    location_features = get_location_features(input_features["Address"])

    features = {
        "Flat_Type": input_features["Flat_Type"],
        "Storey": input_features["Storey"],
        "Floor_Area": input_features["Floor_Area"],
        "Remaining_Lease": input_features["Remaining_Lease"],
        "CPI": input_features["CPI"],
        "Distance_MRT": location_features["Distance_MRT"],
        "Distance_Mall": location_features["Distance_Mall"],
        "Within_1km_of_Pri": location_features["Within_1km_of_Pri"],
        "Mature": input_features["Town"].strip().upper() in MATURE_ESTATES
    }

    # Prepare Input and Predict Price
    input_df = pd.DataFrame([features])
    pred_log = model.predict(input_df, num_iteration=model.best_iteration)
    pred_price = np.expm1(pred_log[0])

    return int(round(pred_price / 1000.0) * 1000)