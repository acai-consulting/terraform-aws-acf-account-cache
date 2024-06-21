data "template_file" "account_cache" {
  template = file("${path.module}/account_cache.yaml.tftpl")
  vars = {
    lambda_name                = var.settings.lambda_name
    lambda_layer_name          = var.settings.lambda_layer_name
    lambda_exec_role_with_path = replace("/${var.settings.lambda_iam_role.path}/${var.settings.lambda_iam_role.name}", "//", "/")
    policy_name                = replace(var.settings.lambda_iam_role.name, "role", "policy")
    ddb_name                   = var.settings.ddb_name
    api_key_name               = var.settings.api_settings.api_key_name
    api_name                   = var.settings.api_settings.api_name
  }
}
