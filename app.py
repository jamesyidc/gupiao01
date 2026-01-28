"""
Flask API 接口
"""
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from datetime import datetime
from analyzer import StockAnalyzer
from models import db

app = Flask(__name__)
CORS(app)  # 允许跨域请求

# 配置
app.config['JSON_AS_ASCII'] = False  # 支持中文
app.config['JSON_SORT_KEYS'] = False


@app.route('/', methods=['GET'])
def index():
    """主页 - 显示可视化界面"""
    return render_template('index.html')


@app.route('/api/theme/top-stocks', methods=['GET'])
def get_theme_top_stocks():
    """
    获取题材前15只成分股
    
    参数:
        theme: 题材名称 (必需)
        date: 日期 YYYY-MM-DD (必需)
        lookback_days: 回溯天数，默认365
        top_n: 返回数量，默认15
    
    返回:
        {
            "success": true,
            "data": [
                {
                    "code": "000001",
                    "name": "平安银行",
                    "limit_up_count": 5
                },
                ...
            ]
        }
    """
    try:
        theme_name = request.args.get('theme')
        date_str = request.args.get('date')
        lookback_days = int(request.args.get('lookback_days', 365))
        top_n = int(request.args.get('top_n', 15))
        
        if not theme_name or not date_str:
            return jsonify({
                'success': False,
                'error': '缺少必需参数: theme 和 date'
            }), 400
        
        # 验证日期格式
        try:
            target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            return jsonify({
                'success': False,
                'error': '日期格式错误，应为 YYYY-MM-DD'
            }), 400
        
        analyzer = StockAnalyzer()
        print(f"[DEBUG] 查询参数: theme={theme_name}, date={target_date}, lookback_days={lookback_days}, top_n={top_n}")
        result = analyzer.get_theme_top_stocks(
            theme_name, 
            target_date, 
            lookback_days, 
            top_n
        )
        print(f"[DEBUG] 查询结果: {result}")
        analyzer.close()
        
        stocks_data = [
            {
                'code': code,
                'name': name,
                'limit_up_count': count
            }
            for code, name, count in result
        ]
        
        return jsonify({
            'success': True,
            'data': {
                'theme': theme_name,
                'date': date_str,
                'lookback_days': lookback_days,
                'stocks': stocks_data,
                'total_count': len(stocks_data)
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/stock/position', methods=['GET'])
def get_stock_position():
    """
    获取个股位置百分比
    
    参数:
        code: 股票代码 (必需)
        date: 日期 YYYY-MM-DD (必需)
        lookback_periods: 回溯交易日数，默认240
    
    返回:
        {
            "success": true,
            "data": {
                "stock_code": "000001",
                "stock_name": "平安银行",
                "current_price": 12.50,
                "lowest_price": 10.00,
                "highest_price": 15.00,
                "position_percent": 50.00,
                "available_periods": 240,
                "target_date": "2024-01-28"
            }
        }
    """
    try:
        stock_code = request.args.get('code')
        date_str = request.args.get('date')
        lookback_periods = int(request.args.get('lookback_periods', 240))
        
        if not stock_code or not date_str:
            return jsonify({
                'success': False,
                'error': '缺少必需参数: code 和 date'
            }), 400
        
        # 验证日期格式
        try:
            target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            return jsonify({
                'success': False,
                'error': '日期格式错误，应为 YYYY-MM-DD'
            }), 400
        
        analyzer = StockAnalyzer()
        result = analyzer.calculate_position_percentage(
            stock_code,
            target_date,
            lookback_periods
        )
        analyzer.close()
        
        if not result:
            return jsonify({
                'success': False,
                'error': f'未找到股票 {stock_code} 的数据'
            }), 404
        
        return jsonify({
            'success': True,
            'data': result
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/theme/position', methods=['GET'])
def get_theme_position():
    """
    获取题材位置百分比（基于成分股平均）
    
    参数:
        theme: 题材名称 (必需)
        date: 日期 YYYY-MM-DD (必需)
        lookback_periods: 回溯交易日数，默认240
    
    返回:
        {
            "success": true,
            "data": {
                "theme_name": "人工智能",
                "constituent_stocks": [...],
                "constituent_count": 15,
                "theme_position_percent": 55.50,
                "target_date": "2024-01-28"
            }
        }
    """
    try:
        theme_name = request.args.get('theme')
        date_str = request.args.get('date')
        lookback_periods = int(request.args.get('lookback_periods', 240))
        
        if not theme_name or not date_str:
            return jsonify({
                'success': False,
                'error': '缺少必需参数: theme 和 date'
            }), 400
        
        # 验证日期格式
        try:
            target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            return jsonify({
                'success': False,
                'error': '日期格式错误，应为 YYYY-MM-DD'
            }), 400
        
        analyzer = StockAnalyzer()
        result = analyzer.calculate_theme_position_percentage(
            theme_name,
            target_date,
            lookback_periods
        )
        analyzer.close()
        
        if not result:
            return jsonify({
                'success': False,
                'error': f'未找到题材 {theme_name} 的数据'
            }), 404
        
        return jsonify({
            'success': True,
            'data': result
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/analysis/compare', methods=['GET'])
def compare_analysis():
    """
    比较个股与题材的位置百分比
    
    参数:
        code: 股票代码 (必需)
        theme: 题材名称 (必需)
        date: 日期 YYYY-MM-DD (必需)
        lookback_periods: 回溯交易日数，默认240
    
    返回:
        {
            "success": true,
            "data": {
                "stock_info": {...},
                "theme_info": {...},
                "comparison": {
                    "position_difference": 5.50,
                    "relative_strength": "强于题材",
                    "is_constituent_stock": true
                },
                "analysis_params": {...}
            }
        }
    """
    try:
        stock_code = request.args.get('code')
        theme_name = request.args.get('theme')
        date_str = request.args.get('date')
        lookback_periods = int(request.args.get('lookback_periods', 240))
        
        if not stock_code or not theme_name or not date_str:
            return jsonify({
                'success': False,
                'error': '缺少必需参数: code, theme 和 date'
            }), 400
        
        # 验证日期格式
        try:
            target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            return jsonify({
                'success': False,
                'error': '日期格式错误，应为 YYYY-MM-DD'
            }), 400
        
        analyzer = StockAnalyzer()
        result = analyzer.compare_stock_with_theme(
            stock_code,
            theme_name,
            target_date,
            lookback_periods
        )
        analyzer.close()
        
        if not result:
            return jsonify({
                'success': False,
                'error': '分析失败，请检查股票代码和题材名称'
            }), 404
        
        return jsonify({
            'success': True,
            'data': result
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/health', methods=['GET'])
def health_check():
    """健康检查"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat()
    })


@app.route('/api/data/submit-batch', methods=['POST'])
def submit_batch_codes():
    """
    批量提交股票代码（只需代码，系统自动查询名称）
    
    请求体:
    {
        "date": "2026-01-28",
        "theme": "人工智能",
        "stock_codes": ["000001", "000002", "600519"]
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': '请求体不能为空'
            }), 400
        
        date_str = data.get('date')
        theme_name = data.get('theme')
        stock_codes = data.get('stock_codes', [])
        
        if not date_str or not theme_name:
            return jsonify({
                'success': False,
                'error': '缺少必需字段: date 和 theme'
            }), 400
        
        if not stock_codes or not isinstance(stock_codes, list):
            return jsonify({
                'success': False,
                'error': 'stock_codes 必须是非空数组'
            }), 400
        
        # 验证日期格式
        try:
            trade_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            return jsonify({
                'success': False,
                'error': '日期格式错误，应为 YYYY-MM-DD'
            }), 400
        
        # 导入数据
        from models import Stock, Theme, LimitUpRecord
        session = db.get_session()
        
        # 获取或创建题材
        theme = session.query(Theme).filter(Theme.name == theme_name).first()
        if not theme:
            theme = Theme(name=theme_name, description=f'手动添加的题材：{theme_name}')
            session.add(theme)
            session.commit()
        
        success_count = 0
        error_list = []
        details = []
        
        # 这里简化处理，实际应该接入股票API查询
        # 暂时使用虚拟名称
        stock_names_map = {
            '000001': '平安银行', '000002': '万科A', '000004': '国农科技',
            '600519': '贵州茅台', '600036': '招商银行', '601318': '中国平安',
            '300750': '宁德时代', '002594': '比亚迪', '000858': '五粮液',
            '300768': '迪普科技', '688027': '国盾量子', '300033': '同花顺',
            '002230': '科大讯飞', '688111': '金山办公', '000063': '中兴通讯'
        }
        
        for stock_code in stock_codes:
            try:
                # 验证股票代码格式
                if not stock_code or len(stock_code) != 6 or not stock_code.isdigit():
                    error_list.append(f'股票代码格式错误: {stock_code}')
                    details.append({
                        'code': stock_code,
                        'name': '',
                        'status': '格式错误'
                    })
                    continue
                
                # 获取或创建股票
                stock = session.query(Stock).filter(Stock.code == stock_code).first()
                if not stock:
                    # 尝试获取股票名称
                    stock_name = stock_names_map.get(stock_code, f'股票{stock_code}')
                    
                    # 创建新股票
                    market = 'SZ' if stock_code.startswith('0') or stock_code.startswith('3') else 'SH'
                    stock = Stock(code=stock_code, name=stock_name, market=market)
                    session.add(stock)
                    session.commit()
                    
                    details.append({
                        'code': stock_code,
                        'name': stock_name,
                        'status': '新建股票'
                    })
                else:
                    details.append({
                        'code': stock_code,
                        'name': stock.name,
                        'status': '已存在'
                    })
                
                # 检查是否已存在该涨停记录
                existing = session.query(LimitUpRecord).filter(
                    LimitUpRecord.stock_id == stock.id,
                    LimitUpRecord.theme_id == theme.id,
                    LimitUpRecord.trade_date == trade_date
                ).first()
                
                if existing:
                    error_list.append(f'股票{stock_code}在{date_str}的{theme_name}题材涨停记录已存在')
                    details[-1]['status'] = '记录已存在'
                    continue
                
                # 创建涨停记录
                limit_up = LimitUpRecord(
                    stock_id=stock.id,
                    theme_id=theme.id,
                    trade_date=trade_date,
                    reason=f'{theme_name}板块活跃',
                    limit_up_time='09:30',
                    open_count=0
                )
                session.add(limit_up)
                success_count += 1
                details[-1]['status'] = '✅ 成功'
                
            except Exception as e:
                error_list.append(f'处理股票{stock_code}时出错: {str(e)}')
                if details and details[-1]['code'] == stock_code:
                    details[-1]['status'] = f'错误: {str(e)}'
                continue
        
        # 提交事务
        session.commit()
        session.close()
        
        result = {
            'success': True,
            'message': f'成功提交{success_count}条涨停记录',
            'success_count': success_count,
            'total_count': len(stock_codes),
            'details': details
        }
        
        if error_list:
            result['errors'] = error_list
            result['error_count'] = len(error_list)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/data/submit', methods=['POST'])
def submit_data():
    """
    提交涨停数据
    
    请求体:
    {
        "date": "2026-01-28",
        "theme": "人工智能",
        "stocks": [
            {
                "code": "000001",
                "name": "平安银行",
                "reason": "AI概念爆发",
                "limit_up_time": "09:30",
                "open_count": 0
            },
            ...
        ]
    }
    
    返回:
    {
        "success": true,
        "message": "成功提交3条涨停记录"
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': '请求体不能为空'
            }), 400
        
        # 验证必需字段
        date_str = data.get('date')
        theme_name = data.get('theme')
        stocks = data.get('stocks', [])
        
        if not date_str or not theme_name:
            return jsonify({
                'success': False,
                'error': '缺少必需字段: date 和 theme'
            }), 400
        
        if not stocks or not isinstance(stocks, list):
            return jsonify({
                'success': False,
                'error': 'stocks 必须是非空数组'
            }), 400
        
        # 验证日期格式
        try:
            trade_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            return jsonify({
                'success': False,
                'error': '日期格式错误，应为 YYYY-MM-DD'
            }), 400
        
        # 导入数据
        from models import Stock, Theme, LimitUpRecord
        session = db.get_session()
        
        # 获取或创建题材
        theme = session.query(Theme).filter(Theme.name == theme_name).first()
        if not theme:
            theme = Theme(name=theme_name, description=f'手动添加的题材：{theme_name}')
            session.add(theme)
            session.commit()
        
        success_count = 0
        error_list = []
        
        for stock_data in stocks:
            try:
                stock_code = stock_data.get('code')
                stock_name = stock_data.get('name')
                
                if not stock_code:
                    error_list.append('股票代码不能为空')
                    continue
                
                # 获取或创建股票
                stock = session.query(Stock).filter(Stock.code == stock_code).first()
                if not stock:
                    if not stock_name:
                        error_list.append(f'股票{stock_code}不存在，且未提供股票名称')
                        continue
                    
                    # 创建新股票
                    market = 'SZ' if stock_code.startswith('0') or stock_code.startswith('3') else 'SH'
                    stock = Stock(code=stock_code, name=stock_name, market=market)
                    session.add(stock)
                    session.commit()
                
                # 检查是否已存在该涨停记录
                existing = session.query(LimitUpRecord).filter(
                    LimitUpRecord.stock_id == stock.id,
                    LimitUpRecord.theme_id == theme.id,
                    LimitUpRecord.trade_date == trade_date
                ).first()
                
                if existing:
                    error_list.append(f'股票{stock_code}在{date_str}的{theme_name}题材涨停记录已存在')
                    continue
                
                # 创建涨停记录
                limit_up = LimitUpRecord(
                    stock_id=stock.id,
                    theme_id=theme.id,
                    trade_date=trade_date,
                    reason=stock_data.get('reason', ''),
                    limit_up_time=stock_data.get('limit_up_time'),
                    open_count=stock_data.get('open_count', 0),
                    turnover_rate=stock_data.get('turnover_rate')
                )
                session.add(limit_up)
                success_count += 1
                
            except Exception as e:
                error_list.append(f'处理股票{stock_data.get("code", "unknown")}时出错: {str(e)}')
                continue
        
        # 提交事务
        session.commit()
        session.close()
        
        result = {
            'success': True,
            'message': f'成功提交{success_count}条涨停记录',
            'success_count': success_count,
            'total_count': len(stocks)
        }
        
        if error_list:
            result['errors'] = error_list
            result['error_count'] = len(error_list)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/data/add-stock', methods=['POST'])
def add_stock():
    """
    添加单个股票基本信息
    
    请求体:
    {
        "code": "000001",
        "name": "平安银行",
        "market": "SZ"
    }
    """
    try:
        data = request.get_json()
        
        code = data.get('code')
        name = data.get('name')
        market = data.get('market', 'SZ')
        
        if not code or not name:
            return jsonify({
                'success': False,
                'error': '缺少必需字段: code 和 name'
            }), 400
        
        from models import Stock
        session = db.get_session()
        
        # 检查是否已存在
        existing = session.query(Stock).filter(Stock.code == code).first()
        if existing:
            session.close()
            return jsonify({
                'success': False,
                'error': f'股票{code}已存在'
            }), 400
        
        # 创建股票
        stock = Stock(code=code, name=name, market=market)
        session.add(stock)
        session.commit()
        session.close()
        
        return jsonify({
            'success': True,
            'message': f'成功添加股票{code} - {name}'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/data/add-theme', methods=['POST'])
def add_theme():
    """
    添加题材
    
    请求体:
    {
        "name": "量子计算",
        "description": "量子计算相关概念"
    }
    """
    try:
        data = request.get_json()
        
        name = data.get('name')
        description = data.get('description', '')
        
        if not name:
            return jsonify({
                'success': False,
                'error': '缺少必需字段: name'
            }), 400
        
        from models import Theme
        session = db.get_session()
        
        # 检查是否已存在
        existing = session.query(Theme).filter(Theme.name == name).first()
        if existing:
            session.close()
            return jsonify({
                'success': False,
                'error': f'题材{name}已存在'
            }), 400
        
        # 创建题材
        theme = Theme(name=name, description=description)
        session.add(theme)
        session.commit()
        session.close()
        
        return jsonify({
            'success': True,
            'message': f'成功添加题材{name}'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/data/themes', methods=['GET'])
def get_themes():
    """获取所有题材列表"""
    try:
        from models import Theme
        session = db.get_session()
        
        themes = session.query(Theme).all()
        
        result = [
            {
                'id': theme.id,
                'name': theme.name,
                'description': theme.description
            }
            for theme in themes
        ]
        
        session.close()
        
        return jsonify({
            'success': True,
            'data': result
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/data/stocks', methods=['GET'])
def get_stocks():
    """获取所有股票列表"""
    try:
        from models import Stock
        session = db.get_session()
        
        stocks = session.query(Stock).all()
        
        result = [
            {
                'id': stock.id,
                'code': stock.code,
                'name': stock.name,
                'market': stock.market
            }
            for stock in stocks
        ]
        
        session.close()
        
        return jsonify({
            'success': True,
            'data': result
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


if __name__ == '__main__':
    # 初始化数据库
    db.create_tables()
    print("数据库初始化完成")
    
    # 启动服务
    app.run(host='0.0.0.0', port=5000, debug=True)
