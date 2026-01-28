"""
测试导入最近几天的涨停数据
"""
import os
import sys
from datetime import datetime, timedelta

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fetch_limit_up_history import get_limit_up_data, import_limit_up_data, classify_theme
from app import app
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def test_recent_days(days=5):
    """测试导入最近几天的数据"""
    logger.info(f"测试导入最近 {days} 天的涨停数据")
    
    total_success = 0
    total_skipped = 0
    
    for i in range(days):
        date = datetime.now() - timedelta(days=i)
        date_str_yyyymmdd = date.strftime('%Y%m%d')
        date_str_yyyy_mm_dd = date.strftime('%Y-%m-%d')
        
        logger.info(f"\n处理日期: {date_str_yyyy_mm_dd}")
        
        # 获取涨停数据
        stocks = get_limit_up_data(date_str_yyyymmdd)
        
        if stocks:
            logger.info(f"获取到 {len(stocks)} 只涨停股票")
            
            # 显示前3只股票
            for stock in stocks[:3]:
                theme = classify_theme(stock['reason'])
                logger.info(f"  {stock['code']} {stock['name']} - {theme} ({stock['reason']})")
            
            # 导入数据
            result = import_limit_up_data(date_str_yyyy_mm_dd, stocks)
            total_success += result['success']
            total_skipped += result['skipped']
            
            logger.info(f"导入结果: 成功 {result['success']}, 跳过 {result['skipped']}, 失败 {result['failed']}")
        else:
            logger.warning(f"{date_str_yyyy_mm_dd} 无涨停数据（可能是周末或节假日）")
    
    logger.info(f"\n总计：成功导入 {total_success} 条，跳过 {total_skipped} 条")


if __name__ == '__main__':
    test_recent_days(5)
