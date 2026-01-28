// API 基础配置
const API_BASE_URL = window.location.origin;

// 全局变量
let positionChart = null;
let compareChart = null;
let currentThemeData = null;

// 工具函数
function showLoading() {
    document.getElementById('loading').style.display = 'block';
    document.getElementById('error-message').style.display = 'none';
}

function hideLoading() {
    document.getElementById('loading').style.display = 'none';
}

function showError(message) {
    const errorElement = document.getElementById('error-message');
    errorElement.textContent = message;
    errorElement.style.display = 'block';
    hideLoading();
}

function hideError() {
    document.getElementById('error-message').style.display = 'none';
}

function formatNumber(num, decimals = 2) {
    return Number(num).toFixed(decimals);
}

function getPositionClass(percent) {
    if (percent < 30) return 'position-low';
    if (percent < 70) return 'position-mid';
    return 'position-high';
}

function getStrengthBadgeClass(strength) {
    if (strength === '强于题材') return 'badge-success';
    if (strength === '弱于题材') return 'badge-danger';
    return 'badge-warning';
}

// API 调用函数
async function fetchThemeTopStocks(theme, date) {
    const response = await fetch(
        `${API_BASE_URL}/api/theme/top-stocks?theme=${encodeURIComponent(theme)}&date=${date}`
    );
    const data = await response.json();
    if (!data.success) {
        throw new Error(data.error || '获取题材成分股失败');
    }
    return data.data;
}

async function fetchThemePosition(theme, date) {
    const response = await fetch(
        `${API_BASE_URL}/api/theme/position?theme=${encodeURIComponent(theme)}&date=${date}`
    );
    const data = await response.json();
    if (!data.success) {
        throw new Error(data.error || '获取题材位置失败');
    }
    return data.data;
}

async function fetchStockPosition(code, date) {
    const response = await fetch(
        `${API_BASE_URL}/api/stock/position?code=${code}&date=${date}`
    );
    const data = await response.json();
    if (!data.success) {
        throw new Error(data.error || '获取个股位置失败');
    }
    return data.data;
}

async function fetchCompareAnalysis(code, theme, date) {
    const response = await fetch(
        `${API_BASE_URL}/api/analysis/compare?code=${code}&theme=${encodeURIComponent(theme)}&date=${date}`
    );
    const data = await response.json();
    if (!data.success) {
        throw new Error(data.error || '对比分析失败');
    }
    return data.data;
}

// 显示题材分析结果
function displayThemeResults(data) {
    // 显示基本信息
    document.getElementById('theme-name').textContent = data.theme_name;
    document.getElementById('theme-date').textContent = data.target_date;
    document.getElementById('theme-count').textContent = data.constituent_count;
    document.getElementById('theme-position').textContent = `${formatNumber(data.theme_position_percent)}%`;

    // 更新位置条
    const positionBar = document.getElementById('theme-position-bar');
    positionBar.style.width = `${data.theme_position_percent}%`;

    // 显示成分股列表
    const tbody = document.getElementById('stocks-tbody');
    tbody.innerHTML = '';
    
    data.constituent_stocks.forEach((stock, index) => {
        const row = document.createElement('tr');
        const positionClass = getPositionClass(stock.position_percent);
        
        row.innerHTML = `
            <td>${index + 1}</td>
            <td><strong>${stock.code}</strong></td>
            <td>${stock.name}</td>
            <td><span class="badge badge-success">${stock.limit_up_count}</span></td>
            <td>¥${formatNumber(stock.current_price)}</td>
            <td class="position-cell ${positionClass}">${formatNumber(stock.position_percent)}%</td>
            <td>
                <button class="btn btn-primary btn-small" onclick="analyzeStock('${stock.code}')">
                    分析
                </button>
            </td>
        `;
        tbody.appendChild(row);
    });

    // 绘制位置分布图表
    drawPositionChart(data.constituent_stocks);

    // 显示结果卡片
    document.getElementById('theme-results').style.display = 'block';
    
    // 保存数据供后续使用
    currentThemeData = data;
}

// 绘制位置分布图表
function drawPositionChart(stocks) {
    const ctx = document.getElementById('position-chart');
    
    // 销毁旧图表
    if (positionChart) {
        positionChart.destroy();
    }

    const labels = stocks.map(s => s.code);
    const positions = stocks.map(s => s.position_percent);
    const colors = positions.map(p => {
        if (p < 30) return '#10b981';
        if (p < 70) return '#f59e0b';
        return '#ef4444';
    });

    positionChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: '位置百分比 (%)',
                data: positions,
                backgroundColor: colors,
                borderColor: colors,
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return `位置: ${formatNumber(context.parsed.y)}%`;
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100,
                    ticks: {
                        callback: function(value) {
                            return value + '%';
                        }
                    }
                }
            }
        }
    });
}

