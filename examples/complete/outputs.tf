output "example_passed" {
  description = "example_passed"
  value       = contains(keys(local.lambda_result), "accountId")
}

output "aws_lambda_invocation" {
  description = "aws_lambda_invocation"
  value       = aws_lambda_invocation.invoke_cache_consumer
}
