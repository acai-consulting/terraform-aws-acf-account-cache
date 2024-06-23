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
data "aws_caller_identity" "current" { provider = aws.core_security }
data "aws_region" "current" { provider = aws.core_security }

# ---------------------------------------------------------------------------------------------------------------------
# ¦ LOCALS
# ---------------------------------------------------------------------------------------------------------------------
locals {
  settings = {
    lambda_name = "test"
  }
}

# ---------------------------------------------------------------------------------------------------------------------
# ¦ MODULE
# ---------------------------------------------------------------------------------------------------------------------
module "org_info_reader" {
  source = "../../org-info-reader"

  settings = {
    trusted_account_ids = ["992382728088"] # Core Security
  }
  providers = {
    aws = aws.org_mgmt
  }
}

module "account_cache" {
  #checkov:skip=CKV_AWS_50
  source = "../../"

  settings = {
    kms_cmk = {
      allowed_principals = ["arn:aws:iam::${data.aws_caller_identity.current.account_id}:root"]
    }
    org_reader_role_arn = module.org_info_reader.iam_role_arn
  }
  providers = {
    aws = aws.core_security
  }
}

module "cache_consumer" {
  source = "./consumer"

  org_reader_role_arn                = module.org_info_reader.iam_role_arn
  ddb_name                           = module.account_cache.ddb_name
  cache_lambda_layer_arn             = module.account_cache.cache_lambda_layer_arn
  cache_lambda_permission_policy_arn = module.account_cache.cache_lambda_permission_policy_arn
  providers = {
    aws = aws.core_security
  }
}

# ---------------------------------------------------------------------------------------------------------------------
# ¦ INVOKE LAMBDA
# ---------------------------------------------------------------------------------------------------------------------
data "aws_lambda_invocation" "invoke_cache_consumer_1" {
  function_name = module.cache_consumer.lambda_name

  input    = <<JSON
{
  "account_id": "${data.aws_caller_identity.current.account_id}"
}
JSON
  provider = aws.core_security
}


data "aws_lambda_invocation" "invoke_cache_consumer_2" {
  function_name = module.cache_consumer.lambda_name

  input    = <<JSON
{
  "query": {
    "exclude": "*",
    "forceInclude": {
        "accountName": [
          {
            "prefix": "aws-testbed-core-"
          }
        ]
    }
  }
}
JSON
  provider = aws.core_security
}
