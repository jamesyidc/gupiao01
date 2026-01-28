# API 测试示例

## 服务地址

- 本地: http://localhost:5000
- 在线: https://5000-i1m9fpfr5tksghv87yttz-a402f90a.sandbox.novita.ai

## 1. 健康检查

```bash
curl "https://5000-i1m9fpfr5tksghv87yttz-a402f90a.sandbox.novita.ai/health"
```

## 2. 获取题材成分股（涨停次数最多的前15只股票）

```bash
# 使用URL编码的中文
curl "https://5000-i1m9fpfr5tksghv87yttz-a402f90a.sandbox.novita.ai/api/theme/top-stocks?theme=%E4%BA%BA%E5%B7%A5%E6%99%BA%E8%83%BD&date=2026-01-27&top_n=15"
```

**参数说明：**
- `theme`: 题材名称（需要URL编码）
  - 人工智能: `%E4%BA%BA%E5%B7%A5%E6%99%BA%E8%83%BD`
  - 新能源汽车: `%E6%96%B0%E8%83%BD%E6%BA%90%E6%B1%BD%E8%BD%A6`
  - 芯片半导体: `%E8%8A%AF%E7%89%87%E5%8D%8A%E5%AF%BC%E4%BD%93`
  - 医药医疗: `%E5%8C%BB%E8%8D%AF%E5%8C%BB%E7%96%97`
  - 5G通信: `5G%E9%80%9A%E4%BF%A1`
- `date`: 日期 (YYYY-MM-DD)
- `top_n`: 返回数量，默认15

**响应示例：**
```json
{
    "success": true,
    "data": {
        "theme": "人工智能",
        "date": "2026-01-27",
        "lookback_days": 365,
        "stocks": [
            {
                "code": "000016",
                "name": "测试股票16",
                "limit_up_count": 9
            },
            {
                "code": "000001",
                "name": "测试股票1",
                "limit_up_count": 8
            }
        ],
        "total_count": 14
    }
}
```

## 3. 获取个股位置百分比

```bash
curl "https://5000-i1m9fpfr5tksghv87yttz-a402f90a.sandbox.novita.ai/api/stock/position?code=000001&date=2026-01-27"
```

**参数说明：**
- `code`: 股票代码
- `date`: 日期 (YYYY-MM-DD)
- `lookback_periods`: 回溯交易日数，默认240

**响应示例：**
```json
{
    "success": true,
    "data": {
        "stock_code": "000001",
        "stock_name": "测试股票1",
        "current_price": 28.45,
        "lowest_price": 23.95,
        "highest_price": 45.53,
        "position_percent": 20.85,
        "available_periods": 214,
        "target_date": "2026-01-27"
    }
}
```

## 4. 获取题材位置百分比

```bash
curl "https://5000-i1m9fpfr5tksghv87yttz-a402f90a.sandbox.novita.ai/api/theme/position?theme=%E4%BA%BA%E5%B7%A5%E6%99%BA%E8%83%BD&date=2026-01-27"
```

**参数说明：**
- `theme`: 题材名称（需要URL编码）
- `date`: 日期 (YYYY-MM-DD)
- `lookback_periods`: 回溯交易日数，默认240

**响应示例：**
```json
{
    "success": true,
    "data": {
        "theme_name": "人工智能",
        "constituent_stocks": [...],
        "constituent_count": 14,
        "theme_position_percent": 35.87,
        "target_date": "2026-01-27"
    }
}
```

## 5. 比较个股与题材（核心功能）

```bash
curl "https://5000-i1m9fpfr5tksghv87yttz-a402f90a.sandbox.novita.ai/api/analysis/compare?code=000001&theme=%E4%BA%BA%E5%B7%A5%E6%99%BA%E8%83%BD&date=2026-01-27"
```

**参数说明：**
- `code`: 股票代码
- `theme`: 题材名称（需要URL编码）
- `date`: 日期 (YYYY-MM-DD)
- `lookback_periods`: 回溯交易日数，默认240

**响应示例：**
```json
{
    "success": true,
    "data": {
        "stock_info": {
            "stock_code": "000001",
            "stock_name": "测试股票1",
            "current_price": 28.45,
            "position_percent": 20.85
        },
        "theme_info": {
            "theme_name": "人工智能",
            "theme_position_percent": 35.87,
            "constituent_count": 14
        },
        "comparison": {
            "position_difference": -15.02,
            "relative_strength": "弱于题材",
            "is_constituent_stock": true
        },
        "analysis_params": {
            "lookback_periods": 240,
            "target_date": "2026-01-27"
        }
    }
}
```

## Python 客户端示例

```python
import requests
import urllib.parse

base_url = "https://5000-i1m9fpfr5tksghv87yttz-a402f90a.sandbox.novita.ai"

# 1. 查询题材成分股
theme = "人工智能"
response = requests.get(f"{base_url}/api/theme/top-stocks", params={
    "theme": theme,
    "date": "2026-01-27",
    "top_n": 15
})
print("题材成分股:", response.json())

# 2. 查询个股位置
response = requests.get(f"{base_url}/api/stock/position", params={
    "code": "000001",
    "date": "2026-01-27"
})
print("个股位置:", response.json())

# 3. 比较分析
response = requests.get(f"{base_url}/api/analysis/compare", params={
    "code": "000001",
    "theme": theme,
    "date": "2026-01-27"
})
result = response.json()
if result['success']:
    data = result['data']
    print(f"\n个股: {data['stock_info']['stock_name']}")
    print(f"个股位置: {data['stock_info']['position_percent']}%")
    print(f"题材位置: {data['theme_info']['theme_position_percent']}%")
    print(f"相对强弱: {data['comparison']['relative_strength']}")
    print(f"位置差异: {data['comparison']['position_difference']}%")
```

## 可用测试数据

### 题材列表
1. 人工智能
2. 新能源汽车
3. 芯片半导体
4. 医药医疗
5. 5G通信

### 股票代码
- 000001 ~ 000050（50只测试股票）

### 数据日期范围
- 2025-02-01 ~ 2026-01-27

## 算法说明

### 位置百分比计算
```
位置百分比 = (当前价 - 最低价) / (最高价 - 最低价) × 100%
```

其中：
- 最低价：过去240个交易日的最低收盘价
- 最高价：过去240个交易日的最高收盘价
- 当前价：目标日期的收盘价

### 题材位置计算
题材位置百分比 = 所有成分股位置百分比的算术平均值

### 相对强弱判断
- `position_difference > 10`: 强于题材
- `-10 ≤ position_difference ≤ 10`: 与题材同步  
- `position_difference < -10`: 弱于题材
