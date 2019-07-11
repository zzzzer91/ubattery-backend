#!/bin/bash

ABSOLUTE_CURRENT_PATH="$(cd "$(dirname $0)";pwd)"
INSTANCE_DIR="${ABSOLUTE_CURRENT_PATH}/instance"

echo '项目初始化中...'

# 如果文件夹不存在，创建文件夹
if [ ! -d "${INSTANCE_DIR}" ]; then
    mkdir "${INSTANCE_DIR}"
    echo "${INSTANCE_DIR} 创建完毕！"
else
    echo "${INSTANCE_DIR} 已存在！"
fi

DATABASE_DIR="${INSTANCE_DIR}/database"
if [ ! -d "${DATABASE_DIR}" ]; then
    mkdir "${DATABASE_DIR}"
    echo "${DATABASE_DIR} 创建完毕！"
else
    echo "${DATABASE_DIR} 已存在！"
fi

MEDIA_DIR="${INSTANCE_DIR}/media"
if [ ! -d "${MEDIA_DIR}" ]; then
    mkdir "${MEDIA_DIR}"
    echo "${MEDIA_DIR} 创建完毕！"
else
    echo "${MEDIA_DIR} 已存在！"
fi

# 生成 .env
ENV_FILE="${ABSOLUTE_CURRENT_PATH}/.env"
MYSQL_ROOT_PASSWORD=''
if [ ! -e "${ENV_FILE}" ]; then
    echo "# docker-compose.yml 中使用的环境变量" > ${ENV_FILE}
    read -p "输入 MySQL root 密码：" MYSQL_ROOT_PASSWORD
    echo "MYSQL_ROOT_PASSWORD=${MYSQL_ROOT_PASSWORD}" > ${ENV_FILE}
    echo "MYSQL_DATA_DIR=${INSTANCE_DIR}/database/mysql" >> ${ENV_FILE}
    echo "REDIS_DATA_DIR=${INSTANCE_DIR}/database/redis" >> ${ENV_FILE}
    echo "${ENV_FILE} 生成完毕！"
else
    echo "${ENV_FILE} 已存在！"
fi

# 生成 config.py
CONFIG_FILE="${INSTANCE_DIR}/config.py"
MYSQL_DATABASE=''
if [ ! -e "${CONFIG_FILE}" ]; then
    echo "# flask 使用的一些敏感配置" > ${CONFIG_FILE}
    read -p "输入 MySQL 数据库名：" MYSQL_DATABASE
    echo "SECRET_KEY = $(python -c 'import os; print(os.urandom(16))')" > ${CONFIG_FILE}
    echo "SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:${MYSQL_ROOT_PASSWORD}@localhost:3306/${MYSQL_DATABASE}'" >> ${CONFIG_FILE}
    echo "${CONFIG_FILE} 生成完毕！"
else
    echo "${CONFIG_FILE} 已存在！"
fi

# 安装项目 Python 依赖
PYTHON_REQUIREMENTS_FILE="${ABSOLUTE_CURRENT_PATH}/requirements.txt"
TSINGHUA_PIP_MIRROR="https://pypi.tuna.tsinghua.edu.cn/simple"
if [ -e "${PYTHON_REQUIREMENTS_FILE}" ]; then
    echo "安装项目 Python 依赖..."
    python3 -m pip install -U -r ${PYTHON_REQUIREMENTS_FILE} -i ${TSINGHUA_PIP_MIRROR}
fi

echo "项目初始化完毕！"