// 显示对比分析结果
function displayCompareResults(data) {
    const stockInfo = data.stock_info;
    const themeInfo = data.theme_info;
    const comparison = data.comparison;

    // 个股信息
    document.getElementById('stock-code').textContent = stockInfo.stock_code;
    document.getElementById('stock-name').textContent = stockInfo.stock_name;
    document.getElementById('stock-price').textContent = `¥${formatNumber(stockInfo.current_price)}`;
    document.getElementById('stock-position').textContent = `${formatNumber(stockInfo.position_percent)}%`;

    // 题材信息
    document.getElementById('compare-theme-name').textContent = themeInfo.theme_name;
    document.getElementById('compare-constituent-count').textContent = themeInfo.constituent_count;
    document.getElementById('is-constituent').textContent = comparison.is_constituent_stock ? '是' : '否';
    document.getElementById('compare-theme-position').textContent = `${formatNumber(themeInfo.theme_position_percent)}%`;

    // 对比结果
    const diffElement = document.getElementById('position-diff');
    const diff = comparison.position_difference;
    diffElement.textContent = `${diff > 0 ? '+' : ''}${formatNumber(diff)}%`;
    diffElement.style.color = diff > 0 ? '#10b981' : '#ef4444';

    const strengthElement = document.getElementById('relative-strength');
    strengthElement.textContent = comparison.relative_strength;
    strengthElement.className = `result-value badge ${getStrengthBadgeClass(comparison.relative_strength)}`;

    // 绘制对比图表
    drawCompareChart(stockInfo.position_percent, themeInfo.theme_position_percent);

    // 显示分析建议
    displayAdvice(comparison);

    // 显示结果卡片
    document.getElementById('compare-results').style.display = 'block';
}

// 绘制对比图表
function drawCompareChart(stockPos, themePos) {
    const ctx = document.getElementById('compare-chart');
    
    // 销毁旧图表
    if (compareChart) {
        compareChart.destroy();
    }

    compareChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['个股位置', '题材位置'],
            datasets: [{
                label: '位置百分比 (%)',
                data: [stockPos, themePos],
                backgroundColor: [
                    stockPos > themePos ? '#10b981' : '#ef4444',
                    '#667eea'
                ],
                borderColor: [
                    stockPos > themePos ? '#10b981' : '#ef4444',
                    '#667eea'
                ],
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100,
                    ticks: {
                        callback: function(value) {
                            return value + '%';
                        }
                    }
                }
            }
        }
    });
}

// 显示分析建议
function displayAdvice(comparison) {
    const adviceBox = document.getElementById('analysis-advice');
    let adviceContent = '<h4>💡 分析建议</h4>';

    if (comparison.relative_strength === '强于题材') {
        adviceContent += `
            <p>该股票表现<strong>强于题材整体</strong>，可能是板块龙头股。</p>
            <p>• 强势特征明显，后续可能继续领涨</p>
            <p>• 注意追高风险，等待回调机会</p>
            <p>• 建议密切关注成交量变化</p>
        `;
    } else if (comparison.relative_strength === '弱于题材') {
        adviceContent += `
            <p>该股票表现<strong>弱于题材整体</strong>，可能存在补涨机会。</p>
            <p>• 如果基本面良好，可关注补涨机会</p>
            <p>• 需要等待题材持续活跃</p>
            <p>• 注意风险，可能是弱势股</p>
        `;
    } else {
        adviceContent += `
            <p>该股票与题材走势<strong>基本同步</strong>。</p>
            <p>• 走势稳健，跟随题材节奏</p>
            <p>• 观察题材热度变化</p>
            <p>• 可作为题材标的关注</p>
        `;
    }

    // 根据位置给出建议
    const stockPos = comparison.position_difference;
    if (stockPos < 20) {
        adviceContent += `<p><strong>位置分析：</strong>处于底部区域，相对安全，适合中长期布局。</p>`;
    } else if (stockPos < 40) {
        adviceContent += `<p><strong>位置分析：</strong>处于中低位，仍有上涨空间，可适量参与。</p>`;
    } else if (stockPos < 60) {
        adviceContent += `<p><strong>位置分析：</strong>处于中位，需要观察市场情绪，控制仓位。</p>`;
    } else if (stockPos < 80) {
        adviceContent += `<p><strong>位置分析：</strong>处于中高位，需谨慎追高，注意止盈。</p>`;
    } else {
        adviceContent += `<p><strong>位置分析：</strong>处于顶部区域，风险较高，建议观望或减仓。</p>`;
    }

    adviceBox.innerHTML = adviceContent;
}

