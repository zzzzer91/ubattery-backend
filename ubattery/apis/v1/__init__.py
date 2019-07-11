from flask import Blueprint

from .index import IndexAPI, API_VERSION, API_BASE_URL
from .analysis import AnalysisAPI
from .users import UsersAPI

api_v1_bp = Blueprint(f'api_{API_VERSION}', __name__, url_prefix=API_BASE_URL)


index_api = IndexAPI.as_view('index_api')
api_v1_bp.add_url_rule(
    '/',
    view_func=index_api,
    methods=['GET']
)

analysis_api = AnalysisAPI.as_view('analysis_api')
api_v1_bp.add_url_rule(
    '/analysis',
    view_func=analysis_api,
    methods=['GET']
)

users_api = UsersAPI.as_view('users_api')
# 虽然这个视图有两条 url 规则，一个 get 的，一个 put 的，
# 但 url_for() 会忽略 <string:user_name>，
# 所以只会取到一条规则
api_v1_bp.add_url_rule(  # 修改用户信息
    '/users/<string:user_name>',
    view_func=users_api,
    methods=['PUT']
)
api_v1_bp.add_url_rule(
    '/users',
    view_func=users_api,
    methods=['GET', 'POST']
)