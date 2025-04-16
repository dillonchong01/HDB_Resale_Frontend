import requests
import json
import pandas as pd

# Authenticate OneMaps API
def authenticate():
    url = "https://www.onemap.gov.sg/api/auth/post/getToken"
    payload = {"email": "dillonchong01@gmail.com",
               "password": "T0126546BClash"
               }
    response = requests.request("POST", url, json=payload)
    
# Obtain Latitude and Longitude from OneMaps
def getLatLong(locations):
    lat_long_df = []
    # Get Lat - Long for each Unique Address
    count = 1
    for location in locations:
        print(count)
        count += 1
        try:
            response = requests.get(f"https://www.onemap.gov.sg/api/common/elastic/search?searchVal={location}&returnGeom=Y&getAddrDetails=N")
            response.raise_for_status()
            data = json.loads(response.content).get("results", [])

            if data:
                latitude, longitude = data[0]["LATITUDE"], data[0]["LONGITUDE"]
            else:
                latitude, longitude = 0, 0
            
            lat_long_df.append((location, latitude, longitude))

        except Exception as e:
            print(f"Request failed for '{location}': {e}")
            lat_long_df.append((location, 0, 0))

    # Create Dataframe of Address, Lat, Long
    lat_long_df = pd.DataFrame(lat_long_df, columns=['Address', 'Lat', 'Long'])

    return lat_long_df


stations = ["Jurong East MRT", "Bukit Batok MRT", "Bukit Gombak MRT", "Choa Chu Kang MRT", "Yew Tee MRT",
            "Kranji MRT", "Marsiling MRT", "Woodlands MRT", "Admiralty MRT", "Sembawang MRT",
            "Canberra MRT", "Yishun MRT", "Khatib MRT", "Yio Chu Kang MRT", "Ang Mo Kio MRT",
            "Bishan MRT", "Braddell MRT", "Toa Payoh MRT", "Novena MRT", "Newton MRT",
            "Orchard MRT", "Somerset MRT", "Dhoby Ghaut MRT", "City Hall MRT", "Raffles Place MRT",
            "Marina Bay MRT", "Marina South Pier MRT", "Changi Airport MRT", "Expo MRT", "Pasir Ris MRT",
            "Tampines MRT", "Simei MRT", "Tanah Merah MRT", "Bedok MRT", "Kembangan MRT",
            "Eunos MRT", "Paya Lebar MRT", "Aljunied MRT", "Kallang MRT", "Lavender MRT",
            "Bugis MRT", "Tanjong Pagar MRT", "Outram Park MRT", "Tiong Bahru MRT", "Redhill MRT",
            "Queenstown MRT", "Commonwealth MRT", "Buona Vista MRT", "Dover MRT", "Clementi MRT",
            "Chinese Garden MRT", "Lakeside MRT", "Boon Lay MRT", "Pioneer MRT", "Joo Koon MRT",
            "Gul Circle MRT", "Tuas Crescent MRT", "Tuas West Road MRT", "Tuas Link MRT", "HarbourFront MRT",
            "Chinatown MRT", "Clarke Quay MRT", "Little India MRT", "Farrer Park MRT", "Boon Keng MRT",
            "Potong Pasir MRT", "Woodleigh MRT", "Serangoon MRT", "Kovan MRT", "Hougang MRT",
            "Buangkok MRT", "Sengkang MRT", "Punggol MRT", "Punggol Coast MRT", "Bras Basah MRT",
            "Esplanade MRT", "Promenade MRT", "Nicoll Highway MRT", "Stadium MRT", "Mountbatten MRT",
            "Dakota MRT", "MacPherson MRT", "Tai Seng MRT", "Bartley MRT", "Lorong Chuan MRT",
            "Marymount MRT", "Caldecott MRT", "Botanic Gardens MRT", "Farrer Road MRT", "Holland Village MRT",
            "one-north MRT", "Kent Ridge MRT", "Haw Par Villa MRT", "Pasir Panjang MRT", "Labrador Park MRT",
            "Telok Blangah MRT", "Bukit Panjang MRT", "Cashew MRT", "Hillview MRT", "Hume MRT",
            "Beauty World MRT", "King Albert Park MRT", "Sixth Avenue MRT", "Tan Kah Kee MRT", "Stevens MRT",
            "Rochor MRT", "Bayfront MRT", "Downtown MRT", "Telok Ayer MRT", "Fort Canning MRT",
            "Bencoolen MRT", "Jalan Besar MRT", "Bendemeer MRT", "Geylang Bahru MRT", "Mattar MRT",
            "Ubi MRT", "Kaki Bukit MRT", "Bedok North MRT", "Bedok Reservoir MRT", "Tampines West MRT",
            "Tampines East MRT", "Upper Changi MRT", "Woodlands North MRT", "Woodlands South MRT", "Springleaf MRT",
            "Lentor MRT", "Mayflower MRT", "Bright Hill MRT", "Upper Thomson MRT", "Napier MRT",
            "Orchard Boulevard MRT", "Great World MRT", "Havelock MRT", "Maxwell MRT", "Shenton Way MRT",
            "Gardens by the Bay MRT", "Tanjong Rhu MRT", "Katong Park MRT", "Tanjong Katong MRT", "Marine Parade MRT",
            "Marine Terrace MRT", "Siglap MRT", "Bayshore MRT"
            ]

