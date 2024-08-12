# Kafka, Flink, Elastic search Project

> **Abdelhakim EL Ghayoubi**

### Overview:

This project aims to establish a data streaming pipeline with storage, processing, and visualization using:

- Kafka for asynchronous messaging
- Flink for processing data
- Hadoop for storage and backup
- Elasticsearch and Kibana for indexing and visualization

![Untitled](Kafka,%20Flink,%20Elastic%20search%20Project%2037586fa574884870a61b51a4aa7e71b8/Untitled%200.png)

- You can also use other tools as you like or add more tools, just make sure they are in sync with each other.

This is my documentation of the project I worked on. I'm using the GitHub API, but you can adjust or replace it with any API you like. Just be sure to change and adjust the code to fit your API specifications. Remember, **<u>the technologies and JARs need to be compatible**</u>; otherwise, you'll get unpleasant errors. I've provided the code and step-by-step guide on how to work with them. _Make sure you don't skip important parts._ Good luck!

## Project Part 1

### **`Github`** API

- Token key for **`Github`** API
  ```bash
  YOUR_GITHUB_TOKEN
  ```
- Kafka info
  - **Start Zookeeper:**
    Kafka uses Zookeeper for distributed coordination. Start Zookeeper by running the following command from the Kafka directory:
        ```bash
        bin/zookeeper-server-start.sh config/zookeeper.properties
        ```
  - **Start Kafka Server:**
    Open a new terminal and start the Kafka server with the following command:

        ```bash
        bin/kafka-server-start.sh config/server.properties
        ```

  - **Create a Topic:**
    Use the following command to create a topic named "my_topic":
        ```bash
        bin/kafka-topics.sh --create --topic my_topic --bootstrap-server localhost:9092 --partitions 1 --replication-factor 1
        ```
  - **List Topics:**
    To see a list of existing topics, run:
        ```bash
        bin/kafka-topics.sh --list --bootstrap-server localhost:9092
        ```
  - **Produce Messages:**
    Use the following command to produce messages to the "**my_topic**" topic:
        ```bash
        bin/kafka-console-producer.sh --topic my_topic --bootstrap-server localhost:9092
        ```
  - **Consume Messages:**
    Open a new terminal and run the following command to consume messages from the "my_topic" topic:
        ```bash
        bin/kafka-console-consumer.sh --topic my_topic --bootstrap-server localhost:9092 --from-beginning
        ```
- Server properties
  - default
    ```python
    # Listener name, hostname and port the broker will advertise to clients.
    # If not set, it uses the value for "listeners".
    advertised.listeners=PLAINTEXT://your.host.name:9092
    ```
  - my config
    ```python
    advertised.listeners=PLAINTEXT://dexter-vm:9092
    ```
- **_My Kafka info_**
  - after starting zookeeper & kafka
    ```bash
    bin/zookeeper-server-start.sh config/zookeeper.properties

    bin/kafka-server-start.sh config/server.properties
    ```
    you should see this in kafka terminal
    ```bash
    [2023-12-03 17:11:15,535] INFO Registered broker 0 at path /brokers/ids/0 with addresses: PLAINTEXT://dexter-VirtualBox:9092, czxid (broker epoch): 124 (kafka.zk.KafkaZkClient)

    dafualt topic: 'my-topic-test'
    boostrap-server: 'dexter-VirtualBox:9092'
    ```
- Read API data
  ```python
  import json
  import requests
  from rich import print
  from time import sleep

  repository_url = 'https://api.github.com/repositories'
  user_url_template = "https://api.github.com/users/{}"

  # Replace 'YOUR_GITHUB_TOKEN' with your actual GitHub token
  github_token = '<YOUR_GITHUB_TOKEN>'

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
  ```
- Kafka Producer
  ```bash
  import json
  import requests
  from kafka import KafkaProducer
  from rich import print
  from time import sleep

  # Replace 'YOUR_GITHUB_TOKEN' with your actual GitHub token
  github_token = 'YOUR_GITHUB_TOKEN'

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
  ```
- Kafka Consumer
  ```bash
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
  ```
  - check if the consumer got the data
    ```bash
    bin/kafka-console-consumer.sh --topic my-topic-test --bootstrap-server dexter-VirtualBox:9092 --from-beginning
    ```
- Kafka with **`HDFS`**
  - start **Hadoop** & create this folder & **`file.json`**
    ```bash
    hadoop fs -mkdir /kafka_project

    hadoop fs -touchz /kafka_project/github_data.json

    hadoop fs -ls /kafka_project/
    -rw-r--r--   1 dexter supergroup          0 2023-12-03 17:35 /kafka_project/github_data.json
    ```
  - install Hadoop lib in python
    ```bash
    pip3 install pydoop
    ```
  - code
    ```python
    # Import necessary libraries
    from kafka import KafkaConsumer
    from json import loads
    from rich import print
    import pydoop.hdfs as hdfs

    # Create a Kafka consumer
    consumer = KafkaConsumer(
        'my_topic',  # Topic to consume messages from
        bootstrap_servers=['dexter-VirtualBox:9092'],  # Kafka server addresses
        auto_offset_reset='earliest',  # Reset offset to the latest available message
        enable_auto_commit=True,  # Enable auto commit of consumed messages
        group_id=None,  # Consumer group ID (None indicates an individual consumer)
        value_deserializer=lambda x: loads(x.decode('utf-8'))  # Deserialize the message value from JSON to Python object
    )

    hdfs_path = 'hdfs://localhost:9000/kafka_project/github_data.json'  # Path to the HDFS file

    # Process incoming messages
    for message in consumer:
        data = message.value  # Get the value of the message (tweet)
        print(data)  # Print the tweet

        with hdfs.open(hdfs_path, 'at') as file:
            print("Storing in HDFS!")
            file.write(f"{data}\n")
    ```
  - check if the file has the date
    ```bash
    dexter@dexter-VirtualBox:~$ hadoop fs -cat /kafka_project/github_data.json
    ```
