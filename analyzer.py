"""
股票数据分析核心算法
"""
from datetime import datetime, timedelta
from sqlalchemy import func, and_
from models import Stock, Theme, DailyPrice, LimitUpRecord, db
import pandas as pd
import numpy as np


class StockAnalyzer:
    """股票数据分析器"""
    
    def __init__(self):
        self.session = db.get_session()
    
    def get_theme_top_stocks(self, theme_name, end_date, lookback_days=365, top_n=None):
        """
        获取指定题材在过去一年内涨停次数最多的前N只股票
        
        新逻辑：
        - 统计该题材所有涨停股票
        - 取前20%的股票作为成分股
        - 最少10只，最多20只
        
        Args:
            theme_name: 题材名称
            end_date: 截止日期
            lookback_days: 回溯天数，默认365天
            top_n: 返回前N只股票，如果为None则自动计算（前20%，10-20只）
            
        Returns:
            list: [(stock_code, stock_name, limit_up_count), ...]
        """
        # 计算起始日期
        if isinstance(end_date, str):
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        start_date = end_date - timedelta(days=lookback_days)
        
        # 查询题材
        theme = self.session.query(Theme).filter(Theme.name == theme_name).first()
        if not theme:
            return []
        
        # 统计每只股票的涨停次数
        all_stocks = self.session.query(
            Stock.code,
            Stock.name,
            func.count(LimitUpRecord.id).label('limit_up_count')
        ).join(
            LimitUpRecord, Stock.id == LimitUpRecord.stock_id
        ).filter(
            and_(
                LimitUpRecord.theme_id == theme.id,
                LimitUpRecord.trade_date >= start_date,
                LimitUpRecord.trade_date <= end_date
            )
        ).group_by(
            Stock.code, Stock.name
        ).order_by(
            func.count(LimitUpRecord.id).desc()
        ).all()
        
        # 如果没有指定top_n，则自动计算
        if top_n is None:
            total_count = len(all_stocks)
            # 前20%
            top_n = int(total_count * 0.2)
            # 限制在10-20之间
            top_n = max(10, min(20, top_n))
        
        result = all_stocks[:top_n]
        return [(r.code, r.name, r.limit_up_count) for r in result]
    
    def calculate_position_percentage(self, stock_code, target_date, lookback_periods=240):
        """
        计算个股在过去N个交易日的位置百分比
        
        算法说明（新逻辑）：
        1. 获取241个交易日的数据（包括240天前的价格）
        2. 第241天（最早的那天）的价格作为起始价格
        3. 从第240天到第1天（当前）这240天内找最高价和最低价
        4. 最低价 = 0%，最高价 = 100%
        5. 计算当前价格（第1天）的位置百分比 = (当前价 - 最低价) / (最高价 - 最低价) * 100
        
        Args:
            stock_code: 股票代码
            target_date: 目标日期
            lookback_periods: 回溯交易日数量，默认240
            
        Returns:
            dict: {
                'current_price': 当前价格,
                'start_price': 起始价格（240天前）,
                'lowest_price': 最低价,
                'highest_price': 最高价,
                'position_percent': 位置百分比,
                'available_periods': 实际可用交易日数量
            }
        """
        # 查询股票
        stock = self.session.query(Stock).filter(Stock.code == stock_code).first()
        if not stock:
            return None
        
        if isinstance(target_date, str):
            target_date = datetime.strptime(target_date, '%Y-%m-%d').date()
        
        # 获取过去241个交易日的价格数据（多取1天作为起始点）
        prices = self.session.query(DailyPrice).filter(
            and_(
                DailyPrice.stock_id == stock.id,
                DailyPrice.trade_date <= target_date
            )
        ).order_by(
            DailyPrice.trade_date.desc()
        ).limit(lookback_periods + 1).all()
        
        if len(prices) < 2:  # 至少需要2天的数据
            return None
        
        # 提取收盘价
        close_prices = [p.close_price for p in prices]
        current_price = close_prices[0]  # 第1天（当前价格）
        
        # 如果有241天的数据，起始价格是第241天（最后一个）
        # 计算区间是从第240天到第1天
        if len(close_prices) >= lookback_periods + 1:
            start_price = close_prices[lookback_periods]  # 第241天的价格
            price_range = close_prices[:lookback_periods]  # 前240天的价格
        else:
            # 如果数据不足241天，用最后一天作为起始
            start_price = close_prices[-1]
            price_range = close_prices[:-1] if len(close_prices) > 1 else close_prices
        
        lowest_price = min(price_range)
        highest_price = max(price_range)
        
        # 计算位置百分比
        if highest_price == lowest_price:
            position_percent = 50.0  # 如果价格没有波动，设为中位
        else:
            position_percent = (current_price - lowest_price) / (highest_price - lowest_price) * 100
        
        return {
            'stock_code': stock_code,
            'stock_name': stock.name,
            'current_price': round(current_price, 2),
            'start_price': round(start_price, 2),
            'lowest_price': round(lowest_price, 2),
            'highest_price': round(highest_price, 2),
            'position_percent': round(position_percent, 2),
            'available_periods': len(prices) - 1,  # 减1因为有一天是起始价格
            'target_date': target_date.strftime('%Y-%m-%d')
        }
    
    def calculate_theme_position_percentage(self, theme_name, target_date, lookback_periods=240):
        """
        计算题材的平均位置百分比
        
        算法说明：
        1. 获取该题材的前15只成分股
        2. 计算每只成分股的位置百分比
        3. 取平均值作为题材的整体位置百分比
        
        Args:
            theme_name: 题材名称
            target_date: 目标日期
            lookback_periods: 回溯交易日数量，默认240
            
        Returns:
            dict: {
                'theme_name': 题材名称,
                'constituent_stocks': 成分股列表,
                'theme_position_percent': 题材位置百分比,
                'target_date': 目标日期
            }
        """
        # 获取题材成分股
        constituent_stocks = self.get_theme_top_stocks(theme_name, target_date)
        
        if not constituent_stocks:
            return None
        
        # 计算每只股票的位置百分比
        stock_positions = []
        valid_positions = []
        
        for code, name, limit_up_count in constituent_stocks:
            position_data = self.calculate_position_percentage(code, target_date, lookback_periods)
            if position_data:
                stock_positions.append({
                    'code': code,
                    'name': name,
                    'limit_up_count': limit_up_count,
                    'position_percent': position_data['position_percent'],
                    'current_price': position_data['current_price']
                })
                valid_positions.append(position_data['position_percent'])
        
        # 计算题材平均位置百分比
        if valid_positions:
            theme_position_percent = round(np.mean(valid_positions), 2)
        else:
            theme_position_percent = None
        
        return {
            'theme_name': theme_name,
            'constituent_stocks': stock_positions,
            'constituent_count': len(stock_positions),
            'theme_position_percent': theme_position_percent,
            'target_date': target_date if isinstance(target_date, str) else target_date.strftime('%Y-%m-%d')
        }
    
    def compare_stock_with_theme(self, stock_code, theme_name, target_date, lookback_periods=240):
        """
        比较个股与题材的位置百分比
        
        Args:
            stock_code: 股票代码
            theme_name: 题材名称
            target_date: 目标日期
            lookback_periods: 回溯交易日数量
            
        Returns:
            dict: 完整的比较分析结果
        """
        # 获取个股位置
        stock_position = self.calculate_position_percentage(stock_code, target_date, lookback_periods)
        
        # 获取题材位置
        theme_position = self.calculate_theme_position_percentage(theme_name, target_date, lookback_periods)
        
        if not stock_position or not theme_position:
            return None
        
        # 计算差异
        position_diff = round(
            stock_position['position_percent'] - theme_position['theme_position_percent'], 
            2
        )
        
        # 判断相对强弱
        if position_diff > 10:
            relative_strength = "强于题材"
        elif position_diff < -10:
            relative_strength = "弱于题材"
        else:
            relative_strength = "与题材同步"
        
        # 检查是否在成分股中
        is_constituent = any(
            s['code'] == stock_code 
            for s in theme_position['constituent_stocks']
        )
        
        return {
            'stock_info': stock_position,
            'theme_info': theme_position,
            'comparison': {
                'position_difference': position_diff,
                'relative_strength': relative_strength,
                'is_constituent_stock': is_constituent
            },
            'analysis_params': {
                'lookback_periods': lookback_periods,
                'target_date': target_date if isinstance(target_date, str) else target_date.strftime('%Y-%m-%d')
            }
        }
    
    def close(self):
        """关闭数据库会话"""
        self.session.close()
