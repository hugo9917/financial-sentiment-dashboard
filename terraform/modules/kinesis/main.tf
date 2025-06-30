resource "aws_kinesis_stream" "main" {
  name             = var.stream_name
  retention_period = 24
  stream_mode_details {
    stream_mode = var.stream_mode
  }
  shard_count = var.stream_mode == "PROVISIONED" ? var.shard_count : null
  tags = merge(var.common_tags, {
    Name = "${var.environment}-kinesis-stream"
  })
} 