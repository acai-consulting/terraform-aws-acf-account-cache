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
# ¦ VARIABLES
# ---------------------------------------------------------------------------------------------------------------------
variable "resource_tags" {
  description = "Tags for the resources"
  type        = map(string)
  default     = {}
}
