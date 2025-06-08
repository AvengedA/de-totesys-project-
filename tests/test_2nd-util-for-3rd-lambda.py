import pytest
import pandas as pd
from unittest.mock import patch, Mock
from src.second_util_for_3rd_lambda import (
    put_table_data_in_warehouse,
    convert_dataframe_to_SQL_query_string,
                                           )


# @pytest.mark.skip(reason="Skipping this test to perform only the previous tests")


def test_function_convert_dataframe_to_SQL_query_string_returns_correct_list_of_query_strings():
    # Act:
    # make a pythonised pandas DataFrame
    # of the kind the function under test 
    # will create in its body:
    mock_python_pandas_df = pd.DataFrame([
        {'id': 1, 'name': 'Abdul', 'team': 1},
        {'id': 2, 'name': 'Neill', 'team': 1},
        {'id': 3, 'name': 'Mukund', 'team': 1}
    ])

    # the query string list that the
    # function under test is expected 
    # to return:
    expected_sql_qrs_list = [
        "INSERT INTO table_here (id, name, team) VALUES ('1', 'Abdul', '1');",
        "INSERT INTO table_here (id, name, team) VALUES ('2', 'Neill', '1');",
        "INSERT INTO table_here (id, name, team) VALUES ('3', 'Mukund', '1');"
                            ]

    # make a pretend pandas.read_parquet() method
    # and give it a return value:
    mock_pandas_rd_pq = Mock(return_value=mock_python_pandas_df)

    # set the patch to function pd.read_parquet():
    with patch('src.second_util_for_3rd_lambda.pd.read_parquet', mock_pandas_rd_pq):
        result_sql_qrs_list = convert_dataframe_to_SQL_query_string('table_here', 'parquet_file_here')

    assert result_sql_qrs_list == expected_sql_qrs_list
    mock_pandas_rd_pq.assert_called_once_with('parquet_file_here')







def test_put_table_data_in_warehouse_executes_all_queries():
    # Arrange
    query_list = [
        "INSERT INTO table1 VALUES (1, 'a')",
        "UPDATE table2 SET col = 'b' WHERE id = 1"
    ]
    
    # mock the Connection object
    mock_conn = Mock()
    
    # make a patch for conn_to_db() and
    # set the patch's return value to 
    # mock COnnection object mock_conn;
    # also patch close_db():
    with patch('src.second_util_for_3rd_lambda.conn_to_db', return_value=mock_conn) as mock_conn_to_db, \
         patch('src.second_util_for_3rd_lambda.close_db') as mock_close_db:
        
        # Act
        put_table_data_in_warehouse(query_list)
        
        # Assert
        mock_conn_to_db.assert_called_once_with('xxwarehouse name herexxx')
        assert mock_conn.run.call_count == len(query_list)
        mock_close_db.assert_called_once()





