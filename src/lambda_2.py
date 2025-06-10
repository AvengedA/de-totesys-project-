from utils_2 import *
import boto3
import datetime
import logging


def lambda_handler(event, context):
    """
    -Get json from the s3 (read_from_s3), read event to find out what
    -Convert the json into python (convert_json_to_python)
    -For each table, read table name then apply correct transformation function
    -Convert into parquet
    -Upload to s3
    """

    """
    example event:
    {
        "Records": [
        {
            "eventVersion": "2.0",
            "eventSource": "aws:s3",
            "awsRegion": "us-east-1",
            "eventTime": "1970-01-01T00:00:00.000Z",
            "eventName": "ObjectCreated:Put",
            "userIdentity": {
                "principalId": "EXAMPLE"
            },
            "requestParameters": {
                "sourceIPAddress": "127.0.0.1"
            },
            "responseElements": {
                "x-amz-request-id": "EXAMPLE123456789",
                "x-amz-id-2": "EXAMPLE123/5678abcdefghijklambdaisawesome/mnopqrstuvwxyzABCDEFGH"
            },
            "s3": {
                "s3SchemaVersion": "1.0",
                "configurationId": "testConfigRule",
                "bucket": {
                    "name": "example-bucket",
                    "ownerIdentity": {
                        "principalId": "EXAMPLE"
                    },
                    "arn": "arn:aws:s3:::example-bucket"
                },
                "object": {
                    "key": "test%2Fkey",
                    "size": 1024,
                    "eTag": "0123456789abcdef0123456789abcdef",
                    "sequencer": "0A1B2C3D4E5F678901"
                }
            }
        }
        ]
    }
    So we want to go for event['Records'][0]['s3']['object']['key']
    """
    # So we want to go for event['Records'][0]['s3']['object']['key']
    logger = logging.getLogger(__name__)
    logger.setLevel("INFO")
    s3_client = boto3.client("s3")
    ingestion_bucket_name = event["Records"][0]["s3"]["bucket"]["name"]
    ingestion_key = event["Records"][0]["s3"]["object"]["key"]
    # sales_order/2025-06-04_09-21-32.json
    processed_bucket_name = "11-processed-bucket"
    timestamp = datetime.datetime.now()

    # Check if the processed bucket is empty, and if so generate date.parquet file
    boto_list_processed_objects = s3_client.list_objects_v2(
        Bucket=processed_bucket_name
    )

    print(boto_list_processed_objects)

    if boto_list_processed_objects["KeyCount"] == 0:
        logger.info("Detected empty processing bucket, creating date.parquet...")
        date_python = transform_to_dim_date()
        date_parquet = convert_into_parquet(date_python)
        date_key = f"{timestamp}/date.parquet"
        upload_to_s3(s3_client, processed_bucket_name, date_key, date_parquet)
        logger.info(f"date.parquet created successfully at {date_key}")

    ingestion_json = read_from_s3(s3_client, ingestion_bucket_name, ingestion_key)
    # [{...}, {...}, {...}]

    split_key = ingestion_key.split("/")
    # ['sales_order', '2025-06-04_09-21-32.json']
    table_name = split_key[0]
    file_name = split_key[1]

    processed_key = f"{timestamp}/{table_name}.parquet"

    ingestion_python = convert_json_to_python(ingestion_json)

    if table_name == "sales_order":
        logger.info(f"Processing {table_name}...")
        processed_python = transform_to_star_schema_fact_table(
            table_name, ingestion_python
        )

    elif table_name == "staff":
        logger.info(f"Processing {table_name}...")
        # get data from the department table with the same timestamped file name
        dept_json = read_from_s3(
            s3_client, ingestion_bucket_name, f"department/{file_name}"
        )
        dept_python = convert_json_to_python(dept_json)
        processed_python = transform_to_dim_staff(ingestion_python, dept_python)

    elif table_name == "address":
        logger.info(f"Processing {table_name}...")
        processed_python = transform_to_dim_location(ingestion_python)

    elif table_name == "design":
        logger.info(f"Processing {table_name}...")
        processed_python = transform_to_dim_design(ingestion_python)

    elif table_name == "counterparty":
        logger.info(f"Processing {table_name}...")
        # get data from the address table with the same timestamped file name
        address_json = read_from_s3(
            s3_client, ingestion_bucket_name, f"address/{file_name}"
        )
        address_python = convert_json_to_python(address_json)
        processed_python = transform_to_dim_counterparty(
            ingestion_python, address_python
        )

    elif table_name == "currency":
        logger.info(f"Processing {table_name}...")
        processed_python = transform_to_dim_currency(ingestion_python)

    else:
        logger.error("invalid table name")

    logger.info(f"Converting {table_name} into Dataframe in Parquet...")
    parquet = convert_into_parquet(processed_python)

    logger.info(f"Uploading {table_name} into {processed_bucket_name}...")
    upload_to_s3(s3_client, processed_bucket_name, processed_key, parquet)
    logger.info(f"Successfully uploaded {processed_key} into {processed_bucket_name}")
