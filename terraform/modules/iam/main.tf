resource "aws_iam_role" "lambda" {
  name = "${var.environment}-lambda-role"
  assume_role_policy = data.aws_iam_policy_document.lambda_assume.json
  tags = var.common_tags
}

data "aws_iam_policy_document" "lambda_assume" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }
  }
}

resource "aws_iam_role_policy" "lambda_policy" {
  name = "${var.environment}-lambda-policy"
  role = aws_iam_role.lambda.id
  policy = data.aws_iam_policy_document.lambda_policy.json
}

data "aws_iam_policy_document" "lambda_policy" {
  statement {
    actions = [
      "logs:CreateLogGroup",
      "logs:CreateLogStream",
      "logs:PutLogEvents"
    ]
    resources = ["arn:aws:logs:*:*:*"]
  }
  statement {
    actions = [
      "kinesis:GetRecords",
      "kinesis:GetShardIterator",
      "kinesis:DescribeStream",
      "kinesis:ListStreams"
    ]
    resources = [var.kinesis_arn]
  }
  statement {
    actions = [
      "s3:PutObject",
      "s3:GetObject",
      "s3:ListBucket"
    ]
    resources = [
      "${var.s3_bucket_arn}",
      "${var.s3_bucket_arn}/*"
    ]
  }
  statement {
    actions = [
      "redshift:DescribeClusters",
      "redshift:GetClusterCredentials",
      "redshift:CreateClusterUser"
    ]
    resources = [var.redshift_arn]
  }
  dynamic "statement" {
    for_each = var.extra_lambda_statements
    content {
      actions   = statement.value.actions
      resources = statement.value.resources
    }
  }
}

# MWAA Role (opcional)
resource "aws_iam_role" "mwaa" {
  count = var.create_mwaa_role ? 1 : 0
  name = "${var.environment}-mwaa-role"
  assume_role_policy = data.aws_iam_policy_document.mwaa_assume.json
  tags = var.common_tags
}

data "aws_iam_policy_document" "mwaa_assume" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["airflow-env.amazonaws.com"]
    }
  }
}

resource "aws_iam_role_policy" "mwaa_policy" {
  count = var.create_mwaa_role ? 1 : 0
  name = "${var.environment}-mwaa-policy"
  role = aws_iam_role.mwaa[0].id
  policy = data.aws_iam_policy_document.mwaa_policy.json
}

data "aws_iam_policy_document" "mwaa_policy" {
  statement {
    actions = [
      "s3:ListBucket",
      "s3:GetObject",
      "s3:PutObject"
    ]
    resources = [
      "${var.s3_bucket_arn}",
      "${var.s3_bucket_arn}/*"
    ]
  }
  
  statement {
    actions = [
      "s3:GetAccountPublicAccessBlock"
    ]
    resources = ["*"]
  }
  
  statement {
    actions = [
      "s3:GetBucketPublicAccessBlock"
    ]
    resources = ["${var.s3_bucket_arn}"]
  }

  statement {
    actions = [
      "logs:CreateLogGroup",
      "logs:CreateLogStream",
      "logs:PutLogEvents"
    ]
    resources = ["arn:aws:logs:*:*:*"]
  }

  statement {
    actions = [
      "kms:Decrypt",
      "kms:GenerateDataKey*"
    ]
    resources = ["*"]
  }

  statement {
    actions = [
      "ec2:DescribeSubnets",
      "ec2:DescribeSecurityGroups",
      "ec2:DescribeVpcs"
    ]
    resources = ["*"]
  }
  
  # Puedes agregar más permisos según lo requiera MWAA
} 