from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import func
import sqlalchemy.dialects.mysql as mysql_type

from ubattery.extensions import db


class User(db.Model):

    __tablename__ = 'user'

    id = db.Column(
        mysql_type.INTEGER, primary_key=True
    )

    name = db.Column(
        mysql_type.CHAR(16), nullable=False, unique=True, index=True
    )

    password = db.Column(
        mysql_type.VARCHAR(128), nullable=False
    )

    # `default` 参数是在 python 中对数据填充默认值，不体现在表中
    # `server_default` 会体现在表中，必须是字符串类型，或某些函数类型，
    # 如 mysql 中的 `curtime()`
    type = db.Column(
        mysql_type.TINYINT(unsigned=True), nullable=False, server_default='0',
        comment='用户类型，1超级用户，0普通用户'
    )

    avatar_name = db.Column(
        mysql_type.VARCHAR(256), nullable=False, server_default='null.jpg',
        comment='头像图片名'
    )

    last_login_time = db.Column(
        mysql_type.DATETIME,
        comment='最后登录时间'
    )

    comment = db.Column(
        mysql_type.VARCHAR(100),
        comment='备注'
    )

    login_count = db.Column(
        mysql_type.INTEGER(unsigned=True), nullable=False, server_default='0',
        comment='登录次数'
    )

    status = db.Column(
        mysql_type.TINYINT(unsigned=True), nullable=False, server_default='1',
        comment='是否允许登录，1 允许，0 禁止'
    )

    create_time = db.Column(
        mysql_type.DATETIME, nullable=False, server_default=func.curtime(),
        comment='创建时间'
    )

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def validate_password(self, password):
        return check_password_hash(self.password, password)


class VehicleData(db.Model):
    """vehicle_id: 4F37195C1A908CFBE0532932A8C0EECB"""

    __tablename__ = 'yutong_vehicle1'

    id = db.Column(mysql_type.INTEGER, primary_key=True)

    province = db.Column(mysql_type.VARCHAR(100), comment='省')

    city = db.Column(mysql_type.VARCHAR(100), comment='城市')

    timestamp = db.Column(mysql_type.DATETIME, index=True, comment='CST 时间')

    bty_t_vol = db.Column(mysql_type.DECIMAL(10, 2), comment='电池总电压')

    bty_t_curr = db.Column(mysql_type.DECIMAL(10, 2), comment='电池总电流')

    battery_soc = db.Column(mysql_type.DECIMAL(5, 2), comment='SOC')

    s_b_max_t = db.Column(mysql_type.INTEGER, comment='电池最高温度')

    max_t_s_b_num = db.Column(mysql_type.INTEGER, comment='最高温度电池号')

    s_b_min_t = db.Column(mysql_type.INTEGER, comment='电池最低温度')

    min_t_s_b_num = db.Column(mysql_type.INTEGER, comment='最低温度电池号')

    s_b_max_v = db.Column(mysql_type.DECIMAL(10, 6), comment='电池最高电压')

    max_v_e_core_num = db.Column(mysql_type.INTEGER, comment='最高电压电芯号')

    s_b_min_v = db.Column(mysql_type.DECIMAL(10, 6), comment='电池最低电压')

    min_v_e_core_num = db.Column(mysql_type.INTEGER, comment='最低电压电芯号')

    p_t_p = db.Column(mysql_type.DECIMAL(10, 2), comment='正向累计电量')

    r_t_p = db.Column(mysql_type.DECIMAL(10, 2), comment='反向累计电量')

    total_mileage = db.Column(mysql_type.INTEGER, comment='总里程')

    bty_sys_rated_capacity = db.Column(mysql_type.INTEGER, comment='额定容量')

    bty_sys_rated_consumption = db.Column(mysql_type.INTEGER, comment='额定能量')

    met_spd = db.Column(mysql_type.INTEGER, comment='车速')

    byt_ma_sys_state = db.Column(mysql_type.INTEGER, comment='充电状态，6 代表充电中')