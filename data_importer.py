"""
数据导入工具 - 用于导入测试数据或真实数据
"""
from datetime import datetime, timedelta
from models import db, Stock, Theme, DailyPrice, LimitUpRecord
import random


class DataImporter:
    """数据导入器"""
    
    def __init__(self):
        self.session = db.get_session()
    
    def import_stocks(self, stocks_data):
        """
        导入股票基本信息
        
        Args:
            stocks_data: [
                {'code': '000001', 'name': '平安银行', 'market': 'SZ'},
                ...
            ]
        """
        for stock_info in stocks_data:
            existing = self.session.query(Stock).filter(
                Stock.code == stock_info['code']
            ).first()
            
            if not existing:
                stock = Stock(
                    code=stock_info['code'],
                    name=stock_info['name'],
                    market=stock_info.get('market', 'SZ')
                )
                self.session.add(stock)
        
        self.session.commit()
        print(f"已导入 {len(stocks_data)} 只股票")
    
    def import_themes(self, themes_data):
        """
        导入题材信息
        
        Args:
            themes_data: [
                {'name': '人工智能', 'description': 'AI相关概念'},
                ...
            ]
        """
        for theme_info in themes_data:
            existing = self.session.query(Theme).filter(
                Theme.name == theme_info['name']
            ).first()
            
            if not existing:
                theme = Theme(
                    name=theme_info['name'],
                    description=theme_info.get('description', '')
                )
                self.session.add(theme)
        
        self.session.commit()
        print(f"已导入 {len(themes_data)} 个题材")
    
    def import_daily_prices(self, stock_code, prices_data):
        """
        导入日线数据
        
        Args:
            stock_code: 股票代码
            prices_data: [
                {
                    'trade_date': '2024-01-28',
                    'open': 12.50,
                    'close': 12.80,
                    'high': 13.00,
                    'low': 12.40,
                    'volume': 1000000,
                    'amount': 12800000
                },
                ...
            ]
        """
        stock = self.session.query(Stock).filter(Stock.code == stock_code).first()
        if not stock:
            print(f"股票 {stock_code} 不存在")
            return
        
        for price_info in prices_data:
            trade_date = datetime.strptime(price_info['trade_date'], '%Y-%m-%d').date()
            
            existing = self.session.query(DailyPrice).filter(
                DailyPrice.stock_id == stock.id,
                DailyPrice.trade_date == trade_date
            ).first()
            
            if not existing:
                daily_price = DailyPrice(
                    stock_id=stock.id,
                    trade_date=trade_date,
                    open_price=price_info.get('open'),
                    close_price=price_info['close'],
                    high_price=price_info.get('high'),
                    low_price=price_info.get('low'),
                    volume=price_info.get('volume'),
                    amount=price_info.get('amount'),
                    change_percent=price_info.get('change_percent')
                )
                self.session.add(daily_price)
        
        self.session.commit()
        print(f"已导入股票 {stock_code} 的 {len(prices_data)} 条日线数据")
    
    def import_limit_up_records(self, records_data):
        """
        导入涨停记录
        
        Args:
            records_data: [
                {
                    'stock_code': '000001',
                    'theme_name': '人工智能',
                    'trade_date': '2024-01-28',
                    'reason': '业绩预增',
                    'limit_up_time': '09:30',
                    'open_count': 0
                },
                ...
            ]
        """
        for record_info in records_data:
            stock = self.session.query(Stock).filter(
                Stock.code == record_info['stock_code']
            ).first()
            
            theme = self.session.query(Theme).filter(
                Theme.name == record_info['theme_name']
            ).first()
            
            if not stock or not theme:
                print(f"股票 {record_info['stock_code']} 或题材 {record_info['theme_name']} 不存在")
                continue
            
            trade_date = datetime.strptime(record_info['trade_date'], '%Y-%m-%d').date()
            
            existing = self.session.query(LimitUpRecord).filter(
                LimitUpRecord.stock_id == stock.id,
                LimitUpRecord.theme_id == theme.id,
                LimitUpRecord.trade_date == trade_date
            ).first()
            
            if not existing:
                limit_up = LimitUpRecord(
                    stock_id=stock.id,
                    theme_id=theme.id,
                    trade_date=trade_date,
                    reason=record_info.get('reason', ''),
                    limit_up_time=record_info.get('limit_up_time'),
                    open_count=record_info.get('open_count', 0),
                    turnover_rate=record_info.get('turnover_rate')
                )
                self.session.add(limit_up)
        
        self.session.commit()
        print(f"已导入 {len(records_data)} 条涨停记录")
    
    def generate_mock_data(self):
        """生成模拟数据用于测试"""
        print("开始生成模拟数据...")
        
        # 1. 创建股票
        stocks = []
        for i in range(1, 51):  # 50只股票
            stocks.append({
                'code': f'{i:06d}',
                'name': f'测试股票{i}',
                'market': 'SZ' if i % 2 == 0 else 'SH'
            })
        self.import_stocks(stocks)
        
        # 2. 创建题材
        themes = [
            {'name': '人工智能', 'description': 'AI相关概念'},
            {'name': '新能源汽车', 'description': '新能源汽车产业链'},
            {'name': '芯片半导体', 'description': '半导体芯片制造'},
            {'name': '医药医疗', 'description': '医药医疗健康'},
            {'name': '5G通信', 'description': '5G通信技术'}
        ]
        self.import_themes(themes)
        
        # 3. 生成日线数据（过去300个交易日）
        end_date = datetime.now().date()
        
        for stock_code in [f'{i:06d}' for i in range(1, 51)]:
            prices = []
            base_price = random.uniform(10, 50)
            current_price = base_price
            
            for day_offset in range(300, 0, -1):
                trade_date = end_date - timedelta(days=day_offset)
                
                # 跳过周末
                if trade_date.weekday() >= 5:
                    continue
                
                # 随机价格波动
                change = random.uniform(-0.05, 0.05)
                current_price = current_price * (1 + change)
                
                open_price = current_price * random.uniform(0.98, 1.02)
                high_price = max(current_price, open_price) * random.uniform(1.0, 1.05)
                low_price = min(current_price, open_price) * random.uniform(0.95, 1.0)
                
                prices.append({
                    'trade_date': trade_date.strftime('%Y-%m-%d'),
                    'open': round(open_price, 2),
                    'close': round(current_price, 2),
                    'high': round(high_price, 2),
                    'low': round(low_price, 2),
                    'volume': random.randint(100000, 10000000),
                    'amount': random.randint(1000000, 100000000)
                })
            
            self.import_daily_prices(stock_code, prices)
        
        # 4. 生成涨停记录
        limit_up_records = []
        theme_names = [t['name'] for t in themes]
        
        for i in range(1, 51):
            stock_code = f'{i:06d}'
            # 随机选择1-2个题材
            stock_themes = random.sample(theme_names, random.randint(1, 2))
            
            for theme_name in stock_themes:
                # 过去一年内随机3-10次涨停
                limit_up_count = random.randint(3, 10)
                
                for _ in range(limit_up_count):
                    days_ago = random.randint(1, 365)
                    trade_date = (end_date - timedelta(days=days_ago)).strftime('%Y-%m-%d')
                    
                    limit_up_records.append({
                        'stock_code': stock_code,
                        'theme_name': theme_name,
                        'trade_date': trade_date,
                        'reason': f'{theme_name}板块活跃',
                        'limit_up_time': f'{random.randint(9, 14):02d}:{random.randint(0, 59):02d}',
                        'open_count': random.randint(0, 3)
                    })
        
        self.import_limit_up_records(limit_up_records)
        
        print("模拟数据生成完成！")
    
    def close(self):
        """关闭会话"""
        self.session.close()


if __name__ == '__main__':
    # 初始化数据库
    db.create_tables()
    
    # 创建导入器并生成模拟数据
    importer = DataImporter()
    importer.generate_mock_data()
    importer.close()
    
    print("\n数据导入完成！可以启动API服务了。")
