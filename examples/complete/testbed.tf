# ---------------------------------------------------------------------------------------------------------------------
# ¦ PROVIDER
# ---------------------------------------------------------------------------------------------------------------------
provider "aws" {
  region = "eu-central-1"
  alias  = "org_mgmt"
  assume_role {
    role_arn = "arn:aws:iam::471112796356:role/OrganizationAccountAccessRole" # ACAI AWS Testbed Org-Mgmt Account
  }
}

provider "aws" {
  region = "eu-central-1"
  alias  = "core_logging"
  assume_role {
    role_arn = "arn:aws:iam::590183833356:role/OrganizationAccountAccessRole" // ACAI AWS Testbed Core Logging Account
  }
}

provider "aws" {
  region = "eu-central-1"
  alias  = "core_security"
  assume_role {
    role_arn = "arn:aws:iam::992382728088:role/OrganizationAccountAccessRole" # ACAI AWS Testbed Core Security Account
  }
}

provider "aws" {
  region = "eu-central-1"
  alias  = "workload"
  assume_role {
    role_arn = "arn:aws:iam::767398146370:role/OrganizationAccountAccessRole" # ACAI AWS Testbed Workload Account
  }
}

provider "aws" {
  region = "eu-central-1"
  assume_role {
    role_arn = "arn:aws:iam::767398146370:role/OrganizationAccountAccessRole" # ACAI AWS Testbed Workload Account
  }
}

# ---------------------------------------------------------------------------------------------------------------------
# ¦ BACKEND
# ---------------------------------------------------------------------------------------------------------------------
terraform {
  backend "remote" {
    organization = "acai"
    hostname     = "app.terraform.io"

    workspaces {
      name = "aws-testbed"
    }
  }
}
