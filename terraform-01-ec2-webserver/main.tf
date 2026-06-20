# Read the default VPC instead of creating a new network for the first beginner example.
data "aws_vpc" "default" {
  default = true
}

# Read all subnets that belong to the default VPC.
data "aws_subnets" "default_vpc" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.default.id]
  }
}

# Read the latest Amazon Linux 2023 AMI from the public SSM parameter store.
data "aws_ssm_parameter" "al2023_ami" {
  name = "/aws/service/ami-amazon-linux-latest/al2023-ami-kernel-default-x86_64"
}

locals {
  selected_subnet_id = sort(data.aws_subnets.default_vpc.ids)[0]

  common_tags = {
    Course  = "cloud-computing-aws"
    Example = "terraform-01-ec2-webserver"
  }
}

resource "aws_security_group" "web" {
  name        = "${var.name_prefix}-web-sg"
  description = "Allow HTTP access to the single EC2 web server"
  vpc_id      = data.aws_vpc.default.id

  ingress {
    description = "Allow Smart Gym"
    from_port   = 8000
    to_port     = 8000
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
}

  tags = merge(local.common_tags, {
    Name = "${var.name_prefix}-web-sg"
  })
}

resource "aws_instance" "web" {
  ami           = data.aws_ssm_parameter.al2023_ami.value
  instance_type = var.instance_type

  subnet_id = local.selected_subnet_id

  associate_public_ip_address = true
  vpc_security_group_ids      = [aws_security_group.web.id]

  user_data = templatefile("${path.module}/user-data.sh", {
    name_prefix = var.name_prefix
  })

  tags = merge(local.common_tags, {
    Name = "${var.name_prefix}-web"
  })
}
