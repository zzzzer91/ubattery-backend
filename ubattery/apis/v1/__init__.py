from flask import Blueprint

from .auth import login, logout
from .index import IndexAPI, API_VERSION, API_BASE_URL
from .mining import MiningAPI
from .users import UsersAPI
from .tasks import TasksAPI

api_v1_bp = Blueprint(f'api_{API_VERSION}', __name__, url_prefix=API_BASE_URL)


api_v1_bp.add_url_rule(
    '/login',
    view_func=login,
    methods=['GET', 'POST']
)

api_v1_bp.add_url_rule(
    '/logout',
    view_func=logout,
    methods=['GET']
)

index_api = IndexAPI.as_view('index_api')
api_v1_bp.add_url_rule(
    '/',
    view_func=index_api,
    methods=['GET']
)

mining_api = MiningAPI.as_view('mining_api')
api_v1_bp.add_url_rule(
    '/mining/<string:name>',
    view_func=mining_api,
    methods=['GET']
)

users_api = UsersAPI.as_view('users_api')
# 虽然这个视图有两条 url 规则，一个 get 的，一个 put 的，
# 但 url_for() 不用参数会忽略 <string:user_name>，
# 所以只会取到一条规则
api_v1_bp.add_url_rule(
    '/users',
    view_func=users_api,
    methods=['GET', 'POST']
)
api_v1_bp.add_url_rule(  # 修改用户信息
    '/users/<string:user_name>',
    view_func=users_api,
    methods=['PUT']
)

tasks_api = TasksAPI.as_view('tasks_api')
api_v1_bp.add_url_rule(
    '/tasks',
    defaults={'task_id': None},
    view_func=tasks_api,
    methods=['GET']
)
api_v1_bp.add_url_rule(
    '/tasks/<string:task_id>',
    view_func=tasks_api,
    methods=['GET', 'DELETE']
)
api_v1_bp.add_url_rule(
    '/tasks/<string:task_name>',
    view_func=tasks_api,
    methods=['POST']
)