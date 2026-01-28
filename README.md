# 股票数据研究系统

一个基于Flask的股票数据分析系统，用于分析题材板块和个股的相对位置关系。

## 功能特点

### 核心功能

1. **题材成分股筛选**
   - 根据过去1年的涨停记录，筛选出每个题材涨停次数最多的前15只股票作为成分股

2. **位置百分比计算**
   - 基于过去240个交易日的价格区间（最低价为0%，最高价为100%）
   - 计算个股当前价格在区间中的位置百分比
   - 计算题材整体位置（成分股位置百分比的平均值）

3. **相对强弱分析**
   - 比较个股与题材的位置百分比差异
   - 判断个股相对于题材的强弱状态
   - 识别是否为题材成分股

## 技术栈

- **后端框架**: Flask 3.0.0
- **数据库**: SQLite + SQLAlchemy
- **数据处理**: Pandas + NumPy
- **API**: RESTful API with CORS support

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 初始化数据库并导入测试数据

```bash
python data_importer.py
```

这将创建数据库表并生成模拟数据：
- 50只测试股票
- 5个题材分类
- 过去300个交易日的日线数据
- 随机生成的涨停记录

### 3. 启动API服务

```bash
python app.py
```

服务将在 `http://0.0.0.0:5000` 启动

## API 接口文档

### 1. 获取题材前15只成分股

**接口**: `GET /api/theme/top-stocks`

**参数**:
- `theme` (必需): 题材名称
- `date` (必需): 日期 (YYYY-MM-DD)
- `lookback_days` (可选): 回溯天数，默认365
- `top_n` (可选): 返回数量，默认15

**示例请求**:
```bash
curl "http://localhost:5000/api/theme/top-stocks?theme=人工智能&date=2024-01-28"
```

**响应示例**:
```json
{
  "success": true,
  "data": {
    "theme": "人工智能",
    "date": "2024-01-28",
    "lookback_days": 365,
    "stocks": [
      {
        "code": "000001",
        "name": "测试股票1",
        "limit_up_count": 8
      }
    ],
    "total_count": 15
  }
}
```

### 2. 获取个股位置百分比

**接口**: `GET /api/stock/position`

**参数**:
- `code` (必需): 股票代码
- `date` (必需): 日期 (YYYY-MM-DD)
- `lookback_periods` (可选): 回溯交易日数，默认240

**示例请求**:
```bash
curl "http://localhost:5000/api/stock/position?code=000001&date=2024-01-28"
```

**响应示例**:
```json
{
  "success": true,
  "data": {
    "stock_code": "000001",
    "stock_name": "测试股票1",
    "current_price": 12.50,
    "lowest_price": 10.00,
    "highest_price": 15.00,
    "position_percent": 50.00,
    "available_periods": 240,
    "target_date": "2024-01-28"
  }
}
```

### 3. 获取题材位置百分比

**接口**: `GET /api/theme/position`

**参数**:
- `theme` (必需): 题材名称
- `date` (必需): 日期 (YYYY-MM-DD)
- `lookback_periods` (可选): 回溯交易日数，默认240

**示例请求**:
```bash
curl "http://localhost:5000/api/theme/position?theme=人工智能&date=2024-01-28"
```

**响应示例**:
```json
{
  "success": true,
  "data": {
    "theme_name": "人工智能",
    "constituent_stocks": [
      {
        "code": "000001",
        "name": "测试股票1",
        "limit_up_count": 8,
        "position_percent": 52.30,
        "current_price": 12.50
      }
    ],
    "constituent_count": 15,
    "theme_position_percent": 55.50,
    "target_date": "2024-01-28"
  }
}
```

### 4. 比较个股与题材 (核心接口)

**接口**: `GET /api/analysis/compare`

**参数**:
- `code` (必需): 股票代码
- `theme` (必需): 题材名称
- `date` (必需): 日期 (YYYY-MM-DD)
- `lookback_periods` (可选): 回溯交易日数，默认240

**示例请求**:
```bash
curl "http://localhost:5000/api/analysis/compare?code=000001&theme=人工智能&date=2024-01-28"
```