- JSON file to CSV
  ```
  ID,Login,Name,HTML URL,Public Repos,Public Gists,Followers,Following
  1,mojombo,Tom Preston-Werner,https://github.com/mojombo,66,62,23705,11
  4,wycats,Yehuda Katz,https://github.com/wycats,284,761,10161,13
  317747,rubinius,Rubinius,https://github.com/rubinius,50,0,17,0
  1,mojombo,Tom Preston-Werner,https://github.com/mojombo,66,62,23705,11
  17,vanpelt,Chris Van Pelt,https://github.com/vanpelt,58,50,224,20
  4,wycats,Yehuda Katz,https://github.com/wycats,284,761,10161,13
  2,defunkt,Chris Wanstrath,https://github.com/defunkt,107,274,21745,214
  21,technoweenie,,https://github.com/technoweenie,177,106,2635,18
  25,caged,Justin Palmer,https://github.com/caged,166,99,2361,44
  27,anotherjesse,Jesse Andrews,https://github.com/anotherjesse,192,68,229,38
  1,mojombo,Tom Preston-Werner,https://github.com/mojombo,66,62,23705,11
  2,defunkt,Chris Wanstrath,https://github.com/defunkt,107,274,21745,214
  22,macournoyer,Marc-André Cournoyer,https://github.com/macournoyer,66,55,1214,56
  37,jamesgolick,James Golick,https://github.com/jamesgolick,110,114,635,30
  2,defunkt,Chris Wanstrath,https://github.com/defunkt,107,274,21745,214
  36,KirinDave,Dave Fayram,https://github.com/KirinDave,83,97,407,10
  46,bmizerany,Blake Mizerany,https://github.com/bmizerany,166,170,1399,36
  47,jnewland,Jesse Newland,https://github.com/jnewland,128,43,723,99
  21,technoweenie,,https://github.com/technoweenie,177,106,2635,18
  47,jnewland,Jesse Newland,https://github.com/jnewland,128,43,723,99
  2,defunkt,Chris Wanstrath,https://github.com/defunkt,107,274,21745,214
  47,jnewland,Jesse Newland,https://github.com/jnewland,128,43,723,99
  30619330,ruby-git,,https://github.com/ruby-git,1,0,2,0
  5,ezmobius,Ezra Zygmuntowicz,https://github.com/ezmobius,22,106,545,13
  71,uggedal,Eivind Uggedal,https://github.com/uggedal,47,43,180,0
  74,mmower,Matt Mower,https://github.com/mmower,78,126,59,1
  75,abhay,Abhay Kumar,https://github.com/abhay,42,2,162,1
  77,benburkert,Ben Burkert,https://github.com/benburkert,138,37,200,7
  75,abhay,Abhay Kumar,https://github.com/abhay,42,2,162,1
  1,mojombo,Tom Preston-Werner,https://github.com/mojombo,66,62,23705,11
  90,sr,Simon Rozet,https://github.com/sr,133,56,569,199
  106,queso,Josh Owens,https://github.com/queso,83,106,339,23
  108,drnic,Dr Nic Williams,https://github.com/drnic,664,265,1752,11
  110,danwrong,Dan Webb,https://github.com/danwrong,32,37,345,31
  18,wayneeseguin,Wayne E Seguin,https://github.com/wayneeseguin,104,95,731,19
  90,sr,Simon Rozet,https://github.com/sr,133,56,569,199
  1,mojombo,Tom Preston-Werner,https://github.com/mojombo,66,62,23705,11
  36,KirinDave,Dave Fayram,https://github.com/KirinDave,83,97,407,10
  90,sr,Simon Rozet,https://github.com/sr,133,56,569,199
  113,mattetti,Matt Aimonetti,https://github.com/mattetti,296,354,0,0
  117,grempe,Glenn Rempe,https://github.com/grempe,42,10,120,27
  18,wayneeseguin,Wayne E Seguin,https://github.com/wayneeseguin,104,95,731,19
  ```
  ```
  ID,Login,Name,HTML URL,Public Repos,Public Gists,Followers,Following
  1,mojombo,Tom Preston-Werner,https://github.com/mojombo,66,62,23705,11
  4,wycats,Yehuda Katz,https://github.com/wycats,284,761,10161,13
  317747,rubinius,Rubinius,https://github.com/rubinius,50,0,17,0
  17,vanpelt,Chris Van Pelt,https://github.com/vanpelt,58,50,224,20
  2,defunkt,Chris Wanstrath,https://github.com/defunkt,107,274,21745,214
  21,technoweenie,,https://github.com/technoweenie,177,106,2635,18
  25,caged,Justin Palmer,https://github.com/caged,166,99,2361,44
  27,anotherjesse,Jesse Andrews,https://github.com/anotherjesse,192,68,229,38
  22,macournoyer,Marc-André Cournoyer,https://github.com/macournoyer,66,55,1214,56
  37,jamesgolick,James Golick,https://github.com/jamesgolick,110,114,635,30
  36,KirinDave,Dave Fayram,https://github.com/KirinDave,83,97,407,10
  46,bmizerany,Blake Mizerany,https://github.com/bmizerany,166,170,1399,36
  47,jnewland,Jesse Newland,https://github.com/jnewland,128,43,723,99
  30619330,ruby-git,,https://github.com/ruby-git,1,0,2,0
  5,ezmobius,Ezra Zygmuntowicz,https://github.com/ezmobius,22,106,545,13
  71,uggedal,Eivind Uggedal,https://github.com/uggedal,47,43,180,0
  74,mmower,Matt Mower,https://github.com/mmower,78,126,59,1
  75,abhay,Abhay Kumar,https://github.com/abhay,42,2,162,1
  77,benburkert,Ben Burkert,https://github.com/benburkert,138,37,200,7
  90,sr,Simon Rozet,https://github.com/sr,133,56,569,199
  106,queso,Josh Owens,https://github.com/queso,83,106,339,23
  108,drnic,Dr Nic Williams,https://github.com/drnic,664,265,1752,11
  110,danwrong,Dan Webb,https://github.com/danwrong,32,37,345,31
  18,wayneeseguin,Wayne E Seguin,https://github.com/wayneeseguin,104,95,731,19
  113,mattetti,Matt Aimonetti,https://github.com/mattetti,296,354,0,0
  117,grempe,Glenn Rempe,https://github.com/grempe,42,10,120,27
  ```
  create file that contain this data so i can load to a table in hive
  ```bash
  1,mojombo,Tom Preston-Werner,https://github.com/mojombo,66,62,23705,11
  4,wycats,Yehuda Katz,https://github.com/wycats,284,761,10161,13
  317747,rubinius,Rubinius,https://github.com/rubinius,50,0,17,0
  17,vanpelt,Chris Van Pelt,https://github.com/vanpelt,58,50,224,20
  2,defunkt,Chris Wanstrath,https://github.com/defunkt,107,274,21745,214
  21,technoweenie,,https://github.com/technoweenie,177,106,2635,18
  25,caged,Justin Palmer,https://github.com/caged,166,99,2361,44
  27,anotherjesse,Jesse Andrews,https://github.com/anotherjesse,192,68,229,38
  22,macournoyer,Marc-André Cournoyer,https://github.com/macournoyer,66,55,1214,56
  37,jamesgolick,James Golick,https://github.com/jamesgolick,110,114,635,30
  36,KirinDave,Dave Fayram,https://github.com/KirinDave,83,97,407,10
  46,bmizerany,Blake Mizerany,https://github.com/bmizerany,166,170,1399,36
  47,jnewland,Jesse Newland,https://github.com/jnewland,128,43,723,99
  30619330,ruby-git,,https://github.com/ruby-git,1,0,2,0
  5,ezmobius,Ezra Zygmuntowicz,https://github.com/ezmobius,22,106,545,13
  71,uggedal,Eivind Uggedal,https://github.com/uggedal,47,43,180,0
  74,mmower,Matt Mower,https://github.com/mmower,78,126,59,1
  75,abhay,Abhay Kumar,https://github.com/abhay,42,2,162,1
  77,benburkert,Ben Burkert,https://github.com/benburkert,138,37,200,7
  90,sr,Simon Rozet,https://github.com/sr,133,56,569,199
  106,queso,Josh Owens,https://github.com/queso,83,106,339,23
  108,drnic,Dr Nic Williams,https://github.com/drnic,664,265,1752,11
  110,danwrong,Dan Webb,https://github.com/danwrong,32,37,345,31
  18,wayneeseguin,Wayne E Seguin,https://github.com/wayneeseguin,104,95,731,19
  113,mattetti,Matt Aimonetti,https://github.com/mattetti,296,354,0,0
  117,grempe,Glenn Rempe,https://github.com/grempe,42,10,120,27
  ```
- Storing data in `**Hive**`
  start hadoop & hive
  ```bash
  start-all.sh

  hive
  ```
  create database
  ```bash
  CREATE DATABASE IF NOT EXISTS kafka_project;
  show databases;
  describe database kafka_project;
  USE kafka_project;
  ```
  create table
  ```bash
  CREATE TABLE github_data (
      id INT,
      login STRING,
      name STRING,
      html_url STRING,
      public_repos INT,
      public_gists INT,
      num_Followers INT,
      num_following INT
  )
  ROW FORMAT DELIMITED
  FIELDS TERMINATED BY ','
  STORED AS TEXTFILE;
  ```
  load file data
  ```bash
  LOAD DATA LOCAL INPATH '/home/dexter/Desktop/github_data.csv' INTO TABLE github_data;
  ```
  ```bash
  SELECT * FROM github_data order by id;
  ```
