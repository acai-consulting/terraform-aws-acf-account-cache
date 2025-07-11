# ---------------------------------------------------------------------------------------------------------------------
# ¦ VERSIONS
# ---------------------------------------------------------------------------------------------------------------------
terraform {
  required_version = ">= 1.3.10"

  required_providers {
    aws = {
      source                = "hashicorp/aws"
      version               = ">= 4.47"
      configuration_aliases = []
    }
  }
}

# ---------------------------------------------------------------------------------------------------------------------
# ¦ DATA
# ---------------------------------------------------------------------------------------------------------------------
data "aws_caller_identity" "current" {}
data "aws_region" "current" {}

# ---------------------------------------------------------------------------------------------------------------------
# ¦ LOCALS
# ---------------------------------------------------------------------------------------------------------------------
locals {
  resource_tags = var.resource_tags
}

# ---------------------------------------------------------------------------------------------------------------------
# ¦ MODULE
# ---------------------------------------------------------------------------------------------------------------------
#tfsec:ignore:AVD-AWS-0066
module "lambda_account_cache_consumer" {
  #checkov:skip=CKV_TF_1: Currently version-tags are used
  #checkov:skip=CKV_AWS_50
  source  = "acai-consulting/lambda/aws"
  version = "1.3.15"

  lambda_settings = {
    function_name = "account-cache-consumer"
    description   = "Query the account-cache."
    layer_arn_list = [
      var.cache_lambda_layer_arn
    ]
    config  = var.lambda_settings
    handler = "main.lambda_handler"
    package = {
      source_path = "${path.module}/lambda-files"
    }
    tracing_mode = var.lambda_settings.tracing_mode
    environment_variables = {
      LOG_LEVEL                = var.lambda_settings.log_level
      ORG_READER_ROLE_ARN      = var.org_reader_role_arn
      CONTEXT_CACHE_TABLE_NAME = var.ddb_name
    }
  }
  resource_tags = local.resource_tags
}


# ---------------------------------------------------------------------------------------------------------------------
# ¦ ASSIGN CACHE POLICY TO LAMBDA EXECUTION ROLE
# ---------------------------------------------------------------------------------------------------------------------
resource "aws_iam_role_policy_attachment" "lambda_account_cache_policy_attachment" {
  role       = module.lambda_account_cache_consumer.execution_iam_role.name
  policy_arn = var.cache_lambda_permission_policy_arn
}
