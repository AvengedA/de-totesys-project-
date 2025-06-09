import pytest
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
from io import BytesIO
from unittest.mock import Mock, patch
from moto import mock_aws
import json
import boto3
from src.First_util_for_3rd_lambda import get_pq_files






@pytest.fixture(scope="function")
def S3_setup():
    with mock_aws():
        S3_client = boto3.client("s3", region_name="eu-west-2")
        S3_client.create_bucket(
            Bucket="11-processed-bucket",
            CreateBucketConfiguration={"LocationConstraint": "eu-west-2"},
                               )

        mock_list_of_keys = ['2025-06-06 12:34:56/date.parquet', '2025-06-06 12:34:56/sales_xxx.parquet']

    # for the date table:        
        data_1 = {
    'name': ['Abdul', 'Neill', 'Mukund'],
    'team': [1, 1, 1]
                    }
    # for the staff table:        
        data_2 = {
    'name': ['Abdul', 'Neill', 'Mukund'],
    'team': [1, 1, 1]
                    }

        table_1 = pa.table(data_1) # for the date table:
        table_2 = pa.table(data_2) # for the staff table:

        # Create in-memory Parquet file
        buffer = BytesIO()


        pq.write_table(table_1, buffer)
        buffer.seek(0)  
        # put mock date table parquet 
        # file into mock S3:
        S3_client.put_object(Bucket="11-processed-bucket", Key='2025-06-06 12:34:56/date.parquet', Body=buffer)


        pq.write_table(table_2, buffer)
        buffer.seek(0)  
        # put mock staff table parquet 
        # file into mock S3:
        S3_client.put_object(Bucket="11-processed-bucket", Key='2025-06-06 12:34:56/staff.parquet', Body=buffer)

        yield S3_client 



def test_get_pq_files_does_something(S3_setup):
    S3_client = S3_setup
    # arrange:
    # make mock list of keys:
    mock_list_of_keys = ['2025-06-06 12:34:56/date.parquet', '2025-06-06 12:34:56/staff.parquet']

    # make date table:
    expected_date_table = {
    'name': ['Abdul', 'Neill', 'Mukund'],
    'team': [1, 1, 1]
                    }

    # make staff table:
    expected_staff_table = {
    'name': ['Abdul', 'Neill', 'Mukund'],
    'team': [1, 1, 1]
                    }
    
    # make dataFrames of date and staff tables:
    # expected_dataFrame_date = pd.DataFrame(expected_date_table)    
    # expected_dataFrame_staff = pd.DataFrame(expected_staff_table)   

    
    # bucket name string:
    bucket = "11-processed-bucket"

    returned_dict = get_pq_files(S3_client, mock_list_of_keys, bucket)

    # expected_data_staff = pa.Table.from_pandas(returned_dict['dim_staff'])
    # expected_data_date = pa.Table.from_pandas(returned_dict['dim_date'])

    result_date_table = returned_dict['dim_date'].to_dict(orient='list')
    result_staff_table = returned_dict['dim_date'].to_dict(orient='list')
    

    assert expected_date_table == result_date_table
    assert expected_staff_table == result_staff_table