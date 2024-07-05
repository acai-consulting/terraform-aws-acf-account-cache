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
| <a name="module_api_endpoint"></a> [api\_endpoint](#module\_api\_endpoint) | ../api-endpoint | n/a |
| <a name="module_llm_backend"></a> [llm\_backend](#module\_llm\_backend) | acai-consulting/lambda/aws | 1.3.6 |

## Resources

| Name | Type |
|------|------|
| [aws_dynamodb_table.conversation_history](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/dynamodb_table) | resource |
| [aws_iam_role_policy.process_user_prompt](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_role_policy) | resource |
| [aws_caller_identity.current](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/data-sources/caller_identity) | data source |
| [aws_iam_policy_document.lambda_permissions](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/data-sources/iam_policy_document) | data source |
| [aws_region.current](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/data-sources/region) | data source |

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| <a name="input_lambda_settings"></a> [lambda\_settings](#input\_lambda\_settings) | HCL map of the Lambda-Settings. | <pre>object({<br>    architecture          = optional(string, "x86_64")<br>    runtime               = optional(string, "python3.10")<br>    log_level             = optional(string, "INFO") # Logging level, e.g. "INFO"<br>    log_retention_in_days = optional(number, 7)      # Retention period for log files, in days<br>    error_forwarder = optional(object({<br>      target_name = string<br>      target_arn  = string<br>    }), null)<br>    memory_size  = optional(number, 512) # Size of the memory, in MB<br>    timeout      = optional(number, 720) # Timeout for the function, in seconds<br>    tracing_mode = optional(string, "Active")<br>    layer_arns = optional(map(any), {<br>      "aws_lambda_powertools_python_layer_arn" = "arn:aws:lambda:$region:017000801446:layer:AWSLambdaPowertoolsPythonV2:40"<br>    })<br>  })</pre> | <pre>{<br>  "architecture": "x86_64",<br>  "error_forwarder": null,<br>  "layer_arns": {<br>    "aws_lambda_powertools_python_layer_arn": "arn:aws:lambda:$region:017000801446:layer:AWSLambdaPowertoolsPythonV2:40"<br>  },<br>  "log_level": "INFO",<br>  "log_retention_in_days": 7,<br>  "memory_size": 512,<br>  "runtime": "python3.10",<br>  "timeout": 720,<br>  "tracing_mode": "Active"<br>}</pre> | no |
| <a name="input_resource_tags"></a> [resource\_tags](#input\_resource\_tags) | Tags for the resources | `map(string)` | `{}` | no |
| <a name="input_settings"></a> [settings](#input\_settings) | n/a | <pre>object({<br>    lambda_name            = optional(string, "acai-account-cache-query-generator")<br>    chat_history_ddb_name  = optional(string, "acai-account-cache-query-generator-chat-history")<br>    bedrock_service_name   = optional(string, "bedrock-runtime")<br>    bedrock_service_region = optional(string, "eu-central-1")<br>    bedrock_model_id       = optional(string, "anthropic.claude-3-haiku-20240307-v1:0")<br>    api_settings = optional(object({<br>      api_key_name      = optional(string, "acai-cache-query-generator-key")<br>      api_name          = optional(string, "acai-cache-query-generator")<br>      api_description   = optional(string, "API to generate a query via a LLM and to execute a query against the cache.")<br>      api_stage_name    = optional(string, "v1")<br>      api_endpoint_name = optional(string, "chat_query")<br>    }), null)<br>  })</pre> | <pre>{<br>  "api_settings": null,<br>  "bedrock_model_id": "anthropic.claude-3-haiku-20240307-v1:0",<br>  "bedrock_service_name": "bedrock-runtime",<br>  "bedrock_service_region": "eu-central-1",<br>  "lambda_name": "acai-account-cache-query-generator"<br>}</pre> | no |

## Outputs

| Name | Description |
|------|-------------|
| <a name="output_api_endpoint"></a> [api\_endpoint](#output\_api\_endpoint) | api\_endpoint |
| <a name="output_lambda_name"></a> [lambda\_name](#output\_lambda\_name) | lambda\_name |
<!-- END_TF_DOCS -->