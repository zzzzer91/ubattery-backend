from flask import jsonify
from flask.views import MethodView

from ubattery.db import get_db


class AnalysisAPI(MethodView):

    def get(self):

        with get_db().cursor() as cursor:
            cursor.execute(
                'SELECT timestamp, bty_t_vol, bty_t_curr, s_b_max_t, s_b_min_t FROM vehicle1 limit 20'
            )
            rows = cursor.fetchall()

        return jsonify({
            'status': True,
            'data': rows
        })
