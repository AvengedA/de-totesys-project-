import os
import pytest
from moto import mock_aws
from src.Lambda_handler import lambda_handler
import boto3
import json

data = [{"design_id": 1, "name": "abdul", "team": 31, "project": "terraform"},{"design_id": 2, "name": "Mukund", "team": 32, "project": "terraform"},{"design_id": 3, "name": "Neil", "team": 33, "project": "terraform"}]

@pytest.fixture(scope="function")
def aws_credentials():
    """Mocked AWS Credentials for moto."""
    os.environ["AWS_ACCESS_KEY_ID"] = "test"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "test"
    os.environ["AWS_SECURITY_TOKEN"] = "test"
    os.environ["AWS_SESSION_TOKEN"] = "test"
    os.environ["AWS_DEFAULT_REGION"] = "eu-west-2"


@pytest.fixture(scope="function")
def S3_setup(aws_credentials):
    with mock_aws():
        yield boto3.client("s3", region_name="eu-west-2")
        

def test_lambda_handler_determine_whether_a_key_exits(S3_setup):
    # arrange
    bucket_name = "11-ingestion-bucket"
    S3_setup.create_bucket(
            Bucket=bucket_name,
            CreateBucketConfiguration={"LocationConstraint": "eu-west-2"},
        )
    S3_setup.put_object(Bucket=bucket_name, Key="design/2521251.json")
    key_prefix = "design"
    
    # Act
    result = lambda_handler(data, key_prefix)
    result2 = lambda_handler(data, "sales")

    # assert
    assert result
    assert result2 == False
    

def test_lambda_handler_creates_new_key(S3_setup):
    # Arrange
    bucket_name = "11-ingestion-bucket"
    key_prefix = "sales"

    S3_setup.create_bucket(Bucket=bucket_name,
                           CreateBucketConfiguration={"LocationConstraint": "eu-west-2"})
    
    # Act 
    result_false = S3_setup.list_objects_v2(Bucket=bucket_name, Prefix=key_prefix)
    lambda_handler(data, key_prefix)
    result_true = S3_setup.list_objects_v2(Bucket=bucket_name, Prefix=key_prefix)
    # assert 
    assert result_false["KeyCount"] == 0
    assert result_true["KeyCount"] == 1