// 分析题材
async function analyzeTheme() {
    const theme = document.getElementById('theme-select').value;
    const date = document.getElementById('date-input').value;

    if (!theme) {
        showError('请选择题材');
        return;
    }

    if (!date) {
        showError('请选择日期');
        return;
    }

    try {
        showLoading();
        hideError();

        const data = await fetchThemePosition(theme, date);
        displayThemeResults(data);
        hideLoading();
    } catch (error) {
        showError(error.message);
    }
}

// 对比分析
async function compareAnalysis() {
    const theme = document.getElementById('theme-select').value;
    const date = document.getElementById('date-input').value;
    const stockCode = document.getElementById('stock-input').value.trim();

    if (!theme) {
        showError('请选择题材');
        return;
    }

    if (!date) {
        showError('请选择日期');
        return;
    }

    if (!stockCode) {
        showError('请输入股票代码');
        return;
    }

    try {
        showLoading();
        hideError();

        const data = await fetchCompareAnalysis(stockCode, theme, date);
        displayCompareResults(data);
        hideLoading();
    } catch (error) {
        showError(error.message);
    }
}

// 分析特定股票（从表格点击）
async function analyzeStock(stockCode) {
    const theme = document.getElementById('theme-select').value;
    const date = document.getElementById('date-input').value;

    // 设置股票代码
    document.getElementById('stock-input').value = stockCode;

    // 执行对比分析
    try {
        showLoading();
        hideError();

        const data = await fetchCompareAnalysis(stockCode, theme, date);
        displayCompareResults(data);
        hideLoading();

        // 滚动到对比结果
        document.getElementById('compare-results').scrollIntoView({ 
            behavior: 'smooth',
            block: 'start'
        });
    } catch (error) {
        showError(error.message);
    }
}

// 清空结果
function clearResults() {
    document.getElementById('theme-results').style.display = 'none';
    document.getElementById('compare-results').style.display = 'none';
    document.getElementById('stock-input').value = '';
    hideError();
    
    // 销毁图表
    if (positionChart) {
        positionChart.destroy();
        positionChart = null;
    }
    if (compareChart) {
        compareChart.destroy();
        compareChart = null;
    }
}

// 初始化
document.addEventListener('DOMContentLoaded', function() {
    // 绑定按钮事件
    document.getElementById('btn-analyze-theme').addEventListener('click', analyzeTheme);
    document.getElementById('btn-compare').addEventListener('click', compareAnalysis);
    document.getElementById('btn-clear').addEventListener('click', clearResults);
    document.getElementById('btn-add-data').addEventListener('click', openDataModal);
    document.getElementById('btn-view-logs').addEventListener('click', openLogsModal);

    // 回车键快捷操作
    document.getElementById('stock-input').addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            compareAnalysis();
        }
    });

    // 模态框相关
    document.getElementById('modal-close').addEventListener('click', closeDataModal);
    document.getElementById('btn-cancel').addEventListener('click', closeDataModal);
    document.getElementById('submit-form').addEventListener('submit', submitData);
    
    // 日志模态框
    document.getElementById('logs-modal-close').addEventListener('click', closeLogsModal);
    document.getElementById('btn-filter-records').addEventListener('click', loadRecords);
    document.getElementById('btn-clear-filter').addEventListener('click', clearFilter);
    document.getElementById('btn-select-all').addEventListener('click', toggleSelectAll);
    document.getElementById('btn-delete-selected').addEventListener('click', deleteSelected);
    document.getElementById('select-all-checkbox').addEventListener('change', function() {
        document.querySelectorAll('.record-checkbox').forEach(cb => {
            cb.checked = this.checked;
        });
    });

    // 点击模态框外部关闭
    document.getElementById('data-modal').addEventListener('click', function(e) {
        if (e.target.id === 'data-modal') {
            closeDataModal();
        }
    });

    // 设置默认日期为今天
    const today = new Date().toISOString().split('T')[0];
    document.getElementById('submit-date').value = today;
    
    // 实时显示股票代码数量
    const stockCodesInput = document.getElementById('stock-codes');
    const stockCountDisplay = document.getElementById('stock-count-display');
    const expectedCountInput = document.getElementById('expected-count');
    
    function updateStockCount() {
        const text = stockCodesInput.value.trim();
        if (!text) {
            stockCountDisplay.textContent = '';
            return;
        }
        
        const codes = text
            .split('\n')
            .map(line => line.trim())
            .filter(line => line.length > 0)
            .filter(code => /^\d{6}$/.test(code));
        
        const count = codes.length;
        const expectedCount = expectedCountInput.value ? parseInt(expectedCountInput.value) : null;
        
        if (expectedCount && count !== expectedCount) {
            stockCountDisplay.innerHTML = `<span style="color: #f59e0b;">⚠️ 实际数量：${count} 只（预期 ${expectedCount} 只）</span>`;
        } else if (expectedCount) {
            stockCountDisplay.innerHTML = `<span style="color: #10b981;">✅ 实际数量：${count} 只（匹配）</span>`;
        } else {
            stockCountDisplay.innerHTML = `<span style="color: #667eea;">📊 实际数量：${count} 只</span>`;
        }
    }
    
    stockCodesInput.addEventListener('input', updateStockCount);
    expectedCountInput.addEventListener('input', updateStockCount);

    console.log('股票数据研究系统已加载');
});

