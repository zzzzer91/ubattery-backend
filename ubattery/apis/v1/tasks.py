import time
from datetime import datetime
from typing import Dict, List

from flask import request, abort
from flask.views import MethodView

from ubattery.common import permission, mapping, checker
from ubattery.extensions import celery, mongo, mysql, cache
from ubattery.blueprints.auth import permission_required


def _compute_charging_process_data(rows: List) -> List[Dict]:
    """计算充电过程。"""

    lst1 = []
    i = -1
    pre = -1
    for row in rows:
        row = dict(row)
        if row['byt_ma_sys_state'] != pre:
            pre = row['byt_ma_sys_state']
            lst1.append([])
            i += 1
        lst1[i].append(row)

    lst2 = []
    for row in lst1:
        if row[0]['byt_ma_sys_state'] == 6:
            lst2.append(row)

    data = []
    for i, row in enumerate(lst2, 1):
        max_vol = max(row, key=lambda x: x['bty_t_vol'])['bty_t_vol']
        last_vol = row[-1]['bty_t_vol']
        sub_vol = max_vol - last_vol
        init_soc = row[0]['battery_soc']
        last_soc = row[-1]['battery_soc']
        first_id = row[0]['id']
        last_id = row[-1]['id']
        d = {
            'index': i,
            'max_vol': float(max_vol),
            'last_vol': float(last_vol),
            'sub_vol': float(sub_vol),
            'init_soc': float(init_soc),
            'last_soc': float(last_soc),
            'first_id': first_id,
            'last_id': last_id,
        }
        data.append(d)

    return data


def _compute_working_condition_data(rows: List) -> List[Dict]:
    pass


def _compute_battery_statistic_data(rows: List) -> List[Dict]:
    """计算电池统计数据。"""

    battery_statistic = {}
    for row in rows:
        key1 = row[0]
        if key1 is not None:
            battery_statistic.setdefault(key1, [0, 0])[0] += 1
        key2 = row[1]
        if key2 is not None:
            battery_statistic.setdefault(key2, [0, 0])[1] += 1

    temp = sorted(battery_statistic.items(), key=lambda x: x[0])
    data = []
    for number, (max_t_count, min_t_count) in temp:
        data.append({
            'number': number,
            'max_t_count': max_t_count,
            'min_t_count': min_t_count
        })
    return data


# 如果你不能马上使用 Celery 实例，用 `shared_task` 代替 task，如 Django 中。
# `ignore_result=True` 该任务不会将结果保存在 redis，提高性能
@celery.task(bind=True, ignore_result=True)
def compute_task(self,
                 task_name_chinese: str,
                 data_come_from: str,
                 request_params: str,
                 create_time: str,
                 # 这三个参数传给 SQl 语句
                 data_come_from_map: str,
                 start_date: str,
                 end_date: str) -> None:
    """根据 task_name_chinese，选择任务交给 celery 执行。

    :param self: Celery 装饰器中添加 `bind=True` 参数。告诉 Celery 发送一个 self 参数到该函数，
                 可以获取一些任务信息，或更新用 `self.update_stat()` 任务状态。
    :param create_time: 任务执行的时间，从外部传入，保持一致性。
    :param data_come_from_map: 从哪张表查询数据，表名。
    :param task_name_chinese: 任务名，中文。
    :param start_date: 数据查询起始日期，>=。
    :param end_date: 数据查询终止日期，<=。
    :param data_come_from: 数据来源的中文名称，用于入库。
    :param request_params: 请求的参数，用于入库
    """

    # 用 celery 产生的 id 做 mongo 主键
    task_id = self.request.id

    if task_name_chinese == '充电过程':
        need_params = 'bty_t_vol, bty_t_curr, battery_soc, id, byt_ma_sys_state'
        compute_alg = _compute_charging_process_data
    elif task_name_chinese == '工况':
        need_params = ''
        compute_alg = _compute_working_condition_data
    elif task_name_chinese == '电池统计':
        need_params = 'max_t_s_b_num, min_t_s_b_num'
        compute_alg = _compute_battery_statistic_data
    else:
        return

    start = time.perf_counter()

    mongo.db['tasks'].insert_one({
        '_id': task_id,
        'taskName': task_name_chinese,
        'dataComeFrom': data_come_from,
        'requestParams': request_params,
        'createTime': create_time,
        'taskStatus': '执行中',
        'comment': None,
        'data': None
    })

    if start_date is None:
        rows = mysql.session.execute(
            'SELECT '
            f'{need_params} '
            f'FROM {data_come_from_map}'
        )
    else:
        rows = mysql.session.execute(
            'SELECT '
            f'{need_params} '
            f'FROM {data_come_from_map} '
            'WHERE timestamp >= :start_date and timestamp <= :end_date',
            {'start_date': start_date, 'end_date': end_date}
        )

    if rows.rowcount == 0:
        mongo.db['tasks'].update_one(
            {'_id': task_id},
            {'$set': {
                'taskStatus': '失败',
                'comment': '无可用数据',
            }}
        )
        return

    # 处理数据
    data = compute_alg(rows)

    used_time = round(time.perf_counter() - start, 2)

    mongo.db['tasks'].update_one(
        {'_id': task_id},
        {'$set': {
            'taskStatus': '完成',
            'comment': f'用时 {used_time}s',
            'data': data
        }}
    )


