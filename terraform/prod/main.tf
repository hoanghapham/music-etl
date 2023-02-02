terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.16"
    }
  }
  required_version = ">= 1.2.0"
}

provider "aws" {
  region     = "us-east-1"
  access_key = var.aws_secret_key_id
  secret_key = var.aws_secret_access_key
  token      = var.aws_session_token
}

provider "aws" {
  alias      = "west"
  region     = "us-east-1"
  access_key = var.aws_secret_key_id
  secret_key = var.aws_secret_access_key
  token      = var.aws_session_token
}


resource "random_pet" "name" {}

resource "aws_security_group" "music-etl-sg" {
  name = "${random_pet.name.id}-sg"
}

resource "aws_security_group_rule" "all-ingress" {
  type              = "ingress"
  from_port         = 0
  to_port           = 65535
  protocol          = "tcp"
  cidr_blocks       = ["0.0.0.0/0"]
  security_group_id = aws_security_group.music-etl-sg.id
}

resource "aws_security_group_rule" "all-egress" {
  type              = "egress"
  from_port         = 0
  to_port           = 65535
  protocol          = "tcp"
  cidr_blocks       = ["0.0.0.0/0"]
  security_group_id = aws_security_group.music-etl-sg.id

}

resource "aws_security_group_rule" "dwh-ingress" {
  type              = "ingress"
  from_port         = 5439
  to_port           = 5439
  protocol          = "tcp"
  cidr_blocks       = ["0.0.0.0/0"]
  security_group_id = aws_security_group.music-etl-sg.id
}

# IAM

resource "aws_iam_policy_attachment" "s3-read-only-att" {
  name       = "s3-read-only-att"
  policy_arn = "arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess"
  roles      = [aws_iam_role.dwh-user.name]
}

resource "aws_iam_policy_attachment" "redshift-all-commands" {
  name       = "redshift-all-commands"
  policy_arn = "arn:aws:iam::aws:policy/AmazonRedshiftAllCommandsFullAccess"
  roles      = [aws_iam_role.dwh-user.name]
}

resource "aws_iam_role" "dwh-user" {
  name = "dwh-user"
  assume_role_policy = jsonencode(
    {
      Statement = [
        {
          Action    = "sts:AssumeRole"
          Effect    = "Allow"
          Principal = { Service = "redshift.amazonaws.com" }
        }
      ]
      Version = "2012-10-17"
    }
  )
}

# Redshift

resource "aws_redshift_cluster" "music-dwh" {
  cluster_identifier     = "music-dwh-cluster"
  database_name          = "dev"
  master_username        = "dwhuser"
  master_password        = var.redshift_password
  node_type              = "dc2.large"
  cluster_type           = "single-node"
  port                   = 5439
  number_of_nodes        = 1
  vpc_security_group_ids = [aws_security_group.music-etl-sg.id]
  iam_roles              = [aws_iam_role.dwh-user.arn]
  skip_final_snapshot    = true
  publicly_accessible    = true
}

resource "aws_s3_bucket" "music-etl-staging" {
  provider      = aws.west
  bucket        = "music-etl-staging"
  force_destroy = true

  tags = {
    Name        = "MusicETL"
    Environment = "Dev"
  }
}

resource "aws_s3_bucket_acl" "private-bucket" {
  provider = aws.west
  bucket   = aws_s3_bucket.music-etl-staging.id
  acl      = "private"
}

# EC2

resource "aws_instance" "music-etl" {

}

resource "aws_ebs_volume" "million-song-dataset" {

}

resource "aws_volume_attachment" "msd-att" {

}

# EBS