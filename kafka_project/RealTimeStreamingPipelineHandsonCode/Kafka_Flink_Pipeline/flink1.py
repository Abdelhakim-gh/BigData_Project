from pyflink.table import TableEnvironment, EnvironmentSettings

env_settings = EnvironmentSettings.in_streaming_mode()
t_env = TableEnvironment.create(env_settings)

t_env.get_config().get_configuration().set_string(
    "pipeline.jars",
    "file:///home/dexter/Desktop/kafka_project/flink-sql-connector-kafka-3.0.2-1.18.jar"
)

source_ddl = """
    CREATE TABLE source_table(
        id INT,
        name VARCHAR,
        owner VARCHAR,
        url VARCHAR,
        description VARCHAR
    ) WITH (
        'connector' = 'kafka',
        'topic' = 'my-test',
        'properties.bootstrap.servers' = 'localhost:9092',
        'properties.group.id' = 'test-3',
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

# Collect the results and print them
results = result_table.execute().collect()
print(results)
# for row in results:
#     print(row)
