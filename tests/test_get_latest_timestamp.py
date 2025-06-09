import pytest
from io import BytesIO
from unittest.mock import Mock
from src.First_util_for_3rd_lambda import get_latest_timestamp




def test_get_latest_timestamp_returns_expected_string():
    # arrange:
    mock_s3 = Mock()
    
    expected_timestamp = "2025-06-06 12:34:56"
    
    mock_response = {
        "Body": BytesIO(expected_timestamp.encode("utf-8"))
                    }
    
    mock_s3.get_object.return_value = mock_response

    # act:
    result_timestamp = get_latest_timestamp(mock_s3, "pretend-ingestion-bucket", "pretend-timestamp-key")

    # assert:
    assert result_timestamp == expected_timestamp
    mock_s3.get_object.assert_called_once_with(Bucket="pretend-ingestion-bucket", Key="pretend-timestamp-key")