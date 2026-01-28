"""
Flask API 接口
"""
from flask import Flask, request, jsonify
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
    """API 根路径"""
    return jsonify({
        'message': '股票数据研究系统 API',
        'version': '1.0.0',
        'endpoints': {
            'theme_top_stocks': '/api/theme/top-stocks',
            'stock_position': '/api/stock/position',
            'theme_position': '/api/theme/position',
            'compare_analysis': '/api/analysis/compare'
        }
    })


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


if __name__ == '__main__':
    # 初始化数据库
    db.create_tables()
    print("数据库初始化完成")
    
    # 启动服务
    app.run(host='0.0.0.0', port=5000, debug=True)
