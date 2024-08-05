"""
This script extracts metadata from a public AWS S3 bucket and enables matching
to DICOM images at NCI's Imaging Data Commons (IDC). 
"""

import io
from collections import defaultdict
import boto3
import pydicom
import csv
import botocore
import re

# S3 Configuration for the public bucket "idc-open-data-two"
BUCKET_NAME = "idc-open-data-two"
s3 = boto3.client(
    "s3", config=botocore.client.Config(signature_version=botocore.UNSIGNED)
)

# Track metadata categories to ensure diversity
seen_metadata = defaultdict(set)

def convert_to_hashable(value):
    """Convert DICOM values to hashable types."""
    if isinstance(value, pydicom.multival.MultiValue) or isinstance(value, list):
        return tuple(value)  # Keep as tuple of original values
    return value

def extract_collection_name(patient_id):
    """Extract collection name by removing numeric part from patient ID."""
    return re.sub(r'\d+', '', patient_id).rstrip('-')

def validate_study_date(date):
    """Validate and correct study date if it seems unreasonable."""
    try:
        year = int(date[:4])
        if year < 1900 or year > 2100:  
            return "Unknown"
        return date
    except ValueError:
        return "Unknown"

def extract_relevant_metadata(dicom_data, object_key):
    """Extracts relevant DICOM tags and handles potential errors."""
    try:
        ds = pydicom.dcmread(dicom_data)
        patient_id = ds.get("PatientID", "Unknown")
        metadata = {
            "S3Key": object_key,  
            "Modality": ds.get("Modality", "Unknown"),
            "StudyDescription": ds.get("StudyDescription", "Unknown"),
            "SeriesDescription": ds.get("SeriesDescription", "Unknown"),
            "Manufacturer": ds.get("Manufacturer", "Unknown"),
            "ImageType": convert_to_hashable(ds.get("ImageType", ["Unknown"])),  # Convert to tuple to be hashable
            "PatientID": patient_id,
            "CollectionName": extract_collection_name(patient_id),  
            "StudyDate": validate_study_date(ds.get("StudyDate", "Unknown")),
            "SeriesNumber": ds.get("SeriesNumber", "Unknown"),
            "InstanceNumber": ds.get("InstanceNumber", "Unknown"),
            "BodyPartExamined": ds.get("BodyPartExamined", "Unknown"),
            "SliceThickness": ds.get("SliceThickness", "Unknown")
        }

        additional_tags = {
            "PathologyNumber": (0x0008, 0x1064),
            "ImageComments": "ImageComments",
        }

        for tag_name, tag_identifier in additional_tags.items():
            if tag_identifier in ds:
                metadata[tag_name] = ds[tag_identifier]

        return metadata

    except (
        pydicom.errors.InvalidDicomError,
        KeyError,
        AttributeError,
    ) as e:
        print(f"Error parsing DICOM data: {e}")
        return None

def write_metadata_to_csv(metadata_list, filename="dicom_metadata.csv"):
    """Writes the extracted metadata to a CSV file."""
    if not metadata_list:
        return

    fieldnames = list(metadata_list[0].keys())

    with open(filename, "w", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(metadata_list)

def process_dicom_objects(prefix=""):
    """Processes DICOM objects in the public S3 bucket."""
    metadata_list = []
    object_count = 0

    paginator = s3.get_paginator("list_objects_v2")
    page_iterator = paginator.paginate(Bucket=BUCKET_NAME, Prefix=prefix)

    for page in page_iterator:
        if "Contents" in page:
            for obj in page["Contents"]:
                if obj["Key"].endswith(".dcm"):
                    object_key = obj["Key"]
                    try:
                        response = s3.get_object(Bucket=BUCKET_NAME, Key=object_key)
                    except botocore.exceptions.ClientError as e:
                        if e.response["Error"]["Code"] == "NoSuchKey":
                            print(f"\nError: The object {object_key} does not exist.")
                        else:
                            raise e
                    else:
                        dicom_bytes = response["Body"].read()
                        file_like_object = io.BytesIO(dicom_bytes)
                        metadata = extract_relevant_metadata(file_like_object, object_key)

                        if metadata:
                            is_diverse = False
                            for category, value in metadata.items():
                                value = convert_to_hashable(value)
                                print(f"Category: {category}, Value: {value}")
                                if value not in seen_metadata[category]:
                                    is_diverse = True
                                    seen_metadata[category].add(value)

                            if is_diverse:
                                print(f"\nMetadata for file (S3 Key): {object_key}")
                                for tag, value in metadata.items():
                                    if isinstance(value, list):
                                        value = [str(v) for v in value]
                                        print(f"{tag}: {value}")
                                    else:
                                        print(f"{tag}: {value}")
                                metadata_list.append(metadata.copy())
                                object_count += 1

                                if object_count >= 5:
                                    write_metadata_to_csv(metadata_list)
                                    return

                # Progress indicator to show that the script is working
                print(f"Processing: {obj['Key']}", end="\r")

                if obj["StorageClass"] == "DIRECTORY":
                    object_count = process_dicom_objects(obj["Key"])
                    if object_count >= 5:
                        break

    write_metadata_to_csv(metadata_list)

# Start processing from the root of the bucket (no prefix)
process_dicom_objects()
