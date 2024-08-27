# ---------------------------------------------------------------------------------------------------------------------
# ¦ VERSIONS
# ---------------------------------------------------------------------------------------------------------------------
terraform {
  required_version = ">= 1.3.10"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 4.47"
    }
  }
}

# ---------------------------------------------------------------------------------------------------------------------
# ¦ LOCALS
# ---------------------------------------------------------------------------------------------------------------------
locals {
  resource_tags = merge(
    var.resource_tags,
    {
      "module_sub" = "API Endpoint"
    }
  )
}

# ---------------------------------------------------------------------------------------------------------------------
# ¦ API GATEWAY KEY
# ---------------------------------------------------------------------------------------------------------------------
resource "aws_api_gateway_api_key" "api_key" {
  name    = var.api_settings.api_key_name
  enabled = true
  tags    = local.resource_tags
}

resource "aws_api_gateway_usage_plan" "api_key_usage_plan" {
  name = "${var.api_settings.api_key_name}-usage-plan"

  api_stages {
    api_id = aws_api_gateway_rest_api.api.id
    stage  = aws_api_gateway_deployment.api_deployment.stage_name
  }

  quota_settings {
    limit  = 1000
    period = "MONTH"
    offset = 1
  }

  throttle_settings {
    burst_limit = 20
    rate_limit  = 10
  }

  tags = local.resource_tags
}

resource "aws_api_gateway_usage_plan_key" "api_key_usage_plan_key" {
  key_id        = aws_api_gateway_api_key.api_key.id
  key_type      = "API_KEY"
  usage_plan_id = aws_api_gateway_usage_plan.api_key_usage_plan.id
}

# ---------------------------------------------------------------------------------------------------------------------
# ¦ API GATEWAY
# ---------------------------------------------------------------------------------------------------------------------
resource "aws_api_gateway_rest_api" "api" {
  #checkov:skip=CKV_AWS_272
  name        = var.api_settings.api_name
  description = var.api_settings.api_description
  endpoint_configuration {
    types = ["REGIONAL"]
  }
  lifecycle {
    create_before_destroy = true
  }
  tags = local.resource_tags
}

resource "aws_lambda_permission" "allowed_triggers" {
  statement_id  = "AllowApiExecution"
  action        = "lambda:InvokeFunction"
  function_name = var.lambda_settings.arn
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.api.execution_arn}/*/*/${var.api_settings.api_endpoint_name}"
}

resource "aws_api_gateway_deployment" "api_deployment" {
  rest_api_id = aws_api_gateway_rest_api.api.id
  stage_name  = var.api_settings.api_stage_name
  triggers = {
    redeployment = sha256(jsonencode(aws_api_gateway_rest_api.api.body))
  }
  lifecycle {
    create_before_destroy = true
  }
  depends_on = [
    aws_api_gateway_integration.cache_endpoint
  ]
}

# ---------------------------------------------------------------------------------------------------------------------
# ¦ API GATEWAY - QUERY CACHE
# ---------------------------------------------------------------------------------------------------------------------
resource "aws_api_gateway_resource" "cache_endpoint" {
  rest_api_id = aws_api_gateway_rest_api.api.id
  parent_id   = aws_api_gateway_rest_api.api.root_resource_id
  path_part   = var.api_settings.api_endpoint_name
}

resource "aws_api_gateway_method" "cache_endpoint" {
  # checkov:skip=CKV2_AWS_53
  rest_api_id      = aws_api_gateway_rest_api.api.id
  resource_id      = aws_api_gateway_resource.cache_endpoint.id
  http_method      = "POST"
  authorization    = "NONE"
  api_key_required = true
}

resource "aws_api_gateway_integration" "cache_endpoint" {
  rest_api_id             = aws_api_gateway_rest_api.api.id
  resource_id             = aws_api_gateway_resource.cache_endpoint.id
  http_method             = aws_api_gateway_method.cache_endpoint.http_method
  integration_http_method = "POST"
  type                    = "AWS"
  uri                     = var.lambda_settings.invoke_arn
}

resource "aws_api_gateway_method_response" "cache_endpoint" {
  rest_api_id = aws_api_gateway_rest_api.api.id
  resource_id = aws_api_gateway_resource.cache_endpoint.id
  http_method = aws_api_gateway_method.cache_endpoint.http_method
  status_code = "200"
  response_parameters = {
    "method.response.header.Access-Control-Allow-Headers" = true,
    "method.response.header.Access-Control-Allow-Methods" = true,
    "method.response.header.Access-Control-Allow-Origin"  = true
  }
}

resource "aws_api_gateway_integration_response" "cache_endpoint" {
  rest_api_id = aws_api_gateway_rest_api.api.id
  resource_id = aws_api_gateway_resource.cache_endpoint.id
  http_method = aws_api_gateway_method.cache_endpoint.http_method
  status_code = aws_api_gateway_method_response.cache_endpoint.status_code
  response_parameters = {
    "method.response.header.Access-Control-Allow-Headers" = "'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token'",
    "method.response.header.Access-Control-Allow-Methods" = "'POST'",
    "method.response.header.Access-Control-Allow-Origin"  = "'*'"
  }
  depends_on = [
    aws_api_gateway_method.cache_endpoint,
    aws_api_gateway_integration.cache_endpoint
  ]
}

resource "aws_api_gateway_method" "options" {
  rest_api_id   = aws_api_gateway_rest_api.api.id
  resource_id   = aws_api_gateway_resource.cache_endpoint.id
  http_method   = "OPTIONS"
  authorization = "NONE"

}
resource "aws_api_gateway_method_response" "options_response_200" {
  rest_api_id = aws_api_gateway_rest_api.MyDemoAPI.id
  resource_id = aws_api_gateway_resource.MyDemoResource.id
  http_method = aws_api_gateway_method.options.http_method
  status_code = "200"
  response_models = {
    "application/json" = "Empty"
  }
  response_parameters = {
    "method.response.header.Access-Control-Allow-Origin"  = true
    "method.response.header.Access-Control-Allow-Headers" = true
    "method.response.header.Access-Control-Allow-Methods" = true
  }
}

resource "aws_api_gateway_integration" "options_integration" {
  rest_api_id = aws_api_gateway_rest_api.api.id
  resource_id = aws_api_gateway_resource.cache_endpoint.id
  http_method = aws_api_gateway_method.options.http_method
  type        = "MOCK"
}

resource "aws_api_gateway_integration_response" "options_integration_response" {
  rest_api_id = aws_api_gateway_rest_api.MyDemoAPI.id
  resource_id = aws_api_gateway_resource.MyDemoResource.id
  http_method = aws_api_gateway_method.options_integration.http_method
  status_code = aws_api_gateway_method_response.options_response_200.status_code
  response_parameters = {
    "method.response.header.Access-Control-Allow-Origin"  = "'*'"
    "method.response.header.Access-Control-Allow-Headers" = "'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token'"
    "method.response.header.Access-Control-Allow-Methods" = "'GET,OPTIONS,POST'"
  }
  response_templates = {
    "application/json" = ""
  }
  depends_on = [
    aws_api_gateway_method.options,
    aws_api_gateway_integration.options_integration
  ]
}
