#!/bin/bash

export FLASK_ENV=production

# 启动数据库
docker-compose up -d

# 前台运行测试
# gunicorn wsgi:app -w 1 -b 0:4000 -k eventlet

# 使用本地套接字，需要 Nginx 作为服务器
# --log-file <file_name> 输出到指定文件
# -D 后台运行
gunicorn wsgi:app -w 3 -b unix:/tmp/ubattery.sock -k eventlet -D
