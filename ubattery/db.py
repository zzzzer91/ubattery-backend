import pymysql
import click
from flask import current_app, g
from flask.cli import with_appcontext


def get_db():
    """返回一个数据库连接。"""

    # g 是一个特殊对象，独立于每一个请求。
    # 在处理请求过程中，它可以用于储存 可能多个函数都会用到的数据。
    # 把连接储存于其中，可以多次使用，而不用在同一个 请求中每次调用 get_db 时都创建一个新的连接。
    if 'db' not in g:
        g.db = pymysql.connect(
            # current_app 是另一个特殊对象，该对象指向处理请求的 Flask 应用。
            # 这里 使用了应用工厂，那么在其余的代码中就不会出现应用对象。
            # 当应用创建后，在处理一个请求时， get_db 会被调用。这样就需要使用 current_app 。
            **current_app.config['DATABASE'],
            # 在默认情况下 cursor 方法返回的是 BaseCursor 类型对象，
            # BaseCursor 类型对象在执行查询后每条记录的结果以列表(list)表示。
            # 如果要返回字典(dict)表示的记录，
            # 就要设置 cursorclass 参数为 pymysql.cursors.DictCursor 类。
            # 但这种方法有缺陷，如在 SQL 语句中使用了某些函数，DATE_FORMAT()，
            # 会导致返回错误的 key 名
            # cursorclass=pymysql.cursors.DictCursor
        )

    return g.db


def close_db(e=None):
    """close_db 通过检查 g.db 来确定连接是否已经建立。

    如果连接已建立，那么 就关闭连接。
    以后会在应用工厂中告诉应用 close_db 函数，这样每次请求后就会调用它。
    """

    db = g.pop('db', None)
    if db:
        db.close()


def init_db():
    """create new tables."""

    db = get_db()

    # `open_resource()` 打开一个文件，该文件名是相对于 app 包的。
    # 这样就不需要考虑以后应用具体部署在哪个位置。 
    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))


# `click.command()` 定义一个名为 init-db 命令行，
# 它调用 init_db 函数，并为用户显示一个成功的消息。 
@click.command('init-db')
@with_appcontext
def init_db_command():
    """Clear existing data and create new tables."""

    init_db()
    click.echo('Initialized the database.')


def init_app(app):
    """Register database functions with the Flask app. This is called by
    the application factory.
    """

    # `app.teardown_appcontext()` 告诉 Flask 在返回响应后进行清理的时候调用此函数。
    app.teardown_appcontext(close_db)
    # `app.cli.add_command()` 添加一个新的 可以与 flask 一起工作的命令。
    app.cli.add_command(init_db_command)
