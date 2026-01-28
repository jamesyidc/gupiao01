# 操作日志功能使用指南

## 📋 功能概述

操作日志系统记录所有数据操作，支持查看操作历史和删除日志以回滚错误数据。

## 🎯 主要功能

### 1. 自动记录操作

系统自动记录以下操作：
- ➕ **添加涨停记录** - 记录提交的日期、题材、股票代码和数量
- 🗑️ **删除涨停记录** - 记录被删除的股票信息

每条日志包含：
- 操作类型（添加/删除）
- 操作时间
- 操作详情（题材、日期、股票等）
- 操作者IP地址
- 关联的数据记录ID（用于回滚）

### 2. 查看操作日志

#### Web界面查看
1. 点击主界面的 **📋 操作日志** 按钮
2. 查看最近的操作历史（显示前20条）
3. 每条日志显示：
   - 操作类型标签（绿色=添加，红色=删除）
   - 操作时间
   - 操作详情
   - IP地址
   - **🗑️ 回滚** 按钮

#### API查看
```bash
# 获取操作日志列表（分页）
curl "http://localhost:5000/api/logs?page=1&page_size=20"

# 过滤特定类型
curl "http://localhost:5000/api/logs?operation_type=add"

# 过滤特定目标类型
curl "http://localhost:5000/api/logs?target_type=limit_up_record"
```

### 3. 删除日志并回滚数据 🔄

当发现数据录入错误时，可以删除对应的日志来回滚数据：

#### Web界面操作
1. 点击 **📋 操作日志** 打开日志列表
2. 找到需要回滚的操作记录
3. 点击该记录右侧的 **🗑️ 回滚** 按钮
4. 确认操作
5. 系统将：
   - 删除该日志记录
   - 自动删除该操作添加的所有涨停记录
   - 显示回滚详情

#### API操作
```bash
# 删除日志ID为1的记录并回滚数据
curl -X DELETE "http://localhost:5000/api/logs/1"
```

返回示例：
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

## 📝 使用场景

### 场景1: 录入错误纠正
**问题**: 不小心把2026-01-28的数据录成了2026-01-29

**解决步骤**:
1. 打开操作日志
2. 找到错误的提交记录（显示日期: 2026-01-29）
3. 点击 **🗑️ 回滚** 按钮
4. 确认回滚，系统自动删除错误数据
5. 重新提交正确的数据（日期: 2026-01-28）

### 场景2: 题材分类错误
**问题**: 把"人工智能"题材的股票误录为"新能源汽车"

**解决步骤**:
1. 打开操作日志
2. 找到错误的提交（题材: 新能源汽车）
3. 点击 **🗑️ 回滚** 删除错误记录
4. 重新提交到正确题材（题材: 人工智能）

### 场景3: 股票代码错误
**问题**: 误录入了错误的股票代码

**解决步骤**:
1. 查看操作日志
2. 找到包含错误股票代码的提交记录
3. 点击回滚按钮删除整批数据
4. 重新提交正确的股票代码列表

### 场景4: 批量删除测试数据
**问题**: 测试时添加了一些测试数据，需要清理

**解决步骤**:
1. 打开操作日志
2. 逐条回滚测试数据的提交记录
3. 或通过API批量删除

## ⚠️ 注意事项

### 回滚机制说明
- **回滚范围**: 删除日志会回滚该操作添加的所有数据
- **不可撤销**: 回滚操作是永久的，无法恢复
- **关联删除**: 会删除该日志记录的所有关联涨停记录

### 最佳实践
1. **谨慎删除**: 删除前仔细核对日志详情
2. **及时纠错**: 发现错误及时回滚，避免影响分析结果
3. **定期检查**: 定期查看操作日志，确保数据质量
4. **备份重要数据**: 对于重要的历史数据，可以考虑导出备份

### 回滚限制
目前支持回滚的操作类型：
- ✅ 添加涨停记录（add + limit_up_record）
- ❌ 删除操作暂不支持回滚（因为原数据已被删除）

