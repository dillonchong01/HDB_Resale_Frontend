import pandas as pd
import numpy as np
import time
import requests
from tqdm import tqdm
from haversine import haversine, Unit

# Returns Coordinate of Nearest Location (Mall/MRT/School) from HDB
def nearest_loc(hdb_lat, hdb_lon, loc_df):
    hdb_point = np.array([hdb_lat, hdb_lon])

    loc_points = loc_df[["Lat", "Long"]].to_numpy()
    dists = np.array([
        haversine(hdb_point, loc, unit=Unit.KILOMETERS) for loc in loc_points
    ])
    min_idx = np.argmin(dists)
    within_1km = None if dists[min_idx] == 0 else dists[min_idx] <= 1
    return loc_df.iloc[min_idx]["Address"], loc_df.iloc[min_idx]["Lat"], loc_df.iloc[min_idx]["Long"], within_1km


# Authenticate OneMaps API
def authenticate():
    url = "https://www.onemap.gov.sg/api/auth/post/getToken"
    payload = {"email": "dillonchong01@gmail.com",
               "password": "T0126546BClash"
               }
    try:
        response = requests.request("POST", url, json=payload)
        response.raise_for_status()
        token = response.json().get('access_token')
        return token
    except requests.exceptions.RequestException as e:
        print(f"Authentication failed: {e}")
        return None
    
# Obtain Distance between HDB and MRT/Mall/School from OneMaps
def getDistance(hdb_lat, hdb_long, loc_lat, loc_long):
    try:
        response = requests.get("https://www.onemap.gov.sg/api/public/routingsvc/route",
                                params={"start": f"{hdb_lat},{hdb_long}",
                                        "end": f"{loc_lat},{loc_long}",
                                        "routeType": "walk"},
                                headers={"Authorization": f"{api_token}"}
                                )

        response.raise_for_status()
        return response.json().get("route_summary", {}).get("total_distance")
            
    except Exception as e:
        return None

# Engineer Distance Features (MRT, Mall, School)
def engineer_distance_features(hdbs, mrts, malls, schools):
    # Initialize Lists to Store Results
    nearest_mrt, mrt_distances = [], []
    nearest_mall, mall_distances = [], []
    nearest_school, within_1km = [], []

    for hdb_lat, hdb_long in tqdm(zip(hdbs["Lat"], hdbs["Long"]), total=len(hdbs)):
        mrt, mrt_lat, mrt_long, _ = nearest_loc(hdb_lat, hdb_long, mrts)
        mrt_dist = getDistance(hdb_lat, hdb_long, mrt_lat, mrt_long)
        mall, mall_lat, mall_long, _ = nearest_loc(hdb_lat, hdb_long, malls)
        mall_dist = getDistance(hdb_lat, hdb_long, mall_lat, mall_long)
        school, _, _, school_1km = nearest_loc(hdb_lat, hdb_long, schools)

        nearest_mrt.append(mrt)
        mrt_distances.append(mrt_dist)
        nearest_mall.append(mall)
        mall_distances.append(mall_dist)
        nearest_school.append(school)
        within_1km.append(school_1km)
    
    # Add New Columns to HDBs Dataframe
    hdbs["Nearest_MRT"] = nearest_mrt
    hdbs["Distance_MRT"] = mrt_distances
    hdbs["Nearest_Mall"] = nearest_mall
    hdbs["Distance_Mall"] = mall_distances
    hdbs["Nearest_Pri_Sch"] = nearest_school
    hdbs["Within_1km_of_Pri"] = within_1km

    return hdbs

if __name__ == "__main__":
    # Authenticate and get API Token
    api_token = authenticate()
    if api_token is None:
        print("Authentication failed. Exiting...")
        exit(1)

    # Read CSVs
    df = pd.read_csv("datasets/Cleaned_Resale_Data.csv")
    mrts = pd.read_csv("datasets/coordinates/MRT_LatLong.csv")
    malls = pd.read_csv("datasets/coordinates/Mall_LatLong.csv")
    schools = pd.read_csv("datasets/coordinates/School_LatLong.csv")
    hdbs = pd.read_csv("datasets/coordinates/HDB_LatLong.csv")
    cpi = pd.read_csv("datasets/CPI.csv")

    hdbs = hdbs.iloc[3001:4001]

    # # Get HDB Distance Features
    hdbs = engineer_distance_features(hdbs, mrts, malls, schools)
    hdbs.to_csv("datasets/HDB_Features.csv", index=False, mode='a', header=False)


    # # Join Engineered Features with Main Dataframe
    # final_df = pd.merge(df, hdbs[["Address", "Distance_MRT", "Distance_Mall", "Within_1km_of_Pri"]], on='Address', how='left')
    # final_df = pd.merge(final_df, cpi, on=['Year', 'Month'], how='left')

    # # Classify Towns into Mature/Non-Mature Estate
    # mature_estates = [
    #     "Ang Mo Kio", "Bedok", "Bishan", "Bukit Merah", "Bukit Timah", "Central", "Clementi",
    #     "Geylang", "Kallang/Whampoa", "Marine Parade", "Pasir Ris", "Queenstown", "Serangoon",
    #     "Tampines", "Toa Payoh"
    #     ] 
    # final_df["Mature"] = final_df["Town"].isin(mature_estates)
    
    # final_df.drop(columns=['Year', 'Month', 'Town', 'Address'], inplace=True)

    # final_df.to_csv("datasets/Final_Resale_Data.csv", index=False)