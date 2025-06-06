
# #####################################
# #
# # Cloudwatch Logs for second lambda
# #
# #####################################


# resource "aws_cloudwatch_metric_alarm" "SecondLambdaError"{
#     alarm_name = "SecondLambdaAlert"
#     comparison_operator = "GreaterThanOrEqualToThreshold"
#     evaluation_periods = "1"
#     metric_name = "Errors"
#     namespace = "AWS/Lambda"
#     statistic = "Sum"
#     threshold = 1
#     period = "60"
#     alarm_description = "Alert If second Lambda function errors"
#     alarm_actions = [aws_sns_topic.lambda_alerts.arn]
#     dimensions = {
#       FunctionName = var.second_lambda_function
#     }

# }