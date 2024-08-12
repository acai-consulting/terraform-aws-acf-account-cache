variable "settings" {
  type = object({
    lambda_layer_name = optional(string, "acai-account-cache-layer")
    architectures     = optional(list(string), ["x86_64"])
    runtimes          = optional(list(string), ["python3.10"])
  })
  default = {
    lambda_layer_name = "acai-account-cache-layer"
    architectures     = ["x86_64"]
    runtimes          = ["python3.10"]
  }

  validation {
    condition = (
      length(var.settings.lambda_layer_name) > 0
    )
    error_message = "The lambda_layer_name must not be empty."
  }
  validation {
    condition = alltrue([
      for arch in var.settings.architectures : contains(["x86_64", "arm64"], arch)
    ])
    error_message = "Architectures must be either 'x86_64' or 'arm64'."
  }
}
