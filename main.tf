provider "aws" {
  region = "ap-south-1"
}


module "vpc" {
  source = "terraform-aws-modules/vpc/aws"

  name = "my-vpc"
  cidr = "10.0.0.0/16"

  azs             = ["${var.avail_zone}-1a", "${var.avail_zone}-1b", "${var.avail_zone}-1c"]
  private_subnets = ["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"]
  public_subnets  = ["10.0.101.0/24", "10.0.102.0/24", "10.0.103.0/24"]

  enable_nat_gateway = true
  enable_vpn_gateway = true

  tags = {
    Terraform = "true"
    Environment = "${var.env_prefix}"
  }
}

module "s3_bucket" {
  source = "terraform-aws-modules/s3-bucket/aws"

  bucket = "devopsritiks-s3-bucket-1"
  acl    = "private"

  control_object_ownership = true
  object_ownership         = "ObjectWriter"

  versioning = {
    enabled = false
  }
}

resource "aws_security_group" "ec2_sg" {
  name        = "ec2-security-group"
  description = "Allow SSH, HTTP, and HTTPS"
  vpc_id      = module.vpc.vpc_id

  tags = {
    Name = "ec2-security-group"
  }
}


resource "aws_security_group_rule" "allow_ssh" {
  security_group_id = aws_security_group.ec2_sg.id
  type              = "ingress"
  from_port         = 22
  to_port           = 22
  protocol         = "tcp"
  cidr_blocks      = ["0.0.0.0/0"]  # Open SSH to all (CHANGE THIS in production)
}

resource "aws_security_group_rule" "allow_http" {
  security_group_id = aws_security_group.ec2_sg.id
  type              = "ingress"
  from_port         = 80
  to_port           = 80
  protocol         = "tcp"
  cidr_blocks      = ["0.0.0.0/0"]
}

resource "aws_security_group_rule" "allow_https" {
  security_group_id = aws_security_group.ec2_sg.id
  type              = "ingress"
  from_port         = 443
  to_port           = 443
  protocol         = "tcp"
  cidr_blocks      = ["0.0.0.0/0"]
}


resource "aws_security_group_rule" "allow_all_outbound" {
  security_group_id = aws_security_group.ec2_sg.id
  type              = "egress"
  from_port         = 0
  to_port           = 0
  protocol         = "-1"
  cidr_blocks      = ["0.0.0.0/0"]
}


module "ec2_instance" {
  source  = "terraform-aws-modules/ec2-instance/aws"

  name = "my-instance-1"
  instance_type = var.instance_type
  key_name = var.ssh_key
  ami = var.ami_id
  monitoring = true

  vpc_security_group_ids = [aws_security_group.ec2_sg.id]
  subnet_id = module.vpc.public_subnets[0]

  associate_public_ip_address = true

  tags = {
    Terraform   = "true"
    Environment = "dev"
  }
}


resource "terraform_data" "ansible_provision" {
  depends_on = [module.ec2_instance]

  provisioner "local-exec" {
    working_dir = "/home/TestUser/wta_jenkins_docker-tf-ans/ansible"
    command = <<EOT
      # Ensure Ansible is installed locally
      if ! command -v ansible &> /dev/null; then
        echo "Installing Ansible..."
         sudo apt update
         sudo apt install software-properties-common
         sudo add-apt-repository --yes --update ppa:ansible/ansible
         sudo apt install ansible

      fi

      # Run Ansible Playbook from local machine
      ansible-playbook -i ${module.ec2_instance.public_ip}, --user=ubuntu --private-key=${var.ssh_key_path} my-playbook.yaml
    EOT
  }
}

