resource "aws_lambda_function" "main" {
  function_name = var.function_name
  handler       = var.handler
  runtime       = var.runtime
  timeout       = var.timeout
  memory_size   = var.memory_size

  # Usa filename si no se especifica s3_bucket, si no usa s3_bucket y s3_key
  filename          = var.s3_bucket == "" ? var.filename : null
  s3_bucket         = var.s3_bucket != "" ? var.s3_bucket : null
  s3_key            = var.s3_bucket != "" ? var.s3_key : null
  s3_object_version = var.s3_bucket != "" && var.s3_object_version != "" ? var.s3_object_version : null
  source_code_hash  = var.s3_bucket == "" && var.filename != "" ? filebase64sha256(var.filename) : null

  role = var.role_arn

  environment {
    variables = var.environment_variables
  }

  tags = merge(var.common_tags, {
    Name = "${var.environment}-lambda"
  })
} 