variable "settings" {
  type = object({
    iam_role = optional(object({
      name                     = optional(string, "acai-account-cache-org-reader-role")
      path                     = optional(string, "/")
      permissions_boundary_arn = optional(string, null)
    }), {
      name                     = "acai-account-cache-org-reader-role"
      path                     = "/"
      permissions_boundary_arn = null
    })
    trusted_account_ids = optional(list(string), [])
    trusted_principals = optional(list(string), [])
  })
  default = {
    iam_role = {
      name                     = "acai-account-cache-org-reader-role"
      path                     = "/"
      permissions_boundary_arn = null
    }
    trusted_account_ids = []
    trusted_principals = []
  }
  validation {
    condition     = length(var.settings.trusted_account_ids) > 0 || length(var.settings.trusted_principals) > 0
    error_message = "Either 'trusted_account_ids' or 'trusted_principals' must be specified."
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