**响应示例**:
```json
{
  "success": true,
  "data": {
    "stock_info": {
      "stock_code": "000001",
      "stock_name": "测试股票1",
      "current_price": 12.50,
      "lowest_price": 10.00,
      "highest_price": 15.00,
      "position_percent": 50.00,
      "available_periods": 240,
      "target_date": "2024-01-28"
    },
    "theme_info": {
      "theme_name": "人工智能",
      "constituent_count": 15,
      "theme_position_percent": 55.50
    },
    "comparison": {
      "position_difference": -5.50,
      "relative_strength": "弱于题材",
      "is_constituent_stock": true
    },
    "analysis_params": {
      "lookback_periods": 240,
      "target_date": "2024-01-28"
    }
  }
}
```

## 数据模型

### 数据库表结构

1. **stocks** - 股票基本信息
   - code: 股票代码
   - name: 股票名称
   - market: 市场 (SH/SZ)

2. **themes** - 题材信息
   - name: 题材名称
   - description: 题材描述

3. **daily_prices** - 日线数据
   - stock_id: 股票ID
   - trade_date: 交易日期
   - open_price, close_price, high_price, low_price
   - volume: 成交量
   - amount: 成交额

4. **limit_up_records** - 涨停记录
   - stock_id: 股票ID
   - theme_id: 题材ID
   - trade_date: 涨停日期
   - reason: 涨停原因
   - limit_up_time: 封板时间
   - open_count: 打开次数

## 算法说明

### 位置百分比计算公式

```
位置百分比 = (当前价格 - 最低价) / (最高价 - 最低价) × 100%
```

其中：
- 最低价：过去N个交易日的最低收盘价
- 最高价：过去N个交易日的最高收盘价
- 当前价格：目标日期的收盘价

### 题材位置计算

题材位置 = 所有成分股位置百分比的算术平均值

### 相对强弱判断

- `position_difference > 10`: 强于题材
- `-10 ≤ position_difference ≤ 10`: 与题材同步
- `position_difference < -10`: 弱于题材

## 项目结构

```
webapp/
├── models.py              # 数据库模型定义
├── analyzer.py            # 核心分析算法
├── app.py                 # Flask API接口
├── data_importer.py       # 数据导入工具
├── requirements.txt       # Python依赖
├── .gitignore            # Git忽略文件
└── README.md             # 项目文档
```

## 开发计划

### 已完成功能
- ✅ 数据库设计和模型定义
- ✅ 题材成分股筛选算法
- ✅ 位置百分比计算算法
- ✅ RESTful API接口
- ✅ 模拟数据生成工具

### 待扩展功能
- ⏳ 真实股票数据接入（Tushare/AKShare）
- ⏳ Web前端界面
- ⏳ 历史回测功能
- ⏳ 可视化图表
- ⏳ 导出Excel报告

## 使用示例

### Python客户端示例

```python
import requests

base_url = "http://localhost:5000"

# 1. 查询题材成分股
response = requests.get(f"{base_url}/api/theme/top-stocks", params={
    "theme": "人工智能",
    "date": "2024-01-28"
})
print(response.json())

# 2. 分析个股与题材
response = requests.get(f"{base_url}/api/analysis/compare", params={
    "code": "000001",
    "theme": "人工智能",
    "date": "2024-01-28"
})
result = response.json()
if result['success']:
    data = result['data']
    print(f"个股位置: {data['stock_info']['position_percent']}%")
    print(f"题材位置: {data['theme_info']['theme_position_percent']}%")
    print(f"相对强弱: {data['comparison']['relative_strength']}")
```

## 注意事项

1. 当前使用模拟数据，生产环境需要接入真实数据源
2. 位置百分比计算基于历史数据，不构成投资建议
3. 默认使用240个交易日（约1年），可根据需求调整
4. 数据库使用SQLite，大数据量建议迁移到PostgreSQL/MySQL

## 许可证

MIT License

## 联系方式

如有问题或建议，欢迎提交Issue。
