#!/usr/bin/env python3
"""
从akshare获取历史涨停数据并导入数据库
时间范围：2024年7月1日 到 现在（2026年1月28日）
"""

import sys
import os
from datetime import datetime, date, timedelta
import time

# 添加项目路径
sys.path.insert(0, '/home/user/webapp')

from models import Stock, Theme, LimitUpRecord, OperationLog, DailyPrice, db
from stock_info import get_stock_name
import json

# 尝试导入akshare
try:
    import akshare as ak
    print("✅ akshare已导入")
except ImportError:
    print("❌ 请先安装akshare: pip install akshare")
    sys.exit(1)


def get_limit_up_stocks_by_date(trade_date):
    """
    获取指定日期的涨停股票
    
    Args:
        trade_date: 交易日期 (字符串格式 'YYYYMMDD')
    
    Returns:
        DataFrame: 涨停股票数据
    """
    try:
        # 使用akshare获取涨停板数据
        # stock_zt_pool_em: 涨停股池
        df = ak.stock_zt_pool_em(date=trade_date)
        
        if df is None or df.empty:
            print(f"  ⚠️ {trade_date} 无涨停数据")
            return None
        
        print(f"  📊 {trade_date} 获取到 {len(df)} 只涨停股")
        return df
        
    except Exception as e:
        print(f"  ❌ {trade_date} 获取失败: {e}")
        return None


def extract_theme_from_concept(concept_str):
    """
    从概念板块中提取主题材
    
    Args:
        concept_str: 概念板块字符串，例如 "人工智能;机器人;芯片概念"
    
    Returns:
        str: 主要题材
    """
    if not concept_str or concept_str == '-':
        return '其他'
    
    # 分割概念
    concepts = str(concept_str).split(';')
    
    # 优先级题材关键词（按重要性排序）
    priority_themes = [
        '人工智能', 'AI', 'ChatGPT', 'DeepSeek',
        '机器人', '工业母机',
        '新能源汽车', '锂电池', '储能',
        '芯片', '半导体', '集成电路',
        '5G', '6G', '通信', '光通信',
        '医药', '医疗', '生物医药', 'CXO',
        '军工', '航天', '航空',
        '量子', '量子计算', '量子通信',
        '光伏', '风电', '氢能源',
        '数字货币', '区块链', '元宇宙',
        '白酒', '食品', '农业',
        '房地产', '建材', '水泥',
        '有色金属', '黄金', '稀土',
        '化工', '石油', '煤炭',
        '银行', '保险', '证券',
    ]
    
    # 检查优先级题材
    for concept in concepts:
        for theme in priority_themes:
            if theme in concept:
                return theme
    
    # 如果没有匹配到优先级题材，返回第一个概念
    return concepts[0] if concepts else '其他'


