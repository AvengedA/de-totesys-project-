from conn_to_db import conn_to_db
from utils import convert_data, read_table
from utils_write_to_ingestion_bucket import create_formatted_timestamp
import os
import json
from datetime import datetime
from botocore.exceptions import ClientError
from dotenv import load_dotenv
import logging


logger = logging.getLogger("MyLogger")

load_dotenv()
# bucket_name = os.environ["bucket_name"]


def get_data_from_db(tables, after_time, conn, read_table, convert_data):
    """
    This function:
        1) loops through a list of all of the types of
                table that exist in the ToteSys
                database, eg 'design'
        2) for each type of table, this function gets
                row data from the ToteSys database if
                that row data has been updated after
                a passed-in moment in time
        3) for each type of table, this function
                converts the row data into a jsonified
                python list of dictionaries
        4) for each type of table, this function
                appends the jsonified python list of
                dicts to a separate list (thus
                creating a list of jsonified python
                lists (plural) of dictionaries)

    Args:
        tables: a list of strings, each string
                representing the name of a table in the
                ToteSys database
        after_time: a timestamp representing a moment in
                time after which this function should
                look in each table in the ToteSys
                database for modified data
        conn: an instance of pg8000's Connection object
        read_table: a utility function that this function
                employs to connect to the ToteSys database
                to get updated data
        convert_data: a utility function that this function
                employs to convert row data that this
                function receives from the ToteSys database
                into a jsonified python list of dictionaries
                (where each dictionary contains data for one
                row of a table)

    Returns:
        a python list each of whose members is a jsonified
                python list of dictionaries

    """
    # read_table() returns, eg, {'sales': [{<data from one row>}, {<data from one row>}, etc]}

    data_list = []
    for table in tables:
        result = read_table(
            table, conn, after_time
        )  # {'design': [{<data from one row>}, {<data from one row>}, etc]}
        prefix = next(iter(result))  # "transactions"
        # data = result[prefix]
        jsonified_data = convert_data(
            result
        )  # jsonified version of {'design': [{<data from one row>}, {<data from one row>}, etc]}
        data_list.append(jsonified_data)
        # data_list is a python list each of whose members is a jsonified
        # version of this: {'design': [{<data from one row>}, {<data from one row>}, etc]}
    return data_list


def write_to_s3(data_list, s3_client, write_to_ingestion_bucket, bucket_name):
    """
    This function:
        1) loops through the passed-in python list,
                each of whose members is a
                jsonified python dictionary
        2) from each jsonified dictionary gets the
                name of the table
        3) looks in the ingestion bucket to determine
                whether one or more keys exist with
                the name of the table at the beginning
                (eg this function looks for one or
                more keys beginning with 'sales/')
        4) if no such key exists this means the
                jsonified python dictionary contains
                data concerning every row of the
                table in question, so this function
                creates an appropriate key
                (eg 'design/<*timestamp-here*>.json')
                and saves the whole table to the
                ingestion bucket
        5) if one or more such keys exist this means
                the table already exists in the
                ingestion bucket, so this function creates
                a new table that contains the updated rows
                and saves the new table to the ingestion
                bucket with a new timestamp.

    Args:
        data_list: a python list each of whose members
            is a jsonified python dictionary, eg a
            jsonified version of
            {'design': [{<data from one row>}, {<data from one row>}, etc]}.
            Each member jsonified dictionary relates
            to one table.
        s3_client: the boto3 client.
        write_to_ingestion_bucket: a utility function
            that this function employs to do the actual
            writing of rows of a table to the
            ingestion bucket.
    Returns:
        None

    """

    # for i in len(data_list):
    #     # i below is a jsonified python list of dictionaries,
    #     # so json.loads(i) is a python list of dictionaries, [{"sales": }, {}, {}, etc],
    #     # so list(json.loads(i).keys()) is a list of the keys in that:
    #     prefix = list(json.loads(i).keys())[data_list.index(i)] # the name of the table
    #     print(prefix)
    #     try:
    #         response = s3_client.list_objects_v2(Bucket=bucket_name, Prefix=prefix)
    #         if response["KeyCount"] > 0:
    #             write_to_ingestion_bucket(json.loads(data_list[i]), bucket_name, prefix)
    #         else:
    #             timestamped = create_formatted_timestamp()
    #             s3_client.put_object(Bucket=bucket_name, Key=f"{prefix}/{timestamped}.json", Body=json.dumps(data_list[i]))

    #     except ClientError as e:
    #         print(e)

    # write_to_ingestion_bucket() must take
    # i)   a jsonified python list of dicts. The list represents updated rows of a table
    # ii)  bucket name string
    # iii) table name string

    # data_list is, eg, [ jsonified {'design': [{<data from one row>}, {<data from one row>}, etc]}, etc].

    for member in data_list:
        table_data = json.loads(
            member
        )  # {'design': [{<data from one row>}, {<data from one row>}, etc]}
        prefix = list(table_data.keys())[0]  # the name of the table
        print(prefix)
        json_data = json.dumps(table_data[prefix])

        try:
            response = s3_client.list_objects_v2(Bucket=bucket_name, Prefix=prefix)
            if response["KeyCount"] > 0:
                write_to_ingestion_bucket(json_data, bucket_name, prefix)
            else:
                timestamped = create_formatted_timestamp()
                s3_client.put_object(
                    Bucket=bucket_name,
                    Key=f"{prefix}/{timestamped}.json",
                    Body=json_data,
                )

        except ClientError as e:
            logger.error("Unable to write to S3")
            return e
