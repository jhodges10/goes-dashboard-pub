from rq import Queue
from redis import Redis
from logging import StreamHandler, FileHandler
import logging
import logstash
import sys
import os

# config - aside from our database, the rest is for use by Flask
from pathlib import Path  # python3 only
from dotenv import load_dotenv
env_path = '.env'
load_dotenv(dotenv_path=env_path, verbose=False)


redis_conn = Redis(os.getenv("REDIS_HOSTNAME", default="localhost"), port=6379)
try:
    q = Queue(connection=redis_conn, default_timeout=60000)
except Exception as e:
    logging.error(f"Unable to connect to redis: {e}")

logstash_host = os.getenv("LOGSTASH_HOSTNAME", default="localhost")

# print(os.environ)

# Logger Setup
logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S')

api_logger = logging.getLogger("api")
api_logger.setLevel(logging.INFO)
api_logger.addHandler(logstash.TCPLogstashHandler(
    logstash_host, 5959, version=1))
api_logger.addHandler(StreamHandler())

logger = logging.getLogger("nasa_api")
# logger.addHandler(logstash.TCPLogstashHandler(logstash_host, 5959, version=1))
# logger.addHandler(StreamHandler())
logger.addHandler(FileHandler('logfile.log'))

# Database Setup
db_us = os.getenv("POSTGRES_USER", default="dashboard")
db_ps = os.getenv("POSTGRES_PASSWORD", default="dashboard")
db_db = os.getenv("POSTGRES_DB", default="dashboard")
db_url = os.getenv("POSTGRES_HOSTNAME", default="localhost")
db_port = os.getenv("POSTGRES_PORT", default=5500)

POSTGRES_URI = f"postgresql://{db_us}:{db_ps}@{db_url}:{db_port}/{db_db}"
