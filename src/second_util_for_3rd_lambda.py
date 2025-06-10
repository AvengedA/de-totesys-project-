import pandas as pd

from conn_to_db import conn_to_db, close_db


# ************************************************************************
# NOTE: this file declares function make_SQL_queries_to_warehouse(),
# which is the 2nd utility function that the third lambda will employ.
# make_SQL_queries_to_warehouse() itself employs these two utility
# functions (both declared below):
# 1) convert_dataframe_to_SQL_query_string() and
# 2) put_table_data_in_warehouse()
# ************************************************************************


def make_SQL_queries_to_warehouse(parq_dict: dict[str : pd.DataFrame]):
    """This function:
        1) receives several pandas DataFrames in a python dictionary
        2) converts each DataFrame into an SQL query
        3) uses the query to put the table data into the posgresql warehouse
        4) employs these two function:
            a) convert_dataframe_to_SQL_query_string()
            b) put_table_data_in_warehouse()

    Args:
        parq_dict: this will be a python dictionary of pandas DataFrames
                that looks like this: {sales_fact: <pandas DataFrame>, etc}
        conn_util: the utility function that returns an instance of
                a pg8000 Connection object

    return:
        None

    """
    list_of_queries = []  # will contain list of query strings
    for key, value in parq_dict.items():
        if value != None:
            list_of_queries = convert_dataframe_to_SQL_query_string(
                key, value
            )  # key = table name,
            # value = pandas dataframe

    put_table_data_in_warehouse(list_of_queries)


def convert_dataframe_to_SQL_query_string(table_name, dataFrame):
    """
    This function:
        1) reads the data in a pandas dataFrame
        2) creates an SQL query string that includes the data
              in the dataframe, one SQL query string for each column
        3) puts the SQL query strings into a python list

    Args:
        table_name: a string representing the name of a table
        dataFrame: a pandas DataFrame containing the data for a table

    Returns:
        A python list of strings, where each string is an SQL query
    """

    # make a list in which the
    # sql query strings will
    # reside:
    sql_query_strs_list = []

    # Convert each row to an
    # INSERT sql query string
    # and put all strings in
    # the list. iterrows() is
    # a pandas method that
    # loops through a DataFrame
    # row by row and for each row
    # returns the index of the
    # row and the row itself as
    # a pandas Series (WON'T
    # WORK without index
    # below, so don't remove!!!):
    for index, row in dataFrame.iterrows():
        columns = ", ".join(dataFrame.columns)
        values = ", ".join(f"'{str(v)}'" if v is not None else "NULL" for v in row)
        sql_query_str = f"INSERT INTO {table_name} ({columns}) VALUES ({values});"
        sql_query_strs_list.append(sql_query_str)

    return sql_query_strs_list


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

    # make the connection to the warehouse
    # (a posgresql database):
    conn = conn_to_db("xxwarehouse name herexxx")

    # send sql queries to the warehouse
    # database:
    for query_string in query_list:
        conn.run(query_string)

    # close the connection to
    # the warehouse:
    close_db()
