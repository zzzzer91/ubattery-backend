#!/bin/bash

# 启动 redis 客户端

project_path=$(cd `dirname $0`; pwd)
project_name="${project_path##*/}"

# echo ${project_name}
docker run -it --rm --network ${project_name}_default redis:5 redis-cli -h ${project_name}_redis_1