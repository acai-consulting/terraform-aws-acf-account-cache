output "ddb_name" {
  description = "ddb_name"
  value       = aws_dynamodb_table.context_cache.name
}

output "cache_lambda_name" {
  description = "cache_lambda_name"
  value       = var.settings.lambda_name
}

output "cache_lambda_layer_arn" {
  description = "cache_lambda_layer_arn"
  value       = module.lambda_layer.arn
}

output "cache_lambda_permission_policy_arn" {
  description = "cache_lambda_permission_policy_arn"
  value       = aws_iam_policy.lambda_account_cache_permissions.arn
}

output "api_endpoint" {
  description = "api_endpoint"
  value       = var.settings.api_settings != null ? module.api_endpoint : null
}

output "core_configuration_to_write" {
  description = "Will be stored to the Account Cache node of the Core Configuration"
  value = {
    provisoned_caches = {
      "${data.aws_caller_identity.current.account_id}" = {
        "${data.aws_region.current.name}" = {
          org_reader_role_arn     = var.settings.org_reader_role_arn
          lambda_arn              = module.lambda_account_cache.lambda.arn
          lambda_layer_arn        = module.lambda_layer.arn
          ddb_table_name          = aws_dynamodb_table.context_cache.name
          cache_access_policy_arn = aws_iam_policy.lambda_account_cache_permissions.arn
          api_endpoint            = var.settings.api_settings != null ? module.api_endpoint[0].api_endpoint : "n/a"
        }
      }
    }
  }
}
