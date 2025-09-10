import boto3

s3 = boto3.client('s3')
bucket_name = 'aivisual'
key = 'audit-data/store123/CRE_Group_Photo/2025-09-08/1757135049.jpg'

obj = s3.get_object(Bucket=bucket_name, Key=key)
image_bytes = obj['Body'].read()

rekognition = boto3.client('rekognition')
response = rekognition.detect_labels(Image={'Bytes': image_bytes}, MaxLabels=5)

print(response)
