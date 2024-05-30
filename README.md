# AWS REPLACE_ME Terraform module

<!-- LOGO -->
<a href="https://acai.gmbh">
  <img src="https://github.com/acai-consulting/acai.public/raw/main/logo/logo_github_readme.png" alt="acai logo" title="ACAI" align="right" height="75" />
</a>

<!-- SHIELDS -->
[![Maintained by acai.gmbh][acai-shield]][acai-url]
[![Terraform Version][terraform-version-shield]][terraform-version-url]

<!-- DESCRIPTION -->
[Terraform][terraform-url] module to deploy REPLACE_ME resources on [AWS][aws-url]

<!-- ARCHITECTURE -->
## Architecture
![architecture][architecture-png]

<!-- FEATURES -->
## Features
* Creates a REPLACE_ME

<!-- USAGE -->
## Usage

### REPLACE_ME
```hcl
module "REPLACE_ME" {
  source  = "acai/REPLACE_ME/aws"
  version = "~> 1.0"

  input1 = "value1"
}
```

<!-- EXAMPLES -->
## Examples

* [`examples/complete`][example-complete-url]

<!-- BEGIN_TF_DOCS -->
## Requirements

| Name | Version |
|------|---------|
| <a name="requirement_terraform"></a> [terraform](#requirement\_terraform) | >= 1.0.0 |
| <a name="requirement_aws"></a> [aws](#requirement\_aws) | >= 4.0 |

## Providers

| Name | Version |
|------|---------|
| <a name="provider_aws"></a> [aws](#provider\_aws) | >= 4.0 |

## Modules

No modules.

## Resources

| Name | Type |
|------|------|
| [aws_caller_identity.this](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/data-sources/caller_identity) | data source |

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|

## Outputs

| Name | Description |
|------|-------------|
| <a name="output_account_id"></a> [account\_id](#output\_account\_id) | account\_id |
| <a name="output_input"></a> [input](#output\_input) | pass through input |
<!-- END_TF_DOCS -->

<!-- AUTHORS -->
## Authors

This module is maintained by [ACAI GmbH][acai-url] with help from [these amazing contributors][contributors-url]

<!-- LICENSE -->
## License

This module is licensed under Apache 2.0
<br />
See [LICENSE][license-url] for full details

<!-- COPYRIGHT -->
<br />
<br />
<p align="center">Copyright &copy; 2024 ACAI GmbH</p>

<!-- MARKDOWN LINKS & IMAGES -->
[acai-shield]: https://img.shields.io/badge/maintained_by-acai.gmbh-CB224B?style=flat
[acai-url]: https://acai.gmbh
[terraform-version-shield]: https://img.shields.io/badge/tf-%3E%3D0.15.0-blue.svg?style=flat&color=blueviolet
[terraform-version-url]: https://www.terraform.io/upgrade-guides/0-15.html
[architecture-png]: https://github.com/acai-consulting/REPLACE_ME/blob/main/docs/architecture.png?raw=true
[release-url]: https://github.com/acai-consulting/REPLACE_ME/releases
[contributors-url]: https://github.com/acai-consulting/REPLACE_ME/graphs/contributors
[license-url]: https://github.com/acai-consulting/REPLACE_ME/tree/main/LICENSE
[terraform-url]: https://www.terraform.io
[aws-url]: https://aws.amazon.com
[example-complete-url]: https://github.com/acai-consulting/REPLACE_ME/tree/main/examples/complete
