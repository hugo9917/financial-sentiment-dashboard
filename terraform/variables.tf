variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "development"
}

variable "vpc_cidr" {
  description = "CIDR block for VPC"
  type        = string
  default     = "10.0.0.0/16"
}

# S3 Configuration
variable "s3_bucket_name" {
  description = "Name of the S3 bucket for data lake"
  type        = string
  default     = "financial-sentiment-data-lake"
}

# Kinesis Configuration
variable "kinesis_stream_name" {
  description = "Name of the Kinesis data stream"
  type        = string
  default     = "financial-data-stream"
}

variable "kinesis_shard_count" {
  description = "Number of shards for Kinesis stream"
  type        = number
  default     = 1
}

# Lambda Configuration
variable "lambda_function_name" {
  description = "Name of the Lambda function"
  type        = string
  default     = "financial-data-processor"
}

variable "lambda_timeout" {
  description = "Lambda function timeout in seconds"
  type        = number
  default     = 300
}

variable "lambda_memory_size" {
  description = "Lambda function memory size in MB"
  type        = number
  default     = 512
}

variable "lambda_handler" {
  description = "Lambda handler"
  type        = string
  default     = "main.lambda_handler"
}

variable "lambda_runtime" {
  description = "Lambda runtime"
  type        = string
  default     = "python3.11"
}

variable "lambda_zip_path" {
  description = "Ruta al archivo ZIP de Lambda"
  type        = string
}

# Redshift Configuration
variable "redshift_cluster_name" {
  description = "Name of the Redshift cluster"
  type        = string
  default     = "financial-sentiment-cluster"
}

variable "redshift_node_type" {
  description = "Redshift node type"
  type        = string
  default     = "dc2.large"
}

variable "redshift_node_count" {
  description = "Number of nodes in Redshift cluster"
  type        = number
  default     = 1
}

variable "redshift_master_username" {
  description = "Redshift master username"
  type        = string
  default     = "admin"
}

variable "redshift_master_password" {
  description = "Redshift master password"
  type        = string
  sensitive   = true
}

variable "redshift_db_name" {
  description = "Nombre de la base de datos de Redshift"
  type        = string
  default     = "dev"
}

# MWAA Configuration
variable "mwaa_environment_name" {
  description = "Name of the MWAA environment"
  type        = string
  default     = "financial-sentiment-airflow"
}

variable "mwaa_max_workers" {
  description = "Maximum number of workers for MWAA"
  type        = number
  default     = 10
}

variable "mwaa_min_workers" {
  description = "Minimum number of workers for MWAA"
  type        = number
  default     = 1
}

variable "mwaa_airflow_version" {
  description = "Versión de Airflow para MWAA"
  type        = string
  default     = "2.7.2"
}

variable "mwaa_dag_s3_path" {
  description = "Ruta S3 para los DAGs de MWAA"
  type        = string
  default     = "dags/"
}

variable "mwaa_webserver_access_mode" {
  description = "Modo de acceso al webserver de MWAA"
  type        = string
  default     = "PUBLIC_ONLY"
}

variable "mwaa_schedulers" {
  description = "Número de schedulers para MWAA"
  type        = number
  default     = 2
}

variable "mwaa_environment_class" {
  description = "Clase de entorno para MWAA"
  type        = string
  default     = "mw1.small"
}

variable "mwaa_airflow_configuration_options" {
  description = "Opciones de configuración de Airflow para MWAA"
  type        = map(string)
  default     = {}
}

# Tags
variable "common_tags" {
  description = "Common tags for all resources"
  type        = map(string)
  default = {
    Project     = "financial-sentiment"
    Environment = "development"
    ManagedBy   = "terraform"
  }
} 