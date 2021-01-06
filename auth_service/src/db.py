import redis
from flask_sqlalchemy import SQLAlchemy

from src.settings import REDIS_HOST, REDIS_PORT

db = SQLAlchemy()
redis_db = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0)
