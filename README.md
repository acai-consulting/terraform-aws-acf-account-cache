# terraform-aws-acf-account-cache

<!-- SHIELDS -->
[![Maintained by acai.gmbh][acai-shield]][acai-url]
[![module-version-shield]][module-release-url]
![terraform-version-shield]
![trivy-shield]
![checkov-shield]

<!-- LOGO -->
<div style="text-align: right; margin-top: -60px;">
<a href="https://acai.gmbh">
  <img src="https://github.com/acai-consulting/acai.public/raw/main/logo/logo_github_readme.png" alt="acai logo" title="ACAI"  width="250" /></a>
</div>
</br>

<!-- BEGIN_ACAI_DOCS -->
## Overview

The `terraform-aws-acf-account-cache` module deploys a serverless AWS account-context cache. This module enables querying and caching of account-context data from AWS Organizations, storing essential details such as account ID, name, status, tags, and organizational unit (OU) hierarchy.

## Cached Account-Context Data

The module retrieves and caches the following details:

```json
{
  "accountId": "654654551430",
  "accountName": "aws-testbed-core-backup",
  "accountStatus": "ACTIVE",
  "accountTags": {
    "owner": "Platform Security Backup Team"
  },
  "ouId": "ou-s2bx-wq9eltfy",
  "ouIdWithPath": "o-5l2vzue7ku/r-s2bx/ou-s2bx-1rsmt2o1/ou-s2bx-wq9eltfy",
  "ouName": "Security",
  "ouNameWithPath": "Root/Core/Security",
  "ouTags": {
    "owner": "Platform Security"
  }
}
```

### Key Features

