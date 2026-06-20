output "instance1_id" {
  value = aws_instance.web1.id
}

output "instance2_id" {
  value = aws_instance.web2.id
}

output "instance1_public_ip" {
  value = aws_instance.web1.public_ip
}

output "instance2_public_ip" {
  value = aws_instance.web2.public_ip
}

output "instance1_public_dns" {
  value = aws_instance.web1.public_dns
}

output "instance2_public_dns" {
  value = aws_instance.web2.public_dns
}
output "alb_dns" {
  value = aws_lb.smartgym.dns_name
}