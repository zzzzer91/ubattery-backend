from datetime import datetime

from flask import session, request, Blueprint

from .extensions import mysql
from .models import User
from .permission import permission_required
from .json_response import build_json_response, ERROR

auth_bp = Blueprint(f'auth', __name__)


@auth_bp.route('/login', methods=('GET', 'POST'))
def login():
    """登录验证"""

    if request.method == 'GET':
        user_id = session.get('user_id')

        if user_id is None:
            return build_json_response(code=ERROR)

        user: User = User.query.get(user_id)

        msg = None
        if user is None:
            msg = 'cookie 获取失败！'
        elif user.status == 0:
            msg = '该用户已被禁止登录！'

        if msg:
            return build_json_response(code=ERROR, msg=msg)

    else:
        data = request.get_json()
        user_name = data['userName']

        user: User = User.query.filter_by(name=user_name).first()

        msg = None
        if user is None:
            msg = '帐号或密码错误！'
        # check_password_hash() 以相同的方式哈希提交的密码并安全的比较哈希值。
        # 如果匹配成功，那么密码就是正确的。
        elif not user.validate_password(data['password']):
            msg = '帐号或密码错误！'
        elif user.status == 0:
            msg = '该用户已被禁止登录！'

        if msg:
            return build_json_response(code=ERROR, msg=msg)

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

    data = {
        'userName': user.name,
        'userType': user.type,
        'avatarName': user.avatar_name,
        'lastLoginTime': user.last_login_time,
        'loginCount': user.login_count
    }
    return build_json_response(data=data)


@auth_bp.route('/logout', methods=('POST',))
@permission_required()
def logout():
    """注销的时候把用户 id 从 session 中移除。"""

    session.clear()

    return build_json_response()