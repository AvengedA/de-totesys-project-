import boto3
from First_util_for_3rd_lambda import get_pandas_dataFrames
from second_util_for_3rd_lambda import make_SQL_queries_to_warehouse


# ***********#***********#***********#***********#***********#***********
# This lambda function employs two utility functions:
# get_pandas_dataFrames() and make_SQL_queries_to_warehouse
# ***********#***********#***********#***********#***********#***********


# use context for logging, performance checks, or debugging.
def lambda_handler(event, context):
    s3_client = boto3.client("s3")

    """
    This function:
        1) has the overall task of 
            i) reading Parquet files in the processed 
            bucket that were put there at a time 
            indicated by the latest time stamp 
            string held in the ingestion bucket, 
            ii) creating SQL query strings that will 
            insert updated table data into tables in 
            the data warehouse (all the rows of a 
            table will be inserted, some or all of
            the rows of a table having been updated),
            iii) connecting to the warehouse,
            iv) making the SQL queries actually  
            put those data in the warehouse and
            v) closing the connection to the warehouse

        2) integrates the following utility functions
            to carry out its task:
                get_parquet_files()
                make_SQL_queries_to_warehouse()
    
    Args:
        event: the event that triggers this lambda
        context: metadata

    Returns:
        None                            
    """

    ingestion_bckt = "11-ingestion-bucket"
    processed_bckt = event["detail"]["name"]

    # create a dictionary that contains the
    # pandas files relating to tables in
    # the warehouse dictionary:
    dataFrames_dict = get_pandas_dataFrames(
        processed_bckt, ingestion_bckt, s3_client, "***timestamp***"
    )

    # dataFrames_dict will look
    # like this:
    # {
    # 'dim_date': dim_table.parquet,
    # ... ,
    # 'facts_sales_order': facts_sales_order.parquet
    # }, where each key is the name of a table
    # in the warehouse database.

    # get the data out of each of the
    # files in the dictionary above and
    # put the data in them into the
    # warehouse database:
    make_SQL_queries_to_warehouse(dataFrames_dict)
