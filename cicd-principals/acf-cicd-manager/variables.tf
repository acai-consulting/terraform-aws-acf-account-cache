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
    api_settings = optional(object({
      api_key_name = optional(string, "acai-cache-key")
      api_name     = optional(string, "acai-cache")
    }), null)
  })
  default = {
    lambda_name       = "acai-account-cache"
    lambda_layer_name = "acai-account-cache-layer"
    lambda_iam_role = {
      name = "acai-account-cache-lambda-role"
      path = "/"
    },
    ddb_name = "acai-account-cache"
    api_settings = {
      api_key_name = "acai-cache-key"
      api_name     = "acai-cache"
    }
  }
}

