variable "region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "project" {
  description = "Project name prefix for resources"
  type        = string
  default     = "ep14-discipline"
}

variable "env" {
  description = "Environment (dev / staging / prod)"
  type        = string
  default     = "dev"
}

variable "metric_db_instance_class" {
  description = "RDS instance class for metric store"
  type        = string
  default     = "db.t4g.medium"
}

variable "db_password" {
  description = "Master password for metric store DB"
  type        = string
  sensitive   = true
}
