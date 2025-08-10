locals {
  bucket_name = "devops-trainee-bucket-${var.unique_id}"
  tags = {
    Name      = var.project_name
    Environment = var.environment
    Owner     = var.owner
    ManagedBy = var.managed_by
  }
}
