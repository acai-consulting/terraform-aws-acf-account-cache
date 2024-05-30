variable "settings" {
  type = object({
    iam_role = object({
      name                     = string
      path                     = optional(string, "/")
      permissions_boundary_arn = optional(string, null)
    })
    trusted_account_ids = optional(list(string), [])
    trusted_principals = optional(list(string), [])
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
