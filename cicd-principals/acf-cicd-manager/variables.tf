variable "settings" {
  type = object({
    lambda_name       = optional(string, "acai-account-cache")
    lambda_layer_name = optional(string, "acai-account-cache-layer")
    lambda_iam_role = optional(object({
      name = optional(string, "acai-account-cache-lambda-role")
      path = optional(string, "/")
      }), {
      name = "acai-account-cache-lambda-role"
      path = "/"
    })
    ddb_name = optional(string, "acai-account-cache")
    api_settings = optional(map(string), null)
  })
  default = {
    lambda_name       = "acai-account-cache"
    lambda_layer_name = "acai-account-cache-layer"
    lambda_iam_role = {
      name = "acai-account-cache-lambda-role"
      path = "/"
    },
    ddb_name = "acai-account-cache"
    api_settings = null
  }
}

