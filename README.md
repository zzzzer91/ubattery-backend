# 电池大数据分析平台后端

电池大数据分析平台后端，RESTful 设计风格，前后端分离。

## 安装依赖

```bash
$ ./setup.sh
```

## 创建配置文件

1、先在当前目录下创建文件夹 *instance* 及 *instance/media*。

2、创建配置文件 *instance/config.py*，并做如下配置：

```python
# 用于加密 cookie 中的 session id
# 输 `python -c 'import os; print(os.urandom(16))'` 生成
SECRET_KEY = b'<随机字符串>'
# MySQL
SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:<密码>@localhost:3306/<数据库名>'
```

## 启动数据库（docker）

```bash
$ docker-compose up
```

## 生成 MySQL 表

```bash
$ flask initdb
```

## 启动 flask

```bash
$ flask run
```

## 其他

### 管理 MySQL

浏览器访问 `127.0.0.1:8080` 端口。

### 管理 Redis

命令行输入：

```bash
$ docker run -it --rm --network <网络名> redis:5 redis-cli -h <redis 主机名>
```

## 设计原则

1. 字段合法性都在前端校验，一旦后台收到了不合法字段，说明前端被绕过，直接返回 500

## TODO

- 测试

- 后台验证数据合法性

