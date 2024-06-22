locals {
  account_cache_rendered = templatefile("${path.module}//account_cache.yaml.tftpl", {
    lambda_name                = var.settings.lambda_name
    lambda_layer_name          = var.settings.lambda_layer_name
    lambda_exec_role_with_path = replace("/${var.settings.lambda_iam_role.path}/${var.settings.lambda_iam_role.name}", "////", "/")
    policy_name                = replace(var.settings.lambda_iam_role.name, "role", "policy")
    ddb_name                   = var.settings.ddb_name
    include_api_gateway        = var.settings.api_settings != null
  })
}
