from flask import jsonify
from flask.views import MethodView

from ubattery.db import get_db


class IndexAPI(MethodView):

    def get(self):
        return jsonify({
            'status': 1,
            'api_version': '1.0',
            'api_base_url': '/api/v1',
            'api_analysis_url': '/api/v1/analysis',
            'api_success_status': 1,
            'api_fail_status': 0
        })


class AnalysisAPI(MethodView):

    def get(self):
        db = get_db()

        with db.cursor() as cursor:
            cursor.execute(
                'SELECT timestamp, bty_t_vol, bty_t_curr, s_b_max_t, s_b_min_t FROM vehicle1 limit 20'
            )
            rows = cursor.fetchall()

        return jsonify({
            'status': 1,
            'data': rows
        })
