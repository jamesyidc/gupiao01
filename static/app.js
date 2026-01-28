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

    // 回车键快捷操作
    document.getElementById('stock-input').addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            compareAnalysis();
        }
    });

    // 模态框相关
    document.getElementById('modal-close').addEventListener('click', closeDataModal);
    document.getElementById('btn-cancel').addEventListener('click', closeDataModal);
    document.getElementById('btn-add-stock-row').addEventListener('click', addStockInputRow);
    document.getElementById('submit-form').addEventListener('submit', submitData);

    // 点击模态框外部关闭
    document.getElementById('data-modal').addEventListener('click', function(e) {
        if (e.target.id === 'data-modal') {
            closeDataModal();
        }
    });

    // 设置默认日期为今天
    const today = new Date().toISOString().split('T')[0];
    document.getElementById('submit-date').value = today;

    // 初始化时添加一行股票输入
    addStockInputRow();

    console.log('股票数据研究系统已加载');
});

// ============ 数据录入功能 ============

let stockRowCounter = 0;

function openDataModal() {
    document.getElementById('data-modal').style.display = 'flex';
    document.getElementById('submit-result').style.display = 'none';
}

function closeDataModal() {
    document.getElementById('data-modal').style.display = 'none';
    document.getElementById('submit-form').reset();
    document.getElementById('stocks-list').innerHTML = '';
    stockRowCounter = 0;
    addStockInputRow();
}

function addStockInputRow() {
    stockRowCounter++;
    const stocksList = document.getElementById('stocks-list');
    
    const row = document.createElement('div');
    row.className = 'stock-input-row';
    row.id = `stock-row-${stockRowCounter}`;
    
    row.innerHTML = `
        <input type="text" name="stock_code" placeholder="股票代码" required>
        <input type="text" name="stock_name" placeholder="股票名称" required>
        <input type="text" name="reason" placeholder="涨停原因（可选）">
        <input type="text" name="limit_up_time" placeholder="09:30">
        <button type="button" class="btn-remove" onclick="removeStockRow('stock-row-${stockRowCounter}')">×</button>
    `;
    
    stocksList.appendChild(row);
}

function removeStockRow(rowId) {
    const row = document.getElementById(rowId);
    if (row) {
        // 至少保留一行
        const stocksList = document.getElementById('stocks-list');
        if (stocksList.children.length > 1) {
            row.remove();
        } else {
            showError('至少需要保留一只股票');
        }
    }
}

async function submitData(e) {
    e.preventDefault();
    
    const date = document.getElementById('submit-date').value;
    const theme = document.getElementById('submit-theme').value.trim();
    
    if (!date || !theme) {
        alert('请填写日期和题材名称');
        return;
    }
    
    // 收集所有股票数据
    const stockRows = document.querySelectorAll('.stock-input-row');
    const stocks = [];
    
    for (let row of stockRows) {
        const code = row.querySelector('input[name="stock_code"]').value.trim();
        const name = row.querySelector('input[name="stock_name"]').value.trim();
        const reason = row.querySelector('input[name="reason"]').value.trim();
        const limitUpTime = row.querySelector('input[name="limit_up_time"]').value.trim();
        
        if (code && name) {
            stocks.push({
                code: code,
                name: name,
                reason: reason || `${theme}板块活跃`,
                limit_up_time: limitUpTime || '09:30',
                open_count: 0
            });
        }
    }
    
    if (stocks.length === 0) {
        alert('请至少添加一只股票');
        return;
    }
    
    // 提交数据
    try {
        showLoading();
        
        const response = await fetch(`${API_BASE_URL}/api/data/submit`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                date: date,
                theme: theme,
                stocks: stocks
            })
        });
        
        const result = await response.json();
        hideLoading();
        
        // 显示结果
        const resultDiv = document.getElementById('submit-result');
        resultDiv.style.display = 'block';
        
        if (result.success) {
            resultDiv.className = 'submit-success';
            let message = `✅ ${result.message}`;
            
            if (result.errors && result.errors.length > 0) {
                message += '\n\n⚠️ 部分错误：\n';
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
