from flask import Flask, render_template, jsonify
from flask_cors import CORS
import json
import os

app = Flask(__name__,
            template_folder='../frontend/templates',
            static_folder='../frontend/static')
CORS(app)

# 加载数据
def load_data():
    data_path = os.path.join(os.path.dirname(__file__), '../data/stocks.json')
    with open(data_path, 'r', encoding='utf-8') as f:
        return json.load(f)

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

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