- Deployable in any AWS account within the AWS Organization.
- Supports queries using a structured syntax: [Account-Query](https://docs.acai.gmbh/json-engine/account-selection/).
- Optionally provisions the Organization-Info-Reader IAM Role for context cache assumption.

## Architecture

![architecture][architecture]

## Deploying the Context Cache

```hcl
module "org_info_reader" {
  source = "git::https://github.com/acai-consulting/terraform-aws-acf-account-cache.git//org-info-reader"

  settings = {
    trusted_account_ids = local.platform_settings.governance.org_mgmt.core_account_ids
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

module "account_cache" {
  source = "git::https://github.com/acai-consulting/terraform-aws-acf-account-cache.git//modules/llm-backend"

  settings = {
    org_reader_role_arn = module.org_info_reader.iam_role_arn
  }
  providers = {
    aws = aws.core_security
  }
}
```

## Cache Consumer

### Terraform Query Example

```terraform
data "aws_lambda_invocation" "query_for_prod_accounts" {
  function_name = local.platform_settings.governance.account_context_cache.lambda_name

  input    = <<JSON
{
  "query": {
    "exclude" : "*",
    "forceInclude" : {
      "ouNameWithPath" : [
        {
          "contains": "/Prod/"
        }
      ]
    }
  }
}
JSON
  provider = aws.core_security
}

locals {
  prod_accounts = jsondecode(data.aws_lambda_invocation.query_for_prod_accounts.result).result.account_ids
}
```

### AWS Lambda Python Integration

To integrate with AWS Lambda, use the provisioned Context Cache Lambda Layer:

```python
import os
from acai.cache.context_cache import ContextCache
from acai.cache_query.context_cache_query import ContextCacheQuery
import logging

LOGLEVEL = os.environ.get('LOG_LEVEL', 'DEBUG').upper()
logging.getLogger().setLevel(LOGLEVEL)
for noisy_log_source in ["boto3", "botocore", "nose", "s3transfer", "urllib3"]:
    logging.getLogger(noisy_log_source).setLevel(logging.WARN)
LOGGER = logging.getLogger()

ORG_READER_ROLE_ARN = os.environ['ORG_READER_ROLE_ARN']
CONTEXT_CACHE_TABLE_NAME = os.environ['CONTEXT_CACHE_TABLE_NAME']

def lambda_handler(event, context):
    context_cache = ContextCache(LOGGER, ORG_READER_ROLE_ARN, CONTEXT_CACHE_TABLE_NAME)
    context_cache_query = ContextCacheQuery(LOGGER, context_cache)
    
    accounts = context_cache_query.query_cache({
        "exclude": "*",
        "forceInclude": [
            {
                "accountTags": {
                    "environment": "Prod"
                },
                "ouNameWithPath": [
                    {
                        "contains": "/BusinessUnit_1/"
                    }
                ]
            }
        ]
    })        

    context_cache.get_member_account_context(accounts[0])
```
<!-- END_ACAI_DOCS -->


<!-- BEGIN_TF_DOCS -->
## Requirements

| Name | Version |
|------|---------|
| <a name="requirement_terraform"></a> [terraform](#requirement\_terraform) | >= 1.3.10 |
| <a name="requirement_aws"></a> [aws](#requirement\_aws) | >= 4.47 |

## Providers

| Name | Version |
|------|---------|
| <a name="provider_aws"></a> [aws](#provider\_aws) | >= 4.47 |

## Modules

| Name | Source | Version |
|------|--------|---------|
| <a name="module_api_endpoint"></a> [api\_endpoint](#module\_api\_endpoint) | ./modules/api-endpoint | n/a |
| <a name="module_lambda_account_cache"></a> [lambda\_account\_cache](#module\_lambda\_account\_cache) | acai-consulting/lambda/aws | 1.3.15 |
| <a name="module_lambda_layer"></a> [lambda\_layer](#module\_lambda\_layer) | ./lambda-layer/python | n/a |

## Resources

| Name | Type |
|------|------|
| [aws_dynamodb_table.context_cache](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/dynamodb_table) | resource |
| [aws_iam_policy.lambda_account_cache_permissions](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_policy) | resource |
| [aws_iam_role.lambda_exec_role](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_role) | resource |
| [aws_iam_role_policy_attachment.lambda_account_cache_policy_attachment](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_role_policy_attachment) | resource |
| [aws_kms_alias.kms_cmk](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/kms_alias) | resource |
| [aws_kms_key.kms_cmk](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/kms_key) | resource |
| [aws_lambda_invocation.invoke](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/lambda_invocation) | resource |
| [aws_caller_identity.current](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/data-sources/caller_identity) | data source |
| [aws_iam_policy_document.kms_cmk](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/data-sources/iam_policy_document) | data source |
| [aws_iam_policy_document.lambda_account_cache_permissions](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/data-sources/iam_policy_document) | data source |
| [aws_iam_policy_document.lambda_exec_role_trust](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/data-sources/iam_policy_document) | data source |
| [aws_region.current](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/data-sources/region) | data source |

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| <a name="input_settings"></a> [settings](#input\_settings) | n/a | <pre>object({<br>    lambda_name       = optional(string, "acai-account-cache")<br>    lambda_schedule   = optional(string, "rate(30 minutes)")<br>    lambda_layer_name = optional(string, "acai-account-cache-layer")<br>    lambda_invocation = optional(bool, false)<br>    lambda_iam_role = optional(object({<br>      name                     = optional(string, "acai-account-cache-lambda-role")<br>      path                     = optional(string, "/")<br>      permissions_boundary_arn = optional(string, null)<br>      }), {<br>      name                     = "acai-account-cache-lambda-role"<br>      path                     = "/"<br>      permissions_boundary_arn = null<br>    })<br>    ddb_name = optional(string, "acai-account-cache")<br>    kms_cmk = optional(object({<br>      alias_name              = optional(string, "alias/acai-account-cache-key")<br>      deletion_window_in_days = optional(number, 30)<br>      policy_override         = optional(list(string), null) # should override the statement_ids 'ReadPermissions' or 'ManagementPermissions'<br>      allowed_principals      = optional(list(string), [])<br>    }), null)<br>    cache_ttl_in_minutes = optional(number, 90)<br>    api_settings = optional(object({<br>      api_key_name      = optional(string, "acai-cache-key")<br>      api_name          = optional(string, "acai-cache")<br>      api_description   = optional(string, "API to access the account context cache.")<br>      api_stage_name    = optional(string, "v1")<br>      api_endpoint_name = optional(string, "cache")<br>    }), null)<br>    org_reader_role_arn = string<br>    drop_attributes     = optional(list(string), [])<br>  })</pre> | n/a | yes |
| <a name="input_lambda_settings"></a> [lambda\_settings](#input\_lambda\_settings) | HCL map of the Lambda-Settings. | <pre>object({<br>    architecture          = optional(string, "x86_64")<br>    runtime               = optional(string, "python3.12")<br>    log_level             = optional(string, "INFO") # Logging level, e.g. "INFO"<br>    log_retention_in_days = optional(number, 7)      # Retention period for log files, in days<br>    error_forwarder = optional(object({<br>      target_name = string<br>      target_arn  = string<br>    }), null)<br>    memory_size  = optional(number, 512) # Size of the memory, in MB<br>    timeout      = optional(number, 720) # Timeout for the function, in seconds<br>    tracing_mode = optional(string, "Active")<br>    layer_arns = optional(map(any), {<br>      "aws_lambda_powertools_python_layer_arn" = "arn:aws:lambda:$region:017000801446:layer:AWSLambdaPowertoolsPythonV2:40"<br>    })<br>  })</pre> | <pre>{<br>  "architecture": "x86_64",<br>  "error_forwarder": null,<br>  "layer_arns": {<br>    "aws_lambda_powertools_python_layer_arn": "arn:aws:lambda:$region:017000801446:layer:AWSLambdaPowertoolsPythonV2:40"<br>  },<br>  "log_level": "INFO",<br>  "log_retention_in_days": 7,<br>  "memory_size": 512,<br>  "runtime": "python3.12",<br>  "timeout": 720,<br>  "tracing_mode": "Active"<br>}</pre> | no |
| <a name="input_resource_tags"></a> [resource\_tags](#input\_resource\_tags) | Tags for the resources | `map(string)` | `{}` | no |

## Outputs

| Name | Description |
|------|-------------|
| <a name="output_api_endpoint"></a> [api\_endpoint](#output\_api\_endpoint) | api\_endpoint |
| <a name="output_cache_lambda_layer_arn"></a> [cache\_lambda\_layer\_arn](#output\_cache\_lambda\_layer\_arn) | cache\_lambda\_layer\_arn |
| <a name="output_cache_lambda_name"></a> [cache\_lambda\_name](#output\_cache\_lambda\_name) | cache\_lambda\_name |
| <a name="output_cache_lambda_permission_policy_arn"></a> [cache\_lambda\_permission\_policy\_arn](#output\_cache\_lambda\_permission\_policy\_arn) | cache\_lambda\_permission\_policy\_arn |
| <a name="output_core_configuration_to_write"></a> [core\_configuration\_to\_write](#output\_core\_configuration\_to\_write) | Will be stored to the Account Cache node of the Core Configuration |
| <a name="output_ddb_name"></a> [ddb\_name](#output\_ddb\_name) | ddb\_name |
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
[module-version-shield]: https://img.shields.io/badge/module_version-1.3.5-CB224B?style=flat
[module-release-url]: https://github.com/acai-consulting/terraform-aws-acf-account-cache/releases
[terraform-version-shield]: https://img.shields.io/badge/tf-%3E%3D1.3.10-blue.svg?style=flat&color=blueviolet
[trivy-shield]: https://img.shields.io/badge/trivy-passed-green
[checkov-shield]: https://img.shields.io/badge/checkov-passed-green
[architecture]: ./docs/terraform-aws-acf-account-cache.png
[license-url]: https://github.com/acai-consulting/terraform-aws-acf-account-cache/tree/main/LICENSE.md
[terraform-url]: https://www.terraform.io
[aws-url]: https://aws.amazon.com
[example-complete-url]: https://github.com/acai-consulting/terraform-aws-acf-account-cache/tree/main/examples/complete
