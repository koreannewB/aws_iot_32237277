#!/bin/bash
set -eux

dnf update -y
dnf install -y git python3 python3-pip

cd /home/ec2-user

git clone https://github.com/koreannewB/aws_iot_32237277.git

cd aws_iot_32237277

python3 -m venv venv
source venv/bin/activate

pip install --upgrade pip
pip install -r requirements.txt

nohup python3 main.py > smartgym.log 2>&1 &