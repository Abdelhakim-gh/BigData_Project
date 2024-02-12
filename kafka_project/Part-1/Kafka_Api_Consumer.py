# Import necessary libraries
from kafka import KafkaConsumer
from json import loads
from rich import print

# Create a Kafka consumer
consumer = KafkaConsumer(
    'my_topic',  # Topic to consume messages from
    bootstrap_servers=['dexter-VirtualBox:9092'],  # Kafka server addresses
    auto_offset_reset='earliest',  # Reset offset to the latest available message
    enable_auto_commit=True,  # Enable auto commit of consumed messages
    group_id=None,  # Consumer group ID (None indicates an individual consumer)
    value_deserializer=lambda x: loads(x.decode('utf-8'))  # Deserialize the message value from JSON to Python object
)

# Process incoming messages
for message in consumer:
    data = message.value  # Get the value of the message (tweet)
    print(data)  # Print the tweet
