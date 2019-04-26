from flask import jsonify
from flask.views import MethodView

from ubattery.db import get_db


class AnalysisAPI(MethodView):

    def get(self):

        with get_db().cursor() as cursor:
            cursor.execute(
                'SELECT '
                'DATE_FORMAT(timestamp, \'%Y-%m-%d %H:%i:%s\'), '
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
                'col_names': ['时间', '电压', '电流', '电池最高温度', '电池最低温度'],
                'rows': rows
            }
        })
