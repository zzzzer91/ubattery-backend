import decimal
from flask.json import JSONEncoder


class DecimalEncoder(JSONEncoder):
    """flask 的 jsonify 不能直接序列化 mysql 的 decimal 类型，需要配置下"""

    def default(self, obj):
        if isinstance(obj, decimal.Decimal):
            # Convert decimal instances to strings.
            return float(obj)
        return super().default(obj)
