from flask import jsonify
from flask.views import MethodView

from ubattery.db import get_db


class AnalysisAPI(MethodView):

    def get(self):

        with get_db().cursor() as cursor:
            cursor.execute(
                'SELECT '
                'DATE_FORMAT(timestamp, \'%H:%i:%s\'), '
                'bty_t_vol, '
                'bty_t_curr, '
                's_b_max_t, '
                's_b_min_t '
                'FROM vehicle1 limit 100'
            )
            rows = cursor.fetchall()

        return jsonify({
            'status': True,
            'data': {
                'xAxis_name': '时间',
                'col_names': ['电压', '电流', '电池最高温度', '电池最低温度'],
                'rows': rows
            }
        })
