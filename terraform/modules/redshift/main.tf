resource "aws_redshift_subnet_group" "main" {
  name       = "${var.environment}-redshift-subnet-group"
  subnet_ids = var.subnet_ids
  tags       = var.common_tags
}

resource "aws_redshift_cluster" "main" {
  cluster_identifier = var.cluster_name
  node_type         = var.node_type
  number_of_nodes   = var.node_count
  master_username   = var.master_username
  master_password   = var.master_password
  database_name     = var.db_name
  cluster_subnet_group_name = aws_redshift_subnet_group.main.name
  vpc_security_group_ids    = var.security_group_ids
  publicly_accessible       = var.publicly_accessible
  skip_final_snapshot       = true
  encrypted                 = true
  availability_zone_relocation_enabled = false
  tags                     = var.common_tags
} 