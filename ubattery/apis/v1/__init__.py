from flask import Blueprint

from .resources import IndexAPI


api = Blueprint('api', __name__)


index_view = IndexAPI.as_view('index_api')
api.add_url_rule(
    '/',
    view_func=index_view,
    methods=['GET']
)