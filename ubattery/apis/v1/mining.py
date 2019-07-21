from flask import request, abort
from flask.views import MethodView

from ubattery.common import checker, mapping
from ubattery.extensions import mysql, mongo
from ubattery.blueprints.auth import permission_required


def _get_base_data():
    """获取基本数据。"""

    args = request.args

    # 因为 data_come_from 会拼接成 sql 语句，为防 sql 注入，须判断下是不是正确表名
    # 映射失败会自动抛出 500
    data_come_from, name_to_field = mapping.MYSQL_NAME_TO_TABLE[args.get('dataComeFrom')]

    start_date = args.get('startDate')
    if start_date is None or not checker.RE_DATETIME_CHECKER.match(start_date):
        abort(500)

    # 必须是 int 类型，不然 pymysql 进行类型转换时会出现错误
    # 如果是 None，int 转换时会自动抛出 500 错误
    data_limit = int(args.get('dataLimit'))
    if data_limit > 10000:  # 限制每次获取的数据
        abort(500)

    need_params = args.get('needParams', '').strip()
    if need_params == '':
        abort(500)
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
        return {
            'status': False,
            'data': '未查询到相关数据！'
        }

    return {
        'status': True,
        'data': data
    }


def _get_battery_statistic_data(name):
    """获取电池的一些统计数据。"""

    data = mongo.db['battery_statistic'].find_one(
        {'_id': name},
        projection={'_id': False, 'data': True}
    )['data']

    if len(data) == 0:
        return {
            'status': False,
            'data': '未查询到相关数据！'
        }

    return {
        'status': True,
        'data': data
    }


class MiningAPI(MethodView):

    decorators = (permission_required(),)

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
            abort(404)
        return json