- Storing data in `**HBase**`
  ```bash
  **Column Family 'github_info'**

  **Col Name:**
  id
  login
  name
  html_url
  public_repos
  public_gists
  num_Followers
  num_following

  **Data:**
  1,mojombo,Tom Preston-Werner,https://github.com/mojombo,66,62,23705,11
  4,wycats,Yehuda Katz,https://github.com/wycats,284,761,10161,13
  317747,rubinius,Rubinius,https://github.com/rubinius,50,0,17,0
  17,vanpelt,Chris Van Pelt,https://github.com/vanpelt,58,50,224,20
  2,defunkt,Chris Wanstrath,https://github.com/defunkt,107,274,21745,214
  21,technoweenie,,https://github.com/technoweenie,177,106,2635,18
  25,caged,Justin Palmer,https://github.com/caged,166,99,2361,44
  27,anotherjesse,Jesse Andrews,https://github.com/anotherjesse,192,68,229,38
  22,macournoyer,Marc-André Cournoyer,https://github.com/macournoyer,66,55,1214,56
  37,jamesgolick,James Golick,https://github.com/jamesgolick,110,114,635,30
  36,KirinDave,Dave Fayram,https://github.com/KirinDave,83,97,407,10
  46,bmizerany,Blake Mizerany,https://github.com/bmizerany,166,170,1399,36
  47,jnewland,Jesse Newland,https://github.com/jnewland,128,43,723,99
  30619330,ruby-git,,https://github.com/ruby-git,1,0,2,0
  5,ezmobius,Ezra Zygmuntowicz,https://github.com/ezmobius,22,106,545,13
  71,uggedal,Eivind Uggedal,https://github.com/uggedal,47,43,180,0
  74,mmower,Matt Mower,https://github.com/mmower,78,126,59,1
  75,abhay,Abhay Kumar,https://github.com/abhay,42,2,162,1
  77,benburkert,Ben Burkert,https://github.com/benburkert,138,37,200,7
  90,sr,Simon Rozet,https://github.com/sr,133,56,569,199
  106,queso,Josh Owens,https://github.com/queso,83,106,339,23
  108,drnic,Dr Nic Williams,https://github.com/drnic,664,265,1752,11
  110,danwrong,Dan Webb,https://github.com/danwrong,32,37,345,31
  18,wayneeseguin,Wayne E Seguin,https://github.com/wayneeseguin,104,95,731,19
  113,mattetti,Matt Aimonetti,https://github.com/mattetti,296,354,0,0
  117,grempe,Glenn Rempe,https://github.com/grempe,42,10,120,27
  ```
  ```bash
  create 'github_users', 'github_info'

  put 'github_users', '1', 'github_info:id', '1'
  put 'github_users', '1', 'github_info:login', 'mojombo'
  put 'github_users', '1', 'github_info:name', 'Tom Preston-Werner'
  put 'github_users', '1', 'github_info:html_url', 'https://github.com/mojombo'
  put 'github_users', '1', 'github_info:public_repos', '66'
  put 'github_users', '1', 'github_info:public_gists', '62'
  put 'github_users', '1', 'github_info:num_followers', '23705'
  put 'github_users', '1', 'github_info:num_following', '11'

  put 'github_users', '4', 'github_info:id', '4'
  put 'github_users', '4', 'github_info:login', 'wycats'
  put 'github_users', '4', 'github_info:name', 'Yehuda Katz'
  put 'github_users', '4', 'github_info:html_url', 'https://github.com/wycats'
  put 'github_users', '4', 'github_info:public_repos', '284'
  put 'github_users', '4', 'github_info:public_gists', '761'
  put 'github_users', '4', 'github_info:num_followers', '10161'
  put 'github_users', '4', 'github_info:num_following', '13'

  put 'github_users', '317747', 'github_info:id', '317747'
  put 'github_users', '317747', 'github_info:login', 'rubinius'
  put 'github_users', '317747', 'github_info:name', 'Rubinius'
  put 'github_users', '317747', 'github_info:html_url', 'https://github.com/rubinius'
  put 'github_users', '317747', 'github_info:public_repos', '50'
  put 'github_users', '317747', 'github_info:public_gists', '0'
  put 'github_users', '317747', 'github_info:num_followers', '17'
  put 'github_users', '317747', 'github_info:num_following', '0'

  put 'github_users', '17', 'github_info:id', '17'
  put 'github_users', '17', 'github_info:login', 'vanpelt'
  put 'github_users', '17', 'github_info:name', 'Chris Van Pelt'
  put 'github_users', '17', 'github_info:html_url', 'https://github.com/vanpelt'
  put 'github_users', '17', 'github_info:public_repos', '58'
  put 'github_users', '17', 'github_info:public_gists', '50'
  put 'github_users', '17', 'github_info:num_followers', '224'
  put 'github_users', '17', 'github_info:num_following', '20'

  put 'github_users', '2', 'github_info:id', '2'
  put 'github_users', '2', 'github_info:login', 'defunkt'
  put 'github_users', '2', 'github_info:name', 'Chris Wanstrath'
  put 'github_users', '2', 'github_info:html_url', 'https://github.com/defunkt'
  put 'github_users', '2', 'github_info:public_repos', '107'
  put 'github_users', '2', 'github_info:public_gists', '274'
  put 'github_users', '2', 'github_info:num_followers', '21745'
  put 'github_users', '2', 'github_info:num_following', '214'

  put 'github_users', '21', 'github_info:id', '21'
  put 'github_users', '21', 'github_info:login', 'technoweenie'
  put 'github_users', '21', 'github_info:name', ''
  put 'github_users', '21', 'github_info:html_url', 'https://github.com/technoweenie'
  put 'github_users', '21', 'github_info:public_repos', '177'
  put 'github_users', '21', 'github_info:public_gists', '106'
  put 'github_users', '21', 'github_info:num_followers', '2635'
  put 'github_users', '21', 'github_info:num_following', '18'

  put 'github_users', '25', 'github_info:id', '25'
  put 'github_users', '25', 'github_info:login', 'caged'
  put 'github_users', '25', 'github_info:name', 'Justin Palmer'
  put 'github_users', '25', 'github_info:html_url', 'https://github.com/caged'
  put 'github_users', '25', 'github_info:public_repos', '166'
  put 'github_users', '25', 'github_info:public_gists', '99'
  put 'github_users', '25', 'github_info:num_followers', '2361'
  put 'github_users', '25', 'github_info:num_following', '44'

  put 'github_users', '27', 'github_info:id', '27'
  put 'github_users', '27', 'github_info:login', 'anotherjesse'
  put 'github_users', '27', 'github_info:name', 'Jesse Andrews'
  put 'github_users', '27', 'github_info:html_url', 'https://github.com/anotherjesse'
  put 'github_users', '27', 'github_info:public_repos', '192'
  put 'github_users', '27', 'github_info:public_gists', '68'
  put 'github_users', '27', 'github_info:num_followers', '229'
  put 'github_users', '27', 'github_info:num_following', '38'

  put 'github_users', '22', 'github_info:id', '22'
  put 'github_users', '22', 'github_info:login', 'macournoyer'
  put 'github_users', '22', 'github_info:name', 'Marc-André Cournoyer'
  put 'github_users', '22', 'github_info:html_url', 'https://github.com/macournoyer'
  put 'github_users', '22', 'github_info:public_repos', '66'
  put 'github_users', '22', 'github_info:public_gists', '55'
  put 'github_users', '22', 'github_info:num_followers', '1214'
  put 'github_users', '22', 'github_info:num_following', '56'

  put 'github_users', '37', 'github_info:id', '37'
  put 'github_users', '37', 'github_info:login', 'jamesgolick'
  put 'github_users', '37', 'github_info:name', 'James Golick'
  put 'github_users', '37', 'github_info:html_url', 'https://github.com/jamesgolick'
  put 'github_users', '37', 'github_info:public_repos', '110'
  put 'github_users', '37', 'github_info:public_gists', '114'
  put 'github_users', '37', 'github_info:num_followers', '635'
  put 'github_users', '37', 'github_info:num_following', '30'

  put 'github_users', '36', 'github_info:id', '36'
  put 'github_users', '36', 'github_info:login', 'KirinDave'
  put 'github_users', '36', 'github_info:name', 'Dave Fayram'
  put 'github_users', '36', 'github_info:html_url', 'https://github.com/KirinDave'
  put 'github_users', '36', 'github_info:public_repos', '83'
  put 'github_users', '36', 'github_info:public_gists', '97'
  put 'github_users', '36', 'github_info:num_followers', '407'
  put 'github_users', '36', 'github_info:num_following', '10'

  put 'github_users', '46', 'github_info:id', '46'
  put 'github_users', '46', 'github_info:login', 'bmizerany'
  put 'github_users', '46', 'github_info:name', 'Blake Mizerany'
  put 'github_users', '46', 'github_info:html_url', 'https://github.com/bmizerany'
  put 'github_users', '46', 'github_info:public_repos', '166'
  put 'github_users', '46', 'github_info:public_gists', '170'
  put 'github_users', '46', 'github_info:num_followers', '1399'
  put 'github_users', '46', 'github_info:num_following', '36'

  put 'github_users', '47', 'github_info:id', '47'
  put 'github_users', '47', 'github_info:login', 'jnewland'
  put 'github_users', '47', 'github_info:name', 'Jesse Newland'
  put 'github_users', '47', 'github_info:html_url', 'https://github.com/jnewland'
  put 'github_users', '47', 'github_info:public_repos', '128'
  put 'github_users', '47', 'github_info:public_gists', '43'
  put 'github_users', '47', 'github_info:num_followers', '723'
  put 'github_users', '47', 'github_info:num_following', '99'

  put 'github_users', '30619330', 'github_info:id', '30619330'
  put 'github_users', '30619330', 'github_info:login', 'ruby-git'
  put 'github_users', '30619330', 'github_info:name', ''
  put 'github_users', '30619330', 'github_info:html_url', 'https://github.com/ruby-git'
  put 'github_users', '30619330', 'github_info:public_repos', '1'
  put 'github_users', '30619330', 'github_info:public_gists', '0'
  put 'github_users', '30619330', 'github_info:num_followers', '2'
  put 'github_users', '30619330', 'github_info:num_following', '0'

  put 'github_users', '5', 'github_info:id', '5'
  put 'github_users', '5', 'github_info:login', 'ezmobius'
  put 'github_users', '5', 'github_info:name', 'Ezra Zygmuntowicz'
  put 'github_users', '5', 'github_info:html_url', 'https://github.com/ezmobius'
  put 'github_users', '5', 'github_info:public_repos', '22'
  put 'github_users', '5', 'github_info:public_gists', '106'
  put 'github_users', '5', 'github_info:num_followers', '545'
  put 'github_users', '5', 'github_info:num_following', '13'

  put 'github_users', '71', 'github_info:id', '71'
  put 'github_users', '71', 'github_info:login', 'uggedal'
  put 'github_users', '71', 'github_info:name', 'Eivind Uggedal'
  put 'github_users', '71', 'github_info:html_url', 'https://github.com/uggedal'
  put 'github_users', '71', 'github_info:public_repos', '47'
  put 'github_users', '71', 'github_info:public_gists', '43'
  put 'github_users', '71', 'github_info:num_followers', '180'
  put 'github_users', '71', 'github_info:num_following', '0'

  put 'github_users', '74', 'github_info:id', '74'
  put 'github_users', '74', 'github_info:login', 'mmower'
  put 'github_users', '74', 'github_info:name', 'Matt Mower'
  put 'github_users', '74', 'github_info:html_url', 'https://github.com/mmower'
  put 'github_users', '74', 'github_info:public_repos', '78'
  put 'github_users', '74', 'github_info:public_gists', '126'
  put 'github_users', '74', 'github_info:num_followers', '59'
  put 'github_users', '74', 'github_info:num_following', '1'

  ```
  ```bash
  put 'github_users', '75', 'github_info:id', '75'
  put 'github_users', '75', 'github_info:login', 'abhay'
  put 'github_users', '75', 'github_info:name', 'Abhay Kumar'
  put 'github_users', '75', 'github_info:html_url', 'https://github.com/abhay'
  put 'github_users', '75', 'github_info:public_repos', '42'
  put 'github_users', '75', 'github_info:public_gists', '2'
  put 'github_users', '75', 'github_info:num_followers', '162'
  put 'github_users', '75', 'github_info:num_following', '1'

  put 'github_users', '77', 'github_info:id', '77'
  put 'github_users', '77', 'github_info:login', 'benburkert'
  put 'github_users', '77', 'github_info:name', 'Ben Burkert'
  put 'github_users', '77', 'github_info:html_url', 'https://github.com/benburkert'
  put 'github_users', '77', 'github_info:public_repos', '138'
  put 'github_users', '77', 'github_info:public_gists', '37'
  put 'github_users', '77', 'github_info:num_followers', '200'
  put 'github_users', '77', 'github_info:num_following', '7'

  put 'github_users', '90', 'github_info:id', '90'
  put 'github_users', '90', 'github_info:login', 'sr'
  put 'github_users', '90', 'github_info:name', 'Simon Rozet'
  put 'github_users', '90', 'github_info:html_url', 'https://github.com/sr'
  put 'github_users', '90', 'github_info:public_repos', '133'
  put 'github_users', '90', 'github_info:public_gists', '56'
  put 'github_users', '90', 'github_info:num_followers', '569'
  put 'github_users', '90', 'github_info:num_following', '199'

  put 'github_users', '106', 'github_info:id', '106'
  put 'github_users', '106', 'github_info:login', 'queso'
  put 'github_users', '106', 'github_info:name', 'Josh Owens'
  put 'github_users', '106', 'github_info:html_url', 'https://github.com/queso'
  put 'github_users', '106', 'github_info:public_repos', '83'
  put 'github_users', '106', 'github_info:public_gists', '106'
  put 'github_users', '106', 'github_info:num_followers', '339'
  put 'github_users', '106', 'github_info:num_following', '23'

  put 'github_users', '108', 'github_info:id', '108'
  put 'github_users', '108', 'github_info:login', 'drnic'
  put 'github_users', '108', 'github_info:name', 'Dr Nic Williams'
  put 'github_users', '108', 'github_info:html_url', 'https://github.com/drnic'
  put 'github_users', '108', 'github_info:public_repos', '664'
  put 'github_users', '108', 'github_info:public_gists', '265'
  put 'github_users', '108', 'github_info:num_followers', '1752'
  put 'github_users', '108', 'github_info:num_following', '11'

  put 'github_users', '110', 'github_info:id', '110'
  put 'github_users', '110', 'github_info:login', 'danwrong'
  put 'github_users', '110', 'github_info:name', 'Dan Webb'
  put 'github_users', '110', 'github_info:html_url', 'https://github.com/danwrong'
  put 'github_users', '110', 'github_info:public_repos', '32'
  put 'github_users', '110', 'github_info:public_gists', '37'
  put 'github_users', '110', 'github_info:num_followers', '345'
  put 'github_users', '110', 'github_info:num_following', '31'

  put 'github_users', '18', 'github_info:id', '18'
  put 'github_users', '18', 'github_info:login', 'wayneeseguin'
  put 'github_users', '18', 'github_info:name', 'Wayne E Seguin'
  put 'github_users', '18', 'github_info:html_url', 'https://github.com/wayneeseguin'
  put 'github_users', '18', 'github_info:public_repos', '104'
  put 'github_users', '18', 'github_info:public_gists', '95'
  put 'github_users', '18', 'github_info:num_followers', '731'
  put 'github_users', '18', 'github_info:num_following', '19'

  put 'github_users', '113', 'github_info:id', '113'
  put 'github_users', '113', 'github_info:login', 'mattetti'
  put 'github_users', '113', 'github_info:name', 'Matt Aimonetti'
  put 'github_users', '113', 'github_info:html_url', 'https://github.com/mattetti'
  put 'github_users', '113', 'github_info:public_repos', '296'
  put 'github_users', '113', 'github_info:public_gists', '354'
  put 'github_users', '113', 'github_info:num_followers', '0'
  put 'github_users', '113', 'github_info:num_following', '0'

  put 'github_users', '117', 'github_info:id', '117'
  put 'github_users', '117', 'github_info:login', 'grempe'
  put 'github_users', '117', 'github_info:name', 'Glenn Rempe'
  put 'github_users', '117', 'github_info:html_url', 'https://github.com/grempe'
  put 'github_users', '117', 'github_info:public_repos', '42'
  put 'github_users', '117', 'github_info:public_gists', '10'
  put 'github_users', '117', 'github_info:num_followers', '120'
  put 'github_users', '117', 'github_info:num_following', '27'
  ```
  ```bash
  put 'github_users', '30619330', 'github_info:id', '30619330'
  put 'github_users', '30619330', 'github_info:login', 'ruby-git'
  put 'github_users', '30619330', 'github_info:name', ''
  put 'github_users', '30619330', 'github_info:html_url', 'https://github.com/ruby-git'
  put 'github_users', '30619330', 'github_info:public_repos', '1'
  put 'github_users', '30619330', 'github_info:public_gists', '0'
  put 'github_users', '30619330', 'github_info:num_followers', '2'
  put 'github_users', '30619330', 'github_info:num_following', '0'

  put 'github_users', '5', 'github_info:id', '5'
  put 'github_users', '5', 'github_info:login', 'ezmobius'
  put 'github_users', '5', 'github_info:name', 'Ezra Zygmuntowicz'
  put 'github_users', '5', 'github_info:html_url', 'https://github.com/ezmobius'
  put 'github_users', '5', 'github_info:public_repos', '22'
  put 'github_users', '5', 'github_info:public_gists', '106'
  put 'github_users', '5', 'github_info:num_followers', '545'
  put 'github_users', '5', 'github_info:num_following', '13'

  put 'github_users', '71', 'github_info:id', '71'
  put 'github_users', '71', 'github_info:login', 'uggedal'
  put 'github_users', '71', 'github_info:name', 'Eivind Uggedal'
  put 'github_users', '71', 'github_info:html_url', 'https://github.com/uggedal'
  put 'github_users', '71', 'github_info:public_repos', '47'
  put 'github_users', '71', 'github_info:public_gists', '43'
  put 'github_users', '71', 'github_info:num_followers', '180'
  put 'github_users', '71', 'github_info:num_following', '0'

  put 'github_users', '74', 'github_info:id', '74'
  put 'github_users', '74', 'github_info:login', 'mmower'
  put 'github_users', '74', 'github_info:name', 'Matt Mower'
  put 'github_users', '74', 'github_info:html_url', 'https://github.com/mmower'
  put 'github_users', '74', 'github_info:public_repos', '78'
  put 'github_users', '74', 'github_info:public_gists', '126'
  put 'github_users', '74', 'github_info:num_followers', '59'
  put 'github_users', '74', 'github_info:num_following', '1'

  put 'github_users', '75', 'github_info:id', '75'
  put 'github_users', '75', 'github_info:login', 'abhay'
  put 'github_users', '75', 'github_info:name', 'Abhay Kumar'
  put 'github_users', '75', 'github_info:html_url', 'https://github.com/abhay'
  put 'github_users', '75', 'github_info:public_repos', '42'
  put 'github_users', '75', 'github_info:public_gists', '2'
  put 'github_users', '75', 'github_info:num_followers', '162'
  put 'github_users', '75', 'github_info:num_following', '1'

  put 'github_users', '77', 'github_info:id', '77'
  put 'github_users', '77', 'github_info:login', 'benburkert'
  put 'github_users', '77', 'github_info:name', 'Ben Burkert'
  put 'github_users', '77', 'github_info:html_url', 'https://github.com/benburkert'
  put 'github_users', '77', 'github_info:public_repos', '138'
  put 'github_users', '77', 'github_info:public_gists', '37'
  put 'github_users', '77', 'github_info:num_followers', '200'
  put 'github_users', '77', 'github_info:num_following', '7'

  put 'github_users', '90', 'github_info:id', '90'
  put 'github_users', '90', 'github_info:login', 'sr'
  put 'github_users', '90', 'github_info:name', 'Simon Rozet'
  put 'github_users', '90', 'github_info:html_url', 'https://github.com/sr'
  put 'github_users', '90', 'github_info:public_repos', '133'
  put 'github_users', '90', 'github_info:public_gists', '56'
  put 'github_users', '90', 'github_info:num_followers', '569'
  put 'github_users', '90', 'github_info:num_following', '199'

  put 'github_users', '106', 'github_info:id', '106'
  put 'github_users', '106', 'github_info:login', 'queso'
  put 'github_users', '106', 'github_info:name', 'Josh Owens'
  put 'github_users', '106', 'github_info:html_url', 'https://github.com/queso'
  put 'github_users', '106', 'github_info:public_repos', '83'
  put 'github_users', '106', 'github_info:public_gists', '106'
  put 'github_users', '106', 'github_info:num_followers', '339'
  put 'github_users', '106', 'github_info:num_following', '23'

  put 'github_users', '108', 'github_info:id', '108'
  put 'github_users', '108', 'github_info:login', 'drnic'
  put 'github_users', '108', 'github_info:name', 'Dr Nic Williams'
  put 'github_users', '108', 'github_info:html_url', 'https://github.com/drnic'
  put 'github_users', '108', 'github_info:public_repos', '664'
  put 'github_users', '108', 'github_info:public_gists', '265'
  put 'github_users', '108', 'github_info:num_followers', '1752'
  put 'github_users', '108', 'github_info:num_following', '11'

  put 'github_users', '110', 'github_info:id', '110'
  put 'github_users', '110', 'github_info:login', 'danwrong'
  put 'github_users', '110', 'github_info:name', 'Dan Webb'
  put 'github_users', '110', 'github_info:html_url', 'https://github.com/danwrong'
  put 'github_users', '110', 'github_info:public_repos', '32'
  put 'github_users', '110', 'github_info:public_gists', '37'
  put 'github_users', '110', 'github_info:num_followers', '345'
  put 'github_users', '110', 'github_info:num_following', '31'

  put 'github_users', '18', 'github_info:id', '18'
  put 'github_users', '18', 'github_info:login', 'wayneeseguin'
  put 'github_users', '18', 'github_info:name', 'Wayne E Seguin'
  put 'github_users', '18', 'github_info:html_url', 'https://github.com/wayneeseguin'
  put 'github_users', '18', 'github_info:public_repos', '104'
  put 'github_users', '18', 'github_info:public_gists', '95'
  put 'github_users', '18', 'github_info:num_followers', '731'
  put 'github_users', '18', 'github_info:num_following', '19'

  put 'github_users', '113', 'github_info:id', '113'
  put 'github_users', '113', 'github_info:login', 'mattetti'
  put 'github_users', '113', 'github_info:name', 'Matt Aimonetti'
  put 'github_users', '113', 'github_info:html_url', 'https://github.com/mattetti'
  put 'github_users', '113', 'github_info:public_repos', '296'
  put 'github_users', '113', 'github_info:public_gists', '354'
  put 'github_users', '113', 'github_info:num_followers', '0'
  put 'github_users', '113', 'github_info:num_following', '0'

  put 'github_users', '117', 'github_info:id', '117'
  put 'github_users', '117', 'github_info:login', 'grempe'
  put 'github_users', '117', 'github_info:name', 'Glenn Rempe'
  put 'github_users', '117', 'github_info:html_url', 'https://github.com/grempe'
  put 'github_users', '117', 'github_info:public_repos', '42'
  put 'github_users', '117', 'github_info:public_gists', '10'
  put 'github_users', '117', 'github_info:num_followers', '120'
  put 'github_users', '117', 'github_info:num_following', '27'
  ```

