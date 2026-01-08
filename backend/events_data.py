"""
历史重要经济和政治事件数据
用于在股票图表上标注关键时间节点
"""

# 格式: {'date': 'YYYY-MM-DD', 'name': '事件名称', 'type': '事件类型', 'impact': '影响程度'}
# type: 'us_election' (美国大选), 'us_rate' (美国利率), 'cn_rate' (中国利率), 'cn_rrr' (中国准备金率), 'global' (全球事件)
# impact: 'high' (重大), 'medium' (中等), 'low' (较小)

HISTORICAL_EVENTS = [
    # 2024年事件
    {'date': '2024-11-05', 'name': '美国总统大选', 'type': 'us_election', 'impact': 'high'},
    {'date': '2024-12-18', 'name': '美联储降息25基点', 'type': 'us_rate', 'impact': 'high'},
    {'date': '2024-11-07', 'name': '美联储降息25基点', 'type': 'us_rate', 'impact': 'high'},
    {'date': '2024-09-18', 'name': '美联储降息50基点', 'type': 'us_rate', 'impact': 'high'},
    {'date': '2024-09-24', 'name': '中国央行降准0.5个百分点', 'type': 'cn_rrr', 'impact': 'high'},
    {'date': '2024-07-22', 'name': '中国央行降息10基点', 'type': 'cn_rate', 'impact': 'medium'},
    {'date': '2024-02-05', 'name': '中国央行降准0.5个百分点', 'type': 'cn_rrr', 'impact': 'high'},

    # 2023年事件
    {'date': '2023-12-13', 'name': '美联储维持利率不变', 'type': 'us_rate', 'impact': 'medium'},
    {'date': '2023-11-01', 'name': '美联储维持利率不变', 'type': 'us_rate', 'impact': 'medium'},
    {'date': '2023-09-20', 'name': '美联储维持利率不变', 'type': 'us_rate', 'impact': 'medium'},
    {'date': '2023-07-26', 'name': '美联储加息25基点', 'type': 'us_rate', 'impact': 'high'},
    {'date': '2023-06-14', 'name': '美联储维持利率不变', 'type': 'us_rate', 'impact': 'medium'},
    {'date': '2023-05-03', 'name': '美联储加息25基点', 'type': 'us_rate', 'impact': 'high'},
    {'date': '2023-03-22', 'name': '美联储加息25基点', 'type': 'us_rate', 'impact': 'high'},
    {'date': '2023-03-27', 'name': '中国央行降准0.25个百分点', 'type': 'cn_rrr', 'impact': 'medium'},
    {'date': '2023-06-13', 'name': '中国央行降息10基点', 'type': 'cn_rate', 'impact': 'medium'},
    {'date': '2023-08-15', 'name': '中国央行降息15基点', 'type': 'cn_rate', 'impact': 'medium'},

    # 2022年事件
    {'date': '2022-11-08', 'name': '美国中期选举', 'type': 'us_election', 'impact': 'high'},
    {'date': '2022-12-14', 'name': '美联储加息50基点', 'type': 'us_rate', 'impact': 'high'},
    {'date': '2022-11-02', 'name': '美联储加息75基点', 'type': 'us_rate', 'impact': 'high'},
    {'date': '2022-09-21', 'name': '美联储加息75基点', 'type': 'us_rate', 'impact': 'high'},
    {'date': '2022-07-27', 'name': '美联储加息75基点', 'type': 'us_rate', 'impact': 'high'},
    {'date': '2022-06-15', 'name': '美联储加息75基点', 'type': 'us_rate', 'impact': 'high'},
    {'date': '2022-05-04', 'name': '美联储加息50基点', 'type': 'us_rate', 'impact': 'high'},
    {'date': '2022-03-16', 'name': '美联储加息25基点', 'type': 'us_rate', 'impact': 'high'},
    {'date': '2022-04-25', 'name': '中国央行降准0.25个百分点', 'type': 'cn_rrr', 'impact': 'medium'},
    {'date': '2022-12-05', 'name': '中国央行降准0.25个百分点', 'type': 'cn_rrr', 'impact': 'medium'},
    {'date': '2022-01-17', 'name': '中国央行降息10基点', 'type': 'cn_rate', 'impact': 'medium'},
    {'date': '2022-08-15', 'name': '中国央行降息10基点', 'type': 'cn_rate', 'impact': 'medium'},

    # 2021年事件
    {'date': '2021-03-17', 'name': '美联储维持利率不变', 'type': 'us_rate', 'impact': 'medium'},
    {'date': '2021-07-05', 'name': '中国央行降准0.5个百分点', 'type': 'cn_rrr', 'impact': 'high'},
    {'date': '2021-12-06', 'name': '中国央行降准0.5个百分点', 'type': 'cn_rrr', 'impact': 'high'},

    # 2020年事件
    {'date': '2020-11-03', 'name': '美国总统大选', 'type': 'us_election', 'impact': 'high'},
    {'date': '2020-03-15', 'name': '美联储紧急降息100基点', 'type': 'us_rate', 'impact': 'high'},
    {'date': '2020-03-03', 'name': '美联储紧急降息50基点', 'type': 'us_rate', 'impact': 'high'},
    {'date': '2020-03-13', 'name': '中国央行定向降准', 'type': 'cn_rrr', 'impact': 'medium'},
    {'date': '2020-04-03', 'name': '中国央行降准+降息', 'type': 'cn_rate', 'impact': 'high'},
    {'date': '2020-03-11', 'name': 'WHO宣布COVID-19全球大流行', 'type': 'global', 'impact': 'high'},
]


def get_events_in_range(start_date, end_date):
    """
    获取指定日期范围内的历史事件

    Args:
        start_date: 开始日期 (datetime对象或字符串 'YYYY-MM-DD')
        end_date: 结束日期 (datetime对象或字符串 'YYYY-MM-DD')

    Returns:
        list: 符合条件的事件列表
    """
    from datetime import datetime

    # 转换为datetime对象
    if isinstance(start_date, str):
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
    if isinstance(end_date, str):
        end_date = datetime.strptime(end_date, '%Y-%m-%d')

    events_in_range = []
    for event in HISTORICAL_EVENTS:
        event_date = datetime.strptime(event['date'], '%Y-%m-%d')
        if start_date <= event_date <= end_date:
            events_in_range.append(event)

    # 按日期排序
    events_in_range.sort(key=lambda x: x['date'])

    return events_in_range


def get_event_color(event_type):
    """
    根据事件类型返回显示颜色

    Args:
        event_type: 事件类型

    Returns:
        str: 颜色代码
    """
    colors = {
        'us_election': '#DC2626',    # 红色 - 美国大选
        'us_rate': '#2563EB',         # 蓝色 - 美国利率
        'cn_rate': '#16A34A',         # 绿色 - 中国利率
        'cn_rrr': '#059669',          # 深绿色 - 中国准备金率
        'global': '#9333EA'           # 紫色 - 全球事件
    }
    return colors.get(event_type, '#6B7280')  # 默认灰色


def get_event_symbol(event_type):
    """
    根据事件类型返回图标样式

    Args:
        event_type: 事件类型

    Returns:
        str: ECharts符号类型
    """
    symbols = {
        'us_election': 'diamond',     # 菱形 - 美国大选
        'us_rate': 'triangle',        # 三角形 - 美国利率
        'cn_rate': 'circle',          # 圆形 - 中国利率
        'cn_rrr': 'rect',             # 矩形 - 中国准备金率
        'global': 'pin'               # 图钉 - 全球事件
    }
    return symbols.get(event_type, 'circle')  # 默认圆形
