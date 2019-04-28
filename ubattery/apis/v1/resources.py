from flask import jsonify, request
from flask.views import MethodView

from ubattery.db import get_db
from ubattery.common.mapping import LABEL_TO_NAME
from ubattery.blueprints.auth import login_required


class AnalysisAPI(MethodView):

    decorators = [login_required]

    def get(self):

        args = request.args

        # TODO 后台参数合法性检查
        start_date = args.get('startDate', '2017-1-1 0:0:0')
        data_limit = int(args.get('dataLimit', 500))
        need_params = args.get('needParams')

        col_names = ['时间']

        if need_params is None or not need_params.strip():
            need_params = ''
        else:
            for k in need_params.split(','):
                col_names.append(LABEL_TO_NAME[k])
            need_params = ',' + need_params

        with get_db().cursor() as cursor:
            cursor.execute(
                'SELECT '
                'DATE_FORMAT(timestamp, \'%%Y-%%m-%%d %%H:%%i:%%s\')'
                f'{need_params} '
                'FROM vehicle1 '
                'WHERE timestamp > %s '
                'LIMIT %s',
                (start_date, data_limit)
            )
            rows = cursor.fetchall()

        return jsonify({
            'status': True,
            'data': {
                'col_names': col_names,
                'rows': rows
            }
        })
