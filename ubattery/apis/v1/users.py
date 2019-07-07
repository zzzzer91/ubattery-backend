from flask import jsonify, request, abort
from flask.views import MethodView
from sqlalchemy.exc import IntegrityError

from ubattery.blueprints.auth import super_user_required
from ubattery.common import checker

from ubattery.extensions import db
from ubattery.models import User


class UsersAPI(MethodView):
    """超级管理员对普通用户的相关操作"""

    # 只有超级管理员才有权限
    decorators = [super_user_required]

    def get(self):
        """获取普通用户列表"""

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

        return jsonify({
            'status': True,
            'data': data
        })

    def post(self):
        """添加新用户"""

        data = request.get_json()

        user_name = data['userName']
        if not checker.RE_SIX_CHARACTER_CHECKER.match(user_name):
            abort(500)

        password = data['password']
        if not checker.RE_SIX_CHARACTER_CHECKER.match(password):
            abort(500)

        comment = data['comment']
        if len(comment) > 64:
            abort(500)

        user = User(name=user_name, comment=comment)
        user.set_password(password)
        db.session.add(user)
        try:
            db.session.commit()
        except IntegrityError:
            return jsonify({
                'status': False,
                'data': '用户已存在！'
            })

        return jsonify({
            'status': True,
            'data': None
        })

    def put(self, user_name):
        """设置用户资料"""

        data = request.get_json()

        comment = data['comment']
        if len(comment) > 64:
            abort(500)

        user_status = data['userStatus']
        if not isinstance(user_status, bool):  # 拿到的是 bool 类型
            abort(500)
        user_status = int(user_status)

        user = User.query.filter_by(name=user_name).first()
        user.comment = comment
        user.status = user_status
        db.session.commit()

        return jsonify({
            'status': True,
            'data': None
        })