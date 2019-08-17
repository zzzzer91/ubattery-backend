from flask.views import MethodView

from ubattery.extensions import cache
from ubattery.permission import permission_required
from ubattery import json_response

API_VERSION = 'v1'
API_BASE_URL = f'/api/{API_VERSION}'


class IndexAPI(MethodView):

    decorators = [permission_required()]

    @cache.cached()
    def get(self):
        data = {
            'api_version': API_VERSION,
            'api_base_url': API_BASE_URL,
            'api_data_format': {
                'code': 'int',
                'msg': 'str',
                'data': 'Dict'
            }
        }
        return json_response.build(json_response.SUCCESS, data=data)