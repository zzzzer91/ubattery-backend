from flask_sqlalchemy import SQLAlchemy
from flask_caching import Cache

db = SQLAlchemy()
# 缓存的默认过期时间是 300 秒
cache = Cache()