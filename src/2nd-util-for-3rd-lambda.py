import pandas as pd
import pyarrow
import pg8000

from src.conn_to_db import conn_to_db, close_db

def make_SQL_queries_to_warehouse(parq_dict: dict[str:pd.DataFrame]):
    """This function:
            1) receives several pandas DataFrames in a python dictionary
            2) converts each DataFrame into an SQL query
            3) uses the query to put the table data into the posgresql warehouse

        Args:
            parq_dict: this will be a python dictionary of pandas DataFrames
                    that looks like this: {sales_fact: <pandas DataFrame>}
            conn_util: the utility function that returns an instance of 
                    a pg8000 Connection object
            
        return:
            None
            
    """
    list_of_queries = [] # will contain list of query strings
    for key, value in parq_dict.items():
        list_of_queries = convert_dataframe_to_SQL_query_string(key, value) # key = table name, 
                                                                             # value = pandas dataframe
        

    put_table_data_in_warehouse(list_of_queries)
    




    # the parquet files in the S3 processed bucket will most likely 
    # have the table name in their name, eg sales_fact.parquet,
    # so the first utility function of the third lambda must 
    # create parq_dict, where each key is the name of the table



    # {
    # "dim_table_xxxxx": <A parquet file>, 
    # "dim_table_yyyy": <A parquet file>,
    # "dim_table_aa": <A parquet file>, 
    # "dim_table_bbb": <A parquet file>,
    # "dim_table_ccc": <A parquet file>, 
    # "dim_table_ddd: <A parquet file>,
    # "facts_table_eee": <A parquet file>,
    # ...
    # }


def convert_dataframe_to_SQL_query_string(table_name, dataFrame):
    """
    This function:
        1) reads the data in a pandas DataFrame
        2) creates an SQL query string that includes the data
              in the dataframe, one SQL query string for each column
        3) puts the SQL query strings into a python list                
    
    Args:
        table_name: a string representing the name of a table
        dataFrame: a pandas DataFrame containing the data for a table            
    
    Returns:
        A python list of strings, where each string is an SQL query
    """

    # Load the Parquet file:
    df = pd.read_parquet(dataFrame)

    # Convert each row to an INSERT statement
    insert_statements = []
    for _, row in df.iterrows():
        columns = ', '.join(df.columns)
    values = ', '.join(f"'{str(v)}'" if v is not None else 'NULL' for v in row)
    sql = f"INSERT INTO {table_name} ({columns}) VALUES ({values});"
    insert_statements.append(sql)

    return insert_statements





def put_table_data_in_warehouse(query_list):
    """
    This function:
        1) opens a connection to the warehouse database
        2) loops through a list of SQL query strings and makes
                the query to the warehouse database
        2) closes the connection to the warehouse database
    
    Args:
        query_list: a list of strings, where each string is an SQL  
            query to be made to the warehouse database
        conn_util: the utility function that makes the connection to
            the warehouse database (and returns an instance of a 
            pg8000 Connection object)
    
    Returns:
        None
    """
     
    conn = conn_to_db('xxwarehouse name herexxx')
    for query_string in query_list:
        conn.run(query_string)
    close_db()        
        