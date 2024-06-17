variable "api_settings" {
  type = object({
    api_key_name      = string
    api_name          = string
    api_description   = string
    api_stage_name    = optional(string, "v1")
    api_endpoint_name = string
  })
}

variable "lambda_settings" {
  type = object({
    arn        = string
    invoke_arn = string
  })
}

# ---------------------------------------------------------------------------------------------------------------------
# ¦ VARIABLES
# ---------------------------------------------------------------------------------------------------------------------
variable "resource_tags" {
  description = "Tags for the resources"
  type        = map(string)
  default     = {}
}
