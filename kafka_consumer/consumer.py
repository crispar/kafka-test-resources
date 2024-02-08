import os
from flask import Flask
from kafka import KafkaConsumer, KafkaProducer
import threading
import json
import itertools
import logging
import time
import random

# Logging configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - [%(process)d] - %(message)s')

app = Flask(__name__)

# Kafka Producer configuration for retry messages
retry_producer = KafkaProducer(
    bootstrap_servers=['kafka01:9092', 'kafka02:9093', 'kafka03:9094'],
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

def process_message(topic, message):
    # Simulate random exceptions for testing retry mechanism
    if random.choice([True, False]):
        raise Exception("Random error for testing retry mechanism.")

    words = message['message'].split()
    combinations = itertools.permutations(words, 3)
    for _ in range(10):  # Print only the first 10 combinations as an example
        combination = next(combinations)
        logging.info(f"Combination: {' '.join(combination)}")

def handle_message(topic, message):
    try:
        process_message(topic, message)
    except Exception as e:
        logging.error(f"Error processing message: {e}")
        # Send failed message to retry_topic
        retry_producer.send('retry_topic', value=message)
        retry_producer.flush()

def kafka_polling_task(topics):
    """
    Continuously polls for new messages from the specified topics.

    Args:
        topics (list): List of topics to poll for messages.

    Returns:
        None
    """
    logging.info("Starting Kafka polling task for topics: {}".format(topics))
    consumer = KafkaConsumer(
        *topics,
        bootstrap_servers=['kafka01:9092', 'kafka02:9093', 'kafka03:9094'],
        value_deserializer=lambda m: json.loads(m.decode('utf-8')),
        auto_offset_reset='earliest',
        group_id='my_flask_group'
    )

    while True:
        message_pack = consumer.poll(timeout_ms=5000)
        if message_pack:
            for partition_messages in message_pack.values():
                for message in partition_messages:
                    handle_message(message.topic, message.value)
        else:
            logging.info("No new messages, waiting...")
        time.sleep(5)

def activate_kafka_polling():
    # Run Kafka polling task in a background thread
    main_thread = threading.Thread(target=kafka_polling_task, args=(['test_topic', 'retry_topic'],), daemon=True)
    main_thread.start()

@app.route('/')
def home():
    activate_kafka_polling()
    return "Flask Kafka Integration Example"

if __name__ == "__main__":
    app.run(debug=True)