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
  resource_tags = merge(
    var.resource_tags,
    {
      "module_provider" = "ACAI GmbH",
      "module_name"     = "terraform-aws-acf-account-cache",
      "module_source"   = "github.com/acai-consulting/terraform-aws-acf-account-cache",
      "module_feature"  = "cache-query-llm-backend",
      "module_version"  = /*inject_version_start*/ "1.3.4" /*inject_version_end*/
    }
  )
}

# ---------------------------------------------------------------------------------------------------------------------
# ¦ DYNAMODB TABLE
# ---------------------------------------------------------------------------------------------------------------------
#tfsec:ignore:AVD-AWS-0024
#tfsec:ignore:AVD-AWS-0025
resource "aws_dynamodb_table" "conversation_history" {
  #checkov:skip=CKV_AWS_28
  #checkov:skip=CKV_AWS_119
  name = var.settings.chat_history_ddb_name

  hash_key     = "sessionID"
  range_key    = "timestamp"
  billing_mode = "PAY_PER_REQUEST"

  ttl {
    attribute_name = "timeToExist"
    enabled        = true
  }

  attribute {
    name = "sessionID"
    type = "S"
  }

  attribute {
    name = "timestamp"
    type = "N"
  }

  tags = local.resource_tags
}

# ---------------------------------------------------------------------------------------------------------------------
# ¦ LLM BACKEND LAMBDA
# ---------------------------------------------------------------------------------------------------------------------
locals {
  # Load and decode the JSON content
  validation_py = file("${path.module}/../../lambda-layer/python/files/python/acai/cache_query/validate_query.py")
  helper_py     = file("${path.module}/../../lambda-layer/python/files/python/acai/cache_query/helper.py")
  wiki_md       = file("${path.module}/../../wiki.md")
}

#tfsec:ignore:AVD-AWS-0066
module "llm_backend" {
  #checkov:skip=CKV_TF_1
  #checkov:skip=CKV_AWS_50
  source  = "acai-consulting/lambda/aws"
  version = "1.3.7"

  lambda_settings = {
    function_name = var.settings.lambda_name
    description   = "Create a context cache query with the help of a LLM."
    layer_arn_list = [
      replace(var.lambda_settings.layer_arns["aws_lambda_powertools_python_layer_arn"], "$region", data.aws_region.current.name),
    ]
    config = var.lambda_settings
    error_handling = var.lambda_settings.error_forwarder == null ? null : {
      central_collector = var.lambda_settings.error_forwarder
    }
    handler = "main.lambda_handler"
    package = {
      source_path = "${path.module}/lambda-files"
      files_to_inject = {
        "acai/cache_query/validate_query.py" : local.validation_py
        "acai/cache_query/helper.py" : local.helper_py
        "wiki.md" : local.wiki_md
      }
    }
    tracing_mode = var.lambda_settings.tracing_mode
    environment_variables = {
      LOG_LEVEL                   = var.lambda_settings.log_level
      BEDROCK_SERVICE_NAME        = var.settings.bedrock_service_name
      BEDROCK_SERVICE_REGION      = var.settings.bedrock_service_region
      BEDROCK_MODEL_ID            = var.settings.bedrock_model_id
      CHAT_HISTORY_DDB_TABLE_NAME = aws_dynamodb_table.conversation_history.name
    }
  }
  resource_tags = local.resource_tags
}

# ---------------------------------------------------------------------------------------------------------------------
# ¦ ASSIGN CACHE POLICY TO LAMBDA EXECUTION ROLE
# ---------------------------------------------------------------------------------------------------------------------
resource "aws_iam_role_policy" "process_user_prompt" {
  name   = replace(module.llm_backend.execution_iam_role.name, "role", "policy")
  role   = module.llm_backend.execution_iam_role.name
  policy = data.aws_iam_policy_document.lambda_permissions.json
}

#tfsec:ignore:AVD-AWS-0057
data "aws_iam_policy_document" "lambda_permissions" {
  #checkov:skip=CKV_AWS_356
  statement {
    sid    = "ReadDataFromBedrock"
    effect = "Allow"
    actions = [
      "bedrock:InvokeModel"
    ]
    resources = ["*"]
  }
  statement {
    sid    = "ConversationHistory"
    effect = "Allow"
    actions = [
      "dynamodb:Query",
      "dynamodb:PutItem",
      "dynamodb:BatchWriteItem"
    ]
    resources = [aws_dynamodb_table.conversation_history.arn]
  }

}

# ---------------------------------------------------------------------------------------------------------------------
# ¦ API ENDPOINT
# ---------------------------------------------------------------------------------------------------------------------
module "api_endpoint" {
  source          = "../api-endpoint"
  count           = var.settings.api_settings != null ? 1 : 0
  api_settings    = var.settings.api_settings
  lambda_settings = module.llm_backend.lambda
  resource_tags   = local.resource_tags
}
