# terraform-aws-acf-account-cache

<!-- SHIELDS -->
[![Maintained by acai.gmbh][acai-shield]][acai-url] 
![module-version-shield]
![terraform-version-shield]
![trivy-shield]
![checkov-shield]
[![Latest Release][release-shield]][release-url]

<!-- LOGO -->
<div style="text-align: right; margin-top: -60px;">
<a href="https://acai.gmbh">
  <img src="https://github.com/acai-consulting/acai.public/raw/main/logo/logo_github_readme.png" alt="acai logo" title="ACAI"  width="250" /></a>
</div>
</br>

<!-- DESCRIPTION -->
[Terraform][terraform-url] module to deploy an AWS account-context cache.

Will query and cache AWS Organization for the following account-context data.

```json
{
    "accountId": "654654551430",
    "accountName": "aws-testbed-core-backup",
    "accountStatus": "ACTIVE",
    "accountTags": {
        "owner": "Foundation Security Backup Team"
    },
    "ouId": "ou-s2bx-wq9eltfy",
    "ouIdWithPath": "o-5l2vzue7ku/r-s2bx/ou-s2bx-1rsmt2o1/ou-s2bx-wq9eltfy",
    "ouName": "Security",
    "ouNameWithPath": "Root/Core/Security",
    "ouTags": {
        "owner": "Foundation Security"
    }
}
```

<!-- ARCHITECTURE -->
## Architecture

![architecture][architecture]

<!-- FEATURES -->
## Features

* The account-context cache can be deployed in any AWS account of the AWS Organization.
* Optionally provision the Organization-Info-Reader IAM Role.

<!-- USAGE -->
## Usage

### terraform-aws-acf-account-cache

```hcl
module "org_info_reader" {
  source = "git::https://github.com/acai-consulting/terraform-aws-acf-account-cache.git//org-info-reader"

  settings = {
    trusted_account_ids = ["992382728088"] # Core Security
  }
  providers = {
    aws = aws.org_mgmt
  }
}

module "account_cache" {
  source = "git::https://github.com/acai-consulting/terraform-aws-acf-account-cache.git"

  settings = {
    org_reader_role_arn = module.org_info_reader.iam_role_arn
  }
  providers = {
    aws = aws.core_security
  }
}

# ---------------------------------------------------------------------------------------------------------------------
# ¦ YOUR LAMBDA AS CACHE CONSUMER
# ---------------------------------------------------------------------------------------------------------------------
module "lambda_account_cache_consumer" {
  #checkov:skip=CKV_TF_1: Currently version-tags are used
  source  = "acai-consulting/lambda/aws"
  version = "~> 1.3.2"

  lambda_settings = {
    function_name = "account-cache-consumer"
    description   = "Query the account-cache."
    layer_arn_list = [
      module.account_cache.cache_lambda_layer_arn
    ]
    handler = "main.lambda_handler"
    package = {
      source_path = "${path.module}/lambda-files"
    }
    environment_variables = {
      ORG_READER_ROLE_ARN      = module.org_info_reader.iam_role_arn
      CONTEXT_CACHE_TABLE_NAME = module.account_cache.ddb_name
    }
  }
  resource_tags = local.resource_tags
}

resource "aws_iam_role_policy_attachment" "lambda_account_cache_policy_attachment" {
  role       = module.lambda_account_cache_consumer.execution_iam_role.name
  policy_arn = module.account_cache.cache_lambda_permission_policy_arn
}
```

<!-- BEGIN_TF_DOCS -->
## Requirements

| Name | Version |
|------|---------|
| <a name="requirement_terraform"></a> [terraform](#requirement\_terraform) | >= 1.0.0 |
| <a name="requirement_aws"></a> [aws](#requirement\_aws) | >= 4.0 |

## Providers

| Name | Version |
|------|---------|
| <a name="provider_aws"></a> [aws](#provider\_aws) | >= 4.0 |

## Modules

No modules.

## Resources

| Name | Type |
|------|------|
| [aws_caller_identity.this](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/data-sources/caller_identity) | data source |

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|

## Outputs

| Name | Description |
|------|-------------|
| <a name="output_account_id"></a> [account\_id](#output\_account\_id) | account\_id |
| <a name="output_input"></a> [input](#output\_input) | pass through input |
<!-- END_TF_DOCS -->

<!-- AUTHORS -->
## Authors

This module is maintained by [ACAI GmbH][acai-url].

<!-- LICENSE -->
## License

See [LICENSE][license-url] for full details.

<!-- COPYRIGHT -->
<br />
<br />
<p align="center">Copyright &copy; 2024 ACAI GmbH</p>

<!-- MARKDOWN LINKS & IMAGES -->
[acai-shield]: https://img.shields.io/badge/maintained_by-acai.gmbh-CB224B?style=flat
[acai-url]: https://acai.gmbh
[module-version-shield]: https://img.shields.io/badge/module_version-1.0.0-CB224B?style=flat
[terraform-version-shield]: https://img.shields.io/badge/tf-%3E%3D1.3.10-blue.svg?style=flat&color=blueviolet
[trivy-shield]: https://img.shields.io/badge/trivy-passed-green
[checkov-shield]: https://img.shields.io/badge/checkov-passed-green
[release-shield]: https://img.shields.io/github/v/release/acai-consulting/terraform-aws-acf-idc?style=flat&color=success
[architecture]: ./docs/terraform-aws-acf-account-cache.svg
[release-url]: https://github.com/acai-consulting/terraform-aws-acf-account-cache/releases
[license-url]: https://github.com/acai-consulting/terraform-aws-acf-idc/tree/main/LICENSE.md
[terraform-url]: https://www.terraform.io
[aws-url]: https://aws.amazon.com
[example-complete-url]: https://github.com/acai-consulting/terraform-aws-acf-account-cache/tree/main/examples/complete
