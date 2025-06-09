import pandas as pd
from io import BytesIO
import pyarrow


# at end of friday 6 june 25 I made
# this assumption:
# each file will be saved in the processed
# bucket under this kind of key:
# “2025-06-06 15:46:33.659888/date.parquet”,
# “2025-06-06 15:51:33.123456/sales_order.parquet”, etc



# ******************************************************************************
# NOTE: The third lambda employs these two utility functions:
# 1) get_pandas_dataFrames(), declared here
# 2) make_SQL_queries_to_warehouse() declared in file 
#   second_util_for_3rd_lambda.py.
#
# get_pandas_dataFrames() employs three other utility functions, also declared 
# in this file. These are:
# 1) get_latest_timestamp()
# 2) get_keys_of_latest_tables()
# 3) get_pq_files()
# ******************************************************************************

def get_pandas_dataFrames(proc_bucket, ing_bucket, S3_client, current_ts_key):
    """ This function will:
            1) read the process S3 bucket for the latest Parquet files
            2) returns a dictionary containing pandas dataframes 
                created from those Parquet files
            3) achieve 1) and 2) above by calling the following 
                utility functions (all declared bellow):
                i)   get_latest_timestamp()
                ii)  get_keys_of_latest_tables() 
                iii) get_pq_files() (which employs utility function
                    return_long_table_name()) 
        Args:
            proc_bucket: a string for the name of the processed S3 bucket  
            ing_bucket:  a string for the name of the ingestion S3 bucket  
            S3_client: the boto3 S3 client
            current_ts_y: a string for the key of the current timestamp
                in the ingestion bucket (will be '***timestamp***')

        Returns:
            A python dictionary that looks like this:
                {
                'dim_date': <pandas dataFrame here>, 
                . . . , 
                'facts_sales_order': <pandas dataFrame here>
                }, where each key is the name of a table in the 
                warehouse database
    """ 
    
    # get latest timestamp string
    # "1900-01-01 00:00:00": 
    latest_ts_hh_mm_ss = get_latest_timestamp(S3_client, ing_bucket, current_ts_key)

    # get a list of the keys for 
    # the latest tables in the 
    # processed bucket:
    list_of_keys = get_keys_of_latest_tables(S3_client, proc_bucket, latest_ts_hh_mm_ss)

    # get the actual objects in 
    # the processed bucket 
    # associated with the keys 
    # in the list just created,
    # convert them into pandas
    # dataFrames and put them in 
    # a list:
    dict_of_dataFrames = get_pq_files(S3_client, list_of_keys, proc_bucket)

    # dict_of_dataFrames will look 
    # like this:
    # {
    # 'dim_date': dim_table.parquet, 
    # ... , 
    # 'facts_sales_order': facts_sales_order.parquet
    # }, where each key is the name of a table
    # in the warehouse database.

    return dict_of_dataFrames









def get_keys_of_latest_tables(S3_client, proc_bucket, ts_prefix):
    """
    This function:
        looks for all keys in the processed bucket that 
            contain string ts_prefix at the beginning
            and returns them

    Args:
        S3_client: a boto3 S3_client
        proc_bucket: a string that is the name of the processed bucket
        ts: a string for the latest timestamp, which the ingestion
            bucket contains

    Returns:
        a python list of strings, each string being the key
        for the latest files in the processed bucket

            """
    response = S3_client.list_objects_v2(
        Bucket=proc_bucket, 
        Prefix=ts_prefix
                                        )
    
    list_of_dicts = response["Contents"]

    return [  dict['Key']   for dict in list_of_dicts  ] # list of strings that are names of the S3 keys








def get_pq_files(S3_client, key_list, proc_bckt):
    """
    This function:
        gets an object from the processed bucket
            for each key in the passed-in list
            and converts the object into a pandas
            dataFrame

    Args:
        S3_client: a boto3 s3 client
        key_list: a python list of strings, each string being 
            a key for an object in the processed bucket 
        proc_bckt: a string for the name of the processed bucket

    Returns:
        A list of pandas dataFrames, each dataFrame representing 
            a Parquet file that came from the processed bucket,
            each Parquet file corresponding to a key in the list
            of keys passed in.
    """    

    # fact_sales_order
# dim_staff
# dim_location
# dim_design
# dim_date
# dim_currency
# dim_counterparty

    # make a template of the 
    # dictionary to return:
    dict_of_dataFrames = {
        'fact_sales_order': None,
        'dim_staff': None,
        'dim_location': None,
        'dim_design': None,
        'dim_date': None,
        'dim_currency': None,
        'dim_counterparty': None,
                         }

# loop through the passed-in list of keys:
    for table_key in key_list:
        # get the short table name from the key:
        # 'xxxxxx/date.parquet'
        table_name = table_key.split('/')[-1].split('.')[0] # eg 'date'
        # knowing the short table name 
        # get the proper (long) table 
        # name (for example 
        # return_long_table_name()
        # converts 'date' to 'dim_date'):
        long_table_name = return_long_table_name(table_name)
        # get the object in the processed 
        # bucket according to its key and 
        # convert it to a pandas dataFrame:
        response = S3_client.get_object(Key=table_key, Bucket=proc_bckt)
        pq_bytes_file = response['Body'].read()
        parquet_buffer = BytesIO(pq_bytes_file)
        dataFrame = pd.read_parquet(parquet_buffer, engine='pyarrow')
        # store the dataFrame in the 
        # dictionary that this function
        # will return:
        dict_of_dataFrames[long_table_name] = dataFrame

    return dict_of_dataFrames



def return_long_table_name(short_name):
    """
    This function:
        1) is employed by utility function get_pq_files()
        2) is a lookup table
        3) returns a long table name for the short 
            table name passed in
    Args:
        short_name: a string that is the short form
            of the name of a table in the warehouse
            database, eg 'date' for 'dim_date' or
            'sales_order' for 'facts_sales_order'            
    Returns:
        the long table name version of a short 
        table name.            
    """
    lookup_dict = {
        'sales_order': 'facts_sales_order',
        'staff': 'dim_staff',
        'location': 'dim_location',
        'design': 'dim_design',
        'date': 'dim_date',
        'currency': 'dim_currency',
        'counterparty': 'dim_counterparty',
                     }
    return lookup_dict[short_name]





def get_latest_timestamp(S3_client, bckt, key):
    """
    This function:
        1) gets the latest timestamp from the ingestion bucket
    Args:
        S3_client: the boto3 s3 client
        bckt: a string for the name of the bucket
        key: the key of the object that is the timestamp
            string (which the ingestion bucket holds)
    Returns:
        A string that is the timestamp
        

    """
    response = S3_client.get_object(Bucket=bckt, Key=key)
    return response["Body"].read().decode("utf-8")
    
