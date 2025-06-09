import pytest
from unittest.mock import patch, Mock
from src.third_lambda import lambda_handler



@patch('src.third_lambda.make_SQL_queries_to_warehouse')
@patch('src.third_lambda.get_pandas_dataFrames')
@patch('src.third_lambda.boto3.client')
def test_lambda_handler_integrates_utility_functions_correctly(mock_boto_client, mock_get_dfs, mock_make_queries):
    # arrange

    # make mock EventBridge event:
    mock_event = {
        'detail': {
            'name': '11-processed-bucket'
                  }
                }

    mock_context = Mock()  # not actually used


    # mock a return value for function 
    # get_pandas_dataFrames()
    mocked_dataFrames_dict = {
        'dim_date': 'dim_date_df',
        'facts_sales_order': 'facts_df'
                             }
    
    mock_get_dfs.return_value = mocked_dataFrames_dict


    # Create fake s3 client
    mock_s3_client = Mock()
    mock_boto_client.return_value = mock_s3_client


    # act:
    lambda_handler(mock_event, mock_context)

    # assert:

    # boto3.client was called correctly
    mock_boto_client.assert_called_once_with('s3')

    # get_pandas_dataFrames was called with correct args
    mock_get_dfs.assert_called_once_with(
        '11-processed-bucket',
        '11-ingestion-bucket',
        mock_s3_client,
        '***timestamp***'
    )

    # test that function make_SQL_queries_to_warehouse() 
    # was called with the mock dictionary
    mock_make_queries.assert_called_once_with(mocked_dataFrames_dict)