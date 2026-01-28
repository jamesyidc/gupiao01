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
    
    def get_theme_top_stocks(self, theme_name, end_date, lookback_days=365, top_n=15):
        """
        获取指定题材在过去一年内涨停次数最多的前N只股票
        
        Args:
            theme_name: 题材名称
            end_date: 截止日期
            lookback_days: 回溯天数，默认365天
            top_n: 返回前N只股票，默认15
            
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
        result = self.session.query(
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
        ).limit(top_n).all()
        
        return [(r.code, r.name, r.limit_up_count) for r in result]
    
    def calculate_position_percentage(self, stock_code, target_date, lookback_periods=240):
        """
        计算个股在过去N个交易日的位置百分比
        
        算法说明：
        1. 获取过去240个交易日的收盘价
        2. 找出最低价作为基准（0%）
        3. 找出最高价作为顶部（100%）
        4. 计算当前价格的位置百分比 = (当前价 - 最低价) / (最高价 - 最低价) * 100
        
        Args:
            stock_code: 股票代码
            target_date: 目标日期
            lookback_periods: 回溯交易日数量，默认240
            
        Returns:
            dict: {
                'current_price': 当前价格,
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
        
        # 获取过去N个交易日的价格数据
        prices = self.session.query(DailyPrice).filter(
            and_(
                DailyPrice.stock_id == stock.id,
                DailyPrice.trade_date <= target_date
            )
        ).order_by(
            DailyPrice.trade_date.desc()
        ).limit(lookback_periods).all()
        
        if not prices:
            return None
        
        # 提取收盘价
        close_prices = [p.close_price for p in prices]
        current_price = close_prices[0]  # 最新价格
        lowest_price = min(close_prices)
        highest_price = max(close_prices)
        
        # 计算位置百分比
        if highest_price == lowest_price:
            position_percent = 50.0  # 如果价格没有波动，设为中位
        else:
            position_percent = (current_price - lowest_price) / (highest_price - lowest_price) * 100
        
        return {
            'stock_code': stock_code,
            'stock_name': stock.name,
            'current_price': round(current_price, 2),
            'lowest_price': round(lowest_price, 2),
            'highest_price': round(highest_price, 2),
            'position_percent': round(position_percent, 2),
            'available_periods': len(prices),
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
