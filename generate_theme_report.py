"""
生成大消费板块TOP20个股百分比位置计算表
"""
from analyzer import StockAnalyzer
from datetime import datetime
import sys

# 创建分析器
analyzer = StockAnalyzer()

# 设置目标日期
target_date = '2026-01-28'

print("="*100)
print(" " * 35 + "大消费板块 TOP20 个股百分比位置计算表")
print("="*100)

# 计算题材位置
result = analyzer.calculate_theme_position_percentage('大消费', target_date, lookback_periods=240)

if not result or not result['constituent_stocks']:
    print("\n❌ 无法获取数据")
    sys.exit(1)

# 表头
print(f"\n{'排名':<6}{'股票名称':<15}{'股票代码':<12}{'出现频次':<12}{'240天内最低价(元)':<18}{'240天内最高价(元)':<18}{'当前股价(元)':<15}{'个股百分比位置':<15}")
print("-" * 100)

# 为了获取更详细的信息，我们需要重新查询每只股票的详细数据
total_position = 0
valid_count = 0

for i, stock in enumerate(result['constituent_stocks'], 1):
    code = stock['code']
    name = stock['name']
    limit_up_count = stock['limit_up_count']
    
    # 获取详细的位置数据
    position_data = analyzer.calculate_position_percentage(code, target_date, lookback_periods=240)
    
    if position_data:
        lowest = position_data['lowest_price']
        highest = position_data['highest_price']
        current = position_data['current_price']
        position_pct = position_data['position_percent']
        
        # 累加位置用于计算平均值
        total_position += position_pct
        valid_count += 1
        
        print(f"{i:<6}{name:<15}{code:<12}{limit_up_count} 次{'':<8}{lowest:<18.2f}{highest:<18.2f}{current:<15.2f}{position_pct:<14.2f}%")

# 计算题材平均位置
if valid_count > 0:
    theme_position = total_position / valid_count
else:
    theme_position = 0

print("="*100)
print("\n大消费题材整体百分比位置")
print("-" * 100)

# 构建求和公式
position_list = [f"{s['position_percent']:.2f}%" for s in result['constituent_stocks']]
formula = " + ".join(position_list)
print(f"\n题材百分比位置 = ({formula}) ÷ {valid_count} = {theme_position:.2f}%")

print("\n" + "="*100)
print("关键结论")
print("="*100)

# 找出位置最高和最低的股票
sorted_stocks = sorted(result['constituent_stocks'], key=lambda x: x['position_percent'], reverse=True)
top3 = sorted_stocks[:3]
bottom1 = sorted_stocks[-1]

# 个股表现分析
top3_str = "、".join([f"{s['name']}（{s['position_percent']:.2f}%）" for s in top3])
print(f"\n1. 个股表现：")
print(f"   {top3_str}为板块核心领涨标的，处于240天区间")
if top3[0]['position_percent'] >= 70:
    print(f"   高位；")
elif top3[0]['position_percent'] >= 50:
    print(f"   中高位；")
else:
    print(f"   中位；")

print(f"   最低的{bottom1['name']}（{bottom1['position_percent']:.2f}%）", end="")
if bottom1['position_percent'] >= 50:
    print("接近区间中值，板块整体呈现分化但中枢偏强；")
elif bottom1['position_percent'] >= 30:
    print("处于区间中下位，板块整体呈现分化；")
else:
    print("处于区间低位，板块整体呈现明显分化；")

# 题材整体分析
print(f"\n2. 题材整体：")
print(f"   大消费板块当前平均位置 {theme_position:.2f}%，", end="")
if theme_position > 50:
    print(f"高于50%中值，处于240天周期内的温和强势区间，板块景气度中等偏上。")
elif theme_position >= 30:
    print(f"处于50%中值附近，处于240天周期内的平衡区间，板块景气度中等。")
else:
    print(f"低于50%中值，处于240天周期内的相对低位区间，板块景气度偏弱，具有上涨空间。")

# 投资建议
print(f"\n3. 投资建议：")
if theme_position >= 70:
    print(f"   题材位于高位区间，建议谨慎，注意风险控制。")
elif theme_position >= 50:
    print(f"   题材位于中高位区间，可适量参与，选择相对低位的个股。")
elif theme_position >= 30:
    print(f"   题材位于中位区间，适合布局，重点关注涨停次数多且位置相对较低的标的。")
else:
    print(f"   题材位于低位区间，具有较大上涨空间，可积极布局龙头股。")

print("\n" + "="*100)
print(f"\n数据日期：{target_date}")
print(f"计算周期：240个交易日")
print(f"成分股数量：{valid_count}只")
print(f"题材平均位置：{theme_position:.2f}%")
print("\n" + "="*100)
