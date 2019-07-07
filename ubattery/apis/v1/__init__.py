from flask import Blueprint

from .index import IndexAPI, API_VERSION, API_BASE_URL
from .analysis import AnalysisAPI
from .users import UsersAPI

api_v1_bp = Blueprint(f'api_{API_VERSION}', __name__, url_prefix=API_BASE_URL)


index_view = IndexAPI.as_view('index_api')
api_v1_bp.add_url_rule(
    '/',
    view_func=index_view,
    methods=['GET']
)

analysis_view = AnalysisAPI.as_view('analysis_api')
api_v1_bp.add_url_rule(
    '/analysis',
    view_func=analysis_view,
    methods=['GET']
)

users_view = UsersAPI.as_view('users_api')
api_v1_bp.add_url_rule(
    '/users',
    view_func=users_view,
    methods=['GET', 'POST']
)
api_v1_bp.add_url_rule(  # 修改用户信息
    '/users/<string:user_name>',
    view_func=users_view,
    methods=['PUT']
)
