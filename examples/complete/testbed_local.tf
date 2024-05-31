# ---------------------------------------------------------------------------------------------------------------------
# ¦ PROVIDER
# ---------------------------------------------------------------------------------------------------------------------
provider "aws" {
  region  = "eu-central-1"
  alias   = "org_mgmt"
  profile = "acai_testbed"
  assume_role {
    role_arn = "arn:aws:iam::471112796356:role/OrganizationAccountAccessRole" # ACAI AWS Testbed Org-Mgmt Account
  }
}

provider "aws" {
  region  = "eu-central-1"
  alias   = "core_logging"
  profile = "acai_testbed"
  assume_role {
    role_arn = "arn:aws:iam::590183833356:role/OrganizationAccountAccessRole" // ACAI AWS Testbed Core Logging Account
  }
}

provider "aws" {
  region  = "eu-central-1"
  alias   = "core_security"
  profile = "acai_testbed"
  assume_role {
    role_arn = "arn:aws:iam::992382728088:role/OrganizationAccountAccessRole" # ACAI AWS Testbed Core Security Account
  }
}

provider "aws" {
  region  = "eu-central-1"
  alias   = "workload"
  profile = "acai_testbed"
  assume_role {
    role_arn = "arn:aws:iam::767398146370:role/OrganizationAccountAccessRole" # ACAI AWS Testbed Workload Account
  }
}


provider "aws" {
  region  = "us-east-1"
  alias   = "workload_use1"
  profile = "acai_testbed"
  assume_role {
    role_arn = "arn:aws:iam::767398146370:role/OrganizationAccountAccessRole" # ACAI AWS Testbed Workload Account
  }
}

provider "aws" {
  region  = "eu-central-1"
  profile = "acai_testbed"
  assume_role {
    role_arn = "arn:aws:iam::767398146370:role/OrganizationAccountAccessRole" # ACAI AWS Testbed Workload Account
  }
}

