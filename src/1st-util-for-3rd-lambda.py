import boto3
from src.utils_write_to_ingestion_bucket import get_most_recent_table_data



def get_parquet_files(bucket, S3_client):
    """This function will:
            1) reads the process S3 bucket for the latest Parquet files
            2) returns those Parquet files
        Arg:
            bucket: a string for the name of the processed S3 bucket  
            S3_client: the boto3 S3 client
        Returns:
            A python list of Parquet files
    """ 

    # <timestamp> folder / parquet_files"    
    list_of_objs = S3_client.list_objects_v2(Bucket = bucket)

    # end of fri6june, Abdul carried out this:
    # S3_client.list_objects_v2(Bucket = bucket)
    # on the processed bucket and got the following in return:
#     {
#     “Contents”: [
#         {
#             “Key”: “2025-06-06 15:46:33.659888/date.parquet”,
#             “LastModified”: “2025-06-06T14:46:34+00:00”,
#             “ETag”: “\”91232da3713aee1ef4240e9cb16afd2a\“”,
#             “ChecksumAlgorithm”: [
#                 “CRC32"
#             ],
#             “ChecksumType”: “FULL_OBJECT”,
#             “Size”: 72673,
#             “StorageClass”: “STANDARD”
#         }
#     ],
#     “RequestCharged”: null,
#     “Prefix”: “”
# }


# ALSO: Niamh says this of the warehouse:
# "They're an RDS db: Feel free to label it warehouse though"
# I think this means that each warehouse (for each project team)
# is an RDS warehouse



    try:
        keys_list = [dict["Key"] for dict in response.get("Contents", [])]
        # ['design/2025-06-02_22-17-19-2513.json', 'design/2025-05-29_22-17-19-2513.json', etc]
        latest_table_key = sorted(keys_list)[
            -1
        ]  # 'design/2025-06-02_22-17-19-2513.json'
        response = S3_client.get_object(Bucket=bucket_name, Key=latest_table_key)
        data = response["Body"].read().decode("utf-8")
        data_as_py_list = json.loads(data)
        return data_as_py_list
    except ClientError as e: 
        return e
    

