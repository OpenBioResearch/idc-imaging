"""
This script interacts with the Imaging Data Commons (IDC) API to 
retrieve a list of collections and saves the output to a JSON file.
It makes a GET request to the IDC API's /collections endpoint and 
writes the response to collections.json for further analysis.
"""

import requests
import json

# Base URL for the IDC API
base_url = "https://api.imaging.datacommons.cancer.gov/v2"

endpoint = "/collections"
url = base_url + endpoint

try:
    response = requests.get(url)
    
    if response.status_code == 200:
        collections = response.json()
        print("Collections retrieved successfully. Writing to collections.json...")
        
        with open("collections.json", "w") as outfile:
            json.dump(collections, outfile, indent=4)
        
        print("Collections data written to collections.json")
    else:
        print(f"Failed to retrieve collections. Status code: {response.status_code}, Message: {response.text}")
except requests.exceptions.RequestException as e:
    print(f"An error occurred: {e}")
