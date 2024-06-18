data "template_file" "account_cache" {
  template = file("${path.module}/account_cache.yaml.tftpl")
  vars = {
    lambda_name       = var.settings.lambda_name
    lambda_layer_name = var.settings.lambda_layer_name
    lambda_iam_role_name = var.settings.lambda_iam_role.name
    lambda_iam_role_path = var.settings.lambda_iam_role.path
    ddb_name          = var.settings.ddb_name
    kms_cmk_alias = var.settings.kms_cmk.alias_name
    api_key_name = var.settings.api_settings.api_key_name
    api_name = var.settings.api_settings.api_key_name
  }
}