## 🔍 API接口详解

### 1. 获取操作日志列表

**接口**: `GET /api/logs`

**请求参数**:
| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| page | int | 否 | 页码，默认1 |
| page_size | int | 否 | 每页条数，默认20 |
| operation_type | string | 否 | 操作类型过滤：add/delete |
| target_type | string | 否 | 目标类型过滤：limit_up_record/stock/theme |

**返回示例**:
```json
{
    "success": true,
    "data": [
        {
            "id": 1,
            "operation_type": "add",
            "operation_time": "2026-01-28 10:00:00",
            "target_type": "limit_up_record",
            "target_id": null,
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
    "total": 100,
    "page": 1,
    "page_size": 20,
    "total_pages": 5
}
```

### 2. 删除操作日志并回滚数据

**接口**: `DELETE /api/logs/{log_id}`

**请求参数**:
- `log_id`: 日志ID（路径参数）

**返回示例**:
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

## 💡 高级技巧

### 1. 批量回滚脚本

如果需要批量删除多条日志，可以使用以下脚本：

```python
import requests

API_BASE = "http://localhost:5000"

# 获取最近的日志
response = requests.get(f"{API_BASE}/api/logs?page=1&page_size=10")
logs = response.json()['data']

# 回滚符合条件的日志
for log in logs:
    if log['details'].get('theme') == '测试题材':
        print(f"回滚日志 {log['id']}: {log['details']}")
        delete_response = requests.delete(f"{API_BASE}/api/logs/{log['id']}")
        print(delete_response.json())
```

### 2. 导出日志记录

```bash
# 导出所有日志到JSON文件
curl "http://localhost:5000/api/logs?page=1&page_size=1000" > operation_logs.json

# 导出特定类型的日志
curl "http://localhost:5000/api/logs?operation_type=add&page_size=500" > add_logs.json
```

### 3. 日志分析

```python
import requests
import pandas as pd

# 获取所有日志
response = requests.get("http://localhost:5000/api/logs?page_size=1000")
logs = response.json()['data']

# 转换为DataFrame分析
df = pd.DataFrame(logs)

# 统计操作类型
print("操作类型统计:")
print(df['operation_type'].value_counts())

# 按题材统计添加次数
add_logs = [log for log in logs if log['operation_type'] == 'add']
themes = [log['details'].get('theme') for log in add_logs]
print("\n题材添加次数统计:")
print(pd.Series(themes).value_counts())
```

## 🎨 界面说明

### 日志列表界面
```
📋 操作日志与数据管理
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
最近操作日志（前20条）

┌─────────────────────────────────────┐
│ ➕ 添加     2026-01-28 10:00:00     │ 🗑️ 回滚
│ 题材：人工智能, 日期：2026-01-28,   │
│ 添加 3 只股票 (000001, 000002,      │
│ 600519)                              │
│ IP: 127.0.0.1                        │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│ 🗑️ 删除     2026-01-28 09:45:00     │ 🗑️ 回滚
│ 删除：000033 同花顺 (人工智能,       │
│ 2026-01-27)                          │
│ IP: 192.168.1.100                    │
└─────────────────────────────────────┘
```

### 回滚确认弹窗
```
⚠️  确认回滚操作

确定要删除此日志并回滚相关数据吗？

此操作将：
• 删除日志记录
• 删除该操作添加的 3 条涨停记录
• 股票: 000001, 000002, 600519
• 题材: 人工智能
• 日期: 2026-01-28

⚠️ 此操作不可撤销！

        [取消]    [确定回滚]
```

## 🔗 相关文档

- [批量输入使用指南](./BATCH_INPUT_GUIDE.md)
- [数据提交API文档](./DATA_SUBMIT_API.md)
- [快速开始指南](./QUICK_START.md)

## 📞 技术支持

如有问题请查看：
- 系统日志: `server.log`
- 数据库文件: `stock_analysis.db`
- API文档: `API_TEST.md`