// ============ 数据录入功能 ============

function openDataModal() {
    document.getElementById('data-modal').style.display = 'flex';
    document.getElementById('submit-result').style.display = 'none';
}

function closeDataModal() {
    document.getElementById('data-modal').style.display = 'none';
    document.getElementById('submit-form').reset();
    
    // 重置日期为今天
    const today = new Date().toISOString().split('T')[0];
    document.getElementById('submit-date').value = today;
}

async function submitData(e) {
    e.preventDefault();
    
    const date = document.getElementById('submit-date').value;
    const theme = document.getElementById('submit-theme').value.trim();
    const stockCodesText = document.getElementById('stock-codes').value.trim();
    const expectedCountInput = document.getElementById('expected-count').value;
    
    if (!date || !theme) {
        alert('请填写日期和题材名称');
        return;
    }
    
    if (!stockCodesText) {
        alert('请输入至少一个股票代码');
        return;
    }
    
    // 解析股票代码（每行一个）
    const stockCodes = stockCodesText
        .split('\n')
        .map(line => line.trim())
        .filter(line => line.length > 0)
        .filter(code => /^\d{6}$/.test(code)); // 验证是6位数字
    
    if (stockCodes.length === 0) {
        alert('请输入有效的股票代码（6位数字）');
        return;
    }
    
    // 数量验证（防呆设计）
    const expectedCount = expectedCountInput ? parseInt(expectedCountInput) : null;
    const actualCount = stockCodes.length;
    
    if (expectedCount && expectedCount !== actualCount) {
        const confirmMsg = `⚠️ 数量不匹配！\n\n预期：${expectedCount} 只股票\n实际：${actualCount} 只股票\n\n是否继续提交？`;
        if (!confirm(confirmMsg)) {
            return;
        }
    }
    
    // 显示处理中的提示
    const resultDiv = document.getElementById('submit-result');
    resultDiv.style.display = 'block';
    resultDiv.className = 'submit-success';
    resultDiv.innerHTML = `<p>正在处理 ${stockCodes.length} 只股票...</p>`;
    
    try {
        showLoading();
        
        // 构建请求数据
        const requestData = {
            date: date,
            theme: theme,
            stock_codes: stockCodes
        };
        
        // 如果有预期数量，添加到请求中（严格验证）
        if (expectedCount) {
            requestData.expected_count = expectedCount;
        }
        
        const response = await fetch(`${API_BASE_URL}/api/data/submit-batch`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(requestData)
        });
        
        const result = await response.json();
        hideLoading();
        
        // 显示结果
        resultDiv.style.display = 'block';
        
        if (result.success) {
            resultDiv.className = 'submit-success';
            let message = `✅ ${result.message}\n\n`;
            
            if (result.details) {
                message += '📊 详细信息：\n';
                result.details.forEach(detail => {
                    message += `• ${detail.code} ${detail.name || '未知'} - ${detail.status}\n`;
                });
            }
            
            if (result.errors && result.errors.length > 0) {
                message += '\n⚠️ 部分错误：\n';
                result.errors.forEach(err => {
                    message += `• ${err}\n`;
                });
            }
            
            resultDiv.innerHTML = `<pre style="white-space: pre-wrap; margin: 0;">${message}</pre>`;
            
            // 3秒后关闭模态框
            setTimeout(() => {
                closeDataModal();
                // 如果当前选择的题材和提交的一致，刷新分析
                const currentTheme = document.getElementById('theme-select').value;
                if (currentTheme === theme) {
                    analyzeTheme();
                }
            }, 3000);
        } else {
            resultDiv.className = 'submit-error';
            resultDiv.textContent = `❌ 提交失败：${result.error}`;
        }
        
    } catch (error) {
        hideLoading();
        const resultDiv = document.getElementById('submit-result');
        resultDiv.style.display = 'block';
        resultDiv.className = 'submit-error';
        resultDiv.textContent = `❌ 提交失败：${error.message}`;
    }
}
        }
        
    } catch (error) {
        hideLoading();
        const resultDiv = document.getElementById('submit-result');
        resultDiv.style.display = 'block';
        resultDiv.className = 'submit-error';
        resultDiv.textContent = `❌ 提交失败：${error.message}`;
    }
}

