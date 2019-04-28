from flask import jsonify, request
from flask.views import MethodView

from ubattery.db import get_db
from ubattery.blueprints.auth import login_required


class AnalysisAPI(MethodView):

    def get(self):

        args = request.args

        # TODO 后台参数合法性检查
        start_date = args.get('startDate', '2015-1-1 1:1:1')
        data_limit = int(args.get('dataLimit', 500))

        with get_db().cursor() as cursor:
            cursor.execute(
                'SELECT '
                'DATE_FORMAT(timestamp, \'%%Y-%%m-%%d %%H:%%i:%%s\'),'
                'bty_t_vol,'
                'bty_t_curr,'
                'met_spd,'
                's_b_max_t,'
                's_b_min_t,'
                's_b_max_v,'
                's_b_min_v'
                ' FROM vehicle1 '
                'WHERE timestamp > %s '
                'LIMIT %s',
                (start_date, data_limit)
            )
            rows = cursor.fetchall()

        return jsonify({
            'status': True,
            'data': {
                'col_names': [
                    '时间', '总电压', '总电流', '车速',
                    '单体最高温度', '单体最低温度', '单体最高电压', '单体最低电压'
                ],
                'rows': rows
            }
        })
