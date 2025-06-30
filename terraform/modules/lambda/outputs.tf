output "function_name" {
  description = "Lambda function name"
  value       = aws_lambda_function.main.function_name
}

output "function_arn" {
  description = "Lambda function ARN"
  value       = aws_lambda_function.main.arn
}

output "role_arn" {
  description = "Lambda IAM role ARN"
  value       = aws_lambda_function.main.role
} 