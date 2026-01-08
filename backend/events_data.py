"""
历史重要经济和政治事件数据（支持自动和手动维护）
用于在股票图表上标注关键时间节点
"""

from datetime import datetime, timedelta

# 手动维护的重要事件（无法从API自动获取的事件）
# 包括：政治事件、全球重大事件等
# 格式: {'date': 'YYYY-MM-DD', 'name': '事件名称', 'type': '事件类型', 'impact': '影响程度'}
# type: 'us_election' (美国大选), 'global' (全球事件)
# impact: 'high' (重大), 'medium' (中等), 'low' (较小)

MANUAL_EVENTS = [
    # 政治事件
    {'date': '2024-11-05', 'name': '美国总统大选', 'type': 'us_election', 'impact': 'high'},
    {'date': '2022-11-08', 'name': '美国中期选举', 'type': 'us_election', 'impact': 'high'},
    {'date': '2020-11-03', 'name': '美国总统大选', 'type': 'us_election', 'impact': 'high'},

    # 全球重大事件
    {'date': '2020-03-11', 'name': 'WHO宣布COVID-19全球大流行', 'type': 'global', 'impact': 'high'},
]

# 缓存：避免频繁调用API
_events_cache = {
    'data': None,
    'timestamp': None,
    'ttl': 3600  # 缓存1小时
}


def fetch_fed_rate_events():
    """
    从AKShare获取美联储利率决议数据

    Returns:
        list: 美联储利率事件列表
    """
    try:
        import akshare as ak

        events = []
        df = ak.macro_bank_usa_interest_rate()

        # 解析数据
        for _, row in df.iterrows():
            try:
                # 日期格式可能是 '2024-12-18' 或其他格式
                date_str = str(row['日期'])
                if 'T' in date_str:
                    date_obj = datetime.fromisoformat(date_str.split('T')[0])
                else:
                    date_obj = datetime.strptime(date_str[:10], '%Y-%m-%d')

                date = date_obj.strftime('%Y-%m-%d')

                # 获取利率值
                current_rate = float(row['当前值'])

                # 尝试获取前值来计算变动
                if '前值' in row and row['前值'] and str(row['前值']).replace('.', '').isdigit():
                    prev_rate = float(row['前值'])
                    change = current_rate - prev_rate

                    if abs(change) >= 0.5:
                        impact = 'high'
                        if change > 0:
                            name = f'美联储加息{abs(change):.0f}基点'
                        else:
                            name = f'美联储降息{abs(change):.0f}基点'
                    elif abs(change) >= 0.1:
                        impact = 'high' if abs(change) >= 0.25 else 'medium'
                        if change > 0:
                            name = f'美联储加息{abs(change)*100:.0f}基点'
                        else:
                            name = f'美联储降息{abs(change)*100:.0f}基点'
                    else:
                        impact = 'medium'
                        name = '美联储维持利率不变'
                else:
                    # 没有前值，只显示当前利率
                    name = f'美联储利率决议({current_rate}%)'
                    impact = 'medium'

                events.append({
                    'date': date,
                    'name': name,
                    'type': 'us_rate',
                    'impact': impact
                })
            except Exception as e:
                print(f"解析美联储数据行失败: {e}, 行数据: {row}")
                continue

        print(f"从AKShare获取到 {len(events)} 条美联储利率事件")
        return events

    except Exception as e:
        print(f"获取美联储利率数据失败: {e}")
        return []


def fetch_china_rrr_events():
    """
    从AKShare获取中国央行存款准备金率数据

    Returns:
        list: 中国央行降准事件列表
    """
    try:
        import akshare as ak

        events = []
        df = ak.macro_china_rrr()

        # 解析数据
        for _, row in df.iterrows():
            try:
                # 日期格式处理
                date_str = str(row['公布时间'])
                date_obj = datetime.strptime(date_str[:10], '%Y-%m-%d')
                date = date_obj.strftime('%Y-%m-%d')

                # 获取存款准备金率变动信息
                if '大型金融机构' in row:
                    rrr_change = str(row['大型金融机构'])

                    # 判断是否降准
                    if '下调' in rrr_change or '降低' in rrr_change:
                        # 提取百分点
                        import re
                        match = re.search(r'(\d+\.?\d*)', rrr_change)
                        if match:
                            change_value = match.group(1)
                            name = f'中国央行降准{change_value}个百分点'
                            impact = 'high' if float(change_value) >= 0.5 else 'medium'
                        else:
                            name = '中国央行降准'
                            impact = 'medium'

                        events.append({
                            'date': date,
                            'name': name,
                            'type': 'cn_rrr',
                            'impact': impact
                        })
            except Exception as e:
                print(f"解析中国央行降准数据行失败: {e}")
                continue

        print(f"从AKShare获取到 {len(events)} 条中国央行降准事件")
        return events

    except Exception as e:
        print(f"获取中国央行降准数据失败: {e}")
        return []


def get_all_events():
    """
    获取所有事件（自动获取 + 手动维护）

    Returns:
        list: 所有事件列表
    """
    global _events_cache

    # 检查缓存
    now = datetime.now()
    if (_events_cache['data'] is not None and
        _events_cache['timestamp'] is not None and
        (now - _events_cache['timestamp']).total_seconds() < _events_cache['ttl']):
        print("使用缓存的事件数据")
        return _events_cache['data']

    # 合并所有事件
    all_events = []

    # 1. 添加手动维护的事件
    all_events.extend(MANUAL_EVENTS)
    print(f"手动维护事件: {len(MANUAL_EVENTS)} 条")

    # 2. 从AKShare获取美联储数据
    fed_events = fetch_fed_rate_events()
    all_events.extend(fed_events)

    # 3. 从AKShare获取中国央行降准数据
    rrr_events = fetch_china_rrr_events()
    all_events.extend(rrr_events)

    # 去重（基于日期和类型）
    seen = set()
    unique_events = []
    for event in all_events:
        key = (event['date'], event['type'])
        if key not in seen:
            seen.add(key)
            unique_events.append(event)

    # 按日期排序
    unique_events.sort(key=lambda x: x['date'])

    print(f"总计事件数: {len(unique_events)} 条（去重后）")

    # 更新缓存
    _events_cache['data'] = unique_events
    _events_cache['timestamp'] = now

    return unique_events


def get_events_in_range(start_date, end_date):
    """
    获取指定日期范围内的历史事件（自动 + 手动）

    Args:
        start_date: 开始日期 (datetime对象或字符串 'YYYY-MM-DD')
        end_date: 结束日期 (datetime对象或字符串 'YYYY-MM-DD')

    Returns:
        list: 符合条件的事件列表
    """
    # 转换为datetime对象
    if isinstance(start_date, str):
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
    if isinstance(end_date, str):
        end_date = datetime.strptime(end_date, '%Y-%m-%d')

    # 获取所有事件（带缓存）
    all_events = get_all_events()

    # 筛选日期范围内的事件
    events_in_range = []
    for event in all_events:
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
