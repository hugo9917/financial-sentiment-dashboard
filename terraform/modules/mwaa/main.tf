resource "aws_mwaa_environment" "main" {
  name                    = var.environment_name
  airflow_version         = var.airflow_version
  dag_s3_path             = var.dag_s3_path
  execution_role_arn      = var.execution_role_arn
  source_bucket_arn       = var.s3_bucket_arn
  webserver_access_mode   = var.webserver_access_mode
  max_workers             = var.max_workers
  min_workers             = var.min_workers
  schedulers              = var.schedulers
  environment_class       = var.environment_class
  network_configuration {
    security_group_ids = var.security_group_ids
    subnet_ids         = var.subnet_ids
  }
  logging_configuration {
    dag_processing_logs {
      enabled   = true
      log_level = "INFO"
    }
    scheduler_logs {
      enabled   = true
      log_level = "INFO"
    }
    task_logs {
      enabled   = true
      log_level = "INFO"
    }
    webserver_logs {
      enabled   = true
      log_level = "INFO"
    }
    worker_logs {
      enabled   = true
      log_level = "INFO"
    }
  }
  airflow_configuration_options = var.airflow_configuration_options
  tags = var.common_tags
} 