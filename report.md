aws 기말 과제 
고가용성을 지원하는 새로운 웹 서비스 또는 웹사이트 개발,

32237277 노건우

이번 과제는 iot시스템에서 라즈베리를 통해 주변의 변화를 센서로 인식하여
웹사이트에 동적으로 반응하는 사이트를 aws와 과제 조건에 맞춰 개조

iotsmartgym 기능
1.카메라로 사람인식시 웹사이트 신호
2.가속도 센서 인식시 웹사이트 신호
3.초음파 센서 인식시 웹사이트신호 
4.n그록이라는 기능으로 인터넷공유

변경점
카메라로 사람인식->mp4영상으로 교체

[오류]
ec2에서 영상yolo모델 너무 큼
->mp4만쓰고 yolo제거

센서-> 코드상 변경
n그록->aws으로 공유



성능변화 테스트

1. 1개의 ec2로 각 100명 500명 1000명 진입시 벤치마킹
2. 2개의 ec2로 alb로 분배하여 100,500,1000명 진입시 벤치마킹 
3. 2개의 테스트 성능 비교



1-1 
    1개의ec2로 웹 사이트 올리기
    4번과제의 내용을 가져와서 사용

    0#
    aws sts get-caller-identity

    권한이 있는지 확인
    1#
    terraform init
    terraform validate
    terraform plan

    Terraform has been successfully initialized!

    You may now begin working with Terraform. Try running "terraform plan" to see
    any changes that are required for your infrastructure. All Terraform commands
    should now work.

    If you ever set or change modules or backend configuration for Terraform,
    rerun this command to reinitialize your working directory. If you forget, other
    commands will detect it and remind you to do so if necessary.

    Success! The configuration is valid.

    첫번째 명령어로 이번과제로 사용할 테라폼이 변경후 문맥상 막히는게 없는것을 확인
    
    2# 
    terraform apply

    Apply complete! Resources: 2 added, 0 changed, 0 destroyed.

    Outputs:

    instance_id = "i-0dd5f13e540c38eb7"
    instance_public_dns = "ec2-54-175-59-103.compute-1.amazonaws.com"
    instance_public_ip = "54.175.59.103"
    security_group_id = "sg-0a7540954f8cb8349"
    selected_subnet_id = "subnet-05f98bc64da45111d"

    테라폼 plan으로 저장한 계획을 실행
    성공적으로 실행됨
    인스턴스 생성 sg생성 서브넷 생성

    3#
    ec2내부 ssh에서 
    cloud-init status 명령어 실행
    status: running [현재 설치중]
    이후 
    status:done [완료됨]

    http://54.209.43.122:8000 사이트 주소로 iot_smart_gym 정상 작동확인





































실제 테스트과정 


1. 가상환경설치


2.가상환경 활성화
Windows:venv\Scripts\activate
Mac / Linux:source venv/bin/activate