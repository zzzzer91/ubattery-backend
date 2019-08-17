from flask import request, abort, url_for
from flask.views import MethodView
from sqlalchemy.exc import IntegrityError

from ubattery.checker import RE_SIX_CHARACTER_CHECKER
from ubattery.extensions import mysql, cache
from ubattery.models import User
from ubattery.permission import permission_required, SUPER_USER
from ubattery.status_code import INTERNAL_SERVER_ERROR
from ubattery import json_response


class UsersAPI(MethodView):
    """超级管理员对普通用户的相关操作"""

    # 只有超级管理员才有权限
    decorators = [permission_required(SUPER_USER)]

    @cache.cached()
    def get(self):
        """获取普通用户列表，这里不能用缓存，因为一旦管理员添加或修改用户，会使用过期缓存。
        但也有解决办法，就是在添加或修改用户后，删除本块缓存。
        """

        users = User.query.filter(User.type != 1).all()

        data = []
        for user in users:
            data.append({
                'userName': user.name,
                'lastLoginTime': user.last_login_time,
                'comment': user.comment,
                'loginCount': user.login_count,
                'userStatus': True if user.status == 1 else False,
                'createTime': user.create_time
            })

        return json_response.build(json_response.SUCCESS, data=data)

    def post(self):
        """添加新用户"""

        data = request.get_json()

        user_name = data['userName']
        if not RE_SIX_CHARACTER_CHECKER.match(user_name):
            abort(INTERNAL_SERVER_ERROR)

        password = data['password']
        if not RE_SIX_CHARACTER_CHECKER.match(password):
            abort(INTERNAL_SERVER_ERROR)

        comment = data['comment']
        if len(comment) > 64:
            abort(INTERNAL_SERVER_ERROR)

        user = User(name=user_name, comment=comment)
        user.set_password(password)
        mysql.session.add(user)
        try:
            mysql.session.commit()
        except IntegrityError:
            return json_response.build(json_response.ERROR, msg='用户已存在！')

        # 删除用户列表缓存
        cache.delete(f'view/{url_for(".users_api")}')

        return json_response.build(json_response.SUCCESS, msg=f'创建用户 {user_name} 成功！')

    def put(self, user_name):
        """设置用户资料"""

        data = request.get_json()

        comment = data['comment']
        if len(comment) > 64:
            abort(INTERNAL_SERVER_ERROR)

        user_status = data['userStatus']
        if not isinstance(user_status, bool):  # 拿到的是 bool 类型
            abort(INTERNAL_SERVER_ERROR)
        user_status = int(user_status)

        user = User.query.filter_by(name=user_name).first()
        user.comment = comment
        user.status = user_status
        mysql.session.commit()

        cache.delete(f'view/{url_for(".users_api")}')

        return json_response.build(json_response.SUCCESS, msg=f'修改用户 {user_name} 成功！')