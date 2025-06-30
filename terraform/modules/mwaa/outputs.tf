output "webserver_url" {
  description = "MWAA webserver URL"
  value       = aws_mwaa_environment.main.webserver_url
}

output "mwaa_arn" {
  description = "MWAA environment ARN"
  value       = aws_mwaa_environment.main.arn
} 