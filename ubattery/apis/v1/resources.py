from flask import jsonify, request
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