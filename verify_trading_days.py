"""
验证交易日计算的正确性
"""
from models import db, DailyPrice, Stock
from datetime import datetime

session = db.get_session()

# 测试股票：东百集团
stock = session.query(Stock).filter_by(code='600693').first()

if stock:
    print("="*80)
    print(f"验证股票: {stock.code} {stock.name}")
    print("="*80)
    
    target_date = datetime(2026, 1, 28).date()
    
    # 获取241条记录
    prices = session.query(DailyPrice).filter(
        DailyPrice.stock_id == stock.id,
        DailyPrice.trade_date <= target_date
    ).order_by(
        DailyPrice.trade_date.desc()
    ).limit(241).all()
    
    print(f"\n获取到 {len(prices)} 条价格记录")
    print(f"\n最新10个交易日:")
    print("-"*80)
    for i, p in enumerate(prices[:10], 1):
        weekday = p.trade_date.strftime('%A')  # 星期几
        print(f"{i:3d}. {p.trade_date} ({weekday:10s}) - 收盘价: {p.close_price:7.2f}")
    
    print(f"\n最早10个交易日:")
    print("-"*80)
    for i, p in enumerate(prices[-10:], len(prices)-9):
        weekday = p.trade_date.strftime('%A')
        print(f"{i:3d}. {p.trade_date} ({weekday:10s}) - 收盘价: {p.close_price:7.2f}")
    
    print("\n" + "="*80)
    print("验证结论:")
    print("="*80)
    
    # 检查是否包含周末
    has_weekend = False
    for p in prices:
        if p.trade_date.weekday() >= 5:  # 周六或周日
            has_weekend = True
            print(f"⚠️  发现周末数据: {p.trade_date} ({p.trade_date.strftime('%A')})")
    
    if not has_weekend:
        print("✅ 所有记录都是交易日（不包含周末）")
    
    print(f"\n✅ 获取的是 {len(prices)} 个交易日的数据")
    print(f"✅ 第1个交易日（当前）: {prices[0].trade_date}")
    print(f"✅ 第241个交易日（起始）: {prices[-1].trade_date}")
    
    # 计算时间跨度
    days_span = (prices[0].trade_date - prices[-1].trade_date).days
    print(f"\n📅 时间跨度: {days_span} 天（自然日）")
    print(f"📊 交易日数量: {len(prices)} 天")
    print(f"📈 平均每周交易日: {len(prices) / (days_span / 7):.2f} 天")

session.close()
