#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
从文本文件导入大消费题材涨停数据
"""
import sys
import re
from datetime import datetime, date
from models import db, Stock, Theme, LimitUpRecord
from stock_info import get_stock_name

def parse_date_string(date_str):
    """
    解析日期字符串
    支持格式：12月18日、1月2日等
    返回：date对象
    """
    # 去除空格
    date_str = date_str.strip()
    
    # 匹配 "X月X日"
    pattern = r'(\d+)\s*月\s*(\d+)\s*日'
    match = re.match(pattern, date_str)
    
    if not match:
        return None
    
    month = int(match.group(1))
    day = int(match.group(2))
    
    # 当前年份
    current_year = datetime.now().year
    
    # 判断是去年还是今年
    # 如果月份大于当前月份，说明是去年的数据
    current_month = datetime.now().month
    if month > current_month or (month == current_month and day > datetime.now().day):
        year = current_year - 1
    else:
        year = current_year
    
    try:
        return date(year, month, day)
    except ValueError:
        return None

def parse_stock_line(line):
    """
    解析股票行
    格式：天虹股份 | 002419 或 深中华 A|000017
    返回：(股票代码, 股票名称) 或 None
    """
    line = line.strip()
    
    # 匹配 "股票名称 | 代码" 或 "股票名称|代码"
    pattern = r'(.+?)\s*\|\s*(\d{6})'
    match = re.match(pattern, line)
    
    if not match:
        return None
    
    stock_name = match.group(1).strip()
    stock_code = match.group(2).strip()
    
    return (stock_code, stock_name)

def import_text_file(file_path, theme_name="大消费"):
    """
    从文本文件导入数据
    """
    print(f"\n开始导入文本文件: {file_path}")
    print(f"目标题材: {theme_name}\n")
    
    # 打开会话
    session = db.get_session()
    
    try:
        # 获取或创建题材
        theme = session.query(Theme).filter_by(name=theme_name).first()
        if not theme:
            theme = Theme(name=theme_name)
            session.add(theme)
            session.commit()
            print(f"✓ 创建新题材: {theme_name}")
        else:
            print(f"✓ 找到题材: {theme_name} (ID: {theme.id})")
        
        # 统计
        total_processed = 0
        total_imported = 0
        total_skipped = 0
        total_failed = 0
        
        current_date = None
        
        # 读取文件
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # 逐行处理
        for i, line in enumerate(lines, 1):
            line = line.strip()
            
            # 跳过空行
            if not line:
                continue
            
            # 跳过第一行（题材名称）
            if i == 1 and line == theme_name:
                continue
            
            # 尝试解析日期
            parsed_date = parse_date_string(line)
            if parsed_date:
                current_date = parsed_date
                print(f"\n处理日期: {current_date}")
                continue
            
            # 解析股票
            stock_info = parse_stock_line(line)
            if not stock_info:
                continue
            
            if not current_date:
                print(f"警告: 行 {i} 没有找到对应日期，跳过")
                continue
            
            stock_code, stock_name = stock_info
            total_processed += 1
            
            try:
                # 获取或创建股票
                stock = session.query(Stock).filter_by(code=stock_code).first()
                if not stock:
                    # 尝试从akshare获取名称
                    fetched_name = get_stock_name(stock_code)
                    if fetched_name and fetched_name != f"股票{stock_code}":
                        stock_name = fetched_name
                    
                    stock = Stock(code=stock_code, name=stock_name)
                    session.add(stock)
                    session.flush()
                    print(f"  ✓ 创建新股票: {stock_code} {stock_name}")
                
                # 检查是否已存在该记录
                existing = session.query(LimitUpRecord).filter_by(
                    stock_id=stock.id,
                    theme_id=theme.id,
                    trade_date=current_date
                ).first()
                
                if existing:
                    total_skipped += 1
                    continue
                
                # 创建涨停记录
                record = LimitUpRecord(
                    stock_id=stock.id,
                    theme_id=theme.id,
                    trade_date=current_date,
                    limit_up_time="09:30"  # 默认封板时间
                )
                session.add(record)
                
                total_imported += 1
                
                # 每50条提交一次
                if total_imported % 50 == 0:
                    session.commit()
                    print(f"  已导入 {total_imported} 条记录...")
                
            except Exception as e:
                session.rollback()
                total_failed += 1
                print(f"  ✗ 导入失败 {stock_code} {stock_name}: {e}")
        
        # 最终提交
        session.commit()
        
        print(f"\n{'='*60}")
        print(f"导入完成！")
        print(f"{'='*60}")
        print(f"处理记录数: {total_processed}")
        print(f"成功导入: {total_imported}")
        print(f"跳过重复: {total_skipped}")
        print(f"导入失败: {total_failed}")
        print(f"{'='*60}\n")
        
        return {
            'processed': total_processed,
            'imported': total_imported,
            'skipped': total_skipped,
            'failed': total_failed
        }
        
    except Exception as e:
        session.rollback()
        print(f"\n✗ 导入过程出错: {e}")
        import traceback
        traceback.print_exc()
        return None
    finally:
        session.close()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        # 默认使用 uploaded_files 目录下的文件
        file_path = "/home/user/uploaded_files/新建文本文档 (7).txt"
    else:
        file_path = sys.argv[1]
    
    result = import_text_file(file_path)
    
    if result:
        print(f"\n最终统计:")
        print(f"  处理: {result['processed']} 条")
        print(f"  导入: {result['imported']} 条")
        print(f"  跳过: {result['skipped']} 条")
        print(f"  失败: {result['failed']} 条")
