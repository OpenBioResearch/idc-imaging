import boto3

# Specify the bucket name and region
bucket_name = 'idc-open-data'  # Replace with your actual bucket name
region = 'us-east-1'          # Replace with the correct region if needed

# Set up the S3 client
s3 = boto3.client('s3')

# Verification step
try:
    response = s3.head_bucket(Bucket=bucket_name)
    print(f"Bucket verification successful: {response}")
except s3.exceptions.NoSuchBucket:
    print(f"Error: Bucket '{bucket_name}' does not exist or incorrect permissions.")
except s3.exceptions.ClientError as e:
    # Handle other potential client errors (access denied, etc.)
    print(f"Error accessing bucket: {e}") 
