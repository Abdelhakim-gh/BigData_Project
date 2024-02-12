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