def import_limit_up_data_from_akshare(start_date, end_date):
    """
    从akshare导入历史涨停数据
    
    Args:
        start_date: 开始日期 (date对象)
        end_date: 结束日期 (date对象)
    """
    session = db.get_session()
    
    try:
        total_success = 0
        total_error = 0
        total_days = 0
        
        current_date = start_date
        
        while current_date <= end_date:
            # 跳过周末
            if current_date.weekday() >= 5:  # 5=周六, 6=周日
                current_date += timedelta(days=1)
                continue
            
            print(f"\n{'='*60}")
            print(f"📅 处理日期: {current_date}")
            print(f"{'='*60}")
            
            # 格式化日期为akshare需要的格式 'YYYYMMDD'
            date_str = current_date.strftime('%Y%m%d')
            
            # 获取涨停数据
            df = get_limit_up_stocks_by_date(date_str)
            
            if df is None or df.empty:
                current_date += timedelta(days=1)
                continue
            
            total_days += 1
            day_success = 0
            theme_stats = {}
            
            # 遍历每只涨停股票
            for idx, row in df.iterrows():
                try:
                    # 提取数据
                    code = str(row.get('代码', '')).strip()
                    name = str(row.get('名称', '')).strip()
                    
                    # 验证股票代码
                    if not code or len(code) != 6 or not code.isdigit():
                        continue
                    
                    # 提取题材
                    concept = row.get('所属行业', '') or row.get('概念板块', '') or ''
                    theme_name = extract_theme_from_concept(concept)
                    
                    # 提取涨停原因
                    reason = str(row.get('涨停原因类别', '') or row.get('涨停原因', '') or f'{theme_name}板块活跃')
                    if len(reason) > 200:
                        reason = reason[:200]
                    
                    # 提取封板时间
                    limit_up_time = str(row.get('首次封板时间', '09:30'))
                    if limit_up_time == 'nan' or not limit_up_time:
                        limit_up_time = '09:30'
                    
                    # 提取打开次数
                    open_count = 0
                    try:
                        open_count = int(row.get('打开次数', 0) or 0)
                    except:
                        pass
                    
                    # 获取或创建题材
                    theme = session.query(Theme).filter(Theme.name == theme_name).first()
                    if not theme:
                        theme = Theme(name=theme_name, description=f'akshare自动导入的题材：{theme_name}')
                        session.add(theme)
                        session.flush()
                    
                    # 获取或创建股票
                    stock = session.query(Stock).filter(Stock.code == code).first()
                    if not stock:
                        # 如果名称为空，尝试从stock_info获取
                        if not name:
                            name = get_stock_name(code)
                        
                        market = 'SZ' if code.startswith(('0', '3')) else 'SH'
                        stock = Stock(code=code, name=name, market=market)
                        session.add(stock)
                        session.flush()
                    
                    # 检查是否已存在该涨停记录
                    existing = session.query(LimitUpRecord).filter(
                        LimitUpRecord.stock_id == stock.id,
                        LimitUpRecord.theme_id == theme.id,
                        LimitUpRecord.trade_date == current_date
                    ).first()
                    
                    if existing:
                        continue  # 跳过已存在的记录
                    
                    # 创建涨停记录
                    limit_up = LimitUpRecord(
                        stock_id=stock.id,
                        theme_id=theme.id,
                        trade_date=current_date,
                        reason=reason,
                        limit_up_time=limit_up_time,
                        open_count=open_count
                    )
                    session.add(limit_up)
                    
                    day_success += 1
                    theme_stats[theme_name] = theme_stats.get(theme_name, 0) + 1
                    
                except Exception as e:
                    print(f"  ⚠️ 处理股票出错: {code if 'code' in locals() else 'unknown'} - {e}")
                    total_error += 1
                    continue
            
            # 提交当天的数据
            session.commit()
            
            # 显示统计
            print(f"\n  ✅ {current_date} 成功导入 {day_success} 条")
            if theme_stats:
                print(f"  📊 题材分布（前5）:")
                for theme, count in sorted(theme_stats.items(), key=lambda x: x[1], reverse=True)[:5]:
                    print(f"     - {theme}: {count} 只")
            
            total_success += day_success
            
            # 记录操作日志
            if day_success > 0:
                log_details = {
                    'source': 'akshare历史涨停数据导入',
                    'date': current_date.strftime('%Y-%m-%d'),
                    'success_count': day_success,
                    'theme_stats': theme_stats
                }
                operation_log = OperationLog(
                    operation_type='add',
                    target_type='limit_up_record',
                    target_id=None,
                    details=json.dumps(log_details, ensure_ascii=False),
                    ip_address='127.0.0.1'
                )
                session.add(operation_log)
                session.commit()
            
            # 下一天
            current_date += timedelta(days=1)
            
            # 延迟避免请求过快
            time.sleep(0.5)
        
        print(f"\n{'='*60}")
        print(f"🎉 所有数据导入完成！")
        print(f"{'='*60}")
        print(f"📊 统计信息:")
        print(f"   - 处理交易日数: {total_days} 天")
        print(f"   - 成功导入: {total_success} 条")
        print(f"   - 失败: {total_error} 条")
        
        return total_success, total_error
        
    except Exception as e:
        session.rollback()
        print(f"❌ 导入失败: {e}")
        return 0, 0
    finally:
        session.close()


def main():
    """主函数"""
    print("="*60)
    print("     从akshare获取历史涨停数据")
    print("="*60)
    
    # 设置日期范围
    start_date = date(2024, 7, 1)  # 2024年7月1日
    end_date = date.today()  # 今天
    
    print(f"\n📅 日期范围:")
    print(f"   开始: {start_date}")
    print(f"   结束: {end_date}")
    print(f"   跨度: {(end_date - start_date).days + 1} 天")
    
    confirm = input("\n是否开始导入？(y/n): ")
    if confirm.lower() != 'y':
        print("❌ 取消导入")
        return
    
    print("\n🚀 开始导入...\n")
    
    # 执行导入
    success, error = import_limit_up_data_from_akshare(start_date, end_date)
    
    print("\n✅ 完成！")
    print("💡 提示：可以在Web界面查看导入的数据")


if __name__ == '__main__':
    main()
