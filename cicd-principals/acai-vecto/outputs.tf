

output "cf_template_map" {
  value = {
    "account_cache.yaml.tftpl" = replace(local.account_cache_rendered, "$$$", "$$")
  }
}
