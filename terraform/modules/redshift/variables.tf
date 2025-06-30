variable "environment" {
  description = "Environment name"
  type        = string
}

variable "cluster_name" {
  description = "Redshift cluster name"
  type        = string
}

variable "node_type" {
  description = "Redshift node type"
  type        = string
  default     = "dc2.large"
}

variable "node_count" {
  description = "Number of nodes"
  type        = number
  default     = 1
}

variable "master_username" {
  description = "Redshift master username"
  type        = string
  default     = "admin"
}

variable "master_password" {
  description = "Redshift master password"
  type        = string
  sensitive   = true
}

variable "db_name" {
  description = "Database name"
  type        = string
  default     = "dev"
}

variable "subnet_ids" {
  description = "List of subnet IDs for Redshift"
  type        = list(string)
}

variable "security_group_ids" {
  description = "List of security group IDs for Redshift"
  type        = list(string)
}

variable "publicly_accessible" {
  description = "Whether the cluster is publicly accessible"
  type        = bool
  default     = false
}

variable "common_tags" {
  description = "Common tags for all resources"
  type        = map(string)
  default     = {}
} 