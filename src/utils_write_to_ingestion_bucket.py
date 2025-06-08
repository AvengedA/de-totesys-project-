from datetime import datetime, timezone
import boto3
import json
from botocore.exceptions import ClientError
import logging


logger = logging.getLogger("Mylogger")


# /src/utils.py


# This is the main function:
def write_to_ingestion_bucket(data: dict | list | str, bucket: str, file_location: str):
    """
    This function:
    1. searches the ingestion bucket for all jsonified table lists
            that are stored under a key that begins with
            file_location and gets the most recent list
    2. converts the most recent list to a python list of dictionaries
    3. updates the appropriate rows in the python list
    4. creates a new json list to represent the updated table
    5. creates a timestamp string that will be part of the name of
            the key under which to store the jsonified list.
    6. stores in the ingestion bucket the new jsonified list that
            represents the updated table. The key for this new json
            list looks like design/2025-05-28_15-45-03.json, where
            'design' is the value of arg file_location and
            '2025-05-28_15-45-03' is a timestamp created in this
            function.
    7. calls the following utility functions (all of which are in this file) 
        to carry out its role:
        i)   get_most_recent_table_data()
        ii)  create_formatted_timestamp()
        iii) update_rows_in_table()
        iv)  save_updated_table_to_S3()
            

    args:
        data: a jsonified list of dictionaries that represents
            rows of a table. Each dictionary contains the data
            of one updated row of the table in the ToteSys database.
        bucket_name: a string, the name of the ingestion S3 bucket.
        file_location: a string, the first part of the key under
            which this function will store in the bucket the json
            list that an updated table. It is also the name of the
            table that has been changed in the ToteSys database.
            Examples: 'design' and 'sales'.

    returns:
        None

    """

    # 1) Get the most recent object that holds a json list that
    # represents a table:
    try:
        client = boto3.client("s3")
        latest_table = get_most_recent_table_data(file_location, client, bucket)
        # latest_table is a jsonified python list of dictionaries
        # 2) Convert json to python:
        if isinstance(data, str):
            updated_rows = json.loads(data)  # python list like [ {}, {}, {}, etc ]
        else:
            updated_rows = data

    except ClientError as e:
        # log error to CloudWatch here
        logger.error("Issue occured while retrieving the most recent table data")

        return e

    try:
        # 3) Insert those updated rows into the retrieved jsonified list of
        # dictionaries that represents the table.
        # updated_table below is a python list of dictionaries:
        updated_table = update_rows_in_table(updated_rows, latest_table, file_location)

        # convert updated_table into json:
        updates_table_json = json.dumps(updated_table)

        # 4) Create a formatted timestamp:
        formatted_ts = create_formatted_timestamp()

        # 5) Make a string for the key under which to store the json list
        # that represents the updated table. Include the formatted
        # timestamp as part of the key:
        new_key = file_location + "/" + formatted_ts + ".json"
    except ClientError as e:
        # log error to CloudWatch here
        logger.error("Ubable to update the S3 bucket with updated rows")

        return e

    try:
        # 6) Store the json list that represents the updated table into
        # in the ingestion bucket under the newly created key:
        save_updated_table_to_S3(updates_table_json, client, new_key, bucket)
    except ClientError as e:
        # log error to CloudWatch here
        logger.error("Unable to save the data to the s3 bucket")

        return e

    return


def get_most_recent_table_data(
    file_location: str, S3_client: boto3.client, bucket_name: str
):
    """
    This function:
        1) gets a list of every jsonified list of
                dictionaries in the bucket if their
                keys begin with file_location. The
                list will be a python list
        2) sorts the list according to time,
                descending
        3) gets the most recent list

    Returns:
        The most recent python list

    Args:
        file_location: a string that looks like
        'design'
        S3_client: the boto3 S3 bucket client
    bucket_name: a string for the bucket name
    """
    try:
        response = S3_client.list_objects_v2(Bucket=bucket_name, Prefix=file_location)
    except ClientError as e:
        return e

    # {
    # 'ResponseMetadata': { ...},
    #     ...
    # 'Contents': [
    #     {
    #     'Key': 'design/xxx.json',
    #     [{...}, {...}, {...}, etc]
    #     },
    #     {
    #     'Key': 'design/yyy.json',
    #     ...
    #     }
    #             ]
    # }
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


def create_formatted_timestamp():
    """
    This function:
        1) creates a timestamp string formatted like this:
            'YYYY-MM-DD_HH-MM-SS_MS'
    Returns:
        The formatted timestamp string
    Args:
        A timestamp that is a datetime object created by
        the datetime module's now() method
    """
    now_dt_object = datetime.now(timezone.utc)
    formatted_ts = now_dt_object.strftime("%Y-%m-%d_%H-%M-%S")
    return formatted_ts


def update_rows_in_table(
    rows_list: list[dict | list], table_list: list[dict[str:object]], file_location: str
):
    """
    This function:
        1) updates the appropriate rows in a
                python list that represesnts a table
    Returns:
        a python list that represents the updated table
    Args:
        rows_list: a python list of dictionaries, each
        dictionary representing a row that contains
        updated data.
        table_list: a python list of dictionaries that
        represents a table
    """

    # file_location is eg 'design'
    key_to_search = file_location + "_id"
    for dct in rows_list:
        for row_dct in table_list:
            if dct[key_to_search] == row_dct[key_to_search]:
                # dict['design_id'] is a dictionary
                # table_list['design_id'] is a dictionary

                # replace the row in table_list
                ind = table_list.index(row_dct)
                table_list[ind] = dct
    return table_list


def save_updated_table_to_S3(
    updated_table: str, S3_client: boto3.client, new_key: str, bucket: str
):
    """
    This function:
        1. takes the updated table and stores
            it in the S3 bucket
    Args:
        updated_table: a jsonified python list of
            dictionaries.
        S3_client: the boto3 client for S3.
        new_key: a string that is the key under
            which the updated table will be
            saved in the S3 bucket.
        bucket: a string that is the name of the
            S3 bucket
    """
    try:
        S3_client.put_object(Bucket=bucket, Key=new_key, Body=updated_table)
    except ClientError as e:
        return e
