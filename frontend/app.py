from flask import Flask, request, render_template, jsonify
import requests

# Initialize Flask app
app = Flask(__name__)

# Health Check to trigger API Warm Up when App Starts
def health_check():
    try:
        url = 'https://hdb-price-service-530401088896.asia-southeast1.run.app/health'
        response = requests.get(url)
        if response.status_code == 200:
            print("API is ready and warmed up.")
        else:
            print("Failed to connect to the API for warm-up.")
    except Exception as e:
        print(f"Error during health check: {e}")
health_check()

# Filter to Format Price with Commas
@app.template_filter('format_price')
def format_price(value):
    return f"${value:,.0f}"

# Define Route to Prediction Form
@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

# Define Route to Handle Form Submission 
@app.route('/predict', methods=['POST'])
def predict():
    # Get Form Data
    flat_type = request.form['Flat_Type']
    storey = request.form['Storey']
    floor_area = request.form['Floor_Area']
    remaining_lease = request.form['Remaining_Lease']
    cpi = request.form['CPI']
    address = request.form['Address']
    town = request.form['Town']

    # Prepare the data for API request
    data = {
        "Flat_Type": flat_type,
        "Storey": storey,
        "Floor_Area": floor_area,
        "Remaining_Lease": remaining_lease,
        "CPI": cpi,
        "Address": address,
        "Town": town
    }

    # Send POST request to your deployed API
    url = 'https://hdb-price-service-530401088896.asia-southeast1.run.app/predict'
    response = requests.post(url, json=data)

    # Handle the response
    if response.status_code == 200:
        result = response.json()
        return render_template('prediction.html', price=result['price'])
    else:
        return jsonify({'error': 'Failed to get prediction'}), 400

if __name__ == '__main__':
    app.run(debug=True)