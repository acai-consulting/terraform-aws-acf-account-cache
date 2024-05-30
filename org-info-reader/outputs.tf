output "org_info_reader_role_arn" {
  description = "ARN of the org_info_reader IAM Role"
  value       = aws_iam_role.org_info_reader.arn
}
