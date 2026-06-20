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
  ingress {
  from_port   = 80
  to_port     = 80
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

resource "aws_instance" "web1" {
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
resource "aws_instance" "web2" {
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
resource "aws_lb" "smartgym" {
  name               = "smartgym-alb"
  internal           = false
  load_balancer_type = "application"

  security_groups = [
    aws_security_group.web.id
  ]

  subnets = sort(data.aws_subnets.default_vpc.ids)
}

resource "aws_lb_target_group" "smartgym" {
  name     = "smartgym-tg"
  port     = 8000
  protocol = "HTTP"

  vpc_id = data.aws_vpc.default.id

  health_check {
    path = "/"
    port = "8000"
  }
}

resource "aws_lb_target_group_attachment" "web1" {
  target_group_arn = aws_lb_target_group.smartgym.arn
  target_id        = aws_instance.web1.id
  port             = 8000
}

resource "aws_lb_target_group_attachment" "web2" {
  target_group_arn = aws_lb_target_group.smartgym.arn
  target_id        = aws_instance.web2.id
  port             = 8000
}

resource "aws_lb_listener" "http" {
  load_balancer_arn = aws_lb.smartgym.arn

  port     = 80
  protocol = "HTTP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.smartgym.arn
  }
}