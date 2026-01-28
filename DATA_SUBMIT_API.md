# 数据提交接口文档

## 📝 概述

本文档介绍如何手动提交股票涨停数据、添加题材和股票信息。

## 🌐 API 基础地址

- **在线**: https://5000-i1m9fpfr5tksghv87yttz-a402f90a.sandbox.novita.ai
- **本地**: http://localhost:5000

---

## 📊 核心接口

### 1. 提交涨停数据（批量）

**接口**: `POST /api/data/submit`

**功能**: 批量提交某个日期、某个题材下的多只股票涨停记录

**请求头**:
```
Content-Type: application/json
```

**请求体**:
```json
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
    {
      "code": "000002",
      "name": "万科A",
      "reason": "人工智能应用",
      "limit_up_time": "10:15",
      "open_count": 1
    }
  ]
}
```

**字段说明**:
- `date` (必需): 涨停日期，格式 YYYY-MM-DD
- `theme` (必需): 题材名称
- `stocks` (必需): 股票数组
  - `code` (必需): 股票代码
  - `name` (可选): 股票名称（如果股票不存在，必须提供）
  - `reason` (可选): 涨停原因
  - `limit_up_time` (可选): 封板时间，如 "09:30"
  - `open_count` (可选): 打开次数，默认0

**响应示例**:
```json
{
  "success": true,
  "message": "成功提交2条涨停记录",
  "success_count": 2,
  "total_count": 2
}
```

**错误响应**:
```json
{
  "success": true,
  "message": "成功提交1条涨停记录",
  "success_count": 1,
  "total_count": 2,
  "error_count": 1,
  "errors": [
    "股票000002在2026-01-28的人工智能题材涨停记录已存在"
  ]
}
```

**curl 示例**:
```bash
curl -X POST https://5000-i1m9fpfr5tksghv87yttz-a402f90a.sandbox.novita.ai/api/data/submit \
  -H "Content-Type: application/json" \
  -d '{
    "date": "2026-01-28",
    "theme": "人工智能",
    "stocks": [
      {
        "code": "000001",
        "name": "平安银行",
        "reason": "AI概念爆发"
      }
    ]
  }'
```

---

### 2. 添加单个股票

**接口**: `POST /api/data/add-stock`

**功能**: 添加股票基本信息

**请求体**:
```json
{
  "code": "000001",
  "name": "平安银行",
  "market": "SZ"
}
```

**字段说明**:
- `code` (必需): 股票代码
- `name` (必需): 股票名称
- `market` (可选): 市场代码，SZ=深圳/SH=上海，默认SZ

**响应示例**:
```json
{
  "success": true,
  "message": "成功添加股票000001 - 平安银行"
}
```

**curl 示例**:
```bash
curl -X POST https://5000-i1m9fpfr5tksghv87yttz-a402f90a.sandbox.novita.ai/api/data/add-stock \
  -H "Content-Type: application/json" \
  -d '{
    "code": "600519",
    "name": "贵州茅台",
    "market": "SH"
  }'
```

---

### 3. 添加题材

**接口**: `POST /api/data/add-theme`

**功能**: 添加新的题材分类

**请求体**:
```json
{
  "name": "量子计算",
  "description": "量子计算相关概念"
}
```

**字段说明**:
- `name` (必需): 题材名称
- `description` (可选): 题材描述

**响应示例**:
```json
{
  "success": true,
  "message": "成功添加题材量子计算"
}
```

**curl 示例**:
```bash
curl -X POST https://5000-i1m9fpfr5tksghv87yttz-a402f90a.sandbox.novita.ai/api/data/add-theme \
  -H "Content-Type: application/json" \
  -d '{
    "name": "量子计算",
    "description": "量子计算相关概念"
  }'
```

---

### 4. 获取所有题材

**接口**: `GET /api/data/themes`

**功能**: 获取系统中所有题材列表

