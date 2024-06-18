

output "cf_template_map" {
  value = {
    "account_cache.yaml.tftpl" = replace(data.template_file.account_cache.rendered, "$$$", "$$")
  }
}
