"""
测试大消费题材的位置计算（新算法）
"""
from analyzer import StockAnalyzer
from datetime import datetime

# 创建分析器
analyzer = StockAnalyzer()

# 设置目标日期
target_date = '2026-01-28'

print("="*80)
print(f"大消费题材位置分析（新算法）")
print(f"目标日期: {target_date}")
print(f"回溯周期: 240个交易日")
print("="*80)
print("\n算法说明:")
print("1. 统计大消费题材中所有涨停股票")
print("2. 取前20%的股票，最少10只，最多20只")
print("3. 获取每只股票241天的数据")
print("4. 第241天的价格作为起始价格")
print("5. 从第240天到第1天（当前）找最高价和最低价")
print("6. 位置% = (当前价 - 最低价) / (最高价 - 最低价) × 100%")
print("7. 题材位置 = 20只成分股位置的平均值")
print("="*80)

# 计算题材位置
result = analyzer.calculate_theme_position_percentage('大消费', target_date, lookback_periods=240)

if result:
    print(f"\n✅ 分析成功！")
    print(f"\n题材名称: {result['theme_name']}")
    print(f"成分股数量: {result['constituent_count']} 只")
    print(f"题材位置百分比: {result['theme_position_percent']}%")
    
    print("\n" + "="*80)
    print("成分股详情:")
    print("="*80)
    print(f"{'排名':<6}{'代码':<10}{'名称':<15}{'涨停次数':<10}{'位置%':<10}{'当前价':<10}")
    print("-"*80)
    
    for i, stock in enumerate(result['constituent_stocks'], 1):
        print(f"{i:<6}{stock['code']:<10}{stock['name']:<15}{stock['limit_up_count']:<10}{stock['position_percent']:<10.2f}{stock['current_price']:<10.2f}")
    
    print("="*80)
    print(f"\n📊 题材整体位置: {result['theme_position_percent']}%")
    
    # 位置分析
    pos = result['theme_position_percent']
    if pos < 30:
        level = "低位区间"
        advice = "题材处于低位，可能具有较大上涨空间"
    elif pos < 70:
        level = "中位区间"
        advice = "题材处于中位，需要结合其他指标判断"
    else:
        level = "高位区间"
        advice = "题材处于高位，注意风险"
    
    print(f"位置评级: {level}")
    print(f"分析建议: {advice}")
    
else:
    print("\n❌ 分析失败，可能原因：")
    print("  1. 题材不存在")
    print("  2. 没有足够的历史价格数据")
    print("  3. 数据库中缺少日线数据")

print("\n" + "="*80)
