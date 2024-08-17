from flask import Flask, render_template, request, jsonify
import requests

app = Flask(__name__)

# Fetch collections from IDC API
def fetch_collections():
    url = "https://api.imaging.datacommons.cancer.gov/v2/collections"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()['collections']
    else:
        raise Exception(f"Failed to retrieve collections: {response.status_code}")

# Fetch collections data dynamically
collections_data = fetch_collections()

# Get unique cancer types and image types
cancer_types = sorted(set(collection['cancer_type'] for collection in collections_data))
image_types = sorted(set(it for collection in collections_data for it in collection['image_types'].split(', ')))

@app.route('/')
def index():
    return render_template('index.html', cancer_types=cancer_types, image_types=image_types)

@app.route('/filter', methods=['POST'])
def filter_collections():
    selected_cancer_type = request.form['cancer_type']
    selected_image_type = request.form['image_type']
    
    filtered_collections = [
        collection for collection in collections_data 
        if selected_cancer_type in collection.get('cancer_type', '') 
        and selected_image_type in collection.get('image_types', '')
    ]
    
    return jsonify(filtered_collections)

if __name__ == '__main__':
    app.run(debug=True)