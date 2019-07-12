import os

import click
from flask import Flask, render_template

from ubattery.json_encoder import MyJSONEncoder
from ubattery.extensions import db, mongo, cache
from ubattery.blueprints.index import index_bp
from ubattery.blueprints.auth import auth_bp
from ubattery.apis import api_v1_bp


def create_app(test_config=None):
    """`create_app()` 是一个应用工厂函数。"""

    # `__name__` 是当前 Python 模块的名称。
    # 应用需要知道在哪里设置路径， 使用 `__name__` 是一个方便的方法。
    # `instance_relative_config=True` 告诉应用配置文件是相对于 instance folder 的相对路径。
    # 实例文件夹在 app 包的外面，用于存放本地数据（例如配置密钥和数据库），不应当提交到版本控制系统。
    app = Flask(
        __name__,
        instance_relative_config=True,
        template_folder='./dist',
        static_folder='./dist/assets'
    )

    # `os.makedirs()` 可以确保 `app.instance_path` 存在。
    # Flask 不会自动创建实例文件夹
    if not os.path.exists(app.instance_path):
        os.mkdir(app.instance_path)

    # 放置一些媒体文件，如图片，视频等
    app.media_folder = os.path.join(app.instance_path, 'media')

    # 放置用户上传头像的文件夹
    app.avatar_folder = os.path.join(app.media_folder, 'avatars')

    # 使用自己的 json 编码器，序列化 MySQL 某些不能直接 json 序列化的类型
    app.json_encoder = MyJSONEncoder

    load_config(app, test_config)

    register_extensions(app)
    register_blueprints(app)
    register_apis(app)
    register_errorhandlers(app)
    register_commands(app)

    return app


def load_config(app, test_config):

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

    db.init_app(app)

    mongo.init_app(app)
    # flask-mongo 有点小问题，
    # 如果在 URI 中配置了数据库，那么认证的时候用的是配置的数据库，而不是 admin，
    # 这会导致失败。
    # 但不配置，db 就会为 None
    # 所以这里我们要手动指定下
    mongo.db = mongo.cx[app.config['MONGO_DATABASE']]

    cache.init_app(app)


def register_blueprints(app):

    app.register_blueprint(index_bp)
    # 本来蓝图 index 的 url 默认是 '/index'，
    # 把它改为 '/'
    app.add_url_rule('/', endpoint='index')

    app.register_blueprint(auth_bp)


def register_apis(app):

    app.register_blueprint(api_v1_bp)


def register_errorhandlers(app):

    # 注册 403 处理页面
    # 缓存函数中的 key_prefix 参数，代表 key 名
    @app.errorhandler(403)
    @cache.cached(key_prefix='errorhandler_forbidden')
    def forbidden(error):
        return render_template('403.html'), 403

    # 注册 404 处理页面
    @app.errorhandler(404)
    @cache.cached(key_prefix='errorhandler_page_not_found')
    def page_not_found(error):
        return render_template('404.html'), 404


def register_commands(app):
    """注册一些有用的命令，通过 `flask <命令名>` 调用。"""

    @app.cli.command('init-db')
    def init_db():
        """初始化表。"""

        db.create_all()
        click.echo('Initialized database.')

    @app.cli.command('clear-cache')
    def clear_cache():
        """清理 Redis 中的缓存。"""

        cache.clear()
        click.echo('Cleared cache.')
