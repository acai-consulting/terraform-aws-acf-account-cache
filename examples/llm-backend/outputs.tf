/*output "example_passed" {
  description = "example_passed"
  value       = contains(keys(local.lambda_result), "accountId")
}
*/
output "llm_backend" {
  description = "llm_backend"
  value       = module.llm_backend
}

output "llm_backend_invocation" {
  description = "llm_backend_invocation"
  value       = jsondecode(data.aws_lambda_invocation.llm_backend.result)
}