// ============ 日志管理功能 ============

function openLogsModal() {
    document.getElementById('logs-modal').style.display = 'flex';
    loadOperationLogs();
}

function closeLogsModal() {
    document.getElementById('logs-modal').style.display = 'none';
}

async function loadRecords() {
    const theme = document.getElementById('filter-theme').value.trim();
    const date = document.getElementById('filter-date').value;
    const stockCode = document.getElementById('filter-stock').value.trim();
    
    const loadingDiv = document.getElementById('records-loading');
    const tbody = document.getElementById('records-tbody');
    
    loadingDiv.style.display = 'block';
    tbody.innerHTML = '';
    
    try {
        const params = new URLSearchParams();
        if (theme) params.append('theme', theme);
        if (date) params.append('date', date);
        if (stockCode) params.append('stock_code', stockCode);
        params.append('limit', '100');
        
        const response = await fetch(`${API_BASE_URL}/api/logs/limit-up-records?${params}`);
        const result = await response.json();
        
        loadingDiv.style.display = 'none';
        
        if (result.success && result.data.length > 0) {
            tbody.innerHTML = '';
            result.data.forEach(record => {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td><input type="checkbox" class="record-checkbox" value="${record.id}"></td>
                    <td>${record.trade_date}</td>
                    <td><strong>${record.stock_code}</strong></td>
                    <td>${record.stock_name}</td>
                    <td>${record.theme_name}</td>
                    <td>${record.reason || '-'}</td>
                    <td>${record.limit_up_time || '-'}</td>
                    <td>
                        <button class="btn btn-small btn-danger" onclick="deleteRecord(${record.id}, '${record.stock_code}', '${record.stock_name}')">
                            删除
                        </button>
                    </td>
                `;
                tbody.appendChild(row);
            });
        } else {
            tbody.innerHTML = '<tr><td colspan="8" style="text-align: center; padding: 40px;">未找到符合条件的记录</td></tr>';
        }
        
    } catch (error) {
        loadingDiv.style.display = 'none';
        tbody.innerHTML = `<tr><td colspan="8" style="text-align: center; padding: 40px; color: red;">加载失败：${error.message}</td></tr>`;
    }
}

function clearFilter() {
    document.getElementById('filter-theme').value = '';
    document.getElementById('filter-date').value = '';
    document.getElementById('filter-stock').value = '';
    document.getElementById('records-tbody').innerHTML = '<tr><td colspan="8" style="text-align: center; padding: 40px;">点击"查询"加载数据</td></tr>';
}

function toggleSelectAll() {
    const checkboxes = document.querySelectorAll('.record-checkbox');
    const allChecked = Array.from(checkboxes).every(cb => cb.checked);
    checkboxes.forEach(cb => cb.checked = !allChecked);
}

async function deleteRecord(recordId, stockCode, stockName) {
    if (!confirm(`确定要删除记录：${stockCode} ${stockName}？`)) {
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE_URL}/api/logs/delete-record/${recordId}`, {
            method: 'DELETE'
        });
        
        const result = await response.json();
        
        if (result.success) {
            alert(result.message);
            loadRecords();  // 重新加载列表
            loadOperationLogs();  // 刷新日志
        } else {
            alert('删除失败：' + result.error);
        }
    } catch (error) {
        alert('删除失败：' + error.message);
    }
}

async function deleteSelected() {
    const checkboxes = document.querySelectorAll('.record-checkbox:checked');
    
    if (checkboxes.length === 0) {
        alert('请先选择要删除的记录');
        return;
    }
    
    if (!confirm(`确定要删除选中的 ${checkboxes.length} 条记录？`)) {
        return;
    }
    
    const recordIds = Array.from(checkboxes).map(cb => parseInt(cb.value));
    
    try {
        const response = await fetch(`${API_BASE_URL}/api/logs/batch-delete`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                record_ids: recordIds
            })
        });
        
        const result = await response.json();
        
        if (result.success) {
            alert(result.message);
            loadRecords();  // 重新加载列表
            loadOperationLogs();  // 刷新日志
        } else {
            alert('删除失败：' + result.error);
        }
    } catch (error) {
        alert('删除失败：' + error.message);
    }
}

