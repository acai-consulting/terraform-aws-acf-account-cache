variable "settings" {
  type = object({
    lambda_name       = optional(string, "acai-account-cache")
    lambda_schedule   = optional(string, "rate(30 minutes)")
    lambda_layer_name = optional(string, "acai-account-cache-layer")
    lambda_invocation = optional(bool, false)
    lambda_iam_role = optional(object({
      name                     = optional(string, "acai-account-cache-lambda-role")
      path                     = optional(string, "/")
      permissions_boundary_arn = optional(string, null)
      }), {
      name                     = "acai-account-cache-lambda-role"
      path                     = "/"
      permissions_boundary_arn = null
    })
    ddb_name = optional(string, "acai-account-cache")
    kms_cmk = optional(object({
      alias_name              = optional(string, "alias/acai-account-cache-key")
      deletion_window_in_days = optional(number, 30)
      policy_override         = optional(list(string), null) # should override the statement_ids 'ReadPermissions' or 'ManagementPermissions'
      allowed_principals      = optional(list(string), [])
    }), null)
    cache_ttl_in_minutes = optional(number, 90)
    api_settings = optional(object({
      api_key_name      = optional(string, "acai-cache-key")
      api_name          = optional(string, "acai-cache")
      api_description   = optional(string, "API to access the account context cache.")
      api_stage_name    = optional(string, "v1")
      api_endpoint_name = optional(string, "cache")
    }), null)
    org_reader_role_arn = string
    drop_attributes     = optional(list(string), [])
  })
}


# ---------------------------------------------------------------------------------------------------------------------
# ¦ LAMBDA SETTINGS
# ---------------------------------------------------------------------------------------------------------------------
variable "lambda_settings" {
  description = "HCL map of the Lambda-Settings."
  type = object({
    architecture          = optional(string, "x86_64")
    runtime               = optional(string, "python3.12")
    log_level             = optional(string, "INFO") # Logging level, e.g. "INFO"
    log_retention_in_days = optional(number, 7)      # Retention period for log files, in days
    error_forwarder = optional(object({
      target_name = string
      target_arn  = string
    }), null)
    memory_size  = optional(number, 512) # Size of the memory, in MB
    timeout      = optional(number, 720) # Timeout for the function, in seconds
    tracing_mode = optional(string, "Active")
    layer_arns = optional(map(any), {
      "aws_lambda_powertools_python_layer_arn" = "arn:aws:lambda:$region:017000801446:layer:AWSLambdaPowertoolsPythonV2:40"
    })
  })

  default = {
    architecture          = "x86_64"
    runtime               = "python3.12"
    log_level             = "INFO"
    log_retention_in_days = 7
    error_forwarder       = null
    memory_size           = 512
    timeout               = 720
    tracing_mode          = "Active"
    layer_arns = {
      "aws_lambda_powertools_python_layer_arn" = "arn:aws:lambda:$region:017000801446:layer:AWSLambdaPowertoolsPythonV2:40"
    }
  }

  validation {
    condition     = var.lambda_settings.architecture == null ? true : contains(["x86_64", "arm64"], var.lambda_settings.architecture)
    error_message = "Architecture must be one of: \"x86_64\", \"arm64\", or null."
  }

  validation {
    condition     = var.lambda_settings.log_level == null ? true : contains(["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"], var.lambda_settings.log_level)
    error_message = "log_level must be one of: \"DEBUG\", \"INFO\", \"WARNING\", \"ERROR\", \"CRITICAL\", or null."
  }

  validation {
    condition     = var.lambda_settings.log_retention_in_days == null ? true : contains([0, 1, 3, 5, 7, 14, 30, 60, 90, 120, 150, 180, 365, 400, 545, 731, 1827, 3653], var.lambda_settings.log_retention_in_days)
    error_message = "log_retention_in_days value must be one of: 0, 1, 3, 5, 7, 14, 30, 60, 90, 120, 150, 180, 365, 400, 545, 731, 1827, 3653, or null."
  }

  validation {
    condition     = var.lambda_settings.tracing_mode == null ? true : contains(["PassThrough", "Active"], var.lambda_settings.tracing_mode)
    error_message = "Value must be \"PassThrough\" or \"Active\"."
  }
}

# ---------------------------------------------------------------------------------------------------------------------
# ¦ VARIABLES
# ---------------------------------------------------------------------------------------------------------------------
variable "resource_tags" {
  description = "Tags for the resources"
  type        = map(string)
  default     = {}
}
