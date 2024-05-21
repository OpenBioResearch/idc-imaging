"""
This module provides functions to extract and process DICOM metadata
from objects stored in an AWS S3 bucket. It focuses on retrieving a 
diverse set of metadata by avoiding duplicates based on specific 
tags. The module utilizes boto3 for S3 interaction and pydicom for 
DICOM parsing.
"""

import io
from collections import defaultdict
import boto3
import pydicom

# S3 Configuration
BUCKET_NAME = "idc-open-data-two"
s3 = boto3.client("s3")

# Track metadata categories to ensure diversity
seen_metadata = defaultdict(set)


def extract_relevant_metadata(dicom_data):
    """Extracts relevant DICOM tags and handles potential pydicom errors.

    Args:
        dicom_data: DICOM data as a file-like object.

    Returns:
        A dictionary containing the extracted metadata, or None if an error occurs.
    """
    try:
        ds = pydicom.dcmread(dicom_data)
        metadata = {
            "Modality": ds.get("Modality", "Unknown"),
            "StudyDescription": ds.get("StudyDescription", "Unknown"),
            "SeriesDescription": ds.get("SeriesDescription", "Unknown"),
            "Manufacturer": ds.get("Manufacturer", "Unknown"),
            "ImageType": ds.get("ImageType", "Unknown"),
        }

        # Additional tags if they exist
        for tag in ["PathologyNumber", "ImageComments"]:
            if tag in ds:
                metadata[tag] = ds[tag]  # Correctly assign the tag value

        return metadata

    # Catch specific pydicom parsing errors
    except (
        pydicom.errors.InvalidDicomError,
        KeyError,
        AttributeError,
    ) as e:  # Include AttributeError for potential missing tag issues
        print(f"Error parsing DICOM data: {e}")
        return None


def process_dicom_objects(prefix="", object_count=0):
    """Processes DICOM objects in an S3 bucket recursively.

    Args:
        prefix: The prefix to filter objects in the bucket.
        object_count: The current count of processed DICOM objects.

    Returns:
        The total count of processed DICOM objects.
    """
    paginator = s3.get_paginator("list_objects_v2")
    page_iterator = paginator.paginate(Bucket=BUCKET_NAME, Prefix=prefix)

    for page in page_iterator:
        if "Contents" in page:
            for obj in page["Contents"]:
                if obj["Key"].endswith(".dcm"):
                    object_key = obj["Key"]
                    response = s3.get_object(Bucket=BUCKET_NAME, Key=object_key)
                    dicom_bytes = response["Body"].read()
                    file_like_object = io.BytesIO(dicom_bytes)
                    metadata = extract_relevant_metadata(file_like_object)

                    if metadata:
                        is_diverse = False
                        for category, value in metadata.items():
                            if isinstance(value, pydicom.multival.MultiValue) and all(
                                isinstance(v, str) for v in value
                            ):
                                value = hash(tuple(value))
                            if value not in seen_metadata[category]:
                                is_diverse = True
                                seen_metadata[category].add(value)

                        if is_diverse:
                            print(f"\nMetadata for file (S3 Key): {object_key}")
                            for tag, value in metadata.items():
                                print(f"{tag}: {value}")

                            object_count += 1
                            if object_count >= 5:
                                return object_count

                elif obj["StorageClass"] == "DIRECTORY":
                    object_count = process_dicom_objects(obj["Key"], object_count)
                    if object_count >= 5:
                        return object_count

    return object_count


# Start processing from the root of the bucket (no prefix)
process_dicom_objects()
