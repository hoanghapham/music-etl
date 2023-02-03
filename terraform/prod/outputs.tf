output "redshift_cluster_endpoint" {
  value = aws_redshift_cluster.music-dwh.endpoint
}

output "s3_bucket_id" {
  value = aws_s3_bucket.music-etl-staging.id
}

output "ec2_public_dns" {
  value = aws_instance.music-etl.public_dns
}

output "iam_role_arn" {
  value = aws_iam_role.dwh-user.arn
}