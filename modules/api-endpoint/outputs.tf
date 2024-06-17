output "api_key_value" {
  description = "api_key_value"
  value       = aws_api_gateway_usage_plan_key.api_key_usage_plan_key.value
}

output "api_endpoint" {
  description = "Cache API endpoint"
  value = "${aws_api_gateway_deployment.api_deployment.invoke_url}/${var.api_settings.api_endpoint_name}"
}
