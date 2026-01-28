#!/usr/bin/env python3
"""
涨停数据手动导入示例
根据截图数据手动创建示例并导入
"""

import sys
import os
from datetime import datetime, date

# 添加项目路径
sys.path.insert(0, '/home/user/webapp')

from models import Stock, Theme, LimitUpRecord, OperationLog, db
from stock_info import get_stock_name
import json


# 根据截图创建示例数据
SAMPLE_DATA = {
    '2025-02-20': [
        {'code': '002896', 'name': '中大力德', 'theme': '机器人', 'reason': '公司主要产品包括精密减速器'},
        {'code': '001306', 'name': '复旦微电', 'theme': '人工智能', 'reason': 'AI眼镜+机器人,全资子公司复旦微拟投资5亿元'},
        {'code': '300336', 'name': '新文化', 'theme': '人工智能', 'reason': '家具+小米概念,公司产品主要包括家具、家纺等'},
        {'code': '301336', 'name': '趣睡科技', 'theme': '人工智能', 'reason': '家具+小米概念,公司产品主要包括家具'},
        {'code': '002929', 'name': '润建股份', 'theme': '通信', 'reason': '阿里+算力+DS概念,公司主要业务涵盖通信网络'},
        {'code': '688059', 'name': '华锋精密', 'theme': 'DeepSeek', 'reason': '(满血版，671B)及其开源的DeepSeek-R1'},
        {'code': '605488', 'name': '福莱新材', 'theme': '机器人', 'reason': '机器人2024年12月26日公司在互动平台表示'},
        {'code': '001314', 'name': '亿道信息', 'theme': 'AI', 'reason': 'AI眼镜公司提供跨领域/跨场景关键自主产品'},
        {'code': '001101', 'name': '合力科技', 'theme': 'AI', 'reason': 'AI眼镜+机械,公司已经与百度签订合作协议'},
    ],
    '2025-02-21': [
        {'code': '603179', 'name': '新泉股份', 'theme': 'AI', 'reason': '新能源车,公司已经与特斯拉建成合作伙伴'},
        {'code': '300622', 'name': '博士眼镜', 'theme': 'AI', 'reason': 'AI眼镜公司已与内头部智能眼镜品牌建立了'},
        {'code': '002025', 'name': '航天电器', 'theme': '军工', 'reason': '军工+中国航天科工集团旗下,主要包含连接器'},
        {'code': '003028', 'name': '振邦智能', 'theme': 'AI', 'reason': 'AI眼镜+机械,2024年1月8日公司接受调研时'},
        {'code': '000818', 'name': '航锦科技', 'theme': '军工', 'reason': '军工+DS概念,2024年2月6日公告,全资子公司'},
        {'code': '605288', 'name': '同庆投资', 'theme': 'MLCC', 'reason': 'MLCC,公司主要业务为电解铜箔产品的研发'},
        {'code': '605376', 'name': '博迁新材', 'theme': 'MLCC', 'reason': 'MLCC,公司主导业务为用电子专用高纯金属粉体材料'},
        {'code': '605286', 'name': '同力日升', 'theme': '储能', 'reason': '储能+电梯,公司持有天朗蓄能51%股权,标的公司'},
    ]
}


def import_sample_data():
    """导入示例数据"""
    session = db.get_session()
    
    try:
        total_success = 0
        total_error = 0
        
        for date_str, stocks_list in SAMPLE_DATA.items():
            print(f"\n{'='*60}")
            print(f"📅 导入日期: {date_str}")
            print(f"{'='*60}")
            
            # 解析日期
            try:
                trade_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            except:
                print(f"⚠️ 日期格式错误: {date_str}")
                continue
            
            success_count = 0
            theme_stats = {}
            
            for stock_data in stocks_list:
                try:
                    code = stock_data['code']
                    name = stock_data['name']
                    theme_name = stock_data['theme']
                    reason = stock_data['reason']
                    
                    # 获取或创建题材
                    theme = session.query(Theme).filter(Theme.name == theme_name).first()
                    if not theme:
                        theme = Theme(name=theme_name, description=f'涨停数据导入的题材：{theme_name}')
                        session.add(theme)
                        session.flush()
                    
                    # 获取或创建股票（优先使用stock_info获取名称）
                    stock = session.query(Stock).filter(Stock.code == code).first()
                    if not stock:
                        # 使用stock_info模块自动获取股票名称
                        stock_name = get_stock_name(code)
                        if stock_name and stock_name != f'股票{code}':
                            name = stock_name  # 使用真实名称
                        
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
                        print(f"  ⚠️ 跳过已存在: {code} {name}")
                        continue
                    
                    # 创建涨停记录
                    limit_up = LimitUpRecord(
                        stock_id=stock.id,
                        theme_id=theme.id,
                        trade_date=trade_date,
                        reason=reason,
                        limit_up_time='09:30',
                        open_count=0
                    )
                    session.add(limit_up)
                    session.flush()
                    
                    success_count += 1
                    theme_stats[theme_name] = theme_stats.get(theme_name, 0) + 1
                    
                    print(f"  ✅ {code} {name} - {theme_name}")
                    
                except Exception as e:
                    print(f"  ❌ {code} {name} - 错误: {e}")
                    total_error += 1
                    continue
            
            # 提交本日期的数据
            session.commit()
            
            print(f"\n📊 {date_str} 统计:")
            print(f"   成功: {success_count} 条")
            for theme, count in sorted(theme_stats.items(), key=lambda x: x[1], reverse=True):
                print(f"   - {theme}: {count} 只")
            
            total_success += success_count
            
            # 记录操作日志
            if success_count > 0:
                log_details = {
                    'source': '手动导入涨停数据',
                    'date': date_str,
                    'success_count': success_count,
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
        
        print(f"\n{'='*60}")
        print(f"🎉 所有数据导入完成！")
        print(f"{'='*60}")
        print(f"✅ 总成功: {total_success} 条")
        print(f"❌ 总失败: {total_error} 条")
        
    except Exception as e:
        session.rollback()
        print(f"❌ 数据库操作失败: {e}")
    finally:
        session.close()


if __name__ == '__main__':
    print("="*60)
    print("     涨停数据导入工具（示例数据）")
    print("="*60)
    print("\n📝 说明：由于无法解压RAR文件，使用截图中的示例数据进行演示")
    print("         实际使用时可以修改 SAMPLE_DATA 字典添加更多数据\n")
    
    import_sample_data()
    
    print("\n✅ 完成！")
    print("💡 提示：可以在Web界面查看导入的数据")
