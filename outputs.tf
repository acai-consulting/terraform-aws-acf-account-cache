output "ddb_name" {
  value = aws_dynamodb_table.context_cache.name
}

output "ddb_ttl_tag_name" {
  value = local.ddb_ttl_tag_name
}

output "cache_lambda_layer_arn" {
  value = aws_lambda_layer_version.layer.arn
}

output "cache_lambda_permission_policy_arn" {
  value = aws_iam_policy.lambda_account_cache_permissions.arn
}
