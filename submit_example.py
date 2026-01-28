"""
数据提交示例脚本

演示如何使用API提交股票涨停数据
"""
import requests
import json

# API基础地址
API_BASE = "http://localhost:5000"
# 如果使用在线地址：
# API_BASE = "https://5000-i1m9fpfr5tksghv87yttz-a402f90a.sandbox.novita.ai"


def submit_limit_up_data(date, theme, stocks):
    """
    提交涨停数据
    
    Args:
        date: 日期，格式 YYYY-MM-DD
        theme: 题材名称
        stocks: 股票列表 [{"code": "000001", "name": "平安银行", ...}, ...]
    
    Returns:
        dict: API响应结果
    """
    url = f"{API_BASE}/api/data/submit"
    
    data = {
        "date": date,
        "theme": theme,
        "stocks": stocks
    }
    
    response = requests.post(url, json=data)
    return response.json()


def add_theme(name, description=""):
    """添加题材"""
    url = f"{API_BASE}/api/data/add-theme"
    data = {"name": name, "description": description}
    response = requests.post(url, json=data)
    return response.json()


def add_stock(code, name, market="SZ"):
    """添加股票"""
    url = f"{API_BASE}/api/data/add-stock"
    data = {"code": code, "name": name, "market": market}
    response = requests.post(url, json=data)
    return response.json()


def get_themes():
    """获取所有题材"""
    url = f"{API_BASE}/api/data/themes"
    response = requests.get(url)
    return response.json()


def get_stocks():
    """获取所有股票"""
    url = f"{API_BASE}/api/data/stocks"
    response = requests.get(url)
    return response.json()


def print_json(data):
    """格式化打印JSON"""
    print(json.dumps(data, ensure_ascii=False, indent=2))


# ============ 使用示例 ============

def example_1_add_theme():
    """示例1: 添加新题材"""
    print("\n" + "="*60)
    print("示例1: 添加新题材 - 元宇宙")
    print("="*60)
    
    result = add_theme("元宇宙", "元宇宙相关概念")
    print_json(result)


def example_2_submit_data():
    """示例2: 提交涨停数据"""
    print("\n" + "="*60)
    print("示例2: 提交2026-01-28的人工智能题材涨停数据")
    print("="*60)
    
    stocks_data = [
        {
            "code": "600519",
            "name": "贵州茅台",
            "reason": "AI+白酒概念",
            "limit_up_time": "09:30",
            "open_count": 0
        },
        {
            "code": "000858",
            "name": "五粮液",
            "reason": "AI赋能传统产业",
            "limit_up_time": "10:00",
            "open_count": 1
        }
    ]
    
    result = submit_limit_up_data("2026-01-28", "人工智能", stocks_data)
    print_json(result)


def example_3_batch_submit():
    """示例3: 批量提交多个题材的数据"""
    print("\n" + "="*60)
    print("示例3: 批量提交多个题材的涨停数据")
    print("="*60)
    
    # 量子计算题材
    quantum_stocks = [
        {
            "code": "300768",
            "name": "迪普科技",
            "reason": "量子通信板块活跃"
        },
        {
            "code": "688027",
            "name": "国盾量子",
            "reason": "量子科技龙头"
        }
    ]
    
    # 新能源题材
    new_energy_stocks = [
        {
            "code": "300750",
            "name": "宁德时代",
            "reason": "电池技术突破"
        },
        {
            "code": "002594",
            "name": "比亚迪",
            "reason": "新能源汽车销量创新高"
        }
    ]
    
    # 提交量子计算
    print("\n提交量子计算题材...")
    result1 = submit_limit_up_data("2026-01-28", "量子计算", quantum_stocks)
    print_json(result1)
    
    # 提交新能源
    print("\n提交新能源汽车题材...")
    result2 = submit_limit_up_data("2026-01-28", "新能源汽车", new_energy_stocks)
    print_json(result2)


def example_4_query_data():
    """示例4: 查询已提交的数据"""
    print("\n" + "="*60)
    print("示例4: 查询已提交的题材和股票")
    print("="*60)
    
    # 查询所有题材
    print("\n所有题材:")
    themes = get_themes()
    if themes['success']:
        for theme in themes['data'][:5]:  # 只显示前5个
            print(f"  - {theme['name']}: {theme['description']}")
    
    # 查询所有股票
    print("\n所有股票（前10个）:")
    stocks = get_stocks()
    if stocks['success']:
        for stock in stocks['data'][:10]:
            print(f"  - {stock['code']} {stock['name']} ({stock['market']})")


def example_5_real_scenario():
    """示例5: 真实场景 - 每日涨停数据录入"""
    print("\n" + "="*60)
    print("示例5: 真实场景 - 每日涨停数据录入")
    print("="*60)
    
    # 假设这是今天采集到的涨停数据
    today = "2026-01-28"
    
    # AI题材涨停股
    ai_data = {
        "date": today,
        "theme": "人工智能",
        "stocks": [
            {"code": "300033", "name": "同花顺", "reason": "AI金融应用", "limit_up_time": "09:35"},
            {"code": "002230", "name": "科大讯飞", "reason": "AI语音龙头", "limit_up_time": "09:30"},
            {"code": "688111", "name": "金山办公", "reason": "AI办公软件", "limit_up_time": "10:00"}
        ]
    }
    
    print(f"\n录入 {today} 的人工智能题材涨停数据...")
    result = requests.post(f"{API_BASE}/api/data/submit", json=ai_data)
    print_json(result.json())
    
    # 验证数据
    print("\n验证: 查询人工智能题材成分股...")
    verify_url = f"{API_BASE}/api/theme/top-stocks"
    params = {"theme": "人工智能", "date": today, "top_n": 10}
    verify_result = requests.get(verify_url, params=params)
    
    if verify_result.json()['success']:
        stocks = verify_result.json()['data']['stocks']
        print(f"\n找到 {len(stocks)} 只成分股:")
        for i, stock in enumerate(stocks, 1):
            print(f"  {i}. {stock['code']} {stock['name']} - 涨停{stock['limit_up_count']}次")


def main():
    """主函数"""
    print("\n" + "="*60)
    print(" 股票数据提交示例")
    print("="*60)
    
    try:
        # 检查API是否可用
        response = requests.get(f"{API_BASE}/health", timeout=5)
        if response.status_code == 200:
            print(f"\n✓ API服务正常: {API_BASE}")
        else:
            print(f"\n✗ API服务异常")
            return
    except Exception as e:
        print(f"\n✗ 无法连接到API: {e}")
        print(f"  请确保服务已启动: python app.py")
        return
    
    # 运行示例（选择要运行的示例）
    # example_1_add_theme()
    # example_2_submit_data()
    # example_3_batch_submit()
    # example_4_query_data()
    example_5_real_scenario()
    
    print("\n" + "="*60)
    print(" 示例运行完成！")
    print("="*60)
    print("\n提示:")
    print("  - 可以在main()函数中选择运行不同的示例")
    print("  - 修改API_BASE变量切换本地/在线环境")
    print("  - 参考 DATA_SUBMIT_API.md 了解完整API文档")


if __name__ == '__main__':
    main()