**响应示例**:
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "name": "人工智能",
      "description": "AI相关概念"
    },
    {
      "id": 2,
      "name": "新能源汽车",
      "description": "新能源汽车产业链"
    }
  ]
}
```

**curl 示例**:
```bash
curl https://5000-i1m9fpfr5tksghv87yttz-a402f90a.sandbox.novita.ai/api/data/themes
```

---

### 5. 获取所有股票

**接口**: `GET /api/data/stocks`

**功能**: 获取系统中所有股票列表

**响应示例**:
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "code": "000001",
      "name": "平安银行",
      "market": "SZ"
    },
    {
      "id": 2,
      "code": "000002",
      "name": "万科A",
      "market": "SZ"
    }
  ]
}
```

**curl 示例**:
```bash
curl https://5000-i1m9fpfr5tksghv87yttz-a402f90a.sandbox.novita.ai/api/data/stocks
```

---

## 💡 使用流程

### 完整流程示例

假设你要提交2026-01-28的"量子计算"题材的涨停数据：

#### 步骤1: 检查题材是否存在
```bash
curl https://5000-i1m9fpfr5tksghv87yttz-a402f90a.sandbox.novita.ai/api/data/themes
```

#### 步骤2: 如果题材不存在，先添加题材
```bash
curl -X POST https://5000-i1m9fpfr5tksghv87yttz-a402f90a.sandbox.novita.ai/api/data/add-theme \
  -H "Content-Type: application/json" \
  -d '{
    "name": "量子计算",
    "description": "量子计算相关概念"
  }'
```

#### 步骤3: 提交涨停数据
```bash
curl -X POST https://5000-i1m9fpfr5tksghv87yttz-a402f90a.sandbox.novita.ai/api/data/submit \
  -H "Content-Type: application/json" \
  -d '{
    "date": "2026-01-28",
    "theme": "量子计算",
    "stocks": [
      {
        "code": "300768",
        "name": "迪普科技",
        "reason": "量子通信板块活跃",
        "limit_up_time": "09:35",
        "open_count": 0
      },
      {
        "code": "688027",
        "name": "国盾量子",
        "reason": "量子科技龙头",
        "limit_up_time": "09:30",
        "open_count": 0
      }
    ]
  }'
```

---

## 📱 Python 调用示例

### 示例1: 批量提交涨停数据

```python
import requests
import json

API_BASE = "https://5000-i1m9fpfr5tksghv87yttz-a402f90a.sandbox.novita.ai"

def submit_limit_up_data(date, theme, stocks):
    """提交涨停数据"""
    url = f"{API_BASE}/api/data/submit"
    
    data = {
        "date": date,
        "theme": theme,
        "stocks": stocks
    }
    
    response = requests.post(url, json=data)
    return response.json()

# 使用示例
stocks_data = [
    {
        "code": "000001",
        "name": "平安银行",
        "reason": "AI概念爆发",
        "limit_up_time": "09:30",
        "open_count": 0
    },
    {
        "code": "000002",
        "name": "万科A",
        "reason": "人工智能应用",
        "limit_up_time": "10:15",
        "open_count": 1
    }
]

result = submit_limit_up_data("2026-01-28", "人工智能", stocks_data)
print(json.dumps(result, ensure_ascii=False, indent=2))
```

### 示例2: 添加题材和股票

```python
import requests

API_BASE = "https://5000-i1m9fpfr5tksghv87yttz-a402f90a.sandbox.novita.ai"

# 1. 添加题材
def add_theme(name, description=""):
    url = f"{API_BASE}/api/data/add-theme"
    data = {"name": name, "description": description}
    response = requests.post(url, json=data)
    return response.json()

# 2. 添加股票
def add_stock(code, name, market="SZ"):
    url = f"{API_BASE}/api/data/add-stock"
    data = {"code": code, "name": name, "market": market}
    response = requests.post(url, json=data)
    return response.json()

# 使用
result1 = add_theme("量子计算", "量子计算相关概念")
print(result1)

result2 = add_stock("300768", "迪普科技", "SZ")
print(result2)
```

### 示例3: 获取数据列表

