"""
为大消费题材的成分股生成模拟日线数据
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models import db, Stock, DailyPrice
from datetime import datetime, timedelta
import random

# 获取数据库会话
session = db.get_session()

# 大消费题材前20只成分股
top_stocks_codes = [
    '600693', '605188', '601086', '600828', '603696',
    '600530', '002187', '603709', '601566', '600865',
    '002329', '000759', '600250', '001234', '601579',
    '600280', '603221', '002910', '002702', '603777'
]

print("="*80)
print("为大消费题材成分股生成模拟日线数据")
print("="*80)

# 设置时间范围：过去400个交易日（覆盖240+的范围）
end_date = datetime(2026, 1, 28)
start_date = end_date - timedelta(days=600)  # 多生成一些数据

total_generated = 0
total_stocks = len(top_stocks_codes)

for i, code in enumerate(top_stocks_codes, 1):
    print(f"\n[{i}/{total_stocks}] 处理股票 {code}...")
    
    # 查询股票
    stock = session.query(Stock).filter_by(code=code).first()
    if not stock:
        print(f"  ❌ 股票 {code} 不存在")
        continue
    
    print(f"  股票名称: {stock.name}")
    
    # 检查是否已有数据
    existing_count = session.query(DailyPrice).filter_by(stock_id=stock.id).count()
    if existing_count > 0:
        print(f"  ⚠️  已有 {existing_count} 条数据，跳过")
        continue
    
    # 生成模拟价格数据
    base_price = random.uniform(5, 50)  # 基础价格
    current_price = base_price
    
    current_date = start_date
    generated = 0
    
    while current_date <= end_date:
        # 跳过周末
        if current_date.weekday() >= 5:
            current_date += timedelta(days=1)
            continue
        
        # 生成随机价格波动（-5% 到 +5%）
        change_percent = random.uniform(-0.05, 0.05)
        current_price = current_price * (1 + change_percent)
        
        # 确保价格在合理范围
        current_price = max(current_price, base_price * 0.5)  # 最多跌50%
        current_price = min(current_price, base_price * 2.0)  # 最多涨100%
        
        # 生成日K线数据
        open_price = current_price * random.uniform(0.98, 1.02)
        high_price = max(open_price, current_price) * random.uniform(1.0, 1.03)
        low_price = min(open_price, current_price) * random.uniform(0.97, 1.0)
        volume = random.randint(100000, 10000000)
        amount = volume * current_price
        
        # 创建日线记录
        daily_price = DailyPrice(
            stock_id=stock.id,
            trade_date=current_date.date(),
            open_price=round(open_price, 2),
            close_price=round(current_price, 2),
            high_price=round(high_price, 2),
            low_price=round(low_price, 2),
            volume=volume,
            amount=round(amount, 2)
        )
        session.add(daily_price)
        generated += 1
        
        current_date += timedelta(days=1)
    
    # 提交该股票的数据
    session.commit()
    total_generated += generated
    print(f"  ✓ 生成 {generated} 条日线数据")

session.close()

print("\n" + "="*80)
print(f"完成！共为 {total_stocks} 只股票生成 {total_generated} 条日线数据")
print("="*80)
