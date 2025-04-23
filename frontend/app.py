from flask import Flask, request, render_template, jsonify
import requests
import polars as pl

# Config
RPI = 197.9     # UPDATE EVERY QUARTER
FLAT_TYPE_MAP = {
    "1 Room": 0, "2 Room": 1, "3 Room": 2,
    "4 Room": 3, "5 Room": 4, "Executive": 5, "Multi-Gen": 6
}
HDB_FEATURE_PATH = "backend/datasets/HDB_Features.csv"
PREDICT_URL = "https://hdb-price-service-530401088896.asia-southeast1.run.app/predict"
HEALTHCHECK_URL = "https://hdb-price-service-530401088896.asia-southeast1.run.app/health"

# ——— Service for Town/Floor Area Lookup Logic ———
class HDBLookupService:
    def __init__(self, csv_path, flat_map):
        self._df = pl.read_csv(csv_path)
        self._flat_map = flat_map

    def lookup(self, address: str, flat_type: str):
        if not address or flat_type not in self._flat_map:
            return None, None

        # Filter with Address
        df = self._df
        filtered = df[df['Address'].str.upper() == address.upper()]
        if filtered.empty:
            return None, None

        # Get Town and Floor Area from Filtered DF
        town = filtered['Town'].iloc[0].title()
        flat_type_area_map = eval(filtered['Flat_Type_Area_Map'].iloc[0])
        floor_area = flat_type_area_map.get(self._flat_map[flat_type])      # Get Floor Area based on Flat Type
        return town, floor_area

# Initialize Flask App
app = Flask(__name__)
hdb = HDBLookupService(HDB_FEATURE_PATH, FLAT_TYPE_MAP)

# ——— Health-Check on Startup ———
def health_check():
    try:
        r = requests.get(HEALTHCHECK_URL)
        print("Warm-up status:", r.status_code)
    except Exception as e:
        print("Warm-up error:", e)

# ——— Filter for Formating Price ———
@app.template_filter('format_price')
def format_price(value):
    try:
        return f"${float(value):,.0f}"
    except:
        return value
    
# ——— JSON Endpoint for Town/Floor Area Values ———
@app.route("/get_address_info")
def get_address_info():
    addr = request.args.get("address", "")
    flat_type = request.args.get("flat_type", "")
    town, area = hdb.lookup(addr, flat_type)
    return jsonify({"town": town, "floor_area": area})

# Define Route to Home Page
@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

# Define Route to Prediction Page
@app.route('/predict', methods=['POST'])
def predict():
    # Get Form Data
    try:
        flat_type       = request.form["Flat_Type"]
        storey          = int(request.form["Storey"])
        floor_area      = float(request.form["Floor_Area"])
        remaining_lease = float(request.form["Remaining_Lease"])
        address         = request.form["Address"]
        town            = request.form["Town"]
    except (KeyError, ValueError):
        return render_template("index.html", error="Please fill in all fields correctly"), 400

    # Prepare the data for API request
    payload = {
        "Flat_Type": flat_type,
        "Storey": storey,
        "Floor_Area": floor_area,
        "Remaining_Lease": remaining_lease,
        "RPI": RPI,
        "Address": address,
        "Town": town
    }

    # Send POST request to deployed API
    try:
        response = requests.post(PREDICT_URL, json=payload)
        response.raise_for_status()
        price = response.json().get("price")
        return render_template("prediction.html", price=price)
    except Exception:
        return render_template("index.html", error="Prediction service unavailable"), 502


# Define Route to About Me
@app.route('/about', methods=['GET'])
def about():
    return render_template('about.html')

if __name__ == '__main__':
    health_check()
    app.run(debug=True)