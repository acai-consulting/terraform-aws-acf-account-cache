output "api_endpoint" {
  description = "api_endpoint"
  value       = var.settings.api_settings != null ? module.api_endpoint : null
}


output "lambda_name" {
  description = "lambda_name"
  value       = module.llm_backend.lambda.name
}
