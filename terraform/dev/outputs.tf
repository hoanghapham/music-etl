output "redshift_cluster_endpoint" {
  value = aws_redshift_cluster.music-dwh.endpoint
}

output "s3_bucket_id" {
  value = aws_s3_bucket.music-etl-staging.id
}

output "iam_role_arn" {
  value = aws_iam_role.dwh-user.arn
}