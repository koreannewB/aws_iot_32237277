[AWS 기반 IoT Smart Gym 고가용성(HA) 웹 서비스 구축 및 성능 분석]
본 프로젝트는 이전 IoT Smart Gym 프로젝트를 기반으로 AWS EC2, ALB, Terraform을 이용하여 고가용성(HA) 환경을 구축하도록 확장한 프로젝트이다.

32237277 노건우

이번 과제는 기존 IoT Smart Gym 프로젝트를 AWS 환경으로 이전하고, Terraform과 ALB를 활용하여 고가용성을 지원하는 웹 서비스로 확장하는 것을 목표로 하였다.

iotsmartgym 기능
1.카메라로 사람인식시 웹사이트 신호
2.가속도 센서 인식시 웹사이트 신호
3.초음파 센서 인식시 웹사이트신호 
4.n그록이라는 기능으로 인터넷공유

프로젝트 변경 사항

1. 기존 YOLO 기반 사람 인식 기능은 EC2 환경에서 모델 크기와 설치 용량 문제로 인해 MP4 영상 재생 방식으로 대체하였다.

2. 실제 센서 입력 대신 코드 내 시뮬레이션 데이터를 사용하도록 수정하였다.

3. 기존 ngrok 기반 인터넷 공유 방식을 AWS EC2 기반 서비스 배포 방식으로 변경하였다.

4. AWS ALB(Application Load Balancer)를 이용하여 고가용성 환경을 구축하였다.




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


