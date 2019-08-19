from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import func
import sqlalchemy.dialects.mysql as mysql_type

from ubattery.extensions import mysql


class User(mysql.Model):
    __tablename__ = 'user'

    id = mysql.Column(
        mysql_type.INTEGER, primary_key=True
    )

    name = mysql.Column(
        mysql_type.CHAR(16), nullable=False, unique=True, index=True
    )

    password = mysql.Column(
        mysql_type.VARCHAR(128), nullable=False
    )

    # `default` 参数是在 python 中对数据填充默认值，不体现在表中
    # `server_default` 会体现在表中，必须是字符串类型，或某些函数类型
    type = mysql.Column(
        mysql_type.TINYINT, nullable=False, server_default='0',
        comment='用户类型，1超级用户，0普通用户'
    )

    avatar_name = mysql.Column(
        mysql_type.VARCHAR(256), nullable=False,
        comment='头像图片名'
    )

    last_login_time = mysql.Column(
        mysql_type.DATETIME,
        comment='最后登录时间'
    )

    comment = mysql.Column(
        mysql_type.VARCHAR(100),
        comment='备注'
    )

    login_count = mysql.Column(
        mysql_type.INTEGER, nullable=False, server_default='0',
        comment='登录次数'
    )

    status = mysql.Column(
        mysql_type.TINYINT, nullable=False, server_default='1',
        comment='是否允许登录，1 允许，0 禁止'
    )

    # 注意 MySQL 5.7 用 `func.CURRENT_TIMESTAMP()`
    # 而不能用 `func.curtime()`，因为还不支持
    create_time = mysql.Column(
        mysql_type.DATETIME, nullable=False, server_default=func.CURRENT_TIMESTAMP(),
        comment='创建时间'
    )

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def validate_password(self, password):
        return check_password_hash(self.password, password)