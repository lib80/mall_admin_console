import redis
from utils.const import REDIS_HOST, REDIS_PORT, REDIS_PASSWORD
redis_conn = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PASSWORD, db=0, decode_responses=True)
