# 操作日志功能演示

## 🎯 完整演示流程

### 第一步：提交测试数据

在Web界面点击 **➕ 录入数据**，或使用API：

```bash
# 提交涨停数据
curl -X POST http://localhost:5000/api/data/submit-batch \
  -H "Content-Type: application/json" \
  -d '{
    "date": "2026-01-28",
    "theme": "人工智能",
    "stock_codes": ["000001", "000002", "600519"]
  }'
```

**返回结果**:
```json
{
    "success": true,
    "message": "成功提交3条涨停记录",
    "success_count": 3,
    "total_count": 3,
    "details": [
        {"code": "000001", "name": "测试股票1", "status": "✅ 成功"},
        {"code": "000002", "name": "测试股票2", "status": "✅ 成功"},
        {"code": "600519", "name": "贵州茅台", "status": "✅ 成功"}
    ]
}
```

✅ **系统自动记录操作日志**

---

### 第二步：查看操作日志

#### 方式1: Web界面
1. 点击主界面的 **📋 操作日志** 按钮
2. 查看刚才的提交记录

#### 方式2: API查询
```bash
curl "http://localhost:5000/api/logs?page=1&page_size=5"
```

**返回结果**:
```json
{
    "success": true,
    "data": [
        {
            "id": 1,
            "operation_type": "add",
            "operation_time": "2026-01-28 07:00:52",
            "target_type": "limit_up_record",
            "details": {
                "theme": "人工智能",
                "date": "2026-01-28",
                "stock_count": 3,
                "stock_codes": ["000001", "000002", "600519"],
                "record_ids": [568, 569, 570]
            },
            "ip_address": "127.0.0.1"
        }
    ],
    "total": 1,
    "page": 1,
    "page_size": 5
}
```

📋 **日志详细记录了所有操作信息**

---

### 第三步：删除日志并回滚数据

#### 场景：发现数据录入错误，需要纠错

#### 方式1: Web界面
1. 打开操作日志界面
2. 找到需要回滚的记录
3. 点击 **🗑️ 回滚** 按钮
4. 确认操作

#### 方式2: API删除
```bash
curl -X DELETE "http://localhost:5000/api/logs/1"
```

**返回结果**:
```json
{
    "success": true,
    "message": "日志删除成功，已回滚3条涨停记录",
    "rollback_count": 3,
    "rollback_info": [
        "000001(人工智能,2026-01-28)",
        "000002(人工智能,2026-01-28)",
        "600519(人工智能,2026-01-28)"
    ]
}
```

🔄 **系统自动删除了3条涨停记录和日志**

---

### 第四步：验证回滚结果

```bash
# 确认日志已删除
curl "http://localhost:5000/api/logs?page=1&page_size=5"

# 确认涨停记录已删除
curl "http://localhost:5000/api/theme/top-stocks?theme=人工智能&date=2026-01-28"
```

✅ **数据已完全回滚，可以重新提交正确的数据**

---

## 🎬 实际应用场景演示

### 场景1: 日期录入错误

**问题**: 今天是2026-01-28，但误把数据录成了2026-01-29

**解决**:
1. 查看操作日志，找到错误的提交（日期显示2026-01-29）
2. 点击回滚按钮
3. 重新提交正确日期的数据（2026-01-28）

```bash
# 1. 提交了错误的数据
curl -X POST http://localhost:5000/api/data/submit-batch \
  -H "Content-Type: application/json" \
  -d '{"date": "2026-01-29", "theme": "人工智能", "stock_codes": ["000001"]}'

# 2. 发现错误，查看日志
curl "http://localhost:5000/api/logs?page=1&page_size=5"

# 3. 删除错误的日志（假设ID为2）
curl -X DELETE "http://localhost:5000/api/logs/2"

# 4. 重新提交正确的数据
curl -X POST http://localhost:5000/api/data/submit-batch \
  -H "Content-Type: application/json" \
  -d '{"date": "2026-01-28", "theme": "人工智能", "stock_codes": ["000001"]}'
```

---

### 场景2: 题材分类错误

**问题**: 把属于"人工智能"的股票误录到"新能源汽车"

**解决**:
```bash
# 1. 误录入到错误题材
curl -X POST http://localhost:5000/api/data/submit-batch \
  -H "Content-Type: application/json" \
  -d '{
    "date": "2026-01-28",
    "theme": "新能源汽车",
    "stock_codes": ["300033", "002230", "688111"]
  }'

# 2. 发现错误，回滚
curl -X DELETE "http://localhost:5000/api/logs/3"

# 3. 重新提交到正确题材
curl -X POST http://localhost:5000/api/data/submit-batch \
  -H "Content-Type: application/json" \
  -d '{
    "date": "2026-01-28",
    "theme": "人工智能",
    "stock_codes": ["300033", "002230", "688111"]
  }'
```

---

### 场景3: 股票代码错误

**问题**: 录入时打错了股票代码

**解决**:
```bash
# 1. 误录入错误的股票代码
curl -X POST http://localhost:5000/api/data/submit-batch \
  -H "Content-Type: application/json" \
  -d '{
    "date": "2026-01-28",
    "theme": "人工智能",
    "stock_codes": ["000001", "000099", "999999"]
  }'
# 注意：000099 和 999999 可能是错误的代码

# 2. 查看提交结果，发现错误
curl "http://localhost:5000/api/logs?page=1&page_size=1"

# 3. 回滚整批数据
curl -X DELETE "http://localhost:5000/api/logs/4"

# 4. 重新提交正确的代码
curl -X POST http://localhost:5000/api/data/submit-batch \
  -H "Content-Type: application/json" \
  -d '{
    "date": "2026-01-28",
    "theme": "人工智能",
    "stock_codes": ["000001", "000002", "600519"]
  }'
```

