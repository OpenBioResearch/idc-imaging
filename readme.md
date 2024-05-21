# DICOM Metadata Extractor for IDC Dataset Exploration

This Python script is designed for exploring the metadata of the publicly available Imaging Data Commons (IDC) dataset, which is stored within the AWS S3 bucket arn:aws:s3:::idc-open-data. It effiiently extracts five (configurable) unique DICOM metadata entries from the IDC's Open Dataset, providing researchers with insights into the variety and distribution of medical imaging data available for their research.

**No AWS Account Required:** This IDC dataset is publicly accessible, so you can use this script without needing an AWS account.

**Prerequisites:** Ensure you have the following installed:
   - Python (3.6 or higher)
   - boto3 (AWS SDK for Python)
   - pydicom

**License:** https://fairsharing.org/FAIRsharing.0b5a1d

