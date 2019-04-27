import functools

from flask import Blueprint, abort, session, g

from ubattery.db import get_db

bp = Blueprint('auth', __name__)


def login_required(view):
    """用户登录以后才能进行相关操作。
    在每个视图中可以使用 装饰器 来完成这个工作。
    装饰器返回一个新的视图，该视图包含了传递给装饰器的原视图。
    新的函数检查用户 是否已载入。
    如果已载入，那么就继续正常执行原视图，否则就重定向到登录页面。
    """

    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            abort(403)

        return view(**kwargs)

    return wrapped_view


# bp.before_app_request() 注册一个在视图函数之前运行的函数，不论其 URL 是什么。
@bp.before_app_request
def load_logged_in_user():
    """load_logged_in_user 检查用户 id 是否已经储存在 session 中，
    并从数据库中获取用户数据，然后储存在 g.user 中。
    g.user 的持续时间比请求要长。
    如果没有用户 id ，或者 id 不存在，那么 g.user 将会是 None 。
    """

    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        with get_db().cursor() as cursor:
            g.user = cursor.execute(
                'SELECT * FROM user WHERE id = ?', (user_id,)
            ).fetchone()