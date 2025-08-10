variable "aws_region" {
  description = "AWS region"
  type        = string
}

variable "project_name" {
  description = "Name of the project"
  type        = string
}

variable "environment" {
  description = "Deployment environment"
  type        = string
  default     = "dev"
}

variable "owner" {
  description = "Owner name"
  type        = string
}

variable "unique_id" {
  description = "Unique ID to make bucket name unique"
  type        = string
}

variable "managed_by" {
  default = "Terraform"
}
