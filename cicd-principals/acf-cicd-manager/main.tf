data "template_file" "account_cache" {
  template = file("${path.module}/account_cache.yaml.tftpl")
  vars = {
  }
}
