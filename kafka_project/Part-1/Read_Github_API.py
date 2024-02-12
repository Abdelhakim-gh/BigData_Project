import json
import requests
from rich import print
from time import sleep

repository_url = 'https://api.github.com/repositories'
user_url_template = "https://api.github.com/users/{}"

# Replace 'YOUR_GITHUB_TOKEN' with your actual GitHub token
github_token = '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'

# Function to fetch data from GitHub API with authorization header
def fetch_user_data(username):
    user_url = user_url_template.format(username)
    headers = {'Authorization': f'token {github_token}'}
    response = requests.get(user_url, headers=headers)
    return response.json()

# Fetch data from GitHub API
data = requests.get(repository_url).json()

for repository in data:
    owner_url = repository['owner']['url']
    owner_data = fetch_user_data(owner_url.split('/')[-1])  # Extracting username from the URL

    # Store the data in the cur_data variable
    cur_data = {
        "ID": owner_data['id'],
        "Login": owner_data['login'],
        "Name": owner_data['name'],
        "HTML URL": owner_data['html_url'],
        "Public Repos": owner_data['public_repos'],
        "Public Gists": owner_data['public_gists'],
        "Followers": owner_data['followers'],
        "Following": owner_data['following']
    }

    print(json.dumps(cur_data, indent=2))  # Pretty-print the data
    sleep(0.5)
