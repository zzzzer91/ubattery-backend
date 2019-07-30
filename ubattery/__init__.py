import click
from flask import Flask


def create_app(test_config=None):
    """`create_app()` 是一个应用工厂函数。"""

    from .json_encoder import MyJSONEncoder

    # `__name__` 是当前 Python 模块的名称。
    # 应用需要知道在哪里设置路径， 使用 `__name__` 是一个方便的方法。
    # `instance_relative_config=True` 告诉应用配置文件是相对于 instance folder 的相对路径。
    # 实例文件夹在 app 包的外面，用于存放本地数据（例如配置密钥和数据库），不应当提交到版本控制系统。
    app = Flask(__name__, instance_relative_config=True)

    # 使用自己的 json 编码器，序列化 MySQL 某些不能直接 json 序列化的类型
    app.json_encoder = MyJSONEncoder

    load_config(app, test_config)

    register_extensions(app)
    register_apis(app)
    register_commands(app)

    return app


def load_config(app, test_config):
    """载入配置。"""

    # `app.config.from_mapping()` 设置一个应用的 缺省配置
    app.config.from_mapping(
        # SECRET_KEY 是被 Flask 和扩展用于保证数据安全的。
        # 在开发过程中， 为了方便可以设置为 'dev' ，但是在发布的时候应当使用一个随机值来重载它。
        SECRET_KEY='dev',
        # 如果设置成 True (默认情况)，Flask-SQLAlchemy 将会追踪对象的修改并且发送信号。
        # 这需要额外的内存， 如果不必要的可以禁用它。
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        # # 连接池大小，默认 5
        SQLALCHEMY_POOL_SIZE=5,
        # 缓存实例，这里使用 redis
        CACHE_TYPE='redis'
    )

    if test_config is None:
        # `app.config.from_pyfile()` 使用 *config.py* 中的值来重载缺省配置，
        # 如果 *config.py* 存在的话。
        # 该文件存放敏感配置，不敏感的放在本文件就行了。
        # 例如，当正式部署的时候，用于设置一个正式的 `SECRET_KEY` 。
        # 参数 `silent` 设为 `True`，使文件不存在时不报错
        app.config.from_pyfile('config.py', silent=True)
    else:
        # 如果传入了 `test_config`，则会优先使用
        app.config.update(test_config)


def register_extensions(app):
    """注册拓展。"""

    from .extensions import mysql, mongo, cache

    # flask-sqlalchemy
    mysql.init_app(app)

    # flask-pymongo
    mongo.init_app(app)
    # flask-mongo 有点小问题，
    # 如果在 URI 中配置了数据库，那么认证的时候用的是配置的数据库，而不是 admin，
    # 这会导致失败。
    # 但不配置，db 就会为 None
    # 所以这里我们要手动指定下
    mongo.db = mongo.cx[app.config['MONGO_DATABASE']]

    # flask-caching
    cache.init_app(app)


def register_apis(app):
    """注册 API 蓝图。"""

    from .apis import api_v1_bp

    app.register_blueprint(api_v1_bp)


def register_commands(app):
    """注册一些有用的命令，通过 `flask <命令名>` 调用。"""

    from .extensions import mysql, cache

    @app.cli.command('init-db')
    def init_db():
        """初始化表。"""

        mysql.create_all()
        click.echo('Initialized database.')

    @app.cli.command('clear-cache')
    def clear_cache():
        """清理 Redis 中的缓存。"""

        cache.clear()
        click.echo('Cleared cache.')