2-1
    이후 2개의 ec2로 고가용성 만들기 


    1#
        기존 1개의 ec2복사후 alb와 리스너 타겟그룹 ec2 2개 생성

    
    2#
        기존 처럼 
        terraform init
        terraform validate
        terraform plan
        실행

    3#
     테라폼 apply

        alb_dns = "smartgym-alb-1484793818.us-east-1.elb.amazonaws.com"
        instance1_id = "i-0da34736dbe9b4ed3"
        instance1_public_dns = "ec2-54-172-111-9.compute-1.amazonaws.com"
        instance1_public_ip = "54.172.111.9"
        instance2_id = "i-09af3588e0c5bf680"
        instance2_public_dns = "ec2-3-95-182-85.compute-1.amazonaws.com"
        instance2_public_ip = "3.95.182.85"
        2개의 인스턴스 생성확인
        aws 웹상 타겟그룹 Healthy 확인
        http://smartgym-alb-1484793818.us-east-1.elb.amazonaws.com/ 확인
        "TargetHealthDescriptions": [
            {
                "Target": {
                    "Id": "i-09af3588e0c5bf680",
                    "Port": 8000
                },
                "HealthCheckPort": "8000",
                "TargetHealth": {
                    "State": "healthy"
                },
                "AdministrativeOverride": {
                    "State": "no_override",
                    "Reason": "AdministrativeOverride.NoOverride",
                    "Description": "No override is currently active on target"
                }
            },
            {
                "Target": {
                    "Id": "i-0da34736dbe9b4ed3",
                    "Port": 8000
                },
                "HealthCheckPort": "8000",
                "TargetHealth": {
                    "State": "healthy"
                },
                "AdministrativeOverride": {
                    "State": "no_override",
                    "Reason": "AdministrativeOverride.NoOverride",
    :

[[[[[벤치]]]]]
    1. 100명 500명 1000명 순서로 밴치
    2. 고가용성확인을 위해 aws웹상 1개의 인스턴스 종료후 다시 벤치

[가독성을위해 나온 코드는 아래쪽 배치]


# 2개의 ec2

    100명 동시접속 
    항목	결과
    총 요청	5000
    성공	5000 (100%)
    평균 응답시간	0.1976초
    최대 응답시간	0.635초
    처리량	497 req/sec
    오류	0

    500명 동시접속 
    항목	결과
    동시 접속 수	500명
    총 요청 수	10,000
    성공 요청 수	10,000 (100%)
    평균 응답 시간	0.445초
    최대 응답 시간	2.100초
    처리량 (Requests/sec)	899 req/sec
    오류 수	0

    1000명 동시접속 결과
    항목	결과
    동시 접속 수	1000명
    총 요청 수	20,000
    성공 요청 수	20,000 (100%)
    평균 응답 시간	0.958초
    최대 응답 시간	4.394초
    처리량 (Requests/sec)	920.6 req/sec
    오류 수	0


결과 분석
    alb를 이용해서 2개의 ec2로 각각 100명 500명 1000명 동시 사용자를 분석했다.
    모든 환경에서 100%로 접속하지만 동시접속자수가늘면서 응답시간이 늘어나는 
    변화를 보였다 허나 오류없이 서비스를 제공받았다.

# 2개의 ec2-> 1개인스턴스오류 발생
    개요 aws웹상 1개의 인스턴스를 중지하였다.
    타겟 그룹네 헬스체크 시 1개의 인스턴스가 작동하지않음을 확인했다.
    허나 http://smartgym-alb-1484793818.us-east-1.elb.amazonaws.com
    로 접속시 여전히 접속은 가능했다.

    장애 상태(EC2 1대) - 100명
    항목	결과
    동시 접속 수	100명
    총 요청 수	5,000
    성공 요청 수	5,000 (100%)
    평균 응답 시간	0.226초
    최대 응답 시간	0.842초
    처리량 (Requests/sec)	419.6 req/sec
    오류 수	0

    장애 상태(EC2 1대) - 500명
    항목	결과
    동시 접속 수	500명
    총 요청 수	10,000
    성공 요청 수	10,000 (100%)
    평균 응답 시간	0.796초
    최대 응답 시간	1.905초
    처리량 (Requests/sec)	603.7 req/sec
    오류 수	0

    장애 상태 (EC2 1대) - 1000명
    항목	결과
    동시 접속 수	1000명
    총 요청 수	20,000
    성공 요청 수	20,000 (100%)
    평균 응답 시간	2.079초
    최대 응답 시간	9.601초
    처리량 (Requests/sec)	461.8 req/sec
    오류 수	0


최종 비교표
환경	동시접속	평균 응답시간	최대 응답시간	처리량 (Req/sec)	성공률
EC2×2	100	        0.198초	        0.635초	        497	100%
EC2×2	500	        0.445초	        2.100초	        899	100%
EC2×2	1000	    0.958초	        4.394초	        921	100%
EC2×1 (장애)100	    0.226초	        0.842초	        420	100%
EC2×1 (장애)500	    0.796초	        1.905초	        604	100%
EC2×1 (장애)1000	2.079초	        9.601초	        462	100%




# [결론]

    최종 결론
    1.기존 IoT Smart Gym 프로젝트를 AWS 환경으로 이식하였다.

    2.기존 ngrok 기반 공유 방식을 AWS EC2 기반 서비스로 변경하였다.

    3.단일 EC2 환경과 ALB를 이용한 다중 EC2 환경을 구축하였다.

    4.ALB를 통해 트래픽을 두 개의 EC2 인스턴스로 분산할 수 있음을 확인하였다.

    5.장애 상황을 가정하여 EC2 한 대를 중지한 뒤에도 서비스가 계속 동작함을          확인하였다.

    6.벤치마킹 결과 모든 테스트에서 100% 요청 성공률을 유지하였다.
    특히 1000명 동시 접속 환경에서 2대 구성은 평균 응답시간 0.958초, 1대 구성은 2.079초로 측정되어 다중 인스턴스 구조가 더 우수한 성능과 안정성을 제공함을 확인하였다.

    7.이를 통해 AWS의 ALB를 활용한 고가용성(High Availability) 구조를 직접 구축하고 검증할 수 있었다.





# 부록 


    실제 테스트 명령어

    terraform init
    terraform validate
    terraform plan
    terraform apply

    100명 동시 접속
    hey -n 5000 -c 100 http://ALB_DNS/

    500명 동시 접속
    hey -n 10000 -c 500 http://ALB_DNS/

    1000명 동시 접속
    hey -n 20000 -c 1000 http://ALB_DNS/


    2개의 인스턴스 100명 동시접속
    Summary:
    Total:        10.0601 secs
    Slowest:      0.6350 secs
    Fastest:      0.1818 secs
    Average:      0.1976 secs
    Requests/sec: 497.0106

    Total data:   21390000 bytes
    Size/request: 4278 bytes

    Response time histogram:
    0.182 [1]     |
    0.227 [4891]  |■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
    0.272 [8]     |
    0.318 [0]     |
    0.363 [0]     |
    0.408 [5]     |
    0.454 [4]     |
    0.499 [25]    |
    0.544 [45]    |
    0.590 [17]    |
    0.635 [4]     |


    Latency distribution:
    10% in 0.1861 secs
    25% in 0.1879 secs
    50% in 0.1903 secs
    75% in 0.1934 secs
    90% in 0.1989 secs
    95% in 0.2034 secs
    99% in 0.5194 secs

    Details (average, fastest, slowest):
    DNS+dialup:   0.0038 secs, 0.1818 secs, 0.6350 secs
    DNS-lookup:   0.0003 secs, 0.0000 secs, 0.0116 secs
    req write:    0.0000 secs, 0.0000 secs, 0.0007 secs
    resp wait:    0.1896 secs, 0.1807 secs, 0.3133 secs
    resp read:    0.0032 secs, 0.0000 secs, 0.1052 secs

    Status code distribution:
    [200] 5000 responses
    2개의 인스턴스 500명 동시접속

    Summary:
    Total:        11.1236 secs
    Slowest:      2.0995 secs
    Fastest:      0.1818 secs
    Average:      0.4448 secs
    Requests/sec: 898.9913

    Total data:   42780000 bytes
    Size/request: 4278 bytes

    Response time histogram:
    0.182 [1]     |
    0.374 [4423]  |■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
    0.565 [2755]  |■■■■■■■■■■■■■■■■■■■■■■■■■
    0.757 [2209]  |■■■■■■■■■■■■■■■■■■■■
    0.949 [307]   |■■■
    1.141 [1]     |
    1.332 [44]    |
    1.524 [192]   |■■
    1.716 [56]    |■
    1.908 [1]     |
    2.100 [11]    |


    Latency distribution:
    10% in 0.1997 secs
    25% in 0.2299 secs
    50% in 0.4223 secs
    75% in 0.5843 secs
    90% in 0.6577 secs
    95% in 0.7911 secs
    99% in 1.5180 secs

    Details (average, fastest, slowest):
    DNS+dialup:   0.0124 secs, 0.1818 secs, 2.0995 secs
    DNS-lookup:   0.0013 secs, 0.0000 secs, 0.0472 secs
    req write:    0.0000 secs, 0.0000 secs, 0.0010 secs
    resp wait:    0.2902 secs, 0.1804 secs, 1.1227 secs
    resp read:    0.1421 secs, 0.0000 secs, 1.5375 secs

    Status code distribution:

    [200] 10000 responses

    2개의 인스턴스 1000명 동시접속
    Summary:
    Total:        21.7244 secs
    Slowest:      4.3940 secs
    Fastest:      0.1817 secs
    Average:      0.9576 secs
    Requests/sec: 920.6224

    Total data:   85560000 bytes
    Size/request: 4278 bytes

    Response time histogram:
    0.182 [1]     |
    0.603 [7282]  |■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
    1.024 [5393]  |■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
    1.445 [3125]  |■■■■■■■■■■■■■■■■■
    1.867 [1893]  |■■■■■■■■■■
    2.288 [1167]  |■■■■■■
    2.709 [326]   |■■
    3.130 [685]   |■■■■
    3.552 [0]     |
    3.973 [22]    |
    4.394 [106]   |■


    Latency distribution:
    10% in 0.1971 secs
    25% in 0.3559 secs
    50% in 0.7470 secs
    75% in 1.2708 secs
    90% in 2.0507 secs
    95% in 2.4233 secs
    99% in 3.0186 secs

    Details (average, fastest, slowest):
    DNS+dialup:   0.0100 secs, 0.1817 secs, 4.3940 secs
    DNS-lookup:   0.0020 secs, 0.0000 secs, 0.0549 secs
    req write:    0.0000 secs, 0.0000 secs, 0.0011 secs
    resp wait:    0.4818 secs, 0.1807 secs, 3.4702 secs
    resp read:    0.4485 secs, 0.0000 secs, 2.3044 secs

    Status code distribution:
    [200] 20000 responses


    2개의 인스턴스 + 1개 인스턴스 중지 100명 동시접속

    Summary:
    Total:        11.9160 secs
    Slowest:      0.8422 secs
    Fastest:      0.1829 secs
    Average:      0.2260 secs
    Requests/sec: 419.6044

    Total data:   21390000 bytes
    Size/request: 4278 bytes

    Response time histogram:
    0.183 [1]     |
    0.249 [4341]  |■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
    0.315 [550]   |■■■■■
    0.381 [3]     |
    0.447 [2]     |
    0.513 [5]     |
    0.578 [16]    |
    0.644 [77]    |■
    0.710 [0]     |
    0.776 [0]     |
    0.842 [5]     |


    Latency distribution:
    10% in 0.1919 secs
    25% in 0.1994 secs
    50% in 0.2157 secs
    75% in 0.2314 secs
    90% in 0.2565 secs
    95% in 0.2726 secs
    99% in 0.5923 secs

    Details (average, fastest, slowest):
    DNS+dialup:   0.0047 secs, 0.1829 secs, 0.8422 secs
    DNS-lookup:   0.0009 secs, 0.0000 secs, 0.0404 secs
    req write:    0.0000 secs, 0.0000 secs, 0.0003 secs
    resp wait:    0.2012 secs, 0.1819 secs, 0.8142 secs
    resp read:    0.0198 secs, 0.0000 secs, 0.1009 secs

    Status code distribution:
    [200] 5000 responses

    2개의 인스턴스 + 1개 인스턴스 중지 500명 동시접속


    Summary:
    Total:        16.5633 secs
    Slowest:      1.9050 secs
    Fastest:      0.1828 secs
    Average:      0.7958 secs
    Requests/sec: 603.7458

    Total data:   42780000 bytes
    Size/request: 4278 bytes

    Response time histogram:
    0.183 [1]     |
    0.355 [127]   |■
    0.527 [9]     |
    0.699 [216]   |■
    0.872 [9255]  |■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
    1.044 [163]   |■
    1.216 [0]     |
    1.388 [0]     |
    1.561 [0]     |
    1.733 [0]     |
    1.905 [229]   |■


    Latency distribution:
    10% in 0.7289 secs
    25% in 0.7427 secs
    50% in 0.7844 secs
    75% in 0.8048 secs
    90% in 0.8397 secs
    95% in 0.8542 secs
    99% in 1.8472 secs

    Details (average, fastest, slowest):
    DNS+dialup:   0.0129 secs, 0.1828 secs, 1.9050 secs
    DNS-lookup:   0.0013 secs, 0.0000 secs, 0.0385 secs
    req write:    0.0000 secs, 0.0000 secs, 0.0003 secs
    resp wait:    0.4879 secs, 0.1816 secs, 1.3073 secs
    resp read:    0.2950 secs, 0.0000 secs, 0.6098 secs

    Status code distribution:
    [200] 10000 responses


    2개의 인스턴스 + 1개 인스턴스 중지 1000명 동시접속

    Summary:
    Total:        43.3109 secs
    Slowest:      9.6009 secs
    Fastest:      0.1831 secs
    Average:      2.0786 secs
    Requests/sec: 461.7770

    Total data:   85560000 bytes
    Size/request: 4278 bytes

    Response time histogram:
    0.183 [1]     |
    1.125 [1180]  |■■■
    2.067 [15145] |■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
    3.008 [1419]  |■■■■
    3.950 [951]   |■■■
    4.892 [113]   |
    5.834 [297]   |■
    6.776 [654]   |■■
    7.717 [226]   |■
    8.659 [2]     |
    9.601 [12]    |


    Latency distribution:
    10% in 1.4529 secs
    25% in 1.6401 secs
    50% in 1.7626 secs
    75% in 1.8967 secs
    90% in 3.1588 secs
    95% in 5.5531 secs
    99% in 7.1259 secs

    Details (average, fastest, slowest):
    DNS+dialup:   0.0115 secs, 0.1831 secs, 9.6009 secs
    DNS-lookup:   0.0019 secs, 0.0000 secs, 0.0581 secs
    req write:    0.0000 secs, 0.0000 secs, 0.0009 secs
    resp wait:    0.9611 secs, 0.1816 secs, 3.8969 secs
    resp read:    1.0866 secs, 0.0000 secs, 8.6276 secs

    Status code distribution:
    [200] 20000 responses

