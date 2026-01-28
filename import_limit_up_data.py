#!/usr/bin/env python3
"""
涨停数据导入工具
从RAR压缩包中提取涨停池数据并导入到股票分析系统
"""

import os
import sys
import re
import subprocess
from datetime import datetime

# 添加项目路径
sys.path.insert(0, '/home/user/webapp')

def extract_rar_with_python():
    """尝试使用Python的子进程调用系统工具解压"""
    rar_file = '/home/user/uploaded_files/涨停捕捉.rar'
    extract_dir = '/home/user/extract_data'
    
    os.makedirs(extract_dir, exist_ok=True)
    
    # 尝试多种解压方法
    commands = [
        ['unrar', 'x', '-o+', rar_file, extract_dir],
        ['7z', 'x', f'-o{extract_dir}', rar_file],
        ['unar', '-o', extract_dir, rar_file],
    ]
    
    for cmd in commands:
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                print(f"✅ 成功使用 {cmd[0]} 解压文件")
                return True
            else:
                print(f"⚠️ {cmd[0]} 解压失败: {result.stderr[:100]}")
        except FileNotFoundError:
            print(f"⚠️ {cmd[0]} 未安装")
        except Exception as e:
            print(f"⚠️ {cmd[0]} 执行出错: {e}")
    
    return False


def parse_limit_up_file(file_path):
    """
    解析涨停池文件
    
    文件格式示例：
    sz002896----中大力德----88.7---- +10%----2---机器人|公司主要产品包括精密减速器...
    
    返回格式：
    [
        {
            'code': '002896',
            'name': '中大力德',
            'price': 88.7,
            'change_pct': 10.0,
            'limit_up_time': '09:30',  # 默认值
            'theme': '机器人',
            'reason': '公司主要产品包括精密减速器...'
        },
        ...
    ]
    """
    stocks = []
    
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                
                # 解析格式: code----name----price----change----rank----theme|reason
                parts = line.split('----')
                if len(parts) < 5:
                    continue
                
                try:
                    code = parts[0].strip()
                    # 移除sz/sh前缀
                    code = code.replace('sz', '').replace('sh', '').replace('SZ', '').replace('SH', '')
                    
                    name = parts[1].strip()
                    price_str = parts[2].strip()
                    change_str = parts[3].strip()
                    
                    # 提取价格
                    try:
                        price = float(price_str)
                    except:
                        price = 0.0
                    
                    # 提取涨幅
                    change_match = re.search(r'([+-]?\d+\.?\d*)%', change_str)
                    change_pct = float(change_match.group(1)) if change_match else 10.0
                    
                    # 提取题材和原因
                    theme = ''
                    reason = ''
                    if len(parts) >= 6:
                        theme_reason = parts[5].strip()
                        if '|' in theme_reason:
                            theme_parts = theme_reason.split('|', 1)
                            theme = theme_parts[0].strip()
                            reason = theme_parts[1].strip() if len(theme_parts) > 1 else ''
                        else:
                            # 如果没有|分隔符，尝试从文本中提取题材
                            # 常见题材关键词
                            theme_keywords = ['机器人', 'AI', '人工智能', '新能源', '芯片', '半导体', 
                                            '医药', '医疗', '5G', '通信', '量子', '金融', '电力',
                                            '有色金属', '黄金', '白酒', '地产', '军工', '航天']
                            for keyword in theme_keywords:
                                if keyword in theme_reason:
                                    theme = keyword
                                    break
                            reason = theme_reason
                    
                    # 如果没有提取到题材，使用默认值
                    if not theme:
                        theme = '其他'
                    
                    stock = {
                        'code': code,
                        'name': name,
                        'price': price,
                        'change_pct': change_pct,
                        'limit_up_time': '09:30',  # 默认封板时间
                        'theme': theme,
                        'reason': reason[:200] if reason else f'{theme}板块活跃'  # 限制长度
                    }
                    
                    stocks.append(stock)
                    
                except Exception as e:
                    print(f"⚠️ 解析行出错: {line[:50]}... - {e}")
                    continue
        
        return stocks
        
    except Exception as e:
        print(f"❌ 读取文件失败: {file_path} - {e}")
        return []


