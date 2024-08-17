# idc-imaging

**Project Overview**

This project integrates with the Imaging Data Commons (IDC) API to facilitate the retrieval and filtering of medical imaging collections. It includes IDC collections retrieval, a Flask web application for dynamic filtering based on cancer type and image type, and DICOM metadata extraction from an AWS S3 bucket.

**No AWS Account Required:** 

The Image Data Commons (IDC)  dataset is publicly accessible, so an AWS account is not required.

## Installation and Usage

**Clone the repository:**

    ```bash
    git clone https://github.com/OpenBioResearch/idc-imaging.git
    cd idc-imaging
    ```

**Create a virtual environment (optional but recommended):**

    ```bash 
    python -m venv .venv
    source .venv/bin/activate  # git bash
    ```

**Install the Python dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

## Running the Python Scripts

To run the Python scripts, use the following commands:

```bash
python idc_collections_filter.py
python idc_metadata_match.py
python idc_nonduplicates_metadata.py
 ```
## Running the Flask App

To run the Flask app, follow these steps:

1. Navigate to the Flask app directory:
    ```bash
    cd flask_app
    ```

2. Run the app:
    ```bash
    python app.py
    ```

3. Open a web browser and go to [http://127.0.0.1:5000/](http://127.0.0.1:5000/) to see the filtering interface.

**Outputs**
    collections.json
    dicom_metadata.csv

**License:** 

Scripts use data from the National Cancer Institute Imaging Data Commons (IDC) Collections, which are distributed under the Creative Commons Attribution (CC BY) license.