```python
import requests

API_BASE = "https://5000-i1m9fpfr5tksghv87yttz-a402f90a.sandbox.novita.ai"

# 获取所有题材
def get_all_themes():
    url = f"{API_BASE}/api/data/themes"
    response = requests.get(url)
    return response.json()

# 获取所有股票
def get_all_stocks():
    url = f"{API_BASE}/api/data/stocks"
    response = requests.get(url)
    return response.json()

# 使用
themes = get_all_themes()
print("题材列表:", themes)

stocks = get_all_stocks()
print("股票列表:", stocks)
```

---

## 🔄 完整工作流示例

```python
import requests
import json

API_BASE = "https://5000-i1m9fpfr5tksghv87yttz-a402f90a.sandbox.novita.ai"

# 1. 检查题材是否存在
themes_response = requests.get(f"{API_BASE}/api/data/themes")
themes = themes_response.json()['data']
theme_names = [t['name'] for t in themes]

# 2. 如果题材不存在，先添加
if "量子计算" not in theme_names:
    add_theme_response = requests.post(
        f"{API_BASE}/api/data/add-theme",
        json={"name": "量子计算", "description": "量子计算相关概念"}
    )
    print("添加题材:", add_theme_response.json())

# 3. 提交涨停数据
submit_data = {
    "date": "2026-01-28",
    "theme": "量子计算",
    "stocks": [
        {
            "code": "300768",
            "name": "迪普科技",
            "reason": "量子通信板块活跃",
            "limit_up_time": "09:35"
        },
        {
            "code": "688027",
            "name": "国盾量子",
            "reason": "量子科技龙头",
            "limit_up_time": "09:30"
        }
    ]
}

submit_response = requests.post(
    f"{API_BASE}/api/data/submit",
    json=submit_data
)
result = submit_response.json()
print("\n提交结果:", json.dumps(result, ensure_ascii=False, indent=2))

# 4. 分析题材
analyze_url = f"{API_BASE}/api/theme/position?theme=量子计算&date=2026-01-28"
analyze_response = requests.get(analyze_url)
print("\n分析结果:", json.dumps(analyze_response.json(), ensure_ascii=False, indent=2))
```

---

## ⚠️ 注意事项

1. **自动创建**: 如果题材不存在，系统会自动创建
2. **股票信息**: 如果股票不存在，必须在stocks数组中提供name字段
3. **重复提交**: 相同日期、相同题材、相同股票的涨停记录不能重复提交
4. **日期格式**: 必须使用 YYYY-MM-DD 格式
5. **批量提交**: 建议使用批量接口，效率更高

---

## 📋 错误代码

| 错误信息 | 说明 | 解决方案 |
|---------|------|---------|
| 请求体不能为空 | POST请求未发送JSON数据 | 检查Content-Type和请求体 |
| 缺少必需字段 | 缺少date、theme或stocks | 补充必需字段 |
| 日期格式错误 | 日期格式不正确 | 使用YYYY-MM-DD格式 |
| 股票已存在 | 股票代码重复 | 使用已存在的股票 |
| 题材已存在 | 题材名称重复 | 使用已存在的题材 |
| 涨停记录已存在 | 该股票该日期该题材已有记录 | 不要重复提交 |

---

## 🎯 快速测试

使用curl快速测试接口是否正常：

```bash
# 测试1: 获取题材列表
curl https://5000-i1m9fpfr5tksghv87yttz-a402f90a.sandbox.novita.ai/api/data/themes

# 测试2: 添加新题材
curl -X POST https://5000-i1m9fpfr5tksghv87yttz-a402f90a.sandbox.novita.ai/api/data/add-theme \
  -H "Content-Type: application/json" \
  -d '{"name":"测试题材","description":"这是测试"}'

# 测试3: 提交涨停数据
curl -X POST https://5000-i1m9fpfr5tksghv87yttz-a402f90a.sandbox.novita.ai/api/data/submit \
  -H "Content-Type: application/json" \
  -d '{
    "date":"2026-01-28",
    "theme":"人工智能",
    "stocks":[
      {"code":"000001","name":"平安银行","reason":"AI概念"}
    ]
  }'
```

完成！现在你可以通过API手动提交涨停数据了。
