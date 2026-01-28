"""
从akshare获取历史涨停数据并导入数据库
时间范围：2024年7月至今
"""
import os
import sys
from datetime import datetime, timedelta
from typing import List, Dict, Set
import time

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


# 题材关键词映射
THEME_KEYWORDS = {
    'AI': ['AI', '人工智能', 'ChatGPT', 'GPT', '大模型', 'AIGC', '算力'],
    '芯片': ['芯片', '半导体', '集成电路', 'IC', '晶圆', '存储芯片', 'GPU'],
    '新能源': ['新能源', '锂电', '电池', '光伏', '风电', '储能', '充电桩'],
    '医药': ['医药', '医疗', '生物', '疫苗', '创新药', 'CXO', '医美'],
    '军工': ['军工', '国防', '航天', '航空', '导弹', '雷达', '无人机'],
    '5G': ['5G', '通信', '物联网', 'IOT', '基站', '光纤', '光模块'],
    '新材料': ['新材料', '碳纤维', '石墨烯', '第三代半导体', '钛合金'],
    '汽车': ['汽车', '新能源车', '智能驾驶', '自动驾驶', '车联网'],
    '黄金': ['黄金', '黄金股', '黄金概念', '贵金属'],
    '有色': ['有色金属', '稀土', '钴', '锂', '铜', '铝', '锌'],
    '机器人': ['机器人', '工业机器人', '人形机器人', '服务机器人'],
    '数字经济': ['数字经济', '数字货币', '区块链', '元宇宙', 'Web3'],
    '网络安全': ['网络安全', '信息安全', '数据安全', '网安'],
    '消费': ['消费', '白酒', '食品', '家电', '零售', '百货'],
    '地产': ['地产', '房地产', '建筑', '水泥', '装修'],
    '金融': ['券商', '银行', '保险', '信托', '金融'],
    '游戏': ['游戏', '手游', '电竞', '云游戏'],
    '传媒': ['传媒', '影视', '广告', '出版', '教育'],
    '旅游': ['旅游', '酒店', '景区', '免税'],
    '农业': ['农业', '种业', '养殖', '化肥', '农药'],
}


def classify_theme(reason: str) -> str:
    """
    根据涨停原因推断题材分类
    
    Args:
        reason: 涨停原因描述
        
    Returns:
        题材名称
    """
    if not reason:
        return "其他"
    
    reason_upper = reason.upper()
    
    # 按关键词匹配
    for theme, keywords in THEME_KEYWORDS.items():
        for keyword in keywords:
            if keyword.upper() in reason_upper:
                return theme
    
    # 如果没有匹配到，返回"其他"
    return "其他"


def get_limit_up_data(date_str: str) -> List[Dict]:
    """
    获取指定日期的涨停数据
    
    Args:
        date_str: 日期字符串，格式：YYYYMMDD
        
    Returns:
        涨停股票列表
    """
    try:
        import akshare as ak
        logger.info(f"正在获取 {date_str} 的涨停数据...")
        
        # 获取涨停数据
        # ak.stock_zt_pool_em 获取当日涨停池
        # ak.stock_zt_pool_previous_em 获取历史涨停池
        df = ak.stock_zt_pool_previous_em(date=date_str)
        
        if df is None or df.empty:
            logger.warning(f"{date_str} 没有涨停数据")
            return []
        
        logger.info(f"{date_str} 共有 {len(df)} 只涨停股票")
        
        # 转换为字典列表
        result = []
        for _, row in df.iterrows():
            try:
                # 获取股票代码（去掉市场前缀）
                code = str(row.get('代码', '')).strip()
                if not code or len(code) != 6:
                    continue
                
                # 获取股票名称
                name = str(row.get('名称', '')).strip()
                if not name:
                    name = get_stock_name(code)
                
                # 获取涨停原因
                reason = str(row.get('涨停原因类别', row.get('所属行业', '')))
                
                # 获取封板时间
                limit_up_time = str(row.get('首次封板时间', row.get('最后封板时间', '09:30'))).strip()
                if not limit_up_time or limit_up_time == 'nan':
                    limit_up_time = '09:30'
                
                # 获取打开次数
                try:
                    open_count = int(row.get('打开次数', 0))
                except:
                    open_count = 0
                
                result.append({
                    'code': code,
                    'name': name,
                    'reason': reason,
                    'limit_up_time': limit_up_time,
                    'open_count': open_count
                })
            except Exception as e:
                logger.error(f"处理股票数据失败: {row}, 错误: {e}")
                continue
        
        return result
        
    except Exception as e:
        logger.error(f"获取 {date_str} 涨停数据失败: {e}")
        return []


