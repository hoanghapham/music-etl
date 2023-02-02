output "redshift_cluster_endpoint" {
  value = aws_redshift_cluster.music-dwh.endpoint
}

output "s3_bucket_arn" {
  value = aws_s3_bucket.music-etl-staging.arn
}

output "iam_role_arn" {
  value = aws_iam_role.dwh-user.arn
}