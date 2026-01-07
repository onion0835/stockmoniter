"""
股票数据抓取模块
使用 AKShare 从股票市场获取实时数据
"""
import akshare as ak
import pandas as pd
from datetime import datetime, timedelta
import json
import os
from typing import Dict, List


class StockDataFetcher:
    """股票数据抓取器"""

    def __init__(self, cache_file='data/cache.json'):
        self.cache_file = cache_file
        self.cache_data = self._load_cache()
        self.cache_duration = timedelta(hours=4)  # 缓存4小时

        # 券商股票代码列表
        self.broker_codes = {
            'tier1': ['600030', '601688', '601211'],  # 中信证券、华泰证券、海通证券
            'tier2': ['600999', '000776', '601066', '601995', '601881'],  # 招商、广发、中信建投、中金、银河
            'tier3': ['000166', '300059', '600958', '601377']  # 申万宏源、东方财富、东方证券、兴业证券
        }

        # 行业分类
        self.industry_keywords = {
            '煤炭': ['煤炭', '焦煤', '焦炭'],
            '交通运输': ['高速', '港口', '物流', '航运'],
            '电力': ['电力', '水电', '华电'],
            '石油': ['石油', '石化', '中石'],
            '金融': ['银行', '保险', '证券'],
            '建材': ['建材', '水泥'],
            '建筑': ['建筑', '基建'],
            '有色金属': ['铝业', '铜业', '有色'],
            '白酒': ['茅台', '五粮液', '白酒'],
            '机械设备': ['机械', '设备'],
            '消费': ['消费', '零售', '时尚']
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

    def _get_industry(self, name: str, industry_raw: str) -> str:
        """识别行业"""
        # 先检查原始行业
        for industry, keywords in self.industry_keywords.items():
            if any(keyword in industry_raw for keyword in keywords):
                return industry

        # 再检查股票名称
        for industry, keywords in self.industry_keywords.items():
            if any(keyword in name for keyword in keywords):
                return industry

        return industry_raw if industry_raw else '其他'

    def fetch_high_dividend_stocks(self) -> Dict[str, List[Dict]]:
        """
        获取高股息股票
        返回分类后的高股息股票列表
        """
        cache_key = 'high_dividend_stocks'

        # 检查缓存
        if self._is_cache_valid(cache_key):
            print("使用缓存的高股息股票数据")
            return self.cache_data[cache_key]['data']

        print("正在从市场获取高股息股票数据...")

        try:
            # 获取A股股票列表
            stock_info = ak.stock_info_a_code_name()

            # 获取股息率数据（使用东方财富的股息率数据）
            dividend_data = ak.stock_dividend_cninfo()

            # 获取市盈率等指标
            stock_em = ak.stock_zh_a_spot_em()

            # 合并数据
            result = {
                'ultra_high': [],
                'stable_high': [],
                'financial': []
            }

            # 处理股息率数据
            for _, row in dividend_data.iterrows():
                try:
                    code = row.get('股票代码', '')
                    name = row.get('股票简称', '')
                    dividend_rate_str = row.get('股息率', '0')

                    # 解析股息率
                    if isinstance(dividend_rate_str, str):
                        dividend_rate = float(dividend_rate_str.replace('%', ''))
                    else:
                        dividend_rate = float(dividend_rate_str)

                    # 只处理股息率大于2%的股票
                    if dividend_rate < 2:
                        continue

                    # 获取行业信息
                    stock_detail = stock_em[stock_em['代码'] == code]
                    industry = ''
                    if not stock_detail.empty:
                        industry = stock_detail.iloc[0].get('行业', '')

                    industry = self._get_industry(name, industry)

                    # 构建股票信息
                    stock = {
                        'name': name,
                        'code': code,
                        'dividend_rate': f"{dividend_rate:.2f}%",
                        'industry': industry,
                        'payout_ratio': '-',
                        'category': ''
                    }

                    # 分类
                    if dividend_rate >= 6:
                        stock['category'] = '超高股息率'
                        result['ultra_high'].append(stock)
                    elif dividend_rate >= 4:
                        # 判断是否为金融股
                        if industry in ['保险', '银行', '证券'] or '金融' in industry:
                            stock['category'] = '金融高股息'
                            result['financial'].append(stock)
                        else:
                            stock['category'] = '稳健高股息'
                            result['stable_high'].append(stock)
                    elif dividend_rate >= 2:
                        if industry in ['保险', '银行', '证券'] or '金融' in industry:
                            stock['category'] = '金融高股息'
                            result['financial'].append(stock)

                except Exception as e:
                    continue

            # 限制每个分类的数量（取前20个）
            result['ultra_high'] = sorted(result['ultra_high'],
                                         key=lambda x: float(x['dividend_rate'].replace('%', '')),
                                         reverse=True)[:20]
            result['stable_high'] = sorted(result['stable_high'],
                                          key=lambda x: float(x['dividend_rate'].replace('%', '')),
                                          reverse=True)[:20]
            result['financial'] = sorted(result['financial'],
                                        key=lambda x: float(x['dividend_rate'].replace('%', '')),
                                        reverse=True)[:20]

            # 保存到缓存
            self.cache_data[cache_key] = {
                'timestamp': datetime.now().isoformat(),
                'data': result
            }
            self._save_cache()

            print(f"获取成功: 超高股息 {len(result['ultra_high'])} 只, "
                  f"稳健高股息 {len(result['stable_high'])} 只, "
                  f"金融高股息 {len(result['financial'])} 只")

            return result

        except Exception as e:
            print(f"获取高股息股票数据失败: {e}")
            # 如果失败，返回缓存数据（即使过期）
            if cache_key in self.cache_data:
                return self.cache_data[cache_key]['data']
            return {'ultra_high': [], 'stable_high': [], 'financial': []}

    def fetch_broker_stocks(self) -> Dict[str, List[Dict]]:
        """
        获取券商股票数据
        返回分层的券商股票列表
        """
        cache_key = 'broker_stocks'

        # 检查缓存
        if self._is_cache_valid(cache_key):
            print("使用缓存的券商股票数据")
            return self.cache_data[cache_key]['data']

        print("正在从市场获取券商股票数据...")

        try:
            # 获取实时行情
            stock_em = ak.stock_zh_a_spot_em()

            result = {
                'tier1': [],
                'tier2': [],
                'tier3': []
            }

            # 券商名称映射
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

            for tier, codes in self.broker_codes.items():
                for code in codes:
                    try:
                        # 查找股票信息
                        stock_detail = stock_em[stock_em['代码'] == code]

                        if not stock_detail.empty:
                            row = stock_detail.iloc[0]
                            name = broker_names.get(code, row.get('名称', ''))

                            stock = {
                                'name': name,
                                'code': code,
                                'revenue': '-',
                                'net_profit': '-',
                                'tier': f"第{['一', '二', '三'][['tier1', 'tier2', 'tier3'].index(tier)]}梯队",
                                'description': tier_descriptions[tier],
                                'price': f"{row.get('最新价', 0):.2f}",
                                'change_pct': f"{row.get('涨跌幅', 0):.2f}%",
                                'market_cap': f"{row.get('总市值', 0) / 100000000:.0f}亿" if row.get('总市值') else '-'
                            }

                            result[tier].append(stock)
                    except Exception as e:
                        print(f"获取券商 {code} 数据失败: {e}")
                        continue

            # 保存到缓存
            self.cache_data[cache_key] = {
                'timestamp': datetime.now().isoformat(),
                'data': result
            }
            self._save_cache()

            print(f"获取券商数据成功: 第一梯队 {len(result['tier1'])} 只, "
                  f"第二梯队 {len(result['tier2'])} 只, "
                  f"第三梯队 {len(result['tier3'])} 只")

            return result

        except Exception as e:
            print(f"获取券商股票数据失败: {e}")
            # 如果失败，返回缓存数据（即使过期）
            if cache_key in self.cache_data:
                return self.cache_data[cache_key]['data']
            return {'tier1': [], 'tier2': [], 'tier3': []}

    def fetch_etf_data(self) -> Dict[str, List[Dict]]:
        """
        获取ETF数据（这部分主要是静态配置，因为ETF产品相对固定）
        """
        # ETF数据相对固定，这里返回预定义的数据
        return {
            'broker': [
                {
                    'name': '证券ETF',
                    'code': '512000',
                    'fund_company': '华宝基金',
                    'description': '跟踪全指证券公司指数',
                    'suitable_for': '综合配置'
                },
                {
                    'name': '证券ETF',
                    'code': '159841',
                    'fund_company': '鹏华基金',
                    'description': '流动性好',
                    'suitable_for': '短线交易'
                }
            ],
            'dividend': [
                {
                    'name': '红利ETF',
                    'code': '515180',
                    'fund_company': '易方达',
                    'description': '跟踪中证红利指数',
                    'suitable_for': '稳健配置'
                },
                {
                    'name': '红利ETF',
                    'code': '510880',
                    'fund_company': '华泰柏瑞',
                    'description': '规模大流动性好',
                    'suitable_for': '长期持有'
                }
            ],
            'bank': [
                {
                    'name': '银行ETF',
                    'code': '512800',
                    'fund_company': '华宝基金',
                    'description': '银行板块配置',
                    'suitable_for': '-'
                }
            ],
            'financial': [
                {
                    'name': '金融ETF',
                    'code': '510230',
                    'fund_company': '国泰基金',
                    'description': '券商+银行+保险',
                    'suitable_for': '-'
                }
            ]
        }

    def fetch_all_data(self) -> Dict:
        """
        获取所有数据
        """
        print("开始获取所有股票数据...")

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

        return {
            'high_dividend_stocks': self.fetch_high_dividend_stocks(),
            'broker_stocks': self.fetch_broker_stocks(),
            'etfs': self.fetch_etf_data(),
            'portfolios': portfolios
        }


# 测试代码
if __name__ == '__main__':
    fetcher = StockDataFetcher()

    print("\n=== 测试获取高股息股票 ===")
    dividend_stocks = fetcher.fetch_high_dividend_stocks()
    print(f"超高股息股票: {len(dividend_stocks['ultra_high'])} 只")
    if dividend_stocks['ultra_high']:
        print(f"示例: {dividend_stocks['ultra_high'][0]}")

    print("\n=== 测试获取券商股票 ===")
    broker_stocks = fetcher.fetch_broker_stocks()
    print(f"第一梯队: {len(broker_stocks['tier1'])} 只")
    if broker_stocks['tier1']:
        print(f"示例: {broker_stocks['tier1'][0]}")
