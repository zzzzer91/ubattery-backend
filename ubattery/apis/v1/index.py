from flask.views import MethodView

from ubattery.blueprints.auth import login_required

API_VERSION = 'v1'
API_BASE_URL = f'/api/{API_VERSION}'


class IndexAPI(MethodView):

    decorators = [login_required]

    def get(self):
        return {
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
        }