from typing import Dict

SUCCESS = 20000
ERROR = 40000


def build_json_response(*, code: int = SUCCESS, msg: str = "", data: Dict = None) -> Dict:
    return {
        'code': code,
        'msg': msg,
        'data': data,
    }