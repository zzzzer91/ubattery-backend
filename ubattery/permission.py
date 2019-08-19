"""用户权限验证。"""

from functools import wraps
from collections import namedtuple

from flask import abort, session

from .status_code import UNAUTHORIZED, FORBIDDEN
from .extensions import cache
from .models import User

UserSimpleInfo = namedtuple('UserSimpleInfo', 'name type')

# 超级用户
SUPER_USER = 64
# 普通用户
COMMON_USER = 0


@cache.memoize()
def _get_user(user_id: int):
    """返回用户信息，使用了缓存。"""

    # 使用 get()，不需要再执行 first()
    user = User.query.get(user_id)
    if user is None:
        return None
    return UserSimpleInfo(user.name, user.type)


def get_current_user():
    """从 session 中 user_id 获取用户信息。"""

    user_id = session.get('user_id')
    # current_app.logger.debug(f'user_id: {user_id}')
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
    """

    def decorate(view):
        @wraps(view)
        def wrapper(*args, **kwargs):
            current_user = get_current_user()
            if current_user is None:
                # 用户未登录
                abort(UNAUTHORIZED)
            if permission is not None and current_user.type < permission:
                # 不符合权限
                abort(FORBIDDEN)
            return view(*args, **kwargs)
        return wrapper
    return decorate

