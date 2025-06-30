output "lambda_role_arn" {
  description = "Lambda IAM role ARN"
  value       = aws_iam_role.lambda.arn
}

output "mwaa_role_arn" {
  description = "MWAA IAM role ARN"
  value       = try(aws_iam_role.mwaa[0].arn, null)
} 