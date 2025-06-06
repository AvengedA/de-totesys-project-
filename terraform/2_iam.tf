# # Create role for second lambda to allow it to be triggered by EventBridge

# #Define
# # Refer back to trust policy, give trust policy to second lambda function
# #Create
# # Second function read ingestion policy
# # Second function triggered by eventbridge

# #Attach
# # Attach read policy to role

# #Can just copy paste iams for first function changing var to second function



# #-----------------
# #Lambda IAM role |
# #----------------


# # policy document same as the one in iam.tf file
# resource "aws_iam_role" "second_lambda_function_role" {
#     name = "role-${var.second_lambda_function}"
#     assume_role_policy = data.aws_iam_policy_document.trust_policy.json
# }

# resource "aws_iam_role_policy_attachment" "second_lambda_cw_policy_attachment" {
#     role = aws_iam_role.second_lambda_function_role.name
#     policy_arn = aws_iam_policy.second_cw_policy.arn
# }
# #--------------------------------
# # Cloud Watch for Second Lambda #
# #--------------------------------

# resource "aws_lambda_permission" "allow_sec_lambda" {
#   action = "lambda:InvokeFunction"
#   function_name = aws_lambda_function.transform_hanlder.function_name # change to second lambda
#   principal = "events.amazonaws.com"
#   source_arn = aws_cloudwatch_event_rule.filter_for_events_from_ingestion_bucket.arn
#   source_account = data.aws_caller_identity.current.account_id
# }

# # ---------------------------------
# # Second Lambda IAM policy for S3 |
# # ---------------------------------
# data "aws_iam_policy_document" "s3_access_policy_doc"{
#   statement {
#     actions = ["s3:Get*", "s3:List*", "s3:Put*"]
#     resources = [
#         "arn:aws:s3:::${var.processed-bucket}",
#         "arn:aws:s3:::${var.processed-bucket}/*"
#     ]
#    }
#   statement {
#     actions = ["s3:Get*", "s3:List*"]
#     resources = [
#         "arn:aws:s3:::${var.ingestion-bucket}",
#         "arn:aws:s3:::${var.ingestion-bucket}/*"
#     ]
#   }
# }

# resource "aws_iam_policy" "s3_access_policy_for_sec_lambda" {
#   name = "s3-policy-${var.second_lambda_function}-access"
#   policy = data.aws_iam_policy_document.s3_access_policy_doc.json
# }

# resource "aws_iam_role_policy_attachment" "second_lambda_s3_write_policy_attachment" {
#   role = aws_iam_role.second_lambda_function_role.name
#   policy_arn = aws_iam_policy.s3_access_policy_for_sec_lambda.arn
# }




# # ----------------------------------
# # Lambda IAM Policy for Cloudwatch |
# # ---------------------------------

# data "aws_iam_policy_document" "second_cloudwatch_document"{
#     statement{
#         actions = ["logs:CreateLogGroup"]
#         resources = ["arn:aws:logs:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:*:*"]
#     }

#     statement {
#         actions = [
#             "logs:CreateLogStream",
#             "logs:PutLogEvents",
#             "logs:PutLogEventsBatch",
#             ]
#         resources = ["arn:aws:logs:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:log-group:/aws/lambda/${var.second_lambda_function}:*"]
#     }
# }

# resource "aws_iam_policy" "second_cw_policy"{
#     name = "cw-policy-${var.second_lambda_function}"
#     description = "Cloudwatch logging policy for second lambda function"
#     policy = data.aws_iam_policy_document.second_cloudwatch_document.json
# }

