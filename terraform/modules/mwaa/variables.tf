variable "environment" {
  description = "Environment name"
  type        = string
}

variable "environment_name" {
  description = "MWAA environment name"
  type        = string
}

variable "airflow_version" {
  description = "Airflow version"
  type        = string
  default     = "2.7.2"
}

variable "dag_s3_path" {
  description = "S3 path for DAGs (e.g. 'dags/')"
  type        = string
  default     = "dags/"
}

variable "s3_bucket_arn" {
  description = "S3 bucket ARN for DAGs and logs"
  type        = string
}

variable "execution_role_arn" {
  description = "IAM role ARN for MWAA"
  type        = string
}

variable "webserver_access_mode" {
  description = "Webserver access mode (PUBLIC_ONLY or PRIVATE_ONLY)"
  type        = string
  default     = "PUBLIC_ONLY"
}

variable "max_workers" {
  description = "Maximum number of workers"
  type        = number
  default     = 10
}

variable "min_workers" {
  description = "Minimum number of workers"
  type        = number
  default     = 1
}

variable "schedulers" {
  description = "Number of schedulers"
  type        = number
  default     = 2
}

variable "environment_class" {
  description = "Environment class (mw1.small, mw1.medium, mw1.large)"
  type        = string
  default     = "mw1.small"
}

variable "subnet_ids" {
  description = "List of subnet IDs for MWAA"
  type        = list(string)
}

variable "security_group_ids" {
  description = "List of security group IDs for MWAA"
  type        = list(string)
}

variable "airflow_configuration_options" {
  description = "Map of Airflow configuration options"
  type        = map(string)
  default     = {}
}

variable "common_tags" {
  description = "Common tags for all resources"
  type        = map(string)
  default     = {}
} 