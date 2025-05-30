import boto3
from src.utils_write_to_ingestion_bucket import write_to_ingestion_bucket
from datetime import datetime
import json

def lambda_handler(data, prefix):
     s3_client = boto3.client("s3")
     bucket_name = "11-ingestion-bucket"

     response = s3_client.list_objects_v2(Bucket=bucket_name, Prefix=prefix)

     if response["KeyCount"] > 0:
        write_to_ingestion_bucket(json.loads(data), bucket_name, prefix)
        return True
     else:
          timestamped = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
          s3_client.put_object(Bucket=bucket_name, Key=f"{prefix}/{timestamped}.json", Body=json.dumps(data))
          return False