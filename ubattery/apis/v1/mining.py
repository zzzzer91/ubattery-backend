from flask import request, abort
from flask.views import MethodView

from ubattery.common import checker, mapping
from ubattery.extensions import mysql, mongo
from ubattery.blueprints.auth import permission_required


def _get_base_data():
    """获取基本数据。"""

    args = request.args

    data_come_from = args.get('dataComeFrom')
    # 因为 data_come_from 会拼接成 sql 语句，为防 sql 注入，须判断下是不是正确表名
    if data_come_from not in mapping.MYSQL_TABLE_TO_NAME:
        abort(500)

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
    col_names = ['时间']
    # 把字段名转换成实际名，同时也是进行 sql 过滤
    for k in need_params.split(','):
        col_names.append(mapping.BASE_LABEL_TO_NAME[k])  # 会过滤不合法参数名

    rows = mysql.session.execute(
        'SELECT '
        'timestamp,'
        f'{need_params} '
        f'FROM {data_come_from} '
        'WHERE timestamp >= :start_date '
        'ORDER BY timestamp '
        'LIMIT :data_limit',
        {'start_date': start_date, 'data_limit': data_limit}
    )
    rows = [tuple(row) for row in rows]
    data = {
        'colNames': col_names,
        'rows': rows
    }

    if len(rows) == 0:
        return {
            'status': False,
            'data': '未查询到相关数据！'
        }

    return {
        'status': True,
        'data': data
    }


def _get_charging_process_data():
    """获取充电过程数据。"""

    data = list(mongo.db['charging_process'].find(
        projection={'_id': 0, 'first_id': 0, 'last_id': 0}
    ))

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
        data = None
        if name == 'base':
            data = _get_base_data()
        elif name == 'charging-process':
            data = _get_charging_process_data()
        return data