from flask_sqlalchemy import SQLAlchemy
from flask_pymongo import PyMongo
from flask_caching import Cache
from flask_socketio import SocketIO
from celery import Celery

mysql = SQLAlchemy()

# 注意 mongo 的 URI 规则和 MySQL 中的稍有不同，
# mongo 在 URI 中指定数据库后，认证时用的是该数据库，而不是 admin
mongo = PyMongo()

# 缓存的默认过期时间是 300 秒
cache = Cache()

socketio = SocketIO()

celery = Celery('ubattery', broker='redis://localhost:6379/0', backend='redis://localhost:6379/0')