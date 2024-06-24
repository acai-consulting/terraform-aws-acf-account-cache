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
# ¦ MODULE
# ---------------------------------------------------------------------------------------------------------------------
module "llm_backend" {
  source = "../../modules/llm-backend"

  providers = {
    aws = aws.core_security
  }
}


data "aws_lambda_invocation" "llm_backend" {
  function_name = module.llm_backend.lambda_name

  input    = <<JSON
{
  "chat_query": "Give me all accounts in the Org Unit 'Production'."
}
JSON
  provider = aws.core_security
  depends_on = [
    module.llm_backend
  ]
}