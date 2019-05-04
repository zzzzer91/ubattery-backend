from flask import Blueprint, jsonify
from flask.views import MethodView

from .v1 import AnalysisAPI, UsersAPI
from ubattery.blueprints.auth import login_required

bp = Blueprint('api', __name__)

API_VERSION = 'v1'
API_BASE_URL = f'/api/{API_VERSION}'


class IndexAPI(MethodView):

    decorators = [login_required]

    def get(self):
        return jsonify({
            'status': True,
            'api_version': API_VERSION,
            'api_base_url': API_BASE_URL,
            'api_url_list': [
                f'{API_BASE_URL}/analysis'
            ],
            'api_data_format': {
                'status': 'bool',
                'data': 'List[Dict]'
            }
        })


index_view = IndexAPI.as_view('index_api')
bp.add_url_rule(
    '/',
    view_func=index_view,
    methods=['GET']
)

analysis_view = AnalysisAPI.as_view('analysis_api')
bp.add_url_rule(
    '/analysis',
    view_func=analysis_view,
    methods=['GET']
)

users_view = UsersAPI.as_view('users_api')
bp.add_url_rule(
    '/users',
    view_func=users_view,
    methods=['GET', 'POST']
)
bp.add_url_rule(
    '/users/<string:user_name>',
    view_func=users_view,
    methods=['PUT']
)
