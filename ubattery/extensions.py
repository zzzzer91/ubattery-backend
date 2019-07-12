from flask_sqlalchemy import SQLAlchemy
from flask_pymongo import PyMongo
from flask_caching import Cache

db = SQLAlchemy()
mongo = PyMongo()
# 缓存的默认过期时间是 300 秒
cache = Cache()