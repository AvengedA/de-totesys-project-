#-----------------------
#First Lambda Function |
#-----------------------

data "archive_file" "first_lambda_archive" {
  type             = "zip"
  output_file_mode = "0666"
  source_dir       = "${path.module}/../src/" # change this to the file with the lambda handler in it
  output_path      = "${path.module}/../function.zip" # place to store the zip before uploading to s3
}

data "archive_file" "layer_archive" {
  type             = "zip"
  output_file_mode = "0666"
  source_dir       = "${path.module}/../layer/" # change this to the layer
  output_path      = "${path.module}/../layer.zip" # where to store the layer before uploading to s3
}

resource "aws_s3_object" "first_lambda_deployment" {
  bucket = aws_s3_bucket.lambda-bucket.bucket
  key    = "first_lambda/lambda.zip"
  source = data.archive_file.first_lambda_archive.output_path
  source_hash = data.archive_file.first_lambda_archive.output_base64sha256
}

resource "aws_s3_object" "layer_deployment" {
  bucket = aws_s3_bucket.lambda-bucket.bucket
  key    = "layer/layer.zip"
  source = data.archive_file.layer_archive.output_path
  source_hash = data.archive_file.layer_archive.output_base64sha256
}

resource "aws_lambda_layer_version" "layer" {
  layer_name          = "layer"
  compatible_runtimes = [var.python_runtime]
  s3_bucket           = aws_s3_bucket.lambda-bucket.bucket
  s3_key              = aws_s3_object.layer_deployment.key
}

resource "aws_lambda_function" "extract_handler" {
  s3_bucket        = aws_s3_bucket.lambda-bucket.bucket
  s3_key           = aws_s3_object.first_lambda_deployment.key

  layers           = [aws_lambda_layer_version.layer.arn]

  function_name    = var.first_lambda_function
  role             = aws_iam_role.first_lambda_function_role.arn
  handler          = "lambda_handler.lambda_handler" # change this to point to the handler
  runtime          = "python3.13"
  source_code_hash = data.archive_file.first_lambda_archive.output_base64sha256
}

resource "aws_lambda_layer_version" "my_layer" {
  layer_name          = "pg8000-layer"
  compatible_runtimes = [var.python_runtime]
  s3_bucket           = aws_s3_bucket.lambda-bucket.bucket  # Correct reference to the bucket name
  s3_key              = "layer.zip"  # Path to the layer zip in the S3 bucket
}
#   environment {
#     variables = {
#       S3_BUCKET_NAME=aws_s3_bucket.data_bucket.bucket
#     }
#   }
