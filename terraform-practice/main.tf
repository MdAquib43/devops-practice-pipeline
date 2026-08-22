terraform {
  required_version = ">= 1.0"

  required_providers {
    local = {
      source = "hashicorp/local"
    }

    aws = {
      source = "hashicorp/aws"
    }
  }

  backend "s3" {
    bucket       = "aquib-terraform-state-237162087889"
    key          = "terraform-practice/terraform.tfstate"
    region       = "us-east-1"
    use_lockfile = true
  }
}

provider "aws" {
  region = "us-east-1"
}

module "file" {
  source = "./modules/file"

  file_name    = "module-file.txt"
  file_content = "Hello from my Terraform module!"
}

resource "aws_s3_bucket" "import_demo" {
  bucket = "aquib-terraform-import-237162087889"
}