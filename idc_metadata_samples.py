import pydicom
import boto3
import io
from collections import defaultdict

def extract_relevant_metadata(dicom_data):
    """Extracts relevant DICOM tags.

    Args:
        dicom_data: DICOM data as a file-like object.

    Returns:
        A dictionary containing the extracted metadata.
    """
    try:
        ds = pydicom.dcmread(dicom_data)
        metadata = {
            'Modality': ds.get('Modality', 'Unknown'),
            'Study Description': ds.get('StudyDescription', 'Unknown'),
            'Series Description': ds.get('SeriesDescription', 'Unknown'),
            'Manufacturer': ds.get('Manufacturer', 'Unknown'),
            'Image Type': ds.get('ImageType', 'Unknown')
        }

        # Additional tags of interest (if they exist)
        if 'PathologyNumber' in ds:  # Corrected check 
            metadata['Pathology Number'] = ds.PathologyNumber
        if 'ImageComments' in ds:
            metadata['Image Comments'] = tuple(ds.ImageComments)

        return metadata

    except Exception as e:
        print(f"Error processing DICOM data: {e}")
        return None


# S3 Configuration
bucket_name = 'idc-open-data-two'  
folder_prefixes = [
    'ffff0e20-57ac-46ec-88e1-285f218c8861/',
    '00043526-70a1-416f-a191-f1280a454597/' 
]
s3 = boto3.client('s3')

# Track metadata categories to ensure diversity
seen_metadata = defaultdict(set)

# Retrieve a maximum of five DICOM objects
object_count = 0

for folder_prefix in folder_prefixes:
    paginator = s3.get_paginator('list_objects_v2')
    page_iterator = paginator.paginate(Bucket=bucket_name, Prefix=folder_prefix)
    for page in page_iterator:
        if "Contents" in page:
            for obj in page['Contents']:
                if obj['Key'].endswith('.dcm'):
                    object_key = obj['Key']

                    # Fetch the DICOM object directly as a stream
                    response = s3.get_object(Bucket=bucket_name, Key=object_key)
                    dicom_bytes = response['Body'].read()

                    # Create a file-like object from the bytes
                    file_like_object = io.BytesIO(dicom_bytes)

                    # Process the file-like object
                    metadata = extract_relevant_metadata(file_like_object)
                    if metadata:
                        # Check for diversity before printing
                        is_diverse = False
                        for category, value in metadata.items():
                            if isinstance(value, pydicom.multival.MultiValue):
                                value = tuple(value) if all(isinstance(v, str) for v in value) else frozenset(value)
                            if value not in seen_metadata[category]:
                                is_diverse = True
                                seen_metadata[category].add(value)

                        if is_diverse:
                            print(f"\nMetadata for file (S3 Key): {object_key}")
                            for tag, value in metadata.items():
                                print(f"{tag}: {value}")

                            object_count += 1
                            if object_count >= 5:
                                break 
