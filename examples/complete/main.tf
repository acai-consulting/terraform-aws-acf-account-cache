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
    trusted_account_ids = ["992382728088"]
  }
  providers = {
    aws = aws.org_mgmt
  }
}

module "cache" {
  source = "../../"

  settings = {
    org_reader_role_arn = module.org_info_reader.iam_role_arn
  }
  providers = {
    aws = aws.core_security
  }
}

module "consumer" {
  source = "./consumer"

  org_reader_role_arn                = module.org_info_reader.iam_role_arn
  ddb_name                           = module.cache.ddb_name
  cache_lambda_layer_arn             = module.cache.cache_lambda_layer_arn
  cache_lambda_permission_policy_arn = module.cache.cache_lambda_permission_policy_arn
  providers = {
    aws = aws.core_security
  }
}
