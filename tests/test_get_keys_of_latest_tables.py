import pytest
from unittest.mock import Mock
from src.First_util_for_3rd_lambda import get_keys_of_latest_tables





def test_get_keys_of_latest_tables_returns_correct_keys():
    # Arrange:
    mock_s3_client = Mock()
    mock_response = {
        "Contents": [
            {"Key": "2025-06-06 00:00:00/date.parquet"},
            {"Key": "2025-06-06 00:00:00/sales_order.parquet"}
                    ]
                    }
    
    mock_s3_client.list_objects_v2.return_value = mock_response

    proc_bucket = "test-bucket"
    ts_prefix = "2025-06-06 12:34:56"

    expected_list = [
        "2025-06-06 00:00:00/date.parquet",
        "2025-06-06 00:00:00/sales_order.parquet"
                     ]

    # act:
    result_list = get_keys_of_latest_tables(
        mock_s3_client, 
        proc_bucket, 
        ts_prefix
                                            )

    # assert
    assert result_list == expected_list
    
    mock_s3_client.list_objects_v2.assert_called_once_with(
        Bucket=proc_bucket, 
        Prefix=ts_prefix
                                                          )

