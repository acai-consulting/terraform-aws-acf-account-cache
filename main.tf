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
      "module_version"  = /*inject_version_start*/ "1.3.4" /*inject_version_end*/
    }
  )
  kms_cmk_provided = var.settings.kms_cmk != null
}


# ---------------------------------------------------------------------------------------------------------------------
# ¦ LAMBDA EXECUTION ROLE
# ---------------------------------------------------------------------------------------------------------------------
resource "aws_iam_role" "lambda_exec_role" {
  name                 = var.settings.lambda_iam_role.name
  path                 = var.settings.lambda_iam_role.path
  permissions_boundary = var.settings.lambda_iam_role.permissions_boundary_arn

  assume_role_policy = data.aws_iam_policy_document.lambda_exec_role_trust.json
}

data "aws_iam_policy_document" "lambda_exec_role_trust" {
  statement {
    sid     = "TrustPolicy"
    effect  = "Allow"
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }
  }
}


# ---------------------------------------------------------------------------------------------------------------------
# ¦ CONDITIONAL KMS CMK
# ---------------------------------------------------------------------------------------------------------------------
resource "aws_kms_key" "kms_cmk" {
  count                   = local.kms_cmk_provided ? 1 : 0
  description             = "This key will be used for encryption the policy repo, CloudWatch LogGroups, sns topics and the configure registry."
  deletion_window_in_days = var.settings.kms_cmk.deletion_window_in_days
  enable_key_rotation     = true
  policy                  = data.aws_iam_policy_document.kms_cmk[0].json
  tags                    = local.resource_tags
}

resource "aws_kms_alias" "kms_cmk" {
  count         = local.kms_cmk_provided ? 1 : 0
  name          = var.settings.kms_cmk.alias_name
  target_key_id = aws_kms_key.kms_cmk[0].key_id
}

#checkov:skip=CKV_AWS_111 : Resources cannot be defined, as KMS Key ARN is not known at creation time
data "aws_iam_policy_document" "kms_cmk" {
  # Checkov Skips for policy checks
  #checkov:skip=CKV_AWS_356 : Resource policy
  #checkov:skip=CKV_AWS_109
  #checkov:skip=CKV_AWS_111

  count                     = local.kms_cmk_provided ? 1 : 0
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
      "kms:CancelKeyDeletion",
      "kms:RotateKeyOnDemand"
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
      type = "AWS"
      identifiers = flatten(concat(
        [aws_iam_role.lambda_exec_role.arn],
        var.settings.kms_cmk.allowed_principals
      ))
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
  }
}

# ---------------------------------------------------------------------------------------------------------------------
# ¦ CACHE POLICY
# ---------------------------------------------------------------------------------------------------------------------
resource "aws_iam_policy" "lambda_account_cache_permissions" {
  name        = replace(var.settings.lambda_iam_role.name, "role", "policy")
  description = "Policy for Lambda function to access DynamoDB, KMS, and assume roles"
  policy      = data.aws_iam_policy_document.lambda_account_cache_permissions.json
}


#organizations wildcard required to include all OUs
#tfsec:ignore:aws-iam-no-policy-wildcards
data "aws_iam_policy_document" "lambda_account_cache_permissions" {
  statement {
    sid    = "AssumeOrgReaderRole"
    effect = "Allow"
    actions = [
      "sts:AssumeRole"
    ]
    resources = [var.settings.org_reader_role_arn]
  }
  statement {
    sid    = "AllowContextCacheAccess"
    effect = "Allow"
    actions = [
      "dynamodb:BatchGetItem",
      "dynamodb:DescribeStream",
      "dynamodb:DescribeTable",
      "dynamodb:GetItem",
      "dynamodb:GetRecords",
      "dynamodb:GetShardIterator",
      "dynamodb:Query",
      "dynamodb:Scan",
      "dynamodb:BatchWriteItem",
      "dynamodb:CreateTable",
      "dynamodb:DeleteItem",
      "dynamodb:UpdateItem",
      "dynamodb:PutItem",
      "dynamodb:ListTagsOfResource"
    ]
    resources = [aws_dynamodb_table.context_cache.arn]
  }
  dynamic "statement" {
    for_each = local.kms_cmk_provided == true ? [1] : []
    content {
      sid    = "AllowKmsFull"
      effect = "Allow"
      actions = [
        "kms:Encrypt",
        "kms:Decrypt",
        "kms:ReEncryptFrom",
        "kms:ReEncrpytTo",
        "kms:GenerateDataKey",
        "kms:GenerateDataKeyPair",
        "kms:GenerateDataKeyPairWithoutPlaintext",
        "kms:GenerateDataKeyWithoutPlaintext",
        "kms:DescribeKey",
        "kms:CreateGrant"
      ]
      resources = [aws_kms_key.kms_cmk[0].arn]
    }
  }
  statement {
    sid    = "AllowStsGetCallerIdentity"
    effect = "Allow"
    actions = [
      "sts:GetCallerIdentity"
    ]
    resources = ["*"]
  }
}

