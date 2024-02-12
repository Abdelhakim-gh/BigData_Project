import tweepy
from json import dumps
from kafka import KafkaProducer
from rich import print
from time import sleep

# Create a Kafka producer
producer = KafkaProducer(
    bootstrap_servers=['vps-data1:9092', 'vps-data2:9092', 'vps-data3:9092'],
    value_serializer=lambda K: dumps(K).encode('utf-8')
)

# Read keys from secret txt file
with open('/home/hadoop/Big_Data/kafka/TwitterKafkaDemo/secrets.txt') as f:
    for line in f:
        if '=' in line:
            key, value = line.strip().split(' = ')
            if key == 'CONSUMER_KEY':
                CONSUMER_KEY = value.strip("'")
            elif key == 'CONSUMER_SECRET':
                CONSUMER_SECRET = value.strip("'")
            elif key == 'ACCESS_TOKEN':
                ACCESS_TOKEN = value.strip("'")
            elif key == 'ACCESS_TOKEN_SECRET':
                ACCESS_TOKEN_SECRET = value.strip("'")

# Set up OAuth authentication with Twitter API
auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)

api = tweepy.API(auth)

# Perform a Twitter search and iterate over the tweets
cursor = tweepy.Cursor(api.search_tweets, q='music', lang="en", tweet_mode='extended').items(100)
for tweet in cursor:
    hashtags = tweet.entities['hashtags']
    hashtext = []
    for j in range(0, len(hashtags)):
        hashtext.append(hashtags[j]['text'])
    
    # Prepare data to be sent to Kafka topic
    cur_data = {
        "id_str": tweet.id_str,
        "username": tweet.user.name,
        "tweet": tweet.full_text,
        "location": tweet.user.location,
        "retweet_count": tweet.retweet_count,
        "favorite_count": tweet.favorite_count,
        "followers_count": tweet.user.followers_count,
        "lang": tweet.lang
    }

    producer.send('my-topic-test', value=cur_data)  # Send data to Kafka topic
    print(cur_data)  # Print the tweet data
    sleep(0.5)  # Pause for 0.5 seconds before processing the next tweet
