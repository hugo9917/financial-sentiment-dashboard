variable "environment" {
  description = "Environment name"
  type        = string
}

variable "stream_name" {
  description = "Kinesis stream name"
  type        = string
}

variable "shard_count" {
  description = "Number of shards"
  type        = number
  default     = 1
}

variable "stream_mode" {
  description = "Kinesis stream mode: ON_DEMAND or PROVISIONED"
  type        = string
  default     = "ON_DEMAND"
}

variable "common_tags" {
  description = "Common tags for all resources"
  type        = map(string)
  default     = {}
} 