def get_task_list() -> List[Dict]:
    """这个函数不太好用缓存，因为会频繁创建任务。"""

    data = []
    for item in mongo.db['tasks'].find(projection={'data': False}):
        item['taskId'] = item.pop('_id')
        data.append(item)
    data.reverse()
    return data


@cache.memoize()
def get_task(task_id: str) -> List[Dict]:
    """获取单个任务数据"""

    return mongo.db['tasks'].find_one(
        {'_id': task_id},
        projection={'_id': False, 'data': True}
    )['data']


class TasksAPI(MethodView):

    decorators = (permission_required(permission.SUPER_USER),)

    def get(self, task_id):
        """返回任务。"""

        # 获取所有任务
        if task_id is None:
            data = get_task_list()
            return {
                'status': True,
                'data': data,
            }

        data = get_task(task_id)
        if data is None:
            cache.delete_memoized(get_task, task_id)
            return {
                'status': False,
                'data': '无可绘制数据！',
            }

        return {
            'status': True,
            'data': data,
        }

    def post(self, task_name):
        """创建任务。"""

        jd = request.get_json()
        # 参数合法性检验
        data_come_from = jd.get('dataComeFrom')
        data_come_from_map, _ = mapping.MYSQL_NAME_TO_TABLE[data_come_from]
        all_data = jd.get('allData')
        start_date = None
        end_date = None

        request_params = '所有数据'
        if all_data is None:
            start_date = jd.get('startDate')
            if start_date is None or not checker.RE_DATETIME_CHECKER.match(start_date):
                abort(500)
            end_date = jd.get('endDate')
            if end_date is None or not checker.RE_DATETIME_CHECKER.match(end_date):
                abort(500)
            request_params = f'{start_date} - {end_date}'

        create_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        if task_name == 'charging-process':
            task_name_chinese = '充电过程'
        # elif task_name == 'working-condition':
        #     task_name_chinese = '工况'
        elif task_name == 'battery-statistic':
            task_name_chinese = '电池统计'
        else:
            return {
                'status': False,
                'data': None,
            }

        # 交给 celery 计算
        # 返回一个 task，可以拿到任务 Id 等属性
        task = compute_task.delay(
            task_name_chinese, data_come_from, request_params, create_time,
            data_come_from_map, start_date, end_date,
        )

        return {
            'status': True,
            'data': {
                'taskName': task_name_chinese,
                'dataComeFrom': data_come_from,
                'requestParams': request_params,
                'taskId': task.id,
                'createTime': create_time,
                'taskStatus': '执行中',
                'comment': None,
            },
        }

    def delete(self, task_id):
        # 取消一个任务，
        # 如果该任务已执行，那么必须设置 `terminate=True` 才能终止它
        # 如果该任务不存在，也不会报错
        compute_task.AsyncResult(task_id).revoke(terminate=True)

        mongo.db['tasks'].delete_one({'_id': task_id})
        return {
            'status': False,
            'data': None,
        }