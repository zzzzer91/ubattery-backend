"""
映射，同时也能过滤不合法字段
"""

# 表名到动力汽车 ID 的转换
MYSQL_TABLE_TO_NAME = {
    'yutong_vehicle1': '4F37195C1A908CFBE0532932A8C0EECB'
}

# 表中字段名到实际名的转换
BASE_LABEL_TO_NAME = {
    'timestamp': '时间',
    'bty_t_vol': '总电压',
    'bty_t_curr': '总电流',
    'met_spd': '车速',
    'p_t_p': '正向累计电量',
    'r_t_p': '反向累计电量',
    'total_mileage': '总里程',
    'battery_soc': 'SOC',
    's_b_max_t': '单体最高温度',
    's_b_min_t': '单体最低温度',
    's_b_max_v': '单体最高电压',
    's_b_min_v': '单体最低电压',
    'max_t_s_b_num': '最高温度电池号',
    'min_t_s_b_num': '最低温度电池号',
    'max_v_e_core_num': '最高电压电池号',
    'min_v_e_core_num': '最低电压电池号',
}

BASE_NAME_TO_LABEL = {
    '时间': 'timestamp',
    '总电压': 'bty_t_vol',
    '总电流': 'bty_t_curr',
    '车速': 'met_spd',
    '正向累计电量': 'p_t_p',
    '反向累计电量': 'r_t_p',
    '总里程': 'total_mileage',
    'SOC': 'battery_soc',
    '单体最高温度': 's_b_max_t',
    '单体最低温度': 's_b_min_t',
    '单体最高电压': 's_b_max_v',
    '单体最低电压': 's_b_min_v',
    '最高温度电池号': 'max_t_s_b_num',
    '最低温度电池号': 'min_t_s_b_num',
    '最高电压电池号': 'max_v_e_core_num',
    '最低电压电池号': 'min_v_e_core_num'
}

CHARGING_PROCESS_LABEL_TO_NAME = {}