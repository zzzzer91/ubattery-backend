#!/bin/bash

export FLASK_ENV=production

# 启动数据库
docker-compose up -d

# 前台运行测试
# gunicorn wsgi:app -w 1 -b 172.18.0.1:5000 -k eventlet

# 使用本地套接字，需要 Nginx 作为服务器
# --log-file <file_name> 输出到指定文件
# -D 后台运行
gunicorn wsgi:app -w 3 -b 172.18.0.1:5000 -k eventlet -D

# 创建后台任务执行者
# -A 指定 celery 实例位置
# -D 后台运行 celery worker
celery -A celery_worker.celery worker --loglevel=INFO --concurrency=2 -D

echo 'OK!'