def import_to_database(stocks_data, trade_date):
    """
    将股票数据导入到数据库
    
    Args:
        stocks_data: 股票数据列表
        trade_date: 交易日期 (date对象)
    """
    from models import Stock, Theme, LimitUpRecord, OperationLog, db
    import json
    
    session = db.get_session()
    
    try:
        success_count = 0
        error_count = 0
        theme_stats = {}  # 统计每个题材的数量
        
        for stock_data in stocks_data:
            try:
                code = stock_data['code']
                name = stock_data['name']
                theme_name = stock_data['theme']
                
                # 验证股票代码格式
                if not code or len(code) != 6 or not code.isdigit():
                    error_count += 1
                    continue
                
                # 获取或创建题材
                theme = session.query(Theme).filter(Theme.name == theme_name).first()
                if not theme:
                    theme = Theme(name=theme_name, description=f'自动导入的题材：{theme_name}')
                    session.add(theme)
                    session.flush()
                
                # 获取或创建股票
                stock = session.query(Stock).filter(Stock.code == code).first()
                if not stock:
                    market = 'SZ' if code.startswith(('0', '3')) else 'SH'
                    stock = Stock(code=code, name=name, market=market)
                    session.add(stock)
                    session.flush()
                
                # 检查是否已存在该涨停记录
                existing = session.query(LimitUpRecord).filter(
                    LimitUpRecord.stock_id == stock.id,
                    LimitUpRecord.theme_id == theme.id,
                    LimitUpRecord.trade_date == trade_date
                ).first()
                
                if existing:
                    continue  # 跳过已存在的记录
                
                # 创建涨停记录
                limit_up = LimitUpRecord(
                    stock_id=stock.id,
                    theme_id=theme.id,
                    trade_date=trade_date,
                    reason=stock_data['reason'],
                    limit_up_time=stock_data['limit_up_time'],
                    open_count=0
                )
                session.add(limit_up)
                
                success_count += 1
                theme_stats[theme_name] = theme_stats.get(theme_name, 0) + 1
                
            except Exception as e:
                print(f"⚠️ 导入股票 {stock_data.get('code', 'unknown')} 失败: {e}")
                error_count += 1
                continue
        
        # 提交事务
        session.commit()
        
        # 记录操作日志
        if success_count > 0:
            log_details = {
                'source': '批量导入涨停池数据',
                'date': trade_date.strftime('%Y-%m-%d'),
                'success_count': success_count,
                'error_count': error_count,
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
        
        print(f"\n✅ 导入完成！")
        print(f"   成功: {success_count} 条")
        print(f"   失败: {error_count} 条")
        print(f"\n📊 各题材统计:")
        for theme, count in sorted(theme_stats.items(), key=lambda x: x[1], reverse=True):
            print(f"   - {theme}: {count} 只")
        
        return success_count, error_count
        
    except Exception as e:
        session.rollback()
        print(f"❌ 数据库操作失败: {e}")
        return 0, len(stocks_data)
    finally:
        session.close()


def process_all_files(extract_dir):
    """处理所有涨停池文件"""
    
    if not os.path.exists(extract_dir):
        print(f"❌ 目录不存在: {extract_dir}")
        return
    
    # 查找所有涨停池文件
    limit_up_files = []
    for root, dirs, files in os.walk(extract_dir):
        for file in files:
            if '涨停池' in file and file.endswith('.txt'):
                file_path = os.path.join(root, file)
                limit_up_files.append(file_path)
    
    if not limit_up_files:
        print("❌ 未找到涨停池文件")
        return
    
    print(f"📁 找到 {len(limit_up_files)} 个涨停池文件\n")
    
    total_success = 0
    total_error = 0
    
    for file_path in sorted(limit_up_files):
        filename = os.path.basename(file_path)
        print(f"\n{'='*60}")
        print(f"📄 处理文件: {filename}")
        print(f"{'='*60}")
        
        # 从文件名提取日期: 2025-02-20_涨停池.txt
        date_match = re.search(r'(\d{4})-(\d{2})-(\d{2})', filename)
        if not date_match:
            print(f"⚠️ 无法从文件名提取日期: {filename}")
            continue
        
        try:
            year, month, day = map(int, date_match.groups())
            trade_date = datetime(year, month, day).date()
        except:
            print(f"⚠️ 日期格式错误: {filename}")
            continue
        
        # 解析文件
        stocks = parse_limit_up_file(file_path)
        print(f"📊 解析到 {len(stocks)} 只股票")
        
        if not stocks:
            print("⚠️ 文件为空或解析失败")
            continue
        
        # 导入数据库
        success, error = import_to_database(stocks, trade_date)
        total_success += success
        total_error += error
    
    print(f"\n{'='*60}")
    print(f"🎉 所有文件处理完成！")
    print(f"{'='*60}")
    print(f"✅ 总成功: {total_success} 条")
    print(f"❌ 总失败: {total_error} 条")


def main():
    """主函数"""
    print("="*60)
    print("     涨停数据批量导入工具")
    print("="*60)
    
    # 第一步：解压RAR文件
    print("\n📦 步骤1: 解压RAR文件...")
    if not extract_rar_with_python():
        print("\n❌ 无法解压RAR文件！")
        print("💡 建议：请手动解压文件到 /home/user/extract_data 目录")
        print("   然后重新运行此脚本")
        return
    
    # 第二步：处理所有文件
    print("\n📊 步骤2: 处理涨停池数据...")
    extract_dir = '/home/user/extract_data'
    process_all_files(extract_dir)
    
    print("\n✅ 完成！")


if __name__ == '__main__':
    main()
