import boto3

# Specify the bucket name and region
bucket_name = 'idc-open-data' 
region = 'us-east-1'         

# Set up the S3 client
s3 = boto3.client('s3')

# Verification step (keep this from the previous script)
try:
    response = s3.head_bucket(Bucket=bucket_name)
    print(f"Bucket verification successful: {response}")
except s3.exceptions.NoSuchBucket:
    print(f"Error: Bucket '{bucket_name}' does not exist or incorrect permissions.")
except s3.exceptions.ClientError as e:
    print(f"Error accessing bucket: {e}") 

# Retrieve a single object
try:
    paginator = s3.get_paginator('list_objects_v2')
    page_iterator = paginator.paginate(Bucket=bucket_name)

    for page in page_iterator:
        if "Contents" in page:
            first_object_key = page['Contents'][0]['Key']  # Get the key of the first object
            response = s3.head_object(Bucket=bucket_name, Key=first_object_key)
            print(f"Metadata of the first object ({first_object_key}): {response}")
            break  # Exit after retrieving the first object
except s3.exceptions.ClientError as e:
    print(f"Error retrieving object: {e}")
