from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
from apscheduler.schedulers.background import BackgroundScheduler
from dotenv import load_dotenv
import json
import os
from datetime import datetime

# 导入数据抓取器
from data_fetcher import StockDataFetcher

# 加载环境变量
load_dotenv()

app = Flask(__name__,
            template_folder='../frontend/templates',
            static_folder='../frontend/static')
CORS(app)

# 配置：是否使用实时数据（默认True）
USE_REALTIME_DATA = os.getenv('USE_REALTIME_DATA', 'true').lower() == 'true'

# 初始化数据抓取器
data_fetcher = StockDataFetcher() if USE_REALTIME_DATA else None

# 数据缓存
cached_data = None
last_update_time = None


def load_static_data():
    """加载静态数据"""
    data_path = os.path.join(os.path.dirname(__file__), '../data/stocks.json')
    with open(data_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def load_data():
    """
    加载数据（根据配置选择实时或静态数据）
    """
    global cached_data, last_update_time

    if USE_REALTIME_DATA:
        # 使用实时数据
        if data_fetcher:
            print("使用实时数据模式")
            try:
                if cached_data is None:
                    # 首次加载数据
                    print("首次加载实时数据...")
                    cached_data = data_fetcher.fetch_all_data()
                    last_update_time = datetime.now()
                return cached_data
            except Exception as e:
                print(f"获取实时数据失败，回退到静态数据: {e}")
                return load_static_data()
        else:
            return load_static_data()
    else:
        # 使用静态数据
        print("使用静态数据模式")
        return load_static_data()


def refresh_data_background():
    """后台刷新数据"""
    global cached_data, last_update_time

    if USE_REALTIME_DATA and data_fetcher:
        try:
            print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 开始后台刷新数据...")
            cached_data = data_fetcher.fetch_all_data()
            last_update_time = datetime.now()
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 数据刷新完成")
        except Exception as e:
            print(f"后台刷新数据失败: {e}")


# 配置定时任务（每4小时刷新一次）
if USE_REALTIME_DATA:
    scheduler = BackgroundScheduler()
    scheduler.add_job(
        func=refresh_data_background,
        trigger="interval",
        hours=4,
        id='refresh_data',
        name='刷新股票数据',
        replace_existing=True
    )
    scheduler.start()
    print("定时任务已启动：每4小时刷新一次数据")


@app.route('/')
def index():
    """主页"""
    return render_template('index.html')


@app.route('/api/stocks/high-dividend')
def get_high_dividend_stocks():
    """获取高股息股票"""
    data = load_data()
    return jsonify(data['high_dividend_stocks'])


@app.route('/api/stocks/brokers')
def get_broker_stocks():
    """获取券商股票"""
    data = load_data()
    return jsonify(data['broker_stocks'])


@app.route('/api/etfs')
def get_etfs():
    """获取ETF列表"""
    data = load_data()
    return jsonify(data['etfs'])


@app.route('/api/portfolios')
def get_portfolios():
    """获取投资组合方案"""
    data = load_data()
    return jsonify(data['portfolios'])


@app.route('/api/all')
def get_all_data():
    """获取所有数据"""
    data = load_data()
    return jsonify(data)


@app.route('/api/summary')
def get_summary():
    """获取摘要统计"""
    data = load_data()

    high_div = data['high_dividend_stocks']
    brokers = data['broker_stocks']
    etfs = data['etfs']

    summary = {
        'total_high_dividend_stocks': (
            len(high_div['ultra_high']) +
            len(high_div['stable_high']) +
            len(high_div['financial'])
        ),
        'total_broker_stocks': (
            len(brokers['tier1']) +
            len(brokers['tier2']) +
            len(brokers['tier3'])
        ),
        'total_etfs': (
            len(etfs['broker']) +
            len(etfs['dividend']) +
            len(etfs['bank']) +
            len(etfs['financial'])
        ),
        'total_portfolios': 3
    }

    return jsonify(summary)


@app.route('/api/refresh', methods=['POST'])
def refresh_data():
    """手动刷新数据"""
    global cached_data, last_update_time

    if not USE_REALTIME_DATA:
        return jsonify({
            'success': False,
            'message': '当前使用静态数据模式，无需刷新'
        })

    try:
        print("手动刷新数据...")
        cached_data = data_fetcher.fetch_all_data()
        last_update_time = datetime.now()

        return jsonify({
            'success': True,
            'message': '数据刷新成功',
            'update_time': last_update_time.strftime('%Y-%m-%d %H:%M:%S')
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'数据刷新失败: {str(e)}'
        }), 500


@app.route('/api/status')
def get_status():
    """获取系统状态"""
    return jsonify({
        'realtime_mode': USE_REALTIME_DATA,
        'last_update_time': last_update_time.strftime('%Y-%m-%d %H:%M:%S') if last_update_time else None,
        'cache_status': 'active' if cached_data else 'empty'
    })


@app.route('/api/stock-chart/<code>')
def get_stock_chart(code):
    """获取股票/ETF的历史行情数据（含同比对比和历史事件标记）"""
    try:
        import akshare as ak
        from datetime import datetime, timedelta
        from events_data import get_events_in_range, get_event_color, get_event_symbol

        # 获取时间范围（默认最近3个月）
        period = request.args.get('period', '3m')

        # 计算当前周期的开始和结束日期
        end_date = datetime.now()
        if period == '1m':
            days = 30
        elif period == '3m':
            days = 90
        elif period == '6m':
            days = 180
        elif period == '1y':
            days = 365
        elif period == '2y':
            days = 730
        else:
            days = 90

        start_date = end_date - timedelta(days=days)

        # 计算去年同期的开始和结束日期
        last_year_end = end_date - timedelta(days=365)
        last_year_start = last_year_end - timedelta(days=days)

        # 格式化日期
        start_date_str = start_date.strftime('%Y%m%d')
        end_date_str = end_date.strftime('%Y%m%d')
        last_year_start_str = last_year_start.strftime('%Y%m%d')
        last_year_end_str = last_year_end.strftime('%Y%m%d')

        def fetch_stock_data(start, end):
            """获取指定时间段的股票数据"""
            try:
                # 尝试获取A股数据
                return ak.stock_zh_a_hist(symbol=code, period="daily", start_date=start, end_date=end, adjust="qfq")
            except:
                # 如果是ETF，尝试ETF接口
                try:
                    return ak.fund_etf_hist_em(symbol=code, period="daily", start_date=start, end_date=end, adjust="qfq")
                except:
                    return None

        # 获取当前周期数据
        df_current = fetch_stock_data(start_date_str, end_date_str)
        if df_current is None or df_current.empty:
            return jsonify({'success': False, 'message': '获取当前数据失败，请稍后重试'}), 404

        # 获取去年同期数据
        df_last_year = fetch_stock_data(last_year_start_str, last_year_end_str)

        # 获取当前时间范围内的历史事件
        events = get_events_in_range(start_date, end_date)

        # 为每个事件添加颜色和图标信息
        events_with_style = []
        for event in events:
            events_with_style.append({
                'date': event['date'],
                'name': event['name'],
                'type': event['type'],
                'impact': event['impact'],
                'color': get_event_color(event['type']),
                'symbol': get_event_symbol(event['type'])
            })

        # 转换当前周期数据格式
        dates = df_current['日期'].astype(str).tolist()

        chart_data = {
            'dates': dates,
            'prices': {
                'open': [float(x) for x in df_current['开盘'].tolist()],
                'close': [float(x) for x in df_current['收盘'].tolist()],
                'high': [float(x) for x in df_current['最高'].tolist()],
                'low': [float(x) for x in df_current['最低'].tolist()],
                'volume': [int(x) for x in df_current['成交量'].tolist()]
            },
            'latest': {
                'price': float(df_current.iloc[-1]['收盘']),
                'change': float(df_current.iloc[-1]['涨跌幅']) if '涨跌幅' in df_current.columns else 0,
                'volume': int(df_current.iloc[-1]['成交量'])
            },
            'events': events_with_style  # 添加历史事件数据
        }

        # 如果去年同期数据存在，添加到返回结果中
        if df_last_year is not None and not df_last_year.empty:
            last_year_dates = df_last_year['日期'].astype(str).tolist()
            chart_data['lastYear'] = {
                'dates': last_year_dates,
                'prices': {
                    'close': [float(x) for x in df_last_year['收盘'].tolist()]
                }
            }

        return jsonify({
            'success': True,
            'code': code,
            'data': chart_data
        })

    except Exception as e:
        print(f"获取股票走势失败: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': f'获取数据失败: {str(e)}'
        }), 500


if __name__ == '__main__':
    # 启动时加载一次数据
    if USE_REALTIME_DATA:
        print("\n" + "="*50)
        print("投资跟踪系统 - 实时数据模式")
        print("="*50)
        print("正在初始化，首次加载可能需要较长时间...")
        try:
            cached_data = data_fetcher.fetch_all_data()
            last_update_time = datetime.now()
            print(f"\n数据加载完成！更新时间: {last_update_time.strftime('%Y-%m-%d %H:%M:%S')}")
        except Exception as e:
            print(f"\n初始化数据失败: {e}")
            print("将在首次访问时重试...")
        print("="*50 + "\n")
    else:
        print("\n投资跟踪系统 - 静态数据模式\n")

    app.run(debug=True, host='0.0.0.0', port=5000)
