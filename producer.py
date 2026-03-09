import json
import random
import time
from confluent_kafka import Producer
from confluent_kafka.admin import AdminClient, NewTopic # 관리자 도구 추가

KAFKA_BROKERS = 'localhost:9092,localhost:9093,localhost:9094'
MAIN_TOPIC = 'oms-order-events'

# --- [Phase 1.5] 핵심: 실무형 토픽 관리 ---
print("⚙️ 카프카 클러스터 토픽 상태를 확인합니다...")
admin_client = AdminClient({'bootstrap.servers': KAFKA_BROKERS})
topic_metadata = admin_client.list_topics(timeout=15)

if MAIN_TOPIC not in topic_metadata.topics:
    # 토픽이 없으면, 파티션 3개, 복제본 3개로 아주 튼튼하게 생성!
    new_topic = NewTopic(MAIN_TOPIC, num_partitions=3, replication_factor=3)
    admin_client.create_topics([new_topic])
    print(f"✅ [{MAIN_TOPIC}] 토픽을 Replication Factor=3으로 튼튼하게 생성했습니다.")
else:
    print(f"✅ [{MAIN_TOPIC}] 토픽이 이미 존재합니다.")
# ---------------------------------------------

p = Producer({
    'bootstrap.servers': KAFKA_BROKERS,
    'acks': 'all',
    'enable.idempotence': True,
    'retries': 5 # 에러 나도 5번까지는 재시도해라!
})

print("🔥 [Phase 1] 고가용성 클러스터로 데이터 발행을 시작합니다...")

for i in range(100): 
    if random.choice([True, False]):
        data = {"order_id": i, "price": 10000, "status": "CREATED"} 
    else:
        data = {"order_id": i, "status": "CREATED"} 
        
    p.produce(MAIN_TOPIC, json.dumps(data).encode('utf-8'))
    time.sleep(1)

p.flush()