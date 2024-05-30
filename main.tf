# ---------------------------------------------------------------------------------------------------------------------
# ¦ REQUIREMENTS
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
  resource_tags = merge(
    var.resource_tags,
    {
      "module_provider" = "ACAI GmbH",
      "module_name"     = "terraform-aws-acf-account-cache",
      "module_source"   = "github.com/acai-consulting/terraform-aws-acf-account-cache",
      "module_version"  = /*inject_version_start*/ "1.0.0" /*inject_version_end*/
    }
  )
}


# ---------------------------------------------------------------------------------------------------------------------
# ¦ KMS CMK
# ---------------------------------------------------------------------------------------------------------------------
resource "aws_kms_key" "kms_cmk" {
  description             = "This key will be used for encryption the policy repo, CloudWatch LogGroups, sns topics and the configure registry."
  deletion_window_in_days = var.settings.kms_cmk.deletion_window_in_days
  enable_key_rotation     = true
  policy                  = data.aws_iam_policy_document.kms_cmk.json
  tags                    = var.resource_tags
}

resource "aws_kms_alias" "kms_cmk" {
  name          = var.settings.kms_cmk.alias_name
  target_key_id = aws_kms_key.kms_cmk.key_id
}

#checkov:skip=CKV_AWS_111 : Resources cannot be defined, as KMS Key ARN is not known at creation time
data "aws_iam_policy_document" "kms_cmk" {
  # Checkov Skips for policy checks
  #checkov:skip=CKV_AWS_356 : Resource policy
  #checkov:skip=CKV_AWS_109
  #checkov:skip=CKV_AWS_111

  override_policy_documents = var.settings.kms_cmk.policy_override

  # Statement for Read Permissions
  statement {
    sid    = "ReadPermissions"
    effect = "Allow"
    principals {
      type        = "AWS"
      identifiers = ["arn:aws:iam::${data.aws_caller_identity.current.account_id}:root"]
    }
    actions = [
      "kms:Describe*",
      "kms:List*",
      "kms:Get*",
    ]
    resources = ["*"]
  }

  # Statement for Management Permissions
  statement {
    sid    = "ManagementPermissions"
    effect = "Allow"
    principals {
      type        = "AWS"
      identifiers = ["arn:aws:iam::${data.aws_caller_identity.current.account_id}:root"]
    }
    actions = [
      "kms:Create*",
      "kms:Describe*",
      "kms:Enable*",
      "kms:Encrypt",
      "kms:List*",
      "kms:Put*",
      "kms:Update*",
      "kms:Revoke*",
      "kms:Disable*",
      "kms:Get*",
      "kms:Delete*",
      "kms:TagResource",
      "kms:UntagResource",
      "kms:ScheduleKeyDeletion",
      "kms:CancelKeyDeletion"
    ]
    resources = ["*"]
  }

  # Statement for Allowing Specific AWS Services
  statement {
    sid    = "AllowServices"
    effect = "Allow"
    principals {
      type = "Service"
      identifiers = [
        "lambda.amazonaws.com",
        "xray.amazonaws.com",
        "dynamodb.amazonaws.com",
        "logs.amazonaws.com"
      ]
    }
    actions = [
      "kms:Encrypt",
      "kms:Decrypt",
      "kms:ReEncrypt*",
      "kms:GenerateDataKey*",
      "kms:Describe*",
      "kms:Get*",
      "kms:List*",
    ]
    resources = ["*"]
  }

  # Statement for Allowing Lambda Execution Role
  statement {
    sid    = "AllowLambdaExecutionRole"
    effect = "Allow"
    principals {
      type        = "AWS"
      identifiers = ["*"]
    }
    actions = [
      "kms:Encrypt",
      "kms:Decrypt",
      "kms:ReEncrypt*",
      "kms:GenerateDataKey*",
      "kms:DescribeKey",
      "kms:CreateGrant"
    ]
    resources = ["*"]
    condition {
      test     = "ArnLike"
      variable = "aws:PrincipalARN"
      values = [
        replace("arn:aws:iam::${data.aws_caller_identity.current.account_id}:role/${var.settings.lambda_iam_role.path}${var.settings.lambda_iam_role.name}", "////", "/")
      ]
    }
  }
}

# ---------------------------------------------------------------------------------------------------------------------
# ¦ MAIN
# ---------------------------------------------------------------------------------------------------------------------
resource "aws_dynamodb_table" "context_cache" {
  name = var.settings.ddb_name

  hash_key     = "accountId"
  range_key    = "contextId"
  billing_mode = "PAY_PER_REQUEST"
  server_side_encryption {
    enabled     = true
    kms_key_arn = aws_kms_key.kms_cmk.arn
  }
  ttl {
    attribute_name = "timeToExist"
    enabled        = true
  }
  attribute {
    name = "accountId"
    type = "S"
  }
  attribute {
    name = "contextId"
    type = "S"
  }

  point_in_time_recovery {
    enabled = false
  }

  tags = var.resource_tags
}


# ---------------------------------------------------------------------------------------------------------------------
# ¦ LAMBDA
# ---------------------------------------------------------------------------------------------------------------------
module "lambda_account_cache" {
  #checkov:skip=CKV_TF_1: Currently version-tags are used
  source  = "acai-consulting/lambda/aws"
  version = "~> 1.3.2"

  lambda_settings = {
    function_name = var.settings.lambda_name
    description   = "Maintain and query the account-cache."
    layer_arn_list = [
    ]
    handler = "main.lambda_handler"
    config  = var.lambda_settings
    error_handling = var.lambda_settings.error_forwarder == null ? null : {
      central_collector = var.lambda_settings.error_forwarder
    }
    package = {
      source_path = "${path.module}/lambda-files"
    }
    tracing_mode = var.lambda_settings.tracing_mode
    environment_variables = {
      CONTEXT_CACHE_TABLE_NAME = aws_dynamodb_table.context_cache.name
    }
  }
  execution_iam_role_settings = {
    new_iam_role = var.settings.lambda_iam_role
  }
  existing_kms_cmk_arn = aws_kms_key.kms_cmk.arn
  resource_tags        = local.resource_tags
}
