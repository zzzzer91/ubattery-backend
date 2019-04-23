from flask import Blueprint

from .resources import IndexAPI, AnalysisAPI


api = Blueprint('api', __name__)


index_view = IndexAPI.as_view('index_api')
api.add_url_rule(
    '/',
    view_func=index_view,
    methods=['GET']
)

batch_view = AnalysisAPI.as_view('analysis_api')
api.add_url_rule(
    '/analysis',
    view_func=batch_view,
    methods=['GET']
)
