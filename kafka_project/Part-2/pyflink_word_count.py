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