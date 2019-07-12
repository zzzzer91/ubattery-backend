from flask import request, abort, jsonify
from flask.views import MethodView

from ubattery.extensions import db, mongo
from ubattery.blueprints.auth import permission_required
from ubattery.common.mapping import TABLE_TO_NAME, LABEL_TO_NAME
from ubattery.common.checker import RE_DATETIME_CHECKER


def _get_base_data():
    """获取基本数据。"""

    args = request.args

    data_come_from = args.get('dataComeFrom')
    # 因为 data_come_from 会拼接成 sql 语句，为防 sql 注入，须判断下是不是正确表名
    if data_come_from not in TABLE_TO_NAME:
        abort(500)

    start_date = args.get('startDate')
    if start_date is None or not RE_DATETIME_CHECKER.match(start_date):
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
        col_names.append(LABEL_TO_NAME[k])  # 会过滤不合法参数名

    rows = db.session.execute(
        'SELECT '
        'DATE_FORMAT(timestamp, \'%Y-%m-%d %H:%i:%s\'),'
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
        'rows': rows,
        'rowCount': len(rows)
    }

    status = True
    if len(rows) == 0:
        status = False
        data = '未查询到相关数据！'

    return {
        'status': status,
        'data': data
    }


def _get_charging_process_data():
    return jsonify(list(mongo.db['charging_process'].find(projection={'_id': 0})))


class MiningAPI(MethodView):

    decorators = (permission_required(),)

    def get(self, name):
        data = None
        if name == 'base':
            data = _get_base_data()
        elif name == 'charging_process':
            data = _get_charging_process_data()
        return data