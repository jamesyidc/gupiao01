"""
股票数据研究系统 - 使用示例

演示如何使用API进行股票和题材分析
"""
import requests
import json
from datetime import datetime

# API 基础URL
BASE_URL = "http://localhost:5000"
# 如果使用在线地址，请使用：
# BASE_URL = "https://5000-i1m9fpfr5tksghv87yttz-a402f90a.sandbox.novita.ai"


def print_json(data):
    """格式化打印JSON数据"""
    print(json.dumps(data, ensure_ascii=False, indent=2))


def example_1_get_theme_stocks():
    """示例1：获取题材成分股"""
    print("\n" + "="*60)
    print("示例1：获取'人工智能'题材的前15只成分股")
    print("="*60)
    
    response = requests.get(f"{BASE_URL}/api/theme/top-stocks", params={
        "theme": "人工智能",
        "date": "2026-01-27",
        "top_n": 15
    })
    
    result = response.json()
    if result['success']:
        data = result['data']
        print(f"\n题材: {data['theme']}")
        print(f"查询日期: {data['date']}")
        print(f"找到 {data['total_count']} 只成分股:\n")
        
        for i, stock in enumerate(data['stocks'], 1):
            print(f"{i:2d}. {stock['code']:8s} {stock['name']:12s} - 涨停 {stock['limit_up_count']} 次")
    else:
        print(f"错误: {result['error']}")


def example_2_get_stock_position():
    """示例2：查询个股位置百分比"""
    print("\n" + "="*60)
    print("示例2：查询个股000001的位置百分比")
    print("="*60)
    
    response = requests.get(f"{BASE_URL}/api/stock/position", params={
        "code": "000001",
        "date": "2026-01-27"
    })
    
    result = response.json()
    if result['success']:
        data = result['data']
        print(f"\n股票信息:")
        print(f"  代码: {data['stock_code']}")
        print(f"  名称: {data['stock_name']}")
        print(f"  当前价格: {data['current_price']:.2f} 元")
        print(f"  最低价格: {data['lowest_price']:.2f} 元（过去{data['available_periods']}个交易日）")
        print(f"  最高价格: {data['highest_price']:.2f} 元")
        print(f"  位置百分比: {data['position_percent']:.2f}%")
        
        # 位置分析
        pos = data['position_percent']
        if pos < 20:
            analysis = "处于底部区域，相对安全"
        elif pos < 40:
            analysis = "处于中低位，仍有上涨空间"
        elif pos < 60:
            analysis = "处于中位，需要观察"
        elif pos < 80:
            analysis = "处于中高位，需谨慎"
        else:
            analysis = "处于顶部区域，风险较高"
        
        print(f"\n  分析: {analysis}")
    else:
        print(f"错误: {result['error']}")


def example_3_get_theme_position():
    """示例3：查询题材位置百分比"""
    print("\n" + "="*60)
    print("示例3：查询'人工智能'题材的整体位置")
    print("="*60)
    
    response = requests.get(f"{BASE_URL}/api/theme/position", params={
        "theme": "人工智能",
        "date": "2026-01-27"
    })
    
    result = response.json()
    if result['success']:
        data = result['data']
        print(f"\n题材: {data['theme_name']}")
        print(f"成分股数量: {data['constituent_count']}")
        print(f"题材位置百分比: {data['theme_position_percent']:.2f}%")
        
        print(f"\n前10只成分股位置:")
        for i, stock in enumerate(data['constituent_stocks'][:10], 1):
            print(f"{i:2d}. {stock['code']:8s} {stock['name']:12s} - "
                  f"位置: {stock['position_percent']:5.2f}%, "
                  f"涨停: {stock['limit_up_count']}次")
    else:
        print(f"错误: {result['error']}")


