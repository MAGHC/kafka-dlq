import json
import pandas as pd
from datetime import datetime
from confluent_kafka import Consumer

# DLQ 토픽만 전문적으로 읽어들이는 Consumer 설정
c = Consumer({
    'bootstrap.servers': 'localhost:9092,localhost:9093,localhost:9094',
    'group.id': 'dlq-backup-group',
    'auto.offset.reset': 'earliest'
})
c.subscribe(['oms-order-dlq'])

print("🔥 [Mini-Firehose] DLQ 데이터 백업 파이프라인 가동 중... (종료: Ctrl+C)")

buffer = []
BATCH_SIZE = 3  # 에러 데이터 3건이 모이면 한 번에 엑셀로 저장 (테스트용)

try:
    while True:
        msg = c.poll(1.0)
        if msg is None: continue
        
        # DLQ 데이터 파싱
        raw_data = msg.value().decode('utf-8')
        dlq_data = json.loads(raw_data)
        
        # 버퍼(리스트)에 추가
        buffer.append({
            "발생시간": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "에러_사유": dlq_data['error_reason'],
            "원본_데이터": dlq_data['original_data']
        })
        
        print(f"📥 [버퍼 적재] 현재 버퍼: {len(buffer)}/{BATCH_SIZE}")

        # 설정한 개수만큼 모이면 엑셀로 저장!
        if len(buffer) >= BATCH_SIZE:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"DLQ_Backup_{timestamp}.xlsx"
            
            # Pandas를 이용해 엑셀 파일 생성
            df = pd.DataFrame(buffer)
            df.to_excel(filename, index=False)
            
            print(f"💾 [백업 완료] {BATCH_SIZE}건의 에러 데이터를 '{filename}'로 저장했습니다!")
            
            # 저장 후 버퍼 비우기 (초기화)
            buffer.clear()

except KeyboardInterrupt:
    print("백업 파이프라인을 종료합니다.")
finally:
    c.close()