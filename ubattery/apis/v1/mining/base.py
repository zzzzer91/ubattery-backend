from flask import request, abort
from flask.views import MethodView

from ubattery import json_response
from ubattery.models import MYSQL_NAME_TO_TABLE
from ubattery.checker import RE_DATETIME_CHECKER
from ubattery.extensions import mysql, mongo
from ubattery.permission import permission_required
from ubattery.status_code import NOT_FOUND, INTERNAL_SERVER_ERROR


def _get_base_data():
    """获取基本数据。"""

    args = request.args

    # 因为 data_come_from 会拼接成 sql 语句，为防 sql 注入，须判断下是不是正确表名
    arg = args.get('dataComeFrom')
    if arg not in MYSQL_NAME_TO_TABLE:
        abort(INTERNAL_SERVER_ERROR)
    data_come_from, name_to_field = MYSQL_NAME_TO_TABLE[arg]

    start_date = args.get('startDate')
    if start_date is None or not RE_DATETIME_CHECKER.match(start_date):
        abort(INTERNAL_SERVER_ERROR)

    # 必须是 int 类型，不然 pymysql 进行类型转换时会出现错误
    # 如果是 None，int 转换时会自动抛出 500 错误
    data_limit = int(args.get('dataLimit'))
    if data_limit > 10000:  # 限制每次获取的数据
        abort(INTERNAL_SERVER_ERROR)

    need_params = args.get('needParams', '').strip()
    if need_params == '':
        abort(INTERNAL_SERVER_ERROR)
    col_names = []
    # 把字段名转换成实际名，同时也是进行 sql 过滤
    for k in need_params.split(','):
        col_names.append(name_to_field[k])  # 会过滤不合法参数名
    col_names = ', '.join(col_names)

    rows = mysql.session.execute(
        'SELECT '
        'timestamp,'
        f'{col_names} '
        f'FROM {data_come_from} '
        'WHERE timestamp >= :start_date '
        'ORDER BY timestamp '
        'LIMIT :data_limit',
        {'start_date': start_date, 'data_limit': data_limit}
    )
    data = [tuple(row) for row in rows]

    if len(data) == 0:
        return json_response.build(code=json_response.ERROR, msg='未查询到相关数据！')

    return json_response.build(data=data)


def _get_battery_statistic_data(name):
    """获取电池的一些统计数据。"""

    data = mongo.db['battery_statistic'].find_one(
        {'_id': name},
        projection={'_id': False, 'data': True}
    )['data']

    if len(data) == 0:
        return json_response.build(code=json_response.ERROR, msg='未查询到相关数据！')

    return json_response.build(data=data)


class BasicDataAPI(MethodView):

    decorators = [permission_required()]

    def get(self, name):
        json = None
        if name == 'base':
            json = _get_base_data()
        elif name == 'charging-process':
            json = _get_battery_statistic_data(name.replace('-', '_'))
        elif name == 'working-condition':
            json = _get_battery_statistic_data(name.replace('-', '_'))
        elif name == 'battery-statistic':
            json = _get_battery_statistic_data(name.replace('-', '_'))
        else:
            abort(NOT_FOUND)
        return json