resource "aws_iam_role_policy_attachment" "lambda_account_cache_policy_attachment" {
  role       = aws_iam_role.lambda_exec_role.name
  policy_arn = aws_iam_policy.lambda_account_cache_permissions.arn
}

# ---------------------------------------------------------------------------------------------------------------------
# ¦ DYNAMO DB CONTEXT CACHE
# ---------------------------------------------------------------------------------------------------------------------
#tfsec:ignore:AVD-AWS-0024 : Not required for a cache
resource "aws_dynamodb_table" "context_cache" {
  #checkov:skip=CKV_AWS_28 : Not required for a cache
  name = var.settings.ddb_name

  hash_key     = "accountId"
  range_key    = "contextId"
  billing_mode = "PAY_PER_REQUEST"
  server_side_encryption {
    enabled     = true
    kms_key_arn = local.kms_cmk_provided ? aws_kms_key.kms_cmk[0].arn : null
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

  tags = merge(
    local.resource_tags,
    {
      "cache_ttl_in_minutes" = var.settings.cache_ttl_in_minutes
    }
  )
}


# ---------------------------------------------------------------------------------------------------------------------
# ¦ LAMBDA LAYER
# ---------------------------------------------------------------------------------------------------------------------
module "lambda_layer" {
  source = "./lambda-layer/python"
  settings = {
    lambda_layer_name = var.settings.lambda_layer_name
    architectures     = [var.lambda_settings.architecture]
    runtimes          = [var.lambda_settings.runtime]
  }
}


# ---------------------------------------------------------------------------------------------------------------------
# ¦ LAMBDA
# ---------------------------------------------------------------------------------------------------------------------
module "lambda_account_cache" {
  #checkov:skip=CKV_TF_1: Currently version-tags are used
  source  = "acai-consulting/lambda/aws"
  version = "1.3.7"

  lambda_settings = {
    function_name = var.settings.lambda_name
    description   = "Maintain and query the account-cache."
    layer_arn_list = [
      replace(var.lambda_settings.layer_arns["aws_lambda_powertools_python_layer_arn"], "$region", data.aws_region.current.name),
      module.lambda_layer.arn
    ]
    handler = "main.lambda_handler"
    config  = var.lambda_settings
    error_handling = var.lambda_settings.error_forwarder == null ? null : {
      central_collector = var.lambda_settings.error_forwarder
    }
    package = {
      source_path = "${path.module}/lambda-files/"
    }
    tracing_mode = var.lambda_settings.tracing_mode
    environment_variables = {
      LOG_LEVEL                = var.lambda_settings.log_level
      ORG_READER_ROLE_ARN      = var.settings.org_reader_role_arn
      CONTEXT_CACHE_TABLE_NAME = aws_dynamodb_table.context_cache.name
      DROP_ATTRIBUTES          = join(",", var.settings.drop_attributes)
    }
  }
  trigger_settings = {
    schedule_expression = var.settings.lambda_schedule
  }
  execution_iam_role_settings = {
    existing_iam_role_name = aws_iam_role.lambda_exec_role.name
  }
  existing_kms_cmk_arn = local.kms_cmk_provided ? aws_kms_key.kms_cmk[0].arn : null
  resource_tags        = local.resource_tags
  depends_on           = [aws_iam_role.lambda_exec_role]
}

# ---------------------------------------------------------------------------------------------------------------------
# ¦ INVOKE LAMBDA
# ---------------------------------------------------------------------------------------------------------------------
resource "aws_lambda_invocation" "invoke" {
  count         = var.settings.lambda_invocation == true ? 1 : 0
  function_name = module.lambda_account_cache.lambda.name

  input = <<JSON
{
  "action": "refresh"
}
JSON
}


# ---------------------------------------------------------------------------------------------------------------------
# ¦ API ENDPOINT
# ---------------------------------------------------------------------------------------------------------------------
module "api_endpoint" {
  source          = "./modules/api-endpoint"
  count           = var.settings.api_settings != null ? 1 : 0
  api_settings    = var.settings.api_settings
  lambda_settings = module.lambda_account_cache.lambda
  resource_tags   = local.resource_tags
}
