from kafka import KafkaProducer, KafkaError
import json
import random
import time

def send_messages_to_kafka():
    """
    Sends multiple batches of messages to Kafka.

    Each batch consists of 10 messages, and there are 5 batches in total.
    The messages are randomly generated from a list of words.
    The Kafka producer is configured with the bootstrap servers and value serializer.

    Returns:
        None
    """
    # Kafka Producer 설정
    producer = KafkaProducer(
        bootstrap_servers=['kafka01:9092', 'kafka02:9093', 'kafka03:9094'],
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )

    words = ["apple", "banana", "cherry", "date", "elderberry", "fig", "grape", "honeydew", "kiwi", "lemon", "mango", "nectarine", "orange", "papaya", "quince", "raspberry", "strawberry", "tangerine", "ugli", "victoria plum", "watermelon", "xigua", "yuzu", "zucchini", "apricot", "blackberry", "coconut", "dragonfruit", "eggplant", "falafel"]

    # 5번 반복하여 메시지 전송
    for _ in range(5):
        # 각 반복에서 10개의 메시지를 전송
        for _ in range(10):
            message = ' '.join(random.choices(words, k=30))
            try:
                producer.send('test_topic', value={"message": message}).get(timeout=10)
            except KafkaError as e:
                print(f"Failed to send message: {e}")
                continue
            producer.flush()
        print(f"Batch of 10 messages sent to Kafka. Waiting 5 seconds before next batch...")
        time.sleep(5)  # 다음 배치 전에 5초 대기

    print("All messages sent to Kafka")

send_messages_to_kafka()
