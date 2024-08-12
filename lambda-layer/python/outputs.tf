output "arn" {
  description = "ARN of the Lambda Layer"
  value       = aws_lambda_layer_version.lambda_layer.arn
}
