"""
从Excel文件导入涨停数据
"""
import os
import sys
import pandas as pd
from datetime import datetime
import re

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models import db, Stock, Theme, LimitUpRecord
from stock_info import get_stock_name
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def parse_stock_info(text):
    """
    解析股票信息：股票名称 | 股票代码
    例如：天虹股份 | 002419
    
    Returns:
        (股票代码, 股票名称) 或 None
    """
    if pd.isna(text) or not text:
        return None
    
    text = str(text).strip()
    
    # 匹配格式：股票名称 | 股票代码
    match = re.match(r'(.+?)\s*\|\s*(\d{6})', text)
    if match:
        name = match.group(1).strip()
        code = match.group(2).strip()
        return (code, name)
    
    return None


def parse_date(text):
    """
    解析日期：12 月 18 日 -> 2025-12-18
    
    Returns:
        日期字符串 YYYY-MM-DD 或 None
    """
    if pd.isna(text) or not text:
        return None
    
    text = str(text).strip()
    
    # 匹配格式：12 月 18 日
    match = re.match(r'(\d+)\s*月\s*(\d+)\s*日', text)
    if match:
        month = int(match.group(1))
        day = int(match.group(2))
        
        # 判断年份（如果月份大于当前月份，说明是去年的）
        now = datetime.now()
        if month > now.month:
            year = now.year - 1
        else:
            year = now.year
        
        return f"{year}-{month:02d}-{day:02d}"
    
    return None


def import_excel_data(file_path):
    """
    从Excel文件导入数据
    
    Args:
        file_path: Excel文件路径
    """
    logger.info(f"开始读取Excel文件: {file_path}")
    
    # 读取Excel
    df = pd.read_excel(file_path, sheet_name=0)
    
    # 获取所有题材列（每个题材占2列，第一列是题材名，第二列是空的）
    columns = list(df.columns)
    themes_columns = []
    
    for i in range(0, len(columns), 2):
        theme_name = columns[i].strip()
        if theme_name and not theme_name.startswith('Unnamed'):
            themes_columns.append((theme_name, i))
    
    logger.info(f"发现 {len(themes_columns)} 个题材：")
    for theme_name, _ in themes_columns:
        logger.info(f"  - {theme_name}")
    
    # 统计信息
    total_stats = {
        'total_themes': len(themes_columns),
        'success_records': 0,
        'failed_records': 0,
        'skipped_records': 0
    }
    
    # 获取数据库会话
    session = db.get_session()
    
    try:
        # 逐个题材处理
        for theme_name, col_idx in themes_columns:
            logger.info(f"\n处理题材: {theme_name}")
            
            # 获取或创建题材
            theme = session.query(Theme).filter_by(name=theme_name).first()
            if not theme:
                theme = Theme(name=theme_name, description=f"{theme_name}板块")
                session.add(theme)
                session.flush()
                logger.info(f"创建新题材: {theme_name}")
            
            # 获取该题材列的数据
            theme_data = df.iloc[:, col_idx]
            
            current_date = None
            stock_count = 0
            
            # 逐行处理
            for idx, value in enumerate(theme_data):
                if pd.isna(value):
                    continue
                
                value_str = str(value).strip()
                
                # 尝试解析日期
                date_str = parse_date(value_str)
                if date_str:
                    current_date = date_str
                    if stock_count > 0:
                        logger.info(f"  {current_date}: 处理了 {stock_count} 只股票")
                        stock_count = 0
                    continue
                
                # 尝试解析股票信息
                stock_info = parse_stock_info(value_str)
                if stock_info and current_date:
                    code, name = stock_info
                    
                    try:
                        # 获取或创建股票
                        stock = session.query(Stock).filter_by(code=code).first()
                        if not stock:
                            # 根据代码判断市场
                            market = 'SZ' if code.startswith(('0', '3')) else 'SH'
                            stock = Stock(code=code, name=name, market=market)
                            session.add(stock)
                            session.flush()
                        
                        # 检查是否已存在该记录
                        trade_date_obj = datetime.strptime(current_date, '%Y-%m-%d').date()
                        existing = session.query(LimitUpRecord).filter_by(
                            stock_id=stock.id,
                            theme_id=theme.id,
                            trade_date=trade_date_obj
                        ).first()
                        
                        if existing:
                            total_stats['skipped_records'] += 1
                            logger.debug(f"跳过已存在: {code} {name}")
                            continue
                        
                        # 创建涨停记录
                        record = LimitUpRecord(
                            stock_id=stock.id,
                            theme_id=theme.id,
                            trade_date=trade_date_obj,
                            reason=f"{theme_name}板块活跃",
                            limit_up_time='09:30',
                            open_count=0
                        )
                        session.add(record)
                        total_stats['success_records'] += 1
                        stock_count += 1
                        
                    except Exception as e:
                        logger.error(f"导入失败: {code} {name} - {e}")
                        total_stats['failed_records'] += 1
            
            # 提交该题材的数据
            session.commit()
            logger.info(f"✓ {theme_name} 导入完成")
        
        # 输出总结
        logger.info("\n" + "="*80)
        logger.info("导入完成！统计信息：")
        logger.info("="*80)
        logger.info(f"处理题材数: {total_stats['total_themes']}")
        logger.info(f"成功导入记录数: {total_stats['success_records']}")
        logger.info(f"跳过重复记录数: {total_stats['skipped_records']}")
        logger.info(f"失败记录数: {total_stats['failed_records']}")
        logger.info("="*80)
        
    except Exception as e:
        session.rollback()
        logger.error(f"导入过程出错: {e}")
        raise
    finally:
        session.close()


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
    else:
        file_path = '/home/user/uploaded_files/1.xlsx'
    
    if not os.path.exists(file_path):
        logger.error(f"文件不存在: {file_path}")
        sys.exit(1)
    
    import_excel_data(file_path)
