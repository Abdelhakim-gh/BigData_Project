import json
import requests
from kafka import KafkaProducer
from rich import print
from time import sleep

# Replace 'YOUR_GITHUB_TOKEN' with your actual GitHub token
github_token = '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'

producer = KafkaProducer(bootstrap_servers=['dexter-VirtualBox:9092'], value_serializer=lambda K: json.dumps(K).encode('utf-8'))

repository_url = 'https://api.github.com/repositories'
user_url_template = "https://api.github.com/users/{}"

def fetch_user_data(username):
    user_url = user_url_template.format(username)
    headers = {'Authorization': f'token {github_token}'}
    response = requests.get(user_url, headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error fetching data for {username}. Status code: {response.status_code}")
        return None

def fetch_repository_data():
    headers = {'Authorization': f'token {github_token}'}
    response = requests.get(repository_url, headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error fetching repository data. Status code: {response.status_code}")
        return []

for repository in fetch_repository_data():
    owner_url = repository['owner']['url']
    owner_data = fetch_user_data(owner_url.split('/')[-1])

    if owner_data:
        cur_data = {
            "ID": owner_data['id'],
            "Login": owner_data['login'],
            "Name": owner_data['name'],
            "HTML_URL": owner_data['html_url'],
            "Public_Repos": owner_data['public_repos'],
            "Public_Gists": owner_data['public_gists'],
            "Followers": owner_data['followers'],
            "Following": owner_data['following']
        }

        producer.send('my_topic', value=cur_data)
        print(json.dumps(cur_data, indent=2))
        sleep(1)