malls = ["100 AM", "111 Somerset", "313@Somerset", "AMK Hub", "Anchorpoint",
         "Aperia Mall", "Bedok Mall", "Bugis Junction", "Bugis+", "Bukit Panjang Plaza",
         "Capitol Singapore", "Causeway Point", "Century Square", "Changi City Point", "Chijmes",
         "Chinatown Point", "Cineleisure Orchard", "City Square Mall", "Clarke Quay", "Clarke Quay Central",
         "Compass One", "Cross Street Exchange", "Downtown East", "East Village", "Eastpoint Mall",
         "Far East Plaza", "Forum The Shopping Mall", "Funan Mall", "Great World", "Greenwich V",
         "HarbourFront Centre", "Heartland Mall Kovan", "Hillion Mall", "HillV2", "Hougang 1",
         "Hougang Mall", "i12 Katong", "Icon Village", "IMM", "ION Orchard",
         "JCube", "Jem", "Jewel Changi Airport", "Jubilee Square", "Junction 10",
         "Junction 8", "Junction 9", "Jurong Point", "Kallang Wave Mall", "Kap Mall",
         "Katong V", "Kinex", "Lot One", "Mandarin Gallery", "Marina Square",
         "Millenia Walk", "NEX", "Ngee Ann City", "Northpoint City", "One Raffles Place",
         "Orchard Central", "Orchard Gateway", "Pacific Plaza", "Palais Renaissance", "Paragon",
         "Parkway Parade", "Paya Lebar Quarter", "Paya Lebar Square", "Plaza Singapura", "Raffles City",
         "Republic Plaza", "Rivervale Mall", "Robertson Walk", "Scotts Square", "Shaw Centre",
         "Shoppes at Marina Bay Sands", "Singpost Centre", "Square 2", "Sun Plaza", "Suntec City",
         "Tampines 1", "Tampines Mall", "Tanglin Mall", "Tanglin Place", "The Cathay",
         "The Centrepoint", "The Clementi Mall", "The Poiz Centre", "The Seletar Mall", "The Star Vista",
         "The Woodleigh Mall", "Thomson Plaza", "Tiong Bahru Plaza", "UE Square", "United Square",
         "Valley Point", "Velocity @ Novena Square", "VivoCity", "Waterway Point", "West Coast Plaza",
         "West Mall", "Westgate", "Wheelock Place", "White Sands", "Wisma Atria",
         "YewTee Point"
         ]

if __name__ == "__main__":
    authenticate()
    # df = pd.read_csv("datasets/Cleaned_Resale_Data.csv")

    # # Get Lat/Long of Resale HDB
    # hdb_locations = df["Address"].unique()
    # hdb_lat_long_df = getLatLong(hdb_locations)
    # hdb_lat_long_df.to_csv("datasets/HDB_LatLong.csv", index=False)

    # # Merge into DF
    # df = pd.merge(df, hdb_lat_long_df, on='Address', how='left')
    # df.to_csv("datasets/Cleaned_Resale_Data_with_LatLong.csv", index=False)

    # # Get Lat/Long of MRTs
    # mrt_lat_long_df = getLatLong(stations)
    # mrt_lat_long_df.to_csv("datasets/MRT_LatLong.csv", index=False)

    # Get Lat/Long of Malls
    # mall_lat_long_df = getLatLong(malls)
    # mall_lat_long_df.to_csv("datasets/Mall_LatLong.csv", index=False)

    # # Get Lat/Long of Schools
    # school_lat_long_df = getLatLong(schools)
    # school_lat_long_df.to_csv("datasets/School_LatLong.csv", index=False)