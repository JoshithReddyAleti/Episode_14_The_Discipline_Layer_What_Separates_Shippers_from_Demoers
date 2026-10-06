# Reference Terraform for the discipline layer stack.
# Adjust regions, sizes, and module sources for your environment.

terraform {
  required_version = ">= 1.5"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.region
}

# --- Vector DB storage (S3 for backups and disk-ANN data) ---
resource "aws_s3_bucket" "vector_data" {
  bucket = "${var.project}-vector-data-${var.env}"
}

resource "aws_s3_bucket_versioning" "vector_data" {
  bucket = aws_s3_bucket.vector_data.id
  versioning_configuration {
    status = "Enabled"
  }
}

# --- Experiment metric store (RDS Postgres) ---
resource "aws_db_instance" "metric_store" {
  identifier             = "${var.project}-metric-store-${var.env}"
  engine                 = "postgres"
  engine_version         = "16.3"
  instance_class         = var.metric_db_instance_class
  allocated_storage      = 100
  storage_encrypted      = true
  db_name                = "metrics"
  username               = "metricsadmin"
  password               = var.db_password
  skip_final_snapshot    = var.env != "prod"
  publicly_accessible    = false
  multi_az               = var.env == "prod"
  backup_retention_period = var.env == "prod" ? 30 : 7
}

# --- Logging bucket for observability ---
resource "aws_s3_bucket" "ai_logs" {
  bucket = "${var.project}-ai-logs-${var.env}"
}

resource "aws_s3_bucket_lifecycle_configuration" "ai_logs" {
  bucket = aws_s3_bucket.ai_logs.id
  rule {
    id     = "log-retention"
    status = "Enabled"
    expiration {
      days = 90
    }
  }
}