---

### 场景4: 清理测试数据

**问题**: 测试时添加了很多测试数据，需要批量清理

**解决**:
```python
import requests

API_BASE = "http://localhost:5000"

# 1. 获取所有日志
response = requests.get(f"{API_BASE}/api/logs?page=1&page_size=100")
logs = response.json()['data']

# 2. 筛选测试数据的日志
test_logs = [
    log for log in logs 
    if '测试' in log['details'].get('theme', '')
]

print(f"找到 {len(test_logs)} 条测试数据日志")

# 3. 批量回滚
for log in test_logs:
    print(f"回滚日志 {log['id']}: {log['details']}")
    response = requests.delete(f"{API_BASE}/api/logs/{log['id']}")
    result = response.json()
    print(f"  - {result['message']}")
    print(f"  - 回滚了 {result['rollback_count']} 条记录")
```

---

## 📊 日志统计分析

### 统计操作次数
```python
import requests
import pandas as pd

# 获取所有日志
response = requests.get("http://localhost:5000/api/logs?page_size=1000")
logs = response.json()['data']

# 转换为DataFrame
df = pd.DataFrame(logs)

print("=== 操作统计 ===")
print(f"总操作次数: {len(df)}")
print(f"添加操作: {len(df[df['operation_type'] == 'add'])}")
print(f"删除操作: {len(df[df['operation_type'] == 'delete'])}")

print("\n=== 每日操作统计 ===")
df['date'] = pd.to_datetime(df['operation_time']).dt.date
daily_stats = df.groupby('date').size()
print(daily_stats)

print("\n=== 题材统计 ===")
add_logs = df[df['operation_type'] == 'add']
themes = []
for details in add_logs['details']:
    if isinstance(details, dict):
        themes.append(details.get('theme', '未知'))

theme_counts = pd.Series(themes).value_counts()
print(theme_counts)
```

---

## 🎨 界面展示

### 操作日志界面
```
┌─────────────────────────────────────────────────────────┐
│                   📋 操作日志与数据管理                  │
│                                                          │
│  最近操作日志（前20条）                                 │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │
│                                                          │
│  ┌────────────────────────────────────────────────┐   │
│  │ ➕ 添加      2026-01-28 10:00:00          🗑️ 回滚 │   │
│  │                                                 │   │
│  │ 题材：人工智能, 日期：2026-01-28,              │   │
│  │ 添加 3 只股票 (000001, 000002, 600519)        │   │
│  │                                                 │   │
│  │ IP: 127.0.0.1                                   │   │
│  └────────────────────────────────────────────────┘   │
│                                                          │
│  ┌────────────────────────────────────────────────┐   │
│  │ ➕ 添加      2026-01-28 09:30:00          🗑️ 回滚 │   │
│  │                                                 │   │
│  │ 题材：新能源汽车, 日期：2026-01-28,           │   │
│  │ 添加 5 只股票 (002594, 300750, ...)           │   │
│  │                                                 │   │
│  │ IP: 192.168.1.100                               │   │
│  └────────────────────────────────────────────────┘   │
│                                                          │
│  ┌────────────────────────────────────────────────┐   │
│  │ 🗑️ 删除     2026-01-27 16:00:00          🗑️ 回滚 │   │
│  │                                                 │   │
│  │ 删除：000033 同花顺 (人工智能, 2026-01-27)    │   │
│  │                                                 │   │
│  │ IP: 127.0.0.1                                   │   │
│  └────────────────────────────────────────────────┘   │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

### 回滚确认弹窗
```
┌──────────────────────────────────────┐
│        ⚠️  确认回滚操作               │
│                                       │
│  确定要删除此日志并回滚相关数据吗？  │
│                                       │
│  此操作将：                           │
│  • 删除日志记录                       │
│  • 删除该操作添加的 3 条涨停记录     │
│  • 股票: 000001, 000002, 600519      │
│  • 题材: 人工智能                     │
│  • 日期: 2026-01-28                   │
│                                       │
│  ⚠️ 此操作不可撤销！                 │
│                                       │
│           [取消]    [确定回滚]        │
└──────────────────────────────────────┘
```

### 回滚成功通知
```
┌──────────────────────────────────────┐
│  ✅ 日志删除成功，已回滚3条涨停记录  │
│                                       │
│  已回滚记录:                          │
│  • 000001(人工智能,2026-01-28)       │
│  • 000002(人工智能,2026-01-28)       │
│  • 600519(人工智能,2026-01-28)       │
└──────────────────────────────────────┘
```

---

## 📌 要点总结

### ✅ 功能优势
1. **自动记录**: 所有操作自动记录，无需手动
2. **详细信息**: 记录操作时间、IP、详情等完整信息
3. **一键回滚**: 点击按钮即可回滚错误数据
4. **批量纠错**: 支持批量删除和回滚
5. **可追溯**: 完整的操作历史便于审计

### ⚠️ 使用注意
1. **谨慎删除**: 回滚操作不可撤销
2. **及时纠错**: 发现错误及时处理
3. **定期检查**: 定期查看日志确保数据质量
4. **备份重要数据**: 对重要数据考虑导出备份

### 🔗 相关文档
- [操作日志功能使用指南](./OPERATION_LOG_GUIDE.md)
- [批量输入使用指南](./BATCH_INPUT_GUIDE.md)
- [数据提交API文档](./DATA_SUBMIT_API.md)

---

**系统已就绪，开始使用吧！** 🚀