## Project Part 2

### **`kafka`** & **`Flink`** streaming

- Installation of requirements
  > `**apache-flink**` & `**Pyflink**` & **`flink-flink-sql-connector-kafka-1.16.3.jar`** should be compatibles meaning **same version** (1.16.3)
  - install `**flink**`: [https://www.youtube.com/watch?v=6uW6u_zuloo](https://www.youtube.com/watch?v=6uW6u_zuloo)
    ```bash
    # start flink
    cd flink

    # to start cluster
    ./bin/start-cluster.sh

    # localhost interface
    localhost:8081

    # to close cluseter
    ./bin/stop-cluster.sh
    ```
  - Make sure Python 3 is installed on your machine
    ```bash
    python3 --version

    # to install python 3 & update packages
    sudo apt update
    sudo apt install python3
    sudo apt dist-upgrade
    ```
  - pip3
    ```bash
    pip3 --version
    ```
  - **`Pyflink`** requirements
    ```bash
    Apache Flink Python API depends on Py4J (currently version 0.10.9.7),
    CloudPickle (currently version 2.2.0),
    python-dateutil (currently version >=2.8.0,<3),
    Apache Beam (currently version >=2.43.0,<2.49.0).
    ```
  - install `**Pyflink**`
    ```bash
    pip3 install apache-flink

    # check if it installed
    pip3 show apache-flink
    ```
    ```bash
    **from pyflink.table import TableEnvironment, EnvironmentSettings**
    # if this line is not marked it means that pyflink is installed
    ```
  - install [flink jar connector](https://mvnrepository.com/artifact/org.apache.flink/flink-sql-connector-kafka) it should be compatible with **`flink, pyflink`** version (1.16.3)
    ```bash
    https://mvnrepository.com/artifact/org.apache.flink/flink-sql-connector-kafka

    # navigate where you have it copy the path & place in
    "file://path to flink kafka connector jar"
    ```
- Setup
  - if you installed `**pyflinlk`\*\* correctly this line should not be marked
    ```bash
    **from pyflink.table import TableEnvironment, EnvironmentSettings**
    # if this line is not marked it means that pyflink is installed
    ```
  - navigate where you have **`flink-sql-kafka-connector`** it copy the path & place in
    ```bash
    "file://path to flink kafka connector jar"
    ```
  - create table base on attribute of your api data & replace information about your **`kafka`** properties
    ```bash
    # example

    CREATE TABLE source_table(
    .....
        ) WITH (
            'connector' = 'kafka',
            'topic' = '<your topic name>',
            'properties.bootstrap.servers' = 'localhost:9092',
            'properties.group.id' = 'test_3',
            'scan.startup.mode' = 'latest-offset',
            'format' = 'json'
        )
    ```
  - before execution make sure you have **`flink`** & **`kafka`** started
  - run the Producer file first then `kafka_flink_streaming.py`
- flink & kafka streaming code
  ```bash
  from pyflink.table import TableEnvironment, EnvironmentSettings

  # Create a TableEnvironment
  env_settings = EnvironmentSettings.in_streaming_mode()
  t_env = TableEnvironment.create(env_settings)

  # Specify connector and format jars
  t_env.get_config().get_configuration().set_string(
      "pipeline.jars",
      "file:///home/dexter/Desktop/kafka_project/flink-sql-connector-kafka-1.16.3.jar"
  )

  # Define source table DDL
  source_ddl = """
      CREATE TABLE source_table (
  	    ID BIGINT,
  	    Login VARCHAR,
  	    Name VARCHAR,
  	    HTML_URL VARCHAR,
  	    Public_Repos INT,
  	    Public_Gists INT,
  	    Followers INT,
  	    Following INT
      ) WITH (
          'connector' = 'kafka',
          'topic' = 'my_topic',
          'properties.bootstrap.servers' = 'localhost:9092',
          'properties.group.id' = 'test_3',
          'scan.startup.mode' = 'latest-offset',
          'format' = 'json'
      )
  """

  # Execute DDL statement to create the source table
  t_env.execute_sql(source_ddl)

  # Retrieve the source table
  source_table = t_env.from_path('source_table')

  print("Source Table Schema:")
  source_table.print_schema()

  # Define a SQL query to select all columns from the source table
  sql_query = "SELECT * FROM source_table"

  # Execute the query and retrieve the result table
  result_table = t_env.sql_query(sql_query)

  # Print the result table to the console
  result_table.execute().print()
  ```
  output
  ```bash
  dexter@dexter-VirtualBox:~/Desktop/kafka_project/RealTimeStreamingPig.py Kafka_Flink_Pipeline$ python3 kafka_flink_streaming
  Source Table Schema:
  (
    `ID` BIGINT,
    `Login` STRING,
    `Name` STRING,
    `HTML_URL` STRING,
    `Public_Repos` INT,
    `Public_Gists` INT,
    `Followers` INT,
    `Following` INT
  )
  +----+----------------------+--------------------------------+--------------------------------+--------------------------------+--------------+--------------+-------------+-------------+
  | op |                   ID |                          Login |                           Name |                       HTML_URL | Public_Repos | Public_Gists |   Followers |   Following |
  +----+----------------------+--------------------------------+--------------------------------+--------------------------------+--------------+--------------+-------------+-------------+
  | +I |                   71 |                        uggedal |                 Eivind Uggedal |     https://github.com/uggedal |           47 |           43 |         180 |           0 |
  | +I |                   74 |                         mmower |                     Matt Mower |      https://github.com/mmower |           78 |          126 |          59 |           1 |
  | +I |                   75 |                          abhay |                    Abhay Kumar |       https://github.com/abhay |           42 |            2 |         162 |           1 |
  | +I |                   77 |                     benburkert |                    Ben Burkert |  https://github.com/benburkert |          138 |           37 |         200 |           7 |
  | +I |                   75 |                          abhay |                    Abhay Kumar |       https://github.com/abhay |           42 |            2 |         162 |           1 |
  | +I |                    1 |                        mojombo |             Tom Preston-Werner |     https://github.com/mojombo |           66 |           62 |       23705 |          11 |
  | +I |                   90 |                             sr |                    Simon Rozet |          https://github.com/sr |          133 |           56 |         573 |         199 |
  | +I |                  106 |                          queso |                     Josh Owens |       https://github.com/queso |           83 |          106 |         338 |          23 |
  | +I |                  108 |                          drnic |                Dr Nic Williams |       https://github.com/drnic |          664 |          265 |        1754 |          11 |
  | +I |                  110 |                       danwrong |                       Dan Webb |    https://github.com/danwrong |           32 |           37 |         345 |          31 |
  | +I |                   18 |                   wayneeseguin |                 Wayne E Seguin | https://github.com/wayneese... |          104 |           95 |         733 |          19 |
  | +I |                   90 |                             sr |                    Simon Rozet |          https://github.com/sr |          133 |           56 |         573 |         199 |
  | +I |                    1 |                        mojombo |             Tom Preston-Werner |     https://github.com/mojombo |           66 |           62 |       23705 |          11 |
  | +I |                   36 |                      KirinDave |                    Dave Fayram |   https://github.com/KirinDave |           83 |           97 |         408 |          10 |
  | +I |                   90 |                             sr |                    Simon Rozet |          https://github.com/sr |          133 |           56 |         573 |         199 |
  | +I |                  113 |                       mattetti |                 Matt Aimonetti |    https://github.com/mattetti |          296 |          354 |           0 |           0 |
  | +I |                  117 |                         grempe |                    Glenn Rempe |      https://github.com/grempe |           42 |           10 |         120 |          27 |
  | +I |                   18 |                   wayneeseguin |                 Wayne E Seguin | https://github.com/wayneese... |          104 |           95 |         733 |          19 |
  | +I |                   18 |                   wayneeseguin |                 Wayne E Seguin | https://github.com/wayneese... |          104 |           95 |         733 |          19 |
  | +I |                   18 |                   wayneeseguin |                 Wayne E Seguin | https://github.com/wayneese... |          104 |           95 |         733 |          19 |
  | +I |                   18 |                   wayneeseguin |                 Wayne E Seguin | https://github.com/wayneese... |          104 |           95 |         733 |          19 |
  | +I |                   18 |                   wayneeseguin |                 Wayne E Seguin | https://github.com/wayneese... |          104 |           95 |         733 |          19 |
  | +I |                   18 |                   wayneeseguin |                 Wayne E Seguin | https://github.com/wayneese... |          104 |           95 |         733 |          19 |
  | +I |                   46 |                      bmizerany |                 Blake Mizerany |   https://github.com/bmizerany |          166 |          170 |        1400 |          36 |
  | +I |                  118 |                         peterc |                   Peter Cooper |      https://github.com/peterc |           42 |          201 |         663 |          61 |
  | +I |                   49 |                       hornbeck |                  John Hornbeck |    https://github.com/hornbeck |            8 |           35 |          70 |          35 |
  | +I |                  121 |                   up_the_irons |                   Garry Dolley | https://github.com/up_the_i... |           43 |            4 |          34 |           6 |
  | +I |                    4 |                         wycats |                    Yehuda Katz |      https://github.com/wycats |          284 |          761 |       10166 |          13 |
  | +I |                  121 |                   up_the_irons |                   Garry Dolley | https://github.com/up_the_i... |           43 |            4 |          34 |           6 |
  | +I |                    2 |                        defunkt |                Chris Wanstrath |     https://github.com/defunkt |          107 |          274 |       21749 |         214 |
  | +I |                   38 |                          atmos |                  Corey Donohoe |       https://github.com/atmos |          170 |          178 |        1314 |         167 |
  | +I |                  124 |                        brosner |                   Brian Rosner |     https://github.com/brosner |          113 |           22 |         929 |         111 |
  | +I |                  121 |                   up_the_irons |                   Garry Dolley | https://github.com/up_the_i... |           43 |            4 |          34 |           6 |
  | +I |                  134 |                       jnicklas |                  Jonas Nicklas |    https://github.com/jnicklas |          147 |           95 |         843 |           8 |
  | +I |                  122 |                    cristibalan |                   Cristi Balan | https://github.com/cristibalan |           24 |           18 |          84 |          34 |
  | +I |                  134 |                       jnicklas |                  Jonas Nicklas |    https://github.com/jnicklas |          147 |           95 |         843 |           8 |
  | +I |                  136 |                   simonjefford |                  Simon Jefford | https://github.com/simonjef... |           81 |           48 |          33 |           3 |
  | +I |                  139 |                 leahneukirchen |                Leah Neukirchen | https://github.com/leahneuk... |          188 |            8 |        1195 |           9 |
  | +I |                  139 |                 leahneukirchen |                Leah Neukirchen | https://github.com/leahneuk... |          188 |            8 |        1195 |           9 |
  | +I |                  108 |                          drnic |                Dr Nic Williams |       https://github.com/drnic |          664 |          265 |        1754 |          11 |
  | +I |                   81 |                     engineyard |              Engine Yard, Inc. |  https://github.com/engineyard |          335 |           25 |          10 |           0 |
  | +I |                  139 |                 leahneukirchen |                Leah Neukirchen | https://github.com/leahneuk... |          188 |            8 |        1195 |           9 |
  | +I |                   18 |                   wayneeseguin |                 Wayne E Seguin | https://github.com/wayneese... |          104 |           95 |         733 |          19 |
  | +I |                   20 |                     kevinclark |                    Kevin Clark |  https://github.com/kevinclark |           41 |           30 |         109 |           6 |
  | +I |                   49 |                       hornbeck |                  John Hornbeck |    https://github.com/hornbeck |            8 |           35 |          70 |          35 |
  | +I |                  124 |                        brosner |                   Brian Rosner |     https://github.com/brosner |          113 |           22 |         929 |         111 |
  | +I |                  141 |                    technomancy |                 Phil Hagelberg | https://github.com/technomancy |           98 |           56 |        2087 |           0 |
  | +I |                   25 |                          caged |                  Justin Palmer |       https://github.com/caged |          166 |           99 |        2363 |          44 |
  | +I |                   25 |                          caged |                  Justin Palmer |       https://github.com/caged |          166 |           99 |        2363 |          44 |
  | +I |                  150 |                      sevenwire |                      Sevenwire |   https://github.com/sevenwire |           14 |            1 |           2 |           0 |
  | +I |                  159 |               technicalpickles |                   Josh Nichols | https://github.com/technica... |          350 |          301 |         978 |         164 |
  | +I |                  145 |                       lazyatom |                     James Adam |    https://github.com/lazyatom |           90 |           58 |         197 |          18 |
  | +I |                  137 |                           josh |                    Joshua Peek |        https://github.com/josh |           28 |            0 |        2421 |         213 |
  | +I |                  164 |                       cdcarter |               Christian Carter |    https://github.com/cdcarter |           91 |           37 |          39 |          15 |
  | +I |                   47 |                       jnewland |                  Jesse Newland |    https://github.com/jnewland |          128 |           43 |         723 |          99 |
  | +I |                   68 |                             bs |               Britt Selvitelle |          https://github.com/bs |           32 |           17 |         137 |          53 |
  | +I |                   90 |                             sr |                    Simon Rozet |          https://github.com/sr |          133 |           56 |         573 |         199 |
  | +I |                  128 |                 collectiveidea |                Collective Idea | https://github.com/collecti... |          174 |            7 |          30 |           0 |
  | +I |                  128 |                 collectiveidea |                Collective Idea | https://github.com/collecti... |          174 |            7 |          30 |           0 |
  | +I |                  128 |                 collectiveidea |                Collective Idea | https://github.com/collecti... |          174 |            7 |          30 |           0 |
  | +I |                  128 |                 collectiveidea |                Collective Idea | https://github.com/collecti... |          174 |            7 |          30 |           0 |
  | +I |                  128 |                 collectiveidea |                Collective Idea | https://github.com/collecti... |          174 |            7 |          30 |           0 |
  | +I |                  128 |                 collectiveidea |                Collective Idea | https://github.com/collecti... |          174 |            7 |          30 |           0 |
  | +I |                  128 |                 collectiveidea |                Collective Idea | https://github.com/collecti... |          174 |            7 |          30 |           0 |
  ```

### **`elasticsearch`** & **`kibana`**

- installation
  - installing elastic
    ```bash
    wget https://artifacts.elastic.co/downloads/elasticsearch/elasticsearch-7.17.15-linux-x86_64.tar.gz
    ```
  - extract it
    ```bash
    tar -xzf elasticsearch-7.17.15-linux-x86_64.tar.gz
    ```
  - navigate to it
    ```bash
    cd elasticsearch-7.17.15/
    ```
  - run elastic
    ```bash
    ./bin/elasticsearch
    ```
  - if you saw this Warning
    ```bash
    warning: usage of JAVA_HOME is deprecated, use ES_JAVA_HOME
    Future versions of Elasticsearch will require Java 11; your Java version from [/usr/lib/jvm/java-8-openjdk-amd64/jre] does not meet this requirement. Consider switching to a distribution of Elasticsearch with a bundled JDK. If you are already using a distribution with a bundled JDK, ensure the JAVA_HOME environment variable is not set.
    warning: usage of JAVA_HOME is deprecated, use ES_JAVA_HOME
    Future versions of Elasticsearch will require Java 11; your Java version from [/usr/lib/jvm/java-8-openjdk-amd64/jre] does not meet this requirement. Consider switching to a distribution of Elasticsearch with a bundled JDK. If you are already using a distribution with a bundled JDK, ensure the JAVA_HOME environment variable is not set.
    ```
    - stop elastic **`ctrl + c`**
    - copy the path where your **`java 11`** & **`bin/elasticsearch`** located & execute it in **`bashrc`** file
    ```bash
    gedit ~/.bashrc

    # replace the path with your path
    export ES_JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64
    /home/dexter/Desktop/elasticsearch/bin/elasticsearch

    source ~/.bashrc
    ```
  - **`elasticsearch`** cluster is running in
    ```bash
    localhost:9200
    ```
    the page is in **`json`** format you should se output similar to this
    ```json
    name	"dexter-VirtualBox"
    cluster_name	"elasticsearch"
    cluster_uuid	"9iQNBdY9TuyYczdM2n162g"
    version
    number	"7.17.15"
    build_flavor	"default"
    build_type	"tar"
    build_hash	"0b8ecfb4378335f4689c4223d1f1115f16bef3ba"
    build_date	"2023-11-10T22:03:46.987399016Z"
    build_snapshot	false
    lucene_version	"8.11.1"
    minimum_wire_compatibility_version	"6.8.0"
    minimum_index_compatibility_version	"6.0.0-beta1"
    tagline	"You Know, for Search"
    ```
  - installing kibana
    ```bash
    curl -O https://artifacts.elastic.co/downloads/kibana/kibana-7.17.15-linux-x86_64.tar.gz
    ```
  - extract it
    ```bash
    tar -xzf kibana-7.17.15-linux-x86_64.tar.gz
    ```
  - navigate to it
    ```bash
    cd kibana-7.17.15-linux-x86_64/
    ```
  - run it **[elastic should be started in order to access elastic web interface UI]**
    ```bash
    ./bin/kibana
    ```
  - **`kibana`** is running in
    ```bash
    localhost:5601
    ```
- setup
  - make sure you put the correct path to your connector jars & include **;** in the first one
    ```python
    # Specify connector and format jars
    t_env.get_config().get_configuration().set_string(
        "pipeline.jars",
        "file:///path to/flink-sql-connector-kafka-1.16.3.jar;"
        "file:///path to/flink-sql-connector-elasticsearch7-3.0.1-1.17.jar"
    )
    ```
  - put the right properties
    ```python
    # Define source table DDL
    source_ddl = """
        CREATE TABLE source_table (
    ....
        ) WITH (
            'connector' = 'kafka',
            'topic' = '<your topic name>',
            'properties.bootstrap.servers' = 'localhost:9092',
            'properties.group.id' = 'test_3',
            'scan.startup.mode' = 'latest-offset',
            'format' = 'json'
        )
    """

    # Define sink table DDL
    sink_ddl = """
        CREATE TABLE sink_table(
    ...
        ) WITH (
            'connector' = 'elasticsearch-7',
            'index' = '<give this a name>',
            'hosts' = 'http://localhost:9200',
            'format' = 'json'
        )
    """
    ```
  - replace the last lines with this
    ```python
    # Process the data
    result_table = source_table
    # Retrieve the sink table
    sink_table = t_env.from_path('sink_table')

    print("Sink Table Schema:")
    sink_table.print_schema()

    # Insert the processed data into the sink table
    result_table.execute_insert('sink_table').wait()
    ```
  - run all (kafka , flink , elastic , kibana)
    ```python
    bin/zookeeper-server-start.sh config/zookeeper.properties
    bin/kafka-server-start.sh config/server.properties
    ./bin/start-cluster.sh
    ./bin/elasticsearch
    ./bin/kibana
    ```
- kafka - flink - elastic - kibana streaming code
  - make sure that kafka , flink , elastic , kibana are running
  - execute this code first then the **`producer`** program
  ```python
  from pyflink.table import TableEnvironment, EnvironmentSettings

  # Create a TableEnvironment
  env_settings = EnvironmentSettings.in_streaming_mode()
  t_env = TableEnvironment.create(env_settings)

  # Specify connector and format jars
  t_env.get_config().get_configuration().set_string(
      "pipeline.jars",
      "file:///home/dexter/Desktop/kafka_project/flink-sql-connector-kafka-1.16.3.jar;"
      "file:///home/dexter/Desktop/kafka_project/flink-sql-connector-elasticsearch7-3.0.1-1.17.jar"
  )

  # Define source table DDL
  source_ddl = """
      CREATE TABLE source_table (
  	    ID BIGINT,
  	    Login VARCHAR,
  	    Name VARCHAR,
  	    HTML_URL VARCHAR,
  	    Public_Repos INT,
  	    Public_Gists INT,
  	    Followers INT,
  	    Following INT
      ) WITH (
          'connector' = 'kafka',
          'topic' = 'my_topic',
          'properties.bootstrap.servers' = 'localhost:9092',
          'properties.group.id' = 'test_3',
          'scan.startup.mode' = 'latest-offset',
          'format' = 'json'
      )
  """

  # Define sink table DDL
  sink_ddl = """
      CREATE TABLE sink_table(
  	    ID BIGINT,
  	    Login VARCHAR,
  	    Name VARCHAR,
  	    HTML_URL VARCHAR,
  	    Public_Repos INT,
  	    Public_Gists INT,
  	    Followers INT,
  	    Following INT
      ) WITH (
          'connector' = 'elasticsearch-7',
          'index' = 'my_data',
          'hosts' = 'http://localhost:9200',
          'format' = 'json'
      )
  """

  # Execute DDL statements to create tables
  t_env.execute_sql(source_ddl)
  t_env.execute_sql(sink_ddl)

  # Retrieve the source table
  source_table = t_env.from_path('source_table')

  print("Source Table Schema:")
  source_table.print_schema()

  # Process the data
  result_table = source_table
  # Retrieve the sink table
  sink_table = t_env.from_path('sink_table')

  print("Sink Table Schema:")
  sink_table.print_schema()

  # Insert the processed data into the sink table
  result_table.execute_insert('sink_table').wait()
  ```
- if the code runs correctly
  - navigate to **localhost:5601**
  - in side bar: **_Stack Management > Index Management > indices_**
  - you should see the name of index written before in the code example: **`'index' = 'my_data'`**
    ![Untitled](Kafka,%20Flink,%20Elastic%20search%20Project%2037586fa574884870a61b51a4aa7e71b8/Untitled%202.png)
  - navigate to **_index Patterns_** in the same level & create template with the same name of the index example : “my_data”
    ![Untitled](Kafka,%20Flink,%20Elastic%20search%20Project%2037586fa574884870a61b51a4aa7e71b8/Untitled%203.png)
  - now inside bar navigate to **_Dashboard > Create_** you should see the index then drag & drop the columns from the left side & choose the proper data schema
    ![Untitled](Kafka,%20Flink,%20Elastic%20search%20Project%2037586fa574884870a61b51a4aa7e71b8/Untitled%204.png)
    - custom your api data & save it
    ![Untitled](Kafka,%20Flink,%20Elastic%20search%20Project%2037586fa574884870a61b51a4aa7e71b8/Untitled%205.png)
- Word count code
  - run this then producer of kafka
  ```python
  from pyflink.table.expressions import col, lit
  from pyflink.common import Row
  from pyflink.table.udf import udf, udtf, ScalarFunction
  from nltk.corpus import stopwords
  import codecs
  import re
  import string

  from pyflink.table import (
      DataTypes, TableEnvironment, EnvironmentSettings
  )

  def word_count_stream_processing():
      # Create a TableEnvironment
      env_settings = EnvironmentSettings.in_streaming_mode()
      t_env = TableEnvironment.create(env_settings)

      # Specify connector and format jars
      t_env.get_config().get_configuration().set_string(
          "pipeline.jars",
          "file:///home/dexter/Desktop/kafka_project/flink-sql-connector-kafka-1.16.3.jar;"
          "file:///home/dexter/Desktop/kafka_project/flink-sql-connector-elasticsearch7-3.0.1-1.17.jar"
      )

      # Define source table DDL
      source_ddl = """
          CREATE TABLE source_table (
              ID BIGINT,
              Login VARCHAR,
              Name VARCHAR,
              HTML_URL VARCHAR,
              Public_Repos INT,
              Public_Gists INT,
              Followers INT,
              Following INT
          ) WITH (
              'connector' = 'kafka',
              'topic' = 'my_topic',
              'properties.bootstrap.servers' = 'localhost:9092',
              'properties.group.id' = 'test_3',
              'scan.startup.mode' = 'latest-offset',
              'format' = 'json'
          )
      """

      sink_ddl = """
          CREATE TABLE sink_table(
              word VARCHAR,
              number BIGINT
          ) WITH (
              'connector' = 'elasticsearch-7',
              'index' = 'demo-word-count',
              'hosts' = 'http://localhost:9200',
              'format' = 'json'
          )
      """

      # Execute source and sink DDLs
      t_env.execute_sql(source_ddl)
      t_env.execute_sql(sink_ddl)

      # Read from source table
      source_table = t_env.from_path('source_table')

      print("\nKafka source table Schema")
      source_table.print_schema()

      # Preprocess the tweet text
      @udf(result_type=DataTypes.STRING())
      def preprocess_text(review):
          review = codecs.decode(review, 'unicode_escape')  # remove escape characters
          review = review[2:-1]
          review = re.sub('((www\.[^\s]+)|(https?://[^\s]+))', 'URL', review)
          review = re.sub('[^\x00-\x7f]', '', review)
          review = re.sub('@[^\s]+', 'USER', review)
          review = re.sub('RT', '', review)
          review = review.lower().replace("ё", "е")
          review = re.sub('[^a-zA-Zа-яА-Я1-9]+', ' ', review)
          review = re.sub(' +', ' ', review)
          return review.strip()

      processed_table = source_table.select(preprocess_text(col('HTML_URL')))

      print("\nData cleaning and processing ...")

      # Split lines into words
      @udtf(result_types=[DataTypes.STRING()])
      def split(line: Row):
          for s in line[0].split():
              yield Row(s)

      word_table = processed_table.flat_map(split).alias('word')
      print("\n\n Splitting lines to words ...")
      # Normalize the word by removing punctuation
      @udf(result_type=DataTypes.STRING())
      def normalize(word: str):
          return word.translate(str.maketrans('', '', string.punctuation))

      normalized_table = word_table.select(normalize(col('word')).alias('word'))
      print("Removing stop words (the, is, a, an, ...)")

      # Initialize the stop word resource with NLTK
      class RemoveStopWord(ScalarFunction):
          stop_words = set(stopwords.words('english'))

          def eval(self, word: str):
              return word not in self.stop_words

      remove_stop_words_udf = udf(RemoveStopWord(), result_type=DataTypes.BOOLEAN())
      filtered_table = normalized_table.filter(remove_stop_words_udf(col('word')))

      # Compute the word count using Table API
      result = filtered_table.group_by(col('word')) \
          .select(col('word'), lit(1).count.alias('number'))

      result.execute_insert('sink_table').wait()
      print("Processing complete!")

  word_count_stream_processing()
  ```
  ![Untitled](Kafka,%20Flink,%20Elastic%20search%20Project%2037586fa574884870a61b51a4aa7e71b8/Untitled%206.png)

---

### Commands to Launch

```bash
bin/zookeeper-server-start.sh config/zookeeper.properties
bin/kafka-server-start.sh config/server.properties

bin/kafka-topics.sh --create --topic my_topic --bootstrap-server localhost:9092 --partitions 1 --replication-factor 1
bin/kafka-topics.sh --list --bootstrap-server localhost:9092
bin/kafka-console-consumer.sh --topic my_topic --bootstrap-server localhost:9092 --from-beginning

./bin/start-cluster.sh

# to check if there is any elastic running
ps aux | grep elasticsearch

# kill the process
pkill -f elasticsearch

./bin/kibana

```

```bash
# to check if there is any elastic running
ps aux | grep elasticsearch

# kill the process
pkill -f elasticsearch
```

```bash
sudo systemctl stop elasticsearch
sudo apt-get purge elasticsearch
sudo apt-get autoremove
sudo rm -rf /etc/elasticsearch
sudo rm -rf /usr/share/elasticsearch
sudo rm -rf /var/lib/elasticsearch
sudo systemctl stop kibana
sudo apt-get remove kibana
sudo apt-get purge kibana

wget https://artifacts.elastic.co/downloads/elasticsearch/elasticsearch-7.17.15-linux-x86_64.tar.gz
tar -xzf elasticsearch-7.17.15-linux-x86_64.tar.gz
cd elasticsearch-7.17.15/
./bin/elasticsearch

elastic: localhost:9200
# for elasticsearch write in terminal this
export ES_JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64
/home/dexter/Desktop/elasticsearch/bin/elasticsearch

installation kibana:
curl -O https://artifacts.elastic.co/downloads/kibana/kibana-7.17.15-linux-x86_64.tar.gz
tar -xzf kibana-7.17.15-linux-x86_64.tar.gz
cd kibana-7.17.15-linux-x86_64/
./bin/kibana

kibana: localhost:5601
```
