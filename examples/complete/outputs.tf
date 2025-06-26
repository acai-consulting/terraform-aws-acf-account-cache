output "example_passed" {
  description = "example_passed"
  value       = contains(keys(jsondecode(resource.aws_lambda_invocation.invoke_cache_consumer_1.result)), "accountId")
}

output "aws_lambda_invocation_1" {
  description = "aws_lambda_invocation_1"
  value       = jsondecode(resource.aws_lambda_invocation.invoke_cache_consumer_1.result)
}

output "aws_lambda_invocation_2" {
  description = "aws_lambda_invocation_2"
  value       = jsondecode(resource.aws_lambda_invocation.invoke_cache_consumer_2.result)
}
