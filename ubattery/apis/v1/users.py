from flask import jsonify, request
from flask.views import MethodView
from werkzeug.security import generate_password_hash
from pymysql import IntegrityError

from ubattery.blueprints.auth import super_user_required
from ubattery.db import get_db
from ubattery.common import checker


class UsersAPI(MethodView):

    decorators = [super_user_required]

    def get(self):
        """获取普通用户列表"""

        db = get_db()
        with db.cursor() as cursor:
            cursor.execute(
                'SELECT '
                'user_name, '
                'DATE_FORMAT(last_login_time, \'%Y-%m-%d %H:%i:%s\'), '
                'comment, '
                'login_count, '
                'user_status '
                'FROM users WHERE user_type != 1'
            )
            rows = cursor.fetchall()

        data = []
        for row in rows:
            data.append({
                'userName': row[0],
                'lastLoginTime': row[1],
                'comment': row[2],
                'loginCount': row[3],
                'userStatus': True if row[4] == 1 else False,
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
            return jsonify({
                'status': False,
                'data': '创建失败！'
            })

        password = data['password']
        if not checker.RE_SIX_CHARACTER_CHECKER.match(password):
            return jsonify({
                'status': False,
                'data': '创建失败！'
            })

        comment = data['comment']
        if len(comment) > 64:
            return jsonify({
                'status': False,
                'data': '创建失败！'
            })

        db = get_db()
        with db.cursor() as cursor:
            try:
                cursor.execute(
                    'INSERT INTO users '
                    '(user_name, password, comment) '
                    'VALUES (%s, %s, %s)',
                    (user_name, generate_password_hash(password), comment)
                )
            except IntegrityError:
                return jsonify({
                    'status': False,
                    'data': '用户已存在！'
                })
            db.commit()

        return jsonify({
            'status': True,
            'data': None
        })

    def put(self, user_name):

        data = request.get_json()

        comment = data['comment']
        if len(comment) > 64:
            return jsonify({
                'status': False,
                'data': '修改失败！'
            })

        user_status = data['userStatus']
        if not isinstance(user_status, bool):  # 拿到的是 bool 类型
            return jsonify({
                'status': False,
                'data': '修改失败！'
            })
        user_status = int(user_status)

        db = get_db()
        with db.cursor() as cursor:
            cursor.execute(
                'UPDATE users '
                'set comment = %s, '
                'user_status = %s '
                'WHERE user_name = %s',
                (comment, user_status, user_name)
            )
            db.commit()

        return jsonify({
            'status': True,
            'data': None
        })