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
