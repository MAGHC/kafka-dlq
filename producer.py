import json
import random
import time
from confluent_kafka import Producer

p = Producer({'bootstrap.servers': 'localhost:9092'})
print("데이터 발행을 시작합니다...")

for i in range(10):
    if random.choice([True, False]):
        data = {"order_id": i, "price": 10000, "status": "CREATED"} # 정상
    else:
        data = {"order_id": i, "status": "CREATED"} # 불량 (price 없음)
        
    p.produce('oms-order-events', json.dumps(data).encode('utf-8'))
    time.sleep(1)

p.flush()
print("데이터 발행 완료!")