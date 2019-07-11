from decimal import Decimal
from datetime import datetime

from flask.json import JSONEncoder


class MyJSONEncoder(JSONEncoder):

    def default(self, obj):

        # MySQL 中的 Decimal 不能直接 json 序列化，要转成 float
        if isinstance(obj, Decimal):
            return float(obj)

        # 把 `datetime` 类型格式化
        if isinstance(obj, datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        return super().default(obj)
