output "dynamodb_table_name" {
  value       = aws_dynamodb_table.ekyc_table.name
  description = "The assigned DynamoDB table name."
}

output "s3_bucket_name" {
  value       = aws_s3_bucket.document_bucket.id
  description = "The secure document storage S3 bucket name."
}

output "lambda_iam_role_arn" {
  value       = aws_iam_role.lambda_exec_role.arn
  description = "The Execution Role ARN configured for AWS Lambda."
}
