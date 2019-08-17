from typing import Dict, Any

SUCCESS = 20000
ERROR = 40000


def build(*, code: int = SUCCESS, msg: str = "", data: Any = None) -> Dict:
    return {
        'code': code,
        'msg': msg,
        'data': data,
    }