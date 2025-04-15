import requests
import pandas as pd

# Import HDB Resale Price Dataframe
def get_HDB_resale_dataframe():
    url = "https://data.gov.sg/api/action/datastore_search"
    limit = 100
    offset = 0
    hdbResale = []

    # Using API, extract the results of HDB Resale Price Dataset, 100 at a time
    while True:
        response = requests.get(
            url,
            params={
                "resource_id": "d_8b84c4ee58e3cfc0ece0d773c8ca6abc",
                "limit": limit,
                "offset": offset
            }
        )
        data = response.json()
        records = data["result"]["records"]
        hdbResale.extend(data["result"]["records"])

        # Stop if we've reached the end
        if len(records) < limit:
            break

        offset += limit
        print(offset)

    return hdbResale

# Clean Data
def cleanData(df):
    # Combine Block and Street Name to get Address
    df["Address"] = df["block"].astype(str) + " " + df["street_name"].astype(str)
    
    # Take Lower Bound of Storey Range
    df["Storey"] = pd.to_numeric(df["storey_range"].str[:2], errors="coerce")

    # Convert 'month' column to Year and Month
    df["Year"] = pd.to_numeric(df["month"].str[:4], errors="coerce")
    df["Month"] = pd.to_numeric(df["month"].str[5:], errors="coerce")

    # Express Remaining Lease in Years
    df["Remaining Lease"] = df["remaining_lease"].apply(
        lambda x: round(int(x.split()[0]) + (int(x.split()[2]) if "month" in x else 0)/12, 3)
        )
    
    # Select Relevant Columns
    df = df[["Year", "Month", "flat_type", "Address", "Storey", "floor_area_sqm", "Remaining Lease", "resale_price"]]
    df = df.rename(columns={
        "flat_type": "Flat Type",
        "floor_area_sqm": "Floor Area",
        "resale_price": "Price"
    })

    return df

if __name__ == "__main__":
    df = pd.read_csv("datasets/Resale.csv")
    df = cleanData(df)
    df.to_csv("datasets/Cleaned_Resale_Data.csv", index=False)