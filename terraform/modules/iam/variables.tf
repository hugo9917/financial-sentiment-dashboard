variable "environment" {
  description = "Environment name"
  type        = string
}

variable "kinesis_arn" {
  description = "Kinesis stream ARN"
  type        = string
  default     = "*"
}

variable "s3_bucket_arn" {
  description = "S3 bucket ARN"
  type        = string
  default     = "*"
}

variable "redshift_arn" {
  description = "Redshift cluster ARN"
  type        = string
  default     = "*"
}

variable "extra_lambda_statements" {
  description = "Extra IAM statements for Lambda (list of maps: {actions, resources})"
  type        = list(object({
    actions   = list(string)
    resources = list(string)
  }))
  default     = []
}

variable "create_mwaa_role" {
  description = "Whether to create MWAA role"
  type        = bool
  default     = false
}

variable "common_tags" {
  description = "Common tags for all resources"
  type        = map(string)
  default     = {}
} 