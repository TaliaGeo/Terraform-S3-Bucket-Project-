resource "aws_s3_bucket" "my_bucket" {
  bucket = local.bucket_name
  force_destroy = true
  
  tags = local.tags

}
  resource "aws_s3_bucket_versioning" "versioning"{
    bucket = aws_s3_bucket.my_bucket.id
    versioning_configuration {
      status = "Enabled"
    }
  }
/*THE OLD WAY resource "aws_s3_bucket" "my_bucket" {
  bucket = "some-name"

  versioning {
    enabled = true
  }
}*/


resource "aws_s3_bucket" "legacy_bucket" {
  bucket = "legacybucket1"
  tags = local.tags
}

resource "aws_s3_bucket_versioning" "legacy_versioning" {
  bucket = aws_s3_bucket.legacy_bucket.id

  versioning_configuration {
    status = "Enabled"
  }
}
