variable "org_reader_role_arn" {
  type = string
}

variable "ddb_name" {
  type = string
}

variable "cache_lambda_layer_arn" {
  type = string
}

variable "cache_lambda_permission_policy_arn" {
  type = string
}

# ---------------------------------------------------------------------------------------------------------------------
# ¦ LAMBDA SETTINGS
# ---------------------------------------------------------------------------------------------------------------------
variable "lambda_settings" {
  description = "HCL map of the Lambda-Settings."
  type = object({
    architecture          = optional(string, "x86_64")
    runtime               = optional(string, "python3.10")
    log_level             = optional(string, "INFO") # Logging level, e.g. "INFO"
    log_retention_in_days = optional(number, 7)      # Retention period for log files, in days
    error_forwarder = optional(object({
      target_name = string
      target_arn  = string
    }), null)
    memory_size  = optional(number, 512) # Size of the memory, in MB
    timeout      = optional(number, 720) # Timeout for the function, in seconds
    tracing_mode = optional(string, "Active")
  })

  default = {
    architecture          = "x86_64"
    runtime               = "python3.10"
    log_level             = "INFO"
    log_retention_in_days = 7
    error_forwarder       = null
    memory_size           = 512
    timeout               = 720
    tracing_mode          = "Active"
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
