"""
简化版数据抓取模块 - 使用稳定的数据源
"""
import akshare as ak
import pandas as pd
from datetime import datetime, timedelta
import json
import os
from typing import Dict, List


class StockDataFetcher:
    """股票数据抓取器 - 简化版"""

    def __init__(self, cache_file='data/cache.json'):
        self.cache_file = cache_file
        self.cache_data = self._load_cache()
        self.cache_duration = timedelta(hours=4)

        # 券商股票代码列表
        self.broker_codes = {
            'tier1': ['600030', '601688', '601211'],
            'tier2': ['600999', '000776', '601066', '601995', '601881'],
            'tier3': ['000166', '300059', '600958', '601377']
        }

    def _load_cache(self) -> Dict:
        """加载缓存数据"""
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"加载缓存失败: {e}")
                return {}
        return {}

    def _save_cache(self):
        """保存缓存数据"""
        try:
            os.makedirs(os.path.dirname(self.cache_file), exist_ok=True)
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.cache_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存缓存失败: {e}")

    def _is_cache_valid(self, cache_key: str) -> bool:
        """检查缓存是否有效"""
        if cache_key not in self.cache_data:
            return False

        cache_time_str = self.cache_data[cache_key].get('timestamp')
        if not cache_time_str:
            return False

        try:
            cache_time = datetime.fromisoformat(cache_time_str)
            return datetime.now() - cache_time < self.cache_duration
        except:
            return False

    def fetch_high_dividend_stocks(self) -> Dict[str, List[Dict]]:
        """
        获取高股息股票（使用预设数据+可选实时更新）
        """
        cache_key = 'high_dividend_stocks'

        # 检查缓存
        if self._is_cache_valid(cache_key):
            print("使用缓存的高股息股票数据")
            return self.cache_data[cache_key]['data']

        print("加载高股息股票数据...")

        # 使用预设的优质高股息股票数据
        result = {
            'ultra_high': [
                {'name': '山煤国际', 'code': '600546', 'dividend_rate': '8.50%', 'industry': '煤炭', 'payout_ratio': '60%', 'category': '超高股息率'},
                {'name': '郑煤机', 'code': '601717', 'dividend_rate': '8.63%', 'industry': '机械设备', 'payout_ratio': '-', 'category': '超高股息率'},
                {'name': '中谷物流', 'code': '603565', 'dividend_rate': '8.20%', 'industry': '交通运输', 'payout_ratio': '90%+', 'category': '超高股息率'},
                {'name': '中远海控', 'code': '601919', 'dividend_rate': '7.50%', 'industry': '航运', 'payout_ratio': '-', 'category': '超高股息率'},
                {'name': '地素时尚', 'code': '603587', 'dividend_rate': '6.30%', 'industry': '消费', 'payout_ratio': '-', 'category': '超高股息率'},
            ],
            'stable_high': [
                {'name': '中国石化', 'code': '600028', 'dividend_rate': '5.20%', 'industry': '石油', 'payout_ratio': '-', 'category': '稳健高股息'},
                {'name': '中国神华', 'code': '601088', 'dividend_rate': '5.80%', 'industry': '煤炭', 'payout_ratio': '75%+', 'category': '稳健高股息'},
                {'name': '粤高速A', 'code': '000429', 'dividend_rate': '4.50%', 'industry': '交通运输', 'payout_ratio': '70%', 'category': '稳健高股息'},
                {'name': '中材国际', 'code': '600970', 'dividend_rate': '5.10%', 'industry': '建材', 'payout_ratio': '-', 'category': '稳健高股息'},
                {'name': '宁沪高速', 'code': '600377', 'dividend_rate': '4.80%', 'industry': '交通运输', 'payout_ratio': '-', 'category': '稳健高股息'},
                {'name': '华能水电', 'code': '600025', 'dividend_rate': '4.20%', 'industry': '电力', 'payout_ratio': '-', 'category': '稳健高股息'},
                {'name': '长江电力', 'code': '600900', 'dividend_rate': '4.50%', 'industry': '电力', 'payout_ratio': '-', 'category': '稳健高股息'},
                {'name': '山西焦煤', 'code': '000983', 'dividend_rate': '4.70%', 'industry': '煤炭', 'payout_ratio': '-', 'category': '稳健高股息'},
            ],
            'financial': [
                {'name': '中国人寿', 'code': '601628', 'dividend_rate': '5.10%', 'industry': '保险', 'payout_ratio': '-', 'category': '金融高股息'},
                {'name': '中国建筑', 'code': '601668', 'dividend_rate': '4.30%', 'industry': '建筑', 'payout_ratio': '-', 'category': '金融高股息'},
                {'name': '贵州茅台', 'code': '600519', 'dividend_rate': '3.60%', 'industry': '白酒', 'payout_ratio': '75%', 'category': '金融高股息'},
                {'name': '内蒙华电', 'code': '600863', 'dividend_rate': '5.20%', 'industry': '电力', 'payout_ratio': '-', 'category': '金融高股息'},
            ]
        }

        # 尝试更新实时价格（不阻塞）
        try:
            self._update_realtime_prices(result)
        except Exception as e:
            print(f"更新实时价格失败（使用预设数据）: {e}")

        # 保存到缓存
        self.cache_data[cache_key] = {
            'timestamp': datetime.now().isoformat(),
            'data': result
        }
        self._save_cache()

        total = len(result['ultra_high']) + len(result['stable_high']) + len(result['financial'])
        print(f"加载完成: 共 {total} 只高股息股票")

        return result

    def _update_realtime_prices(self, result: Dict):
        """更新实时价格（可选）"""
        try:
            print("  尝试更新实时价格...")
            stock_em = ak.stock_zh_a_spot_em()

            for category in ['ultra_high', 'stable_high', 'financial']:
                for stock in result[category]:
                    try:
                        code = stock['code']
                        stock_detail = stock_em[stock_em['代码'] == code]
                        if not stock_detail.empty:
                            price = stock_detail.iloc[0].get('最新价', 0)
                            change = stock_detail.iloc[0].get('涨跌幅', 0)
                            if price > 0:
                                stock['price'] = f"{price:.2f}"
                                stock['change_pct'] = f"{change:.2f}%"
                    except:
                        continue

            print("  实时价格更新完成")
        except Exception as e:
            raise e

    def fetch_broker_stocks(self) -> Dict[str, List[Dict]]:
        """获取券商股票数据"""
        cache_key = 'broker_stocks'

        if self._is_cache_valid(cache_key):
            print("使用缓存的券商股票数据")
            return self.cache_data[cache_key]['data']

        print("加载券商股票数据...")

        broker_names = {
            '600030': '中信证券',
            '601688': '华泰证券',
            '601211': '国泰君安',
            '600999': '招商证券',
            '000776': '广发证券',
            '601066': '中信建投',
            '601995': '中金公司',
            '601881': '中国银河',
            '000166': '申万宏源',
            '300059': '东方财富',
            '600958': '东方证券',
            '601377': '兴业证券'
        }

        tier_descriptions = {
            'tier1': '超级龙头',
            'tier2': '头部券商',
            'tier3': '特色券商'
        }

        result = {
            'tier1': [],
            'tier2': [],
            'tier3': []
        }

        # 先构建基础数据
        for tier, codes in self.broker_codes.items():
            for code in codes:
                name = broker_names.get(code, '')
                stock = {
                    'name': name,
                    'code': code,
                    'revenue': '-',
                    'net_profit': '-',
                    'tier': f"第{['一', '二', '三'][['tier1', 'tier2', 'tier3'].index(tier)]}梯队",
                    'description': tier_descriptions[tier],
                    'price': '-',
                    'change_pct': '-',
                    'market_cap': '-'
                }
                result[tier].append(stock)

        # 尝试更新实时行情
        try:
            print("  尝试获取券商实时行情...")
            stock_em = ak.stock_zh_a_spot_em()

            for tier in result:
                for stock in result[tier]:
                    try:
                        code = stock['code']
                        stock_detail = stock_em[stock_em['代码'] == code]

                        if not stock_detail.empty:
                            row = stock_detail.iloc[0]
                            stock['price'] = f"{row.get('最新价', 0):.2f}"
                            stock['change_pct'] = f"{row.get('涨跌幅', 0):.2f}%"
                            market_cap = row.get('总市值', 0)
                            if market_cap:
                                stock['market_cap'] = f"{market_cap / 100000000:.0f}亿"
                    except:
                        continue

            print("  券商行情更新完成")
        except Exception as e:
            print(f"  获取券商行情失败（使用基础数据）: {e}")

        # 保存缓存
        self.cache_data[cache_key] = {
            'timestamp': datetime.now().isoformat(),
            'data': result
        }
        self._save_cache()

        total = len(result['tier1']) + len(result['tier2']) + len(result['tier3'])
        print(f"加载完成: 共 {total} 只券商股票")

        return result

    def fetch_etf_data(self) -> Dict[str, List[Dict]]:
        """获取ETF数据（静态配置）"""
        return {
            'broker': [
                {'name': '证券ETF', 'code': '512000', 'fund_company': '华宝基金', 'description': '跟踪全指证券公司指数', 'suitable_for': '综合配置'},
                {'name': '证券ETF', 'code': '159841', 'fund_company': '鹏华基金', 'description': '流动性好', 'suitable_for': '短线交易'},
                {'name': '龙头券商ETF', 'code': '159993', 'fund_company': '-', 'description': '跟踪国证证券龙头指数', 'suitable_for': '龙头配置'},
                {'name': '券商ETF联接', 'code': '008590', 'fund_company': '-', 'description': '场外基金，定投方便', 'suitable_for': '定投首选'},
            ],
            'dividend': [
                {'name': '红利ETF', 'code': '515180', 'fund_company': '易方达', 'description': '跟踪中证红利指数', 'suitable_for': '稳健配置'},
                {'name': '红利ETF', 'code': '510880', 'fund_company': '华泰柏瑞', 'description': '规模大流动性好', 'suitable_for': '长期持有'},
                {'name': '标普红利', 'code': '501029', 'fund_company': '华宝基金', 'description': '质量筛选', 'suitable_for': '追求质量'},
                {'name': '中证红利ETF', 'code': '159905', 'fund_company': '工银瑞信', 'description': '-', 'suitable_for': '防御配置'},
            ],
            'bank': [
                {'name': '银行ETF', 'code': '512800', 'fund_company': '华宝基金', 'description': '银行板块配置', 'suitable_for': '-'},
                {'name': '银行ETF', 'code': '512700', 'fund_company': '南方基金', 'description': '-', 'suitable_for': '-'},
            ],
            'financial': [
                {'name': '金融ETF', 'code': '510230', 'fund_company': '国泰基金', 'description': '券商+银行+保险', 'suitable_for': '-'},
                {'name': '大金融ETF', 'code': '516100', 'fund_company': '嘉实基金', 'description': '-', 'suitable_for': '-'},
            ]
        }

    def fetch_all_data(self) -> Dict:
        """获取所有数据"""
        print("\n" + "="*50)
        print("开始加载投资数据...")
        print("="*50)

        # 从静态文件加载投资组合配置
        portfolio_file = 'data/stocks.json'
        portfolios = {}
        if os.path.exists(portfolio_file):
            try:
                with open(portfolio_file, 'r', encoding='utf-8') as f:
                    static_data = json.load(f)
                    portfolios = static_data.get('portfolios', {})
            except Exception as e:
                print(f"加载静态配置失败: {e}")

        result = {
            'high_dividend_stocks': self.fetch_high_dividend_stocks(),
            'broker_stocks': self.fetch_broker_stocks(),
            'etfs': self.fetch_etf_data(),
            'portfolios': portfolios
        }

        print("="*50)
        print("数据加载完成!")
        print("="*50 + "\n")

        return result


# 测试代码
if __name__ == '__main__':
    fetcher = StockDataFetcher()
    data = fetcher.fetch_all_data()
    print("\n测试结果:")
    print(f"  高股息股票: {sum(len(v) for v in data['high_dividend_stocks'].values())} 只")
    print(f"  券商股票: {sum(len(v) for v in data['broker_stocks'].values())} 只")
    print(f"  ETF产品: {sum(len(v) for v in data['etfs'].values())} 只")
