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
# ¦ LOCALS
# ---------------------------------------------------------------------------------------------------------------------
locals {
  resource_tags = merge(
    var.resource_tags,
    {
      "module_provider" = "ACAI GmbH",
      "module_name"     = "terraform-aws-acf-account-cache",
      "module_source"   = "github.com/acai-consulting/terraform-aws-acf-account-cache",
      "module_sub_path" = "org-info-reader"
      "module_version"  = /*inject_version_start*/ "1.3.3" /*inject_version_end*/
    }
  )
}

# ---------------------------------------------------------------------------------------------------------------------
# ¦ ORG INFO READER ROLE
# ---------------------------------------------------------------------------------------------------------------------
resource "aws_iam_role" "org_info_reader" {
  name                 = var.settings.iam_role.name
  path                 = var.settings.iam_role.path
  permissions_boundary = var.settings.iam_role.permissions_boundary_arn
  assume_role_policy   = data.aws_iam_policy_document.org_info_reader_trust.json
}

data "aws_iam_policy_document" "org_info_reader_trust" {
  statement {
    sid    = "TrustPolicy"
    effect = "Allow"
    principals {
      type = "AWS"
      identifiers = flatten(concat(
        var.settings.trusted_principals,
        formatlist("arn:aws:iam::%s:root", var.settings.trusted_account_ids)
      ))
    }
    actions = [
      "sts:AssumeRole"
    ]
  }
}

resource "aws_iam_role_policy" "org_info_reader" {
  name   = "OrgInfoReaderPolicy"
  role   = aws_iam_role.org_info_reader.name
  policy = data.aws_iam_policy_document.org_info_reader.json
}

#tfsec:ignore:AVD-AWS-0057
data "aws_iam_policy_document" "org_info_reader" {
  #checkov:skip=CKV_AWS_356   
  statement {
    sid    = "AllowOrgAndAccountInfoAccess"
    effect = "Allow"
    actions = [
      "organizations:List*",
      "organizations:Describe*",
      "account:Get*"
    ]
    resources = ["*"]
  }
}
