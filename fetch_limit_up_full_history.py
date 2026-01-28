"""
批量导入2024年7月至今的所有涨停数据
支持断点续传
"""
import os
import sys
from datetime import datetime, timedelta
import time
import json

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fetch_limit_up_history import get_limit_up_data, import_limit_up_data, get_trading_dates
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 进度文件
PROGRESS_FILE = 'import_progress.json'


def load_progress():
    """加载导入进度"""
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, 'r') as f:
            return json.load(f)
    return {'last_date': None, 'imported_dates': [], 'stats': {}}


def save_progress(progress):
    """保存导入进度"""
    with open(PROGRESS_FILE, 'w') as f:
        json.dump(progress, f, ensure_ascii=False, indent=2)


def import_by_month(year, month):
    """
    按月导入数据
    
    Args:
        year: 年份
        month: 月份
        
    Returns:
        导入统计
    """
    # 计算月份的起止日期
    start_date = f"{year}-{month:02d}-01"
    
    # 计算下个月的第一天
    if month == 12:
        next_year = year + 1
        next_month = 1
    else:
        next_year = year
        next_month = month + 1
    
    # 月末日期
    next_month_first = datetime(next_year, next_month, 1)
    end_date = (next_month_first - timedelta(days=1)).strftime('%Y-%m-%d')
    
    logger.info(f"\n{'='*80}")
    logger.info(f"开始导入 {year}年{month}月 数据 ({start_date} 至 {end_date})")
    logger.info(f"{'='*80}")
    
    # 获取交易日列表
    trading_dates = get_trading_dates(start_date, end_date)
    
    month_stats = {
        'total_dates': len(trading_dates),
        'success_dates': 0,
        'failed_dates': 0,
        'total_stocks': 0,
        'success_stocks': 0,
        'failed_stocks': 0,
        'skipped_stocks': 0
    }
    
    # 加载进度
    progress = load_progress()
    imported_dates = set(progress.get('imported_dates', []))
    
    # 逐日导入
    for i, date_str in enumerate(trading_dates, 1):
        try:
            # 检查是否已导入
            if date_str in imported_dates:
                logger.info(f"[{i}/{len(trading_dates)}] {date_str}: ✓ 已导入，跳过")
                continue
            
            logger.info(f"[{i}/{len(trading_dates)}] 处理日期: {date_str}")
            
            # 获取涨停数据
            stocks = get_limit_up_data(date_str)
            
            if stocks:
                # 转换日期格式为 YYYY-MM-DD
                import_date = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:]}"
                
                # 导入数据
                result = import_limit_up_data(import_date, stocks)
                
                month_stats['success_dates'] += 1
                month_stats['total_stocks'] += result['total']
                month_stats['success_stocks'] += result['success']
                month_stats['failed_stocks'] += result['failed']
                month_stats['skipped_stocks'] += result['skipped']
                
                logger.info(f"✓ {date_str}: {result['success']} 成功, {result['skipped']} 跳过, {result['failed']} 失败")
                
                # 标记为已导入
                imported_dates.add(date_str)
                progress['imported_dates'] = list(imported_dates)
                progress['last_date'] = date_str
                save_progress(progress)
                
            else:
                logger.warning(f"✗ {date_str}: 无涨停数据")
                # 即使无数据也标记为已处理
                imported_dates.add(date_str)
                progress['imported_dates'] = list(imported_dates)
                save_progress(progress)
            
            # 休息一下，避免请求过快
            time.sleep(0.5)
            
        except Exception as e:
            logger.error(f"处理 {date_str} 时出错: {e}")
            month_stats['failed_dates'] += 1
            continue
    
    # 输出月份统计
    logger.info(f"\n{year}年{month}月 导入完成:")
    logger.info(f"  - 处理日期数: {month_stats['total_dates']}")
    logger.info(f"  - 成功: {month_stats['success_dates']}, 失败: {month_stats['failed_dates']}")
    logger.info(f"  - 导入股票记录数: {month_stats['total_stocks']}")
    logger.info(f"  - 成功: {month_stats['success_stocks']}, 跳过: {month_stats['skipped_stocks']}, 失败: {month_stats['failed_stocks']}")
    
    return month_stats


def main():
    """主函数"""
    logger.info("="*80)
    logger.info("开始批量导入历史涨停数据")
    logger.info("时间范围: 2024年7月 至 今")
    logger.info("="*80)
    
    # 获取当前日期
    now = datetime.now()
    
    # 生成要导入的月份列表
    months_to_import = []
    
    # 2024年7月到12月
    for month in range(7, 13):
        months_to_import.append((2024, month))
    
    # 2025年1月到当前月
    for month in range(1, now.month + 1):
        months_to_import.append((2025, month))
    
    # 2026年1月到当前月（如果是2026年）
    if now.year >= 2026:
        for month in range(1, now.month + 1):
            months_to_import.append((2026, month))
    
    logger.info(f"共需要处理 {len(months_to_import)} 个月的数据")
    
    # 统计信息
    total_stats = {
        'total_months': len(months_to_import),
        'success_months': 0,
        'total_dates': 0,
        'success_dates': 0,
        'failed_dates': 0,
        'total_stocks': 0,
        'success_stocks': 0,
        'failed_stocks': 0,
        'skipped_stocks': 0
    }
    
    # 逐月导入
    for i, (year, month) in enumerate(months_to_import, 1):
        try:
            logger.info(f"\n处理第 {i}/{len(months_to_import)} 个月: {year}年{month}月")
            
            month_stats = import_by_month(year, month)
            
            total_stats['success_months'] += 1
            total_stats['total_dates'] += month_stats['total_dates']
            total_stats['success_dates'] += month_stats['success_dates']
            total_stats['failed_dates'] += month_stats['failed_dates']
            total_stats['total_stocks'] += month_stats['total_stocks']
            total_stats['success_stocks'] += month_stats['success_stocks']
            total_stats['failed_stocks'] += month_stats['failed_stocks']
            total_stats['skipped_stocks'] += month_stats['skipped_stocks']
            
        except Exception as e:
            logger.error(f"处理 {year}年{month}月 时出错: {e}")
            continue
    
    # 输出总结
    logger.info("\n" + "="*80)
    logger.info("全部导入完成！总体统计信息：")
    logger.info("="*80)
    logger.info(f"处理月份数: {total_stats['total_months']}")
    logger.info(f"  - 成功: {total_stats['success_months']}")
    logger.info(f"\n处理日期数: {total_stats['total_dates']}")
    logger.info(f"  - 成功: {total_stats['success_dates']}")
    logger.info(f"  - 失败: {total_stats['failed_dates']}")
    logger.info(f"\n处理股票记录数: {total_stats['total_stocks']}")
    logger.info(f"  - 成功导入: {total_stats['success_stocks']}")
    logger.info(f"  - 跳过重复: {total_stats['skipped_stocks']}")
    logger.info(f"  - 导入失败: {total_stats['failed_stocks']}")
    logger.info("="*80)
    
    # 清理进度文件
    if os.path.exists(PROGRESS_FILE):
        os.remove(PROGRESS_FILE)
        logger.info("已清理进度文件")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        logger.info("\n用户中断操作，进度已保存，可以稍后继续")
    except Exception as e:
        logger.error(f"发生错误: {e}")
        import traceback
        traceback.print_exc()