async function loadOperationLogs() {
    const logsContainer = document.getElementById('operation-logs-list');
    logsContainer.innerHTML = '<p style="text-align: center; padding: 20px;">加载中...</p>';
    
    try {
        const response = await fetch(`${API_BASE_URL}/api/logs?page=1&page_size=20`);
        const result = await response.json();
        
        if (result.success && result.data.length > 0) {
            logsContainer.innerHTML = '';
            result.data.forEach(log => {
                const logItem = document.createElement('div');
                logItem.className = `log-item log-${log.operation_type}`;
                
                const typeText = log.operation_type === 'add' ? '➕ 添加' : '🗑️ 删除';
                const typeClass = log.operation_type === 'add' ? 'type-add' : 'type-delete';
                
                let detailsHtml = '';
                if (log.details) {
                    if (log.operation_type === 'add') {
                        // 只显示日期和题材，不展开股票代码
                        detailsHtml = `<strong>${log.details.date}</strong> - ${log.details.theme} (${log.details.stock_count} 只股票)`;
                    } else if (log.operation_type === 'delete') {
                        detailsHtml = `删除：${log.details.stock_code} ${log.details.stock_name} (${log.details.theme_name}, ${log.details.trade_date})`;
                    }
                }
                
                logItem.innerHTML = `
                    <div class="log-header">
                        <span class="log-type ${typeClass}">${typeText}</span>
                        <span class="log-time">${log.operation_time}</span>
                        <button class="btn-delete-log" data-log-id="${log.id}" title="删除日志并回滚数据">🗑️ 回滚</button>
                    </div>
                    <div class="log-details">${detailsHtml}</div>
                    <div class="log-ip">IP: ${log.ip_address || '未知'}</div>
                `;
                
                logsContainer.appendChild(logItem);
            });
            
            // 添加删除日志按钮的事件监听
            document.querySelectorAll('.btn-delete-log').forEach(btn => {
                btn.addEventListener('click', async function() {
                    const logId = this.getAttribute('data-log-id');
                    if (confirm('确定要删除此日志并回滚相关数据吗？此操作不可撤销！')) {
                        await deleteOperationLog(logId);
                    }
                });
            });
        } else {
            logsContainer.innerHTML = '<p style="text-align: center; padding: 20px;">暂无操作日志</p>';
        }
    } catch (error) {
        logsContainer.innerHTML = `<p style="text-align: center; padding: 20px; color: red;">加载失败：${error.message}</p>`;
    }
}

async function deleteOperationLog(logId) {
    try {
        const response = await fetch(`${API_BASE_URL}/api/logs/${logId}`, {
            method: 'DELETE'
        });
        const result = await response.json();
        
        if (result.success) {
            showNotification(`✅ ${result.message}`, 'success');
            if (result.rollback_info && result.rollback_info.length > 0) {
                showNotification(`已回滚记录: ${result.rollback_info.join(', ')}`, 'info');
            }
            // 刷新日志列表
            loadOperationLogs();
            // 刷新涨停记录列表
            if (typeof loadLimitUpRecords === 'function') {
                loadLimitUpRecords();
            }
        } else {
            showNotification(`❌ 删除失败: ${result.error}`, 'error');
        }
    } catch (error) {
        showNotification(`❌ 删除失败: ${error.message}`, 'error');
    }
}

function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 15px 20px;
        background: ${type === 'success' ? '#4caf50' : type === 'error' ? '#f44336' : '#2196f3'};
        color: white;
        border-radius: 4px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.2);
        z-index: 10000;
        animation: slideIn 0.3s ease-in-out;
    `;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease-in-out';
        setTimeout(() => {
            document.body.removeChild(notification);
        }, 300);
    }, 3000);
}
