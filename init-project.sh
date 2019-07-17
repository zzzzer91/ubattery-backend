#!/bin/bash

ABSOLUTE_CURRENT_PATH="$(cd "$(dirname $0)";pwd)"
INSTANCE_DIR="${ABSOLUTE_CURRENT_PATH}/instance"
DATABASE_DIR="${INSTANCE_DIR}/database"
MEDIA_DIR="${INSTANCE_DIR}/media"
CONFIG_FILE="${INSTANCE_DIR}/config.py"
ENV_FILE="${ABSOLUTE_CURRENT_PATH}/.env"
PYTHON_REQUIREMENTS_FILE="${ABSOLUTE_CURRENT_PATH}/requirements.txt"

# python pip 的源
PIP_MIRROR="https://pypi.tuna.tsinghua.edu.cn/simple"

echo '项目初始化中...'

# 如果文件夹不存在，创建文件夹
if [ ! -d "${INSTANCE_DIR}" ]; then
    mkdir "${INSTANCE_DIR}"
    echo "${INSTANCE_DIR} 创建完毕！"
else
    echo "${INSTANCE_DIR} 已存在！"
fi

if [ ! -d "${DATABASE_DIR}" ]; then
    mkdir "${DATABASE_DIR}"
    echo "${DATABASE_DIR} 创建完毕！"
else
    echo "${DATABASE_DIR} 已存在！"
fi

if [ ! -d "${MEDIA_DIR}" ]; then
    mkdir "${MEDIA_DIR}"
    echo "${MEDIA_DIR} 创建完毕！"
else
    echo "${MEDIA_DIR} 已存在！"
fi

mysql_root_password=''
mysql_database=''
mongo_root_password=''
mongo_database=''
read -p "输入 MySQL root 密码：" mysql_root_password
read -p "输入 MySQL 数据库名：" mysql_database
read -p "输入 Mongo root 密码：" mongo_root_password
read -p "输入 Mongo 数据库名：" mongo_database

# 生成 config.py
echo "# flask 使用的一些敏感配置" > ${CONFIG_FILE}
#
echo "# 用于加密 cookie 中的 session id" >> ${CONFIG_FILE}
echo "SECRET_KEY = $(python -c 'import os; print(os.urandom(16))')" >> ${CONFIG_FILE}
#
echo "# MySQL" >> ${CONFIG_FILE}
echo "SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:${mysql_root_password}@localhost:3306/${mysql_database}'" >> ${CONFIG_FILE}
#
echo "# MongoDB" >> ${CONFIG_FILE}
echo "MONGO_URI = 'mongodb://root:${mongo_root_password}@localhost:27017'" >> ${CONFIG_FILE}
echo "MONGO_DATABASE = '${mongo_database}'" >> ${CONFIG_FILE}
#
echo "# Redis" >> ${CONFIG_FILE}
echo "REDIS_URL = 'redis://@localhost:6379/0'" >> ${CONFIG_FILE}
#
echo "# flask-caching" >> ${CONFIG_FILE}
echo "CACHE_REDIS_URL = REDIS_URL" >> ${CONFIG_FILE}
#
echo "# celery" >> ${CONFIG_FILE}
echo "CELERY_BROKER_URL = REDIS_URL" >> ${CONFIG_FILE}
echo "CELERY_RESULT_BACKEND = REDIS_URL" >> ${CONFIG_FILE}
#
echo "${CONFIG_FILE} 生成完毕！"

# 生成 .env
echo "# docker-compose.yml 中使用的环境变量" > ${ENV_FILE}
echo "# 注意值两边的单双引号，会被当作值的一部分，这在 docker-compose 中会出现问题" >> ${ENV_FILE}
#
echo "# MySQL" >> ${ENV_FILE}
echo "MYSQL_ROOT_PASSWORD=${mysql_root_password}" >> ${ENV_FILE}
echo "MYSQL_DATA_DIR=${DATABASE_DIR}/mysql" >> ${ENV_FILE}
#
echo "# Mongo" >> ${ENV_FILE}
echo "MONGO_INITDB_ROOT_USERNAME=root" >> ${ENV_FILE}
echo "MONGO_INITDB_ROOT_PASSWORD=${mongo_root_password}" >> ${ENV_FILE}
echo "MONGO_DATA_DIR=${DATABASE_DIR}/mongo" >> ${ENV_FILE}
#
echo "# Redis" >> ${ENV_FILE}
echo "REDIS_DATA_DIR=${DATABASE_DIR}/redis" >> ${ENV_FILE}
#
echo "${ENV_FILE} 生成完毕！"

# 安装项目 Python 依赖
if [ -e "${PYTHON_REQUIREMENTS_FILE}" ]; then
    echo "安装并更新项目的 Python 依赖..."
    python3 -m pip install -U -r ${PYTHON_REQUIREMENTS_FILE} -i ${PIP_MIRROR}
fi

echo "项目初始化完毕！"