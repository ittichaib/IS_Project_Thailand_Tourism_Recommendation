import tweepy
import json

# Step 1: Set up Twitter API credentials
API_KEY = 'dllmDpdQkSaVDHOBY4MbMXAI9'
API_SECRET_KEY = 'Qa7vEvVAwpwIDVBm61149ffrZYaNtY7dD48ONqr4bGNtCA04ya'
ACCESS_TOKEN = '1819611229218033664-ivSNkqUdhSezu8PGavFdBBtsTpMqcP'
ACCESS_TOKEN_SECRET = '92K2zPF8DvNrslXxYL48zL0eJEsmL6k6E4MYhdft4qIbS'
BEARER_TOKEN = 'AAAAAAAAAAAAAAAAAAAAAIoovQEAAAAAcTbg3pX8K9wCGPDyu9fVricbQQA%3D8vP65IzhcOdPLuW7tNNG0nws12kdUrEnAkAAPxzDeXlPr8uJeF'

# Step 2: Authenticate to Twitter using v2 API
client = tweepy.Client(bearer_token=BEARER_TOKEN)

# Step 3: Define a function to gather tweets using v2 API
def gather_tweets_v2(query, max_tweets=100):
    tweets_data = []
    for tweet in tweepy.Paginator(client.search_recent_tweets, query=query, tweet_fields=['created_at', 'text', 'author_id', 'geo'], max_results=100).flatten(limit=max_tweets):
        tweets_data.append({
            'created_at': tweet.created_at,
            'username': tweet.author_id,  # V2 API returns user ID instead of screen_name
            'text': tweet.text,
            'location': tweet.geo  # Note: V2 API requires additional permissions for detailed location info
        })
    return tweets_data

# Step 4: Use the function to gather tweets related to Thailand tourism attractions
query = "Thailand tourism OR Thailand attraction OR Thailand travel OR Thailand vacation"
tweets = gather_tweets_v2(query=query, max_tweets=200)  # Gather 200 tweets

# Optional: Save tweets to a JSON file
with open('thailand_tourism_reviews_2024.json', 'w') as outfile:
    json.dump(tweets, outfile, indent=4)

# Print a sample tweet
print(tweets[0])