import os

from flask import Flask

TEMPLATE_FOLDER = './dist'


def create_app(test_config=None):
    """`create_app()` 是一个应用工厂函数。"""

    # `__name__` 是当前 Python 模块的名称。
    # 应用需要知道在哪里设置路径， 使用 `__name__` 是一个方便的方法。
    # `instance_relative_config=True` 告诉应用配置文件是相对于 instance folder 的相对路径。
    # 实例文件夹在 app 包的外面，用于存放本地数据（例如配置密钥和数据库），不应当提交到版本控制系统。
    app = Flask(__name__,
                instance_relative_config=True,
                template_folder=TEMPLATE_FOLDER,
                static_folder=f'{TEMPLATE_FOLDER}/assets')

    load_config(app, test_config)

    register_db(app)
    register_blueprints(app)
    register_apis(app)
    register_errors(app)

    return app


def load_config(app, test_config):
    # `os.makedirs()` 可以确保 `app.instance_path` 存在。
    # Flask 不会自动创建实例文件夹，但是必须确保创建这个文件夹，
    # 因为 SQLite 数据库文件会被 保存在里面。
    if not os.path.exists(app.instance_path):
        os.makedirs(app.instance_path)

    # `app.config.from_mapping()` 设置一个应用的 缺省配置
    app.config.from_mapping(
        # SECRET_KEY 是被 Flask 和扩展用于保证数据安全的。
        # 在开发过程中， 为了方便可以设置为 'dev' ，但是在发布的时候应当使用一个随机值来重载它。
        SECRET_KEY='dev'
    )

    if test_config is None:
        # `app.config.from_pyfile()` 使用 *config.py* 中的值来重载缺省配置，
        # 如果 *config.py* 存在的话。
        # 例如，当正式部署的时候，用于设置一个正式的 `SECRET_KEY` 。
        # 参数 `silent` 设为 `True`，使文件不存在时不报错
        app.config.from_pyfile('config.py', silent=True)
    else:
        # 如果传入了 `test_config`，则会优先使用
        app.config.update(test_config)


def register_db(app):
    from . import db

    db.init_app(app)


def register_blueprints(app):
    from .blueprints.index import bp as index_bp
    from .blueprints.auth import bp as auth_bp

    app.register_blueprint(index_bp)
    # 本来蓝图 index 的 url 默认是 '/index'，
    # 把它改为 '/'
    app.add_url_rule('/', endpoint='index')

    app.register_blueprint(auth_bp)


def register_apis(app):
    from .apis import bp, API_BASE_URL

    app.register_blueprint(bp, url_prefix=API_BASE_URL)


def register_errors(app):
    from flask import render_template

    # 注册 404 处理页面
    @app.errorhandler(404)
    def page_not_found(error):
        return render_template('404.html'), 404