def import_limit_up_data(date_str: str, stocks: List[Dict]) -> Dict:
    """
    导入涨停数据到数据库
    
    Args:
        date_str: 日期字符串，格式：YYYY-MM-DD
        stocks: 涨停股票列表
        
    Returns:
        导入结果统计
    """
    if not stocks:
        return {'total': 0, 'success': 0, 'failed': 0, 'skipped': 0}
    
    success_count = 0
    failed_count = 0
    skipped_count = 0
    
    # 获取数据库会话
    session = db.get_session()
    
    try:
        for stock_data in stocks:
            try:
                code = stock_data['code']
                name = stock_data['name']
                reason = stock_data['reason']
                limit_up_time = stock_data['limit_up_time']
                open_count = stock_data['open_count']
                
                # 根据原因推断题材
                theme_name = classify_theme(reason)
                
                # 获取或创建题材
                theme = session.query(Theme).filter_by(name=theme_name).first()
                if not theme:
                    theme = Theme(name=theme_name, description=f"{theme_name}板块")
                    session.add(theme)
                    session.flush()
                    logger.info(f"创建新题材: {theme_name}")
                
                # 获取或创建股票
                stock = session.query(Stock).filter_by(code=code).first()
                if not stock:
                    # 根据代码判断市场
                    market = 'SZ' if code.startswith(('0', '3')) else 'SH'
                    stock = Stock(code=code, name=name, market=market)
                    session.add(stock)
                    session.flush()
                    logger.debug(f"创建新股票: {code} {name}")
                
                # 检查是否已存在该记录
                # 将日期字符串转换为date对象
                from datetime import date as date_type
                trade_date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
                
                existing = session.query(LimitUpRecord).filter_by(
                    stock_id=stock.id,
                    theme_id=theme.id,
                    trade_date=trade_date_obj
                ).first()
                
                if existing:
                    skipped_count += 1
                    logger.debug(f"跳过已存在的记录: {code} {name} - {theme_name}")
                    continue
                
                # 创建涨停记录
                # 将日期字符串转换为date对象
                from datetime import date as date_type
                trade_date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
                
                record = LimitUpRecord(
                    stock_id=stock.id,
                    theme_id=theme.id,
                    trade_date=trade_date_obj,
                    reason=reason,
                    limit_up_time=limit_up_time,
                    open_count=open_count
                )
                session.add(record)
                success_count += 1
                logger.debug(f"导入成功: {code} {name} - {theme_name}")
                
            except Exception as e:
                logger.error(f"导入失败: {stock_data}, 错误: {e}")
                failed_count += 1
                continue
        
        # 提交事务
        session.commit()
        logger.info(f"{date_str} 导入完成: 成功 {success_count}, 跳过 {skipped_count}, 失败 {failed_count}")
        
    except Exception as e:
        session.rollback()
        logger.error(f"提交事务失败: {e}")
        return {'total': len(stocks), 'success': 0, 'failed': len(stocks), 'skipped': 0}
    finally:
        session.close()
    
    return {
        'total': len(stocks),
        'success': success_count,
        'failed': failed_count,
        'skipped': skipped_count
    }


def get_trading_dates(start_date: str, end_date: str) -> List[str]:
    """
    生成交易日列表（简化版，生成所有工作日）
    实际应该调用交易日历API
    
    Args:
        start_date: 开始日期 YYYY-MM-DD
        end_date: 结束日期 YYYY-MM-DD
        
    Returns:
        交易日列表 YYYYMMDD
    """
    dates = []
    current = datetime.strptime(start_date, '%Y-%m-%d')
    end = datetime.strptime(end_date, '%Y-%m-%d')
    
    while current <= end:
        # 跳过周末
        if current.weekday() < 5:  # 0-4 是周一到周五
            dates.append(current.strftime('%Y%m%d'))
        current += timedelta(days=1)
    
    return dates


def main():
    """主函数"""
    logger.info("="*80)
    logger.info("开始获取历史涨停数据")
    logger.info("="*80)
    
    # 设置时间范围：2024年7月1日到今天
    start_date = '2024-07-01'
    end_date = datetime.now().strftime('%Y-%m-%d')
    
    logger.info(f"时间范围: {start_date} 至 {end_date}")
    
    # 获取交易日列表
    trading_dates = get_trading_dates(start_date, end_date)
    logger.info(f"共有 {len(trading_dates)} 个工作日需要处理")
    
    # 统计信息
    total_stats = {
        'total_dates': len(trading_dates),
        'success_dates': 0,
        'failed_dates': 0,
        'total_stocks': 0,
        'success_stocks': 0,
        'failed_stocks': 0,
        'skipped_stocks': 0
    }
    
    # 逐日获取并导入数据
    for i, date_str in enumerate(trading_dates, 1):
        try:
            logger.info(f"\n[{i}/{len(trading_dates)}] 处理日期: {date_str}")
            
            # 获取涨停数据
            stocks = get_limit_up_data(date_str)
            
            if stocks:
                # 转换日期格式为 YYYY-MM-DD
                import_date = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:]}"
                
                # 导入数据
                result = import_limit_up_data(import_date, stocks)
                
                total_stats['success_dates'] += 1
                total_stats['total_stocks'] += result['total']
                total_stats['success_stocks'] += result['success']
                total_stats['failed_stocks'] += result['failed']
                total_stats['skipped_stocks'] += result['skipped']
                
                logger.info(f"✓ {date_str}: {result['success']} 成功, {result['skipped']} 跳过, {result['failed']} 失败")
            else:
                logger.warning(f"✗ {date_str}: 无涨停数据")
            
            # 休息一下，避免请求过快
            time.sleep(0.5)
            
        except Exception as e:
            logger.error(f"处理 {date_str} 时出错: {e}")
            total_stats['failed_dates'] += 1
            continue
    
    # 输出总结
    logger.info("\n" + "="*80)
    logger.info("导入完成！统计信息：")
    logger.info("="*80)
    logger.info(f"处理日期数: {total_stats['total_dates']}")
    logger.info(f"  - 成功: {total_stats['success_dates']}")
    logger.info(f"  - 失败: {total_stats['failed_dates']}")
    logger.info(f"\n处理股票记录数: {total_stats['total_stocks']}")
    logger.info(f"  - 成功导入: {total_stats['success_stocks']}")
    logger.info(f"  - 跳过重复: {total_stats['skipped_stocks']}")
    logger.info(f"  - 导入失败: {total_stats['failed_stocks']}")
    logger.info("="*80)


if __name__ == '__main__':
    main()
