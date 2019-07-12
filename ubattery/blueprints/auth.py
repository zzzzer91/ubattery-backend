import functools
from datetime import datetime

from flask import Blueprint, abort, session, request, current_app

from ubattery.extensions import mysql, cache
from ubattery.models import User

auth_bp = Blueprint('auth', __name__)


@cache.memoize()
def _get_user(user_id: int):
    """返回用户信息，使用了缓存。"""

    # 使用 get()，不需要再执行 first()
    user = User.query.get(user_id)
    if user is None:
        return None
    return {'name': user.name, 'type': user.type}


def get_current_user():
    """从 session 中 user_id 获取用户信息。"""

    user_id = session.get('user_id')
    current_app.logger.debug(f'user_id: {user_id}')
    if user_id is None:
        return None
    user = _get_user(user_id)
    # 该用户 id 不存在，删除其缓存
    if user is None:
        cache.delete_memoized(_get_user, user_id)
    return user


def permission_required(permission=None):
    """用户需要相关权限才能操作。

    :param permission: 指定了用户需要的权限，None 代表普通用户。

    TODO 权限名规范化。
    """

    def decorate(view):
        @functools.wraps(view)
        def wrapper(*args, **kwargs):
            current_user = get_current_user()
            if current_user is None:
                abort(403)
            if permission is not None and current_user['type'] != permission:
                # 不符合权限
                abort(403)
            return view(*args, **kwargs)
        return wrapper
    return decorate


@auth_bp.route('/login', methods=('GET', 'POST'))
def login():

    if request.method == 'GET':
        user_id = session.get('user_id')

        if user_id is None:
            return {
                'status': False,
                'data': None
            }

        user: User = User.query.get(user_id)

        error = None
        if user is None:
            error = 'cookie 获取失败！'
        elif user.status == 0:
            error = '该用户已被禁止登录！'

        if error:
            return {
                'status': False,
                'data': error
            }

    else:
        data = request.get_json()
        user_name = data['userName']

        user: User = User.query.filter_by(name=user_name).first()

        error = None
        if user is None:
            error = '帐号或密码错误！'
        # check_password_hash() 以相同的方式哈希提交的密码并安全的比较哈希值。
        # 如果匹配成功，那么密码就是正确的。
        elif not user.validate_password(data['password']):
            error = '帐号或密码错误！'
        elif user.status == 0:
            error = '该用户已被禁止登录！'

        if error:
            return {
                'status': False,
                'data': error
            }

        # 更新登录时间
        user.last_login_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        user.login_count += 1
        mysql.session.commit()

    # session 是一个 dict ，它用于储存横跨请求的值。
    # 当验证 成功后，用户的 id 被储存于一个新的会话中。
    # 会话数据被储存到一个 向浏览器发送的 cookie 中，在后继请求中，浏览器会返回它。
    # Flask 会安全对数据进行 签名 以防数据被篡改。
    # 默认存活时间为到浏览器关闭
    session.clear()
    # 现在用户的 id 已被储存在 session 中，可以被后续的请求使用。
    # 请每个请求的开头，如果用户已登录，那么其用户信息应当被载入，以使其可用于其他视图。
    session['user_id'] = user.id

    return {
        'status': True,
        'data': {
            'userName': user.name,
            'userType': user.type,
            'avatarName': user.avatar_name,
            'lastLoginTime': user.last_login_time,
            'loginCount': user.login_count
        }
    }


@auth_bp.route('/logout')
@permission_required()
def logout():
    """注销的时候把用户 id 从 session 中移除。"""

    session.clear()

    return {
        'status': True,
        'data': None
    }