# ---------------------------------------------------------------------------------------------------------------------
# ¦ REQUIREMENTS
# ---------------------------------------------------------------------------------------------------------------------
terraform {
  required_version = ">= 1.3.10"

  required_providers {
    aws = {
      source                = "hashicorp/aws"
      version               = ">= 4.47"
      configuration_aliases = []
    }
  }
}


# ---------------------------------------------------------------------------------------------------------------------
# ¦ LAMBDA LAYER
# ---------------------------------------------------------------------------------------------------------------------
data "archive_file" "lambda_layer_package" {
  type        = "zip"
  source_dir  = "${path.module}/files"
  output_path = "${path.module}/zipped_package.zip"
}

resource "aws_lambda_layer_version" "lambda_layer" {
  layer_name               = var.settings.layer_name
  filename                 = data.archive_file.lambda_layer_package.output_path
  compatible_runtimes      = var.settings.runtimes
  compatible_architectures = var.settings.architectures
  source_code_hash         = data.archive_file.lambda_layer_package.output_base64sha256
  lifecycle {
    ignore_changes = [filename]
  }
}

