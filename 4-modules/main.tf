
provider "aws" {
  region = "us-east-1"
}

terraform {
  required_providers {
    aws = {
      source = "hashicorp/aws"
    }
  }
}

locals {
  extra_tag = "extra-tag"
}

resource "aws_instance" "example" {
  for_each = var.service_names

  ami                    = "ami-0e86e20dae9224db8" # Ubuntu 20.04 LTS // us-east-1
  instance_type          = "t2.micro"
  subnet_id              = module.vpc.public_subnets[0]
  vpc_security_group_ids = [module.terraform-sg.security_group_id] 
  associate_public_ip_address = true 

  tags = {
    ExtraTag = local.extra_tag
    Name     = "EC2-${each.key}"
  }
}


resource "aws_instance" "example1" {
  ami                    = "ami-0e86e20dae9224db8" # Ubuntu 20.04 LTS // us-east-1
  instance_type          = "t2.micro"
  subnet_id              = module.vpc.public_subnets[1]
  vpc_security_group_ids = [module.terraform-sg.security_group_id] 
  associate_public_ip_address = true 

  tags = {
    ExtraTag = local.extra_tag
    Name     = "EC2-us-east-1b"
  }
}


resource "aws_cloudwatch_log_group" "ec2_log_group" {
  for_each = var.service_names


  tags = {
    Environment = "test"
    Service     = each.key
  }
  lifecycle {
    create_before_destroy = true
  }
}