def example_4_compare_analysis():
    """示例4：比较个股与题材的相对强弱"""
    print("\n" + "="*60)
    print("示例4：分析个股000001相对于'人工智能'题材的强弱")
    print("="*60)
    
    response = requests.get(f"{BASE_URL}/api/analysis/compare", params={
        "code": "000001",
        "theme": "人工智能",
        "date": "2026-01-27"
    })
    
    result = response.json()
    if result['success']:
        data = result['data']
        
        stock_info = data['stock_info']
        theme_info = data['theme_info']
        comparison = data['comparison']
        
        print(f"\n【个股信息】")
        print(f"  代码: {stock_info['stock_code']}")
        print(f"  名称: {stock_info['stock_name']}")
        print(f"  当前价格: {stock_info['current_price']:.2f} 元")
        print(f"  位置百分比: {stock_info['position_percent']:.2f}%")
        
        print(f"\n【题材信息】")
        print(f"  题材: {theme_info['theme_name']}")
        print(f"  成分股数量: {theme_info['constituent_count']}")
        print(f"  题材位置百分比: {theme_info['theme_position_percent']:.2f}%")
        
        print(f"\n【比较分析】")
        print(f"  是否为成分股: {'是' if comparison['is_constituent_stock'] else '否'}")
        print(f"  位置差异: {comparison['position_difference']:+.2f}%")
        print(f"  相对强弱: {comparison['relative_strength']}")
        
        # 投资建议
        print(f"\n【分析建议】")
        if comparison['relative_strength'] == '强于题材':
            print("  该股票表现强于题材整体，可能是板块龙头")
            print("  建议：关注后续走势，注意回调风险")
        elif comparison['relative_strength'] == '弱于题材':
            print("  该股票表现弱于题材整体，可能存在补涨机会")
            print("  建议：如果基本面良好，可关注补涨机会")
        else:
            print("  该股票与题材走势同步")
            print("  建议：观察题材热度变化")
    else:
        print(f"错误: {result['error']}")


def example_5_batch_compare():
    """示例5：批量比较多只股票"""
    print("\n" + "="*60)
    print("示例5：批量分析'人工智能'题材中的多只股票")
    print("="*60)
    
    # 先获取题材成分股
    response = requests.get(f"{BASE_URL}/api/theme/top-stocks", params={
        "theme": "人工智能",
        "date": "2026-01-27",
        "top_n": 5
    })
    
    result = response.json()
    if not result['success']:
        print(f"错误: {result['error']}")
        return
    
    stocks = result['data']['stocks']
    
    print(f"\n正在分析前5只成分股...\n")
    print(f"{'排名':4s} {'代码':8s} {'名称':12s} {'个股位置':8s} {'题材位置':8s} {'差异':8s} {'强弱':10s}")
    print("-" * 80)
    
    for i, stock in enumerate(stocks, 1):
        # 查询每只股票的比较分析
        response = requests.get(f"{BASE_URL}/api/analysis/compare", params={
            "code": stock['code'],
            "theme": "人工智能",
            "date": "2026-01-27"
        })
        
        if response.json()['success']:
            data = response.json()['data']
            stock_pos = data['stock_info']['position_percent']
            theme_pos = data['theme_info']['theme_position_percent']
            diff = data['comparison']['position_difference']
            strength = data['comparison']['relative_strength']
            
            print(f"{i:4d} {stock['code']:8s} {stock['name']:12s} "
                  f"{stock_pos:7.2f}% {theme_pos:7.2f}% "
                  f"{diff:+7.2f}% {strength:10s}")


def main():
    """主函数"""
    print("\n" + "="*60)
    print(" 股票数据研究系统 - API使用示例")
    print("="*60)
    
    try:
        # 检查服务是否可用
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            print(f"\n✓ API服务运行正常")
            print(f"  服务地址: {BASE_URL}")
        else:
            print(f"\n✗ API服务异常")
            return
    except Exception as e:
        print(f"\n✗ 无法连接到API服务: {e}")
        print(f"  请确保服务已启动: python app.py")
        return
    
    # 运行示例
    example_1_get_theme_stocks()
    example_2_get_stock_position()
    example_3_get_theme_position()
    example_4_compare_analysis()
    example_5_batch_compare()
    
    print("\n" + "="*60)
    print(" 示例运行完成！")
    print("="*60)


if __name__ == '__main__':
    main()
