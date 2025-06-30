terraform {
  required_version = ">= 1.0"
  
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  backend "s3" {
    bucket = "financial-sentiment-terraform-state"
    key    = "terraform.tfstate"
    region = "us-east-1"
  }
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project     = "financial-sentiment"
      Environment = var.environment
      ManagedBy   = "terraform"
    }
  }
}

# Data sources
data "aws_caller_identity" "current" {}
data "aws_region" "current" {}

# VPC and Networking
module "vpc" {
  source = "./modules/vpc"
  
  environment = var.environment
  vpc_cidr    = var.vpc_cidr
}

# S3 Data Lake
module "s3" {
  source = "./modules/s3"
  
  environment = var.environment
  bucket_name = var.s3_bucket_name
}

# Kinesis Data Streams
module "kinesis" {
  source = "./modules/kinesis"
  
  environment      = var.environment
  stream_name      = var.kinesis_stream_name
  shard_count      = var.kinesis_shard_count
  common_tags      = var.common_tags
}

# Lambda Functions
module "lambda" {
  source = "./modules/lambda"
  
  environment           = var.environment
  function_name         = var.lambda_function_name
  handler               = var.lambda_handler
  runtime               = var.lambda_runtime
  timeout               = var.lambda_timeout
  memory_size           = var.lambda_memory_size
  filename              = var.lambda_zip_path
  role_arn              = module.iam.lambda_role_arn
  environment_variables = {
    S3_BUCKET     = module.s3.bucket_name
    KINESIS_STREAM = module.kinesis.stream_name
  }
  common_tags           = var.common_tags
}

# Redshift Cluster
module "redshift" {
  source = "./modules/redshift"
  
  environment     = var.environment
  cluster_name    = var.redshift_cluster_name
  node_type       = var.redshift_node_type
  node_count      = var.redshift_node_count
  master_username = var.redshift_master_username
  master_password = var.redshift_master_password
  db_name         = var.redshift_db_name
  subnet_ids      = module.vpc.private_subnet_ids
  security_group_ids = [module.vpc.redshift_security_group_id]
  publicly_accessible = false
  common_tags     = var.common_tags
}

# MWAA (Managed Workflows for Apache Airflow)
module "mwaa" {
  source = "./modules/mwaa"
  
  environment     = var.environment
  environment_name = var.mwaa_environment_name
  airflow_version  = var.mwaa_airflow_version
  dag_s3_path      = var.mwaa_dag_s3_path
  s3_bucket_arn    = module.s3.bucket_arn
  execution_role_arn = module.iam.mwaa_role_arn
  webserver_access_mode = var.mwaa_webserver_access_mode
  max_workers      = var.mwaa_max_workers
  min_workers      = var.mwaa_min_workers
  schedulers       = var.mwaa_schedulers
  environment_class = var.mwaa_environment_class
  subnet_ids       = module.vpc.private_subnet_ids
  security_group_ids = [module.vpc.mwaa_security_group_id]
  airflow_configuration_options = var.mwaa_airflow_configuration_options
  common_tags      = var.common_tags
}

# IAM Roles and Policies
module "iam" {
  source = "./modules/iam"
  
  environment     = var.environment
  kinesis_arn     = module.kinesis.stream_arn
  s3_bucket_arn   = module.s3.bucket_arn
  redshift_arn    = module.redshift.cluster_arn
  create_mwaa_role = true
  common_tags     = var.common_tags
}

# Outputs
output "s3_bucket_name" {
  description = "Name of the S3 bucket for data lake"
  value       = module.s3.bucket_name
}

output "kinesis_stream_name" {
  description = "Name of the Kinesis data stream"
  value       = module.kinesis.stream_name
}

output "lambda_function_name" {
  description = "Name of the Lambda function"
  value       = module.lambda.function_name
}

output "redshift_cluster_endpoint" {
  description = "Redshift cluster endpoint"
  value       = module.redshift.cluster_endpoint
}

output "mwaa_webserver_url" {
  description = "MWAA webserver URL"
  value       = module.mwaa.webserver_url
} 