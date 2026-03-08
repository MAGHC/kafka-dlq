import json
from confluent_kafka import Consumer, Producer

c = Consumer({
    'bootstrap.servers': 'localhost:9092',
    'group.id': 'oms-group',
    'auto.offset.reset': 'earliest'
})
c.subscribe(['oms-order-events'])

dlq_p = Producer({'bootstrap.servers': 'localhost:9092'})
print("컨슈머 실행 중... (종료하려면 Ctrl+C)")

try:
    while True:
        msg = c.poll(1.0)
        if msg is None: continue
        
        raw_data = msg.value().decode('utf-8')
        
        try:
            data = json.loads(raw_data)
            if 'price' not in data:
                raise ValueError("필수 필드 'price'가 누락되었습니다.")
            print(f"✅ [정상 처리 완료] 주문 ID: {data['order_id']}")

        except Exception as e:
            print(f"🚨 [에러 발생! DLQ로 격리] 사유: {e}")
            dlq_message = {"error_reason": str(e), "original_data": raw_data}
            dlq_p.produce('oms-order-dlq', json.dumps(dlq_message).encode('utf-8'))
            dlq_p.flush()

except KeyboardInterrupt:
    pass
finally:
    c.close()