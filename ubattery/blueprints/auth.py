import functools

from flask import Blueprint, abort, session, g, request, jsonify
from werkzeug.security import check_password_hash

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
# 这时全局的
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
            cursor.execute(
                'SELECT * FROM user WHERE id = %s', (user_id,)
            )

            g.user = cursor.fetchone()


@bp.route('/login', methods=('POST',))
def login():
    """Log in a registered user by adding the user id to the session."""

    data = request.get_json()

    with get_db().cursor() as cursor:
        cursor.execute(
            'SELECT id, password FROM user WHERE username = %s', (data['userName'],)
        )

        user_info = cursor.fetchone()

    error = None
    if user_info is None:
        error = '帐号错误！'
    # check_password_hash() 以相同的方式哈希提交的密码并安全的比较哈希值。
    # 如果匹配成功，那么密码就是正确的。
    elif not check_password_hash(user_info[1], data['password']):
        error = '密码错误！'

    # 成功
    if error is None:
        # session 是一个 dict ，它用于储存横跨请求的值。
        # 当验证 成功后，用户的 id 被储存于一个新的会话中。
        # 会话数据被储存到一个 向浏览器发送的 cookie 中，在后继请求中，浏览器会返回它。
        # Flask 会安全对数据进行 签名 以防数据被篡改。
        session.clear()
        # 现在用户的 id 已被储存在 session 中，可以被后续的请求使用。
        # 请每个请求的开头，如果用户已登录，那么其用户信息应当被载入，以使其可用于其他视图。
        session['user_id'] = user_info[0]

        return jsonify({
            'status': True,
            'data': error
        })

    return jsonify({
        'status': False,
        'data': error
    })


@bp.route('/logout')
def logout():
    """注销的时候需要把用户 id 从 session 中移除。
    然后 load_logged_in_user 就不会在后继请求中载入用户了。
    """

    session.clear()
    return jsonify({
        'status': True,
        'data': None
    })