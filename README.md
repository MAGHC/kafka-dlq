

**"대용량 트래픽 환경에서의 내결함성(Fault Tolerance) 보장 파이프라인 구축"**

## 프로젝트 배경 및 목적 
대규모 이커머스/물류 시스템(예: 주문 관리 시스템)에서는 초당 수많은 데이터가 실시간으로 쏟아집니다. 이때 필수 값이 누락되거나 타입이 맞지 않는 '불량 데이터'가 단 1건이라도 섞여 들어오면 전체 데이터 파이프라인이 멈춰버리는 치명적인 장애가 발생가능
이를 방지하기 위해, 에러가 발생해도 시스템이 멈추지 않고 불량 데이터만 따로 빼내어 안전하게 보관 및 분석할 수 있는 DLQ(Dead Letter Queue) 자동화 파이프라인을 구축

## 기술 스택 (Tech Stack)
Message Broker: Apache Kafka (단일 노드 KRaft 모드 경량화 도입)

Infrastructure: Docker, Docker-compose

Application (Data Pipeline): Python (confluent-kafka)

Data Processing: Pandas (마이크로 배치 및 엑셀 변환)


## 전체 시스템 아키텍처 및 데이터 흐름 (How)
시스템은 크게 3개의 독립적인 애플리케이션과 1개의 메시지 브로커로 구성되어 유기적으로 동작합니다.

[1단계] 데이터 발생 (Producer): 실시간 주문 데이터를 모사하여 정상 데이터와 필수 필드(price)가 누락된 불량 데이터를 섞어 메인 토픽(oms-order-events)으로 발행

[2단계] 실시간 검수 및 DLQ 라우팅 (Main Consumer): * 메인 토픽의 데이터를 실시간으로 소비(Consume)

데이터 파싱 중 예외(Exception)가 발생하면, 프로세스를 종료하지 않고 해당 원본 데이터와 에러 사유를 묶어 즉시 에러 전용 토픽(oms-order-dlq)으로 우회(Routing)

[3단계] 마이크로 배치 및 자동 백업 (Mini-Firehose Consumer):

에러 토픽(oms-order-dlq)만을 전문적으로 구독

클라우드 API 호출 비용을 최적화하기 위해 데이터가 들어올 때마다 건건이 저장하지 않고, 메모리에 일정 크기(Batch Size)만큼 버퍼링

버퍼가 차면 Pandas를 활용해 비개발자(운영 담당자)도 쉽게 읽을 수 있는 엑셀(.xlsx) 파일로 자동 변환하여 백업



### 실행순서

1. 카프카 실행 
docker-compose up -d
2. 에러가 발생해서 DLQ로 넘어오는 데이터를 낚아채서 엑셀로 만드는 py 먼저 대기
python dlq_to_excel.py
3. 메인 데이터를 받아서 검사하고, 불량품을 DLQ로 쳐낼 py 실행
python consumer.py
4. 데이터 쏘는 스크립트 실행 
python producer.py