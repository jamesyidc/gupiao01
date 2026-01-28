"""
股票信息查询工具 - 简化版
使用内置股票列表 + akshare备用查询
"""
import logging
from typing import Dict, Optional

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 常见股票代码映射表（可以根据需要扩充）
STOCK_NAMES_MAP = {
    # 主板深圳
    '000001': '平安银行',
    '000002': '万科A',
    '000004': '国农科技',
    '000006': '深振业A',
    '000009': '中国宝安',
    '000012': '南玻A',
    '000027': '深圳能源',
    '000039': '中集集团',
    '000050': '深天马A',
    '000063': '中兴通讯',
    '000100': 'TCL科技',
    '000426': '兴业银行',
    '000506': '中润资源',
    '000603': '盛达资源',
    '000629': '攀钢钒钛',
    '000630': '铜陵有色',
    '000657': '中钨高新',
    '000737': '南风化工',
    '000751': '锌业股份',
    '000858': '五粮液',
    
    # 主板上海
    '600000': '浦发银行',
    '600004': '白云机场',
    '600009': '上海机场',
    '600016': '民生银行',
    '600019': '宝钢股份',
    '600028': '中国石化',
    '600029': '南方航空',
    '600030': '中信证券',
    '600036': '招商银行',
    '600048': '保利发展',
    '600050': '中国联通',
    '600104': '上汽集团',
    '600111': '北方稀土',
    '600276': '恒瑞医药',
    '600309': '万华化学',
    '600519': '贵州茅台',
    '600547': '山东黄金',
    '600690': '海尔智家',
    '600887': '伊利股份',
    '600900': '长江电力',
    '601006': '大秦铁路',
    '601012': '隆基绿能',
    '601088': '中国神华',
    '601166': '兴业银行',
    '601169': '北京银行',
    '601288': '农业银行',
    '601318': '中国平安',
    '601328': '交通银行',
    '601398': '工商银行',
    '601601': '中国太保',
    '601628': '中国人寿',
    '601668': '中国建筑',
    '601688': '华泰证券',
    '601766': '中国中车',
    '601818': '光大银行',
    '601857': '中国石油',
    '601888': '中国中免',
    '601899': '紫金矿业',
    '601919': '中远海控',
    '601939': '建设银行',
    '601985': '中国核电',
    '601988': '中国银行',
    '601998': '中信银行',
    
    # 创业板
    '300001': '特锐德',
    '300002': '神州泰岳',
    '300003': '乐普医疗',
    '300014': '亿纬锂能',
    '300015': '爱尔眼科',
    '300033': '同花顺',
    '300059': '东方财富',
    '300122': '智飞生物',
    '300124': '汇川技术',
    '300142': '沃森生物',
    '300223': '北京君正',
    '300274': '阳光电源',
    '300347': '泰格医药',
    '300408': '三环集团',
    '300450': '先导智能',
    '300496': '中科创达',
    '300498': '温氏股份',
    '300628': '亿联网络',
    '300661': '圣邦股份',
    '300750': '宁德时代',
    '300760': '迈瑞医疗',
    '300768': '迪普科技',
    
    # 科创板
    '688001': '华兴源创',
    '688008': '澜起科技',
    '688012': '中微公司',
    '688027': '国盾量子',
    '688036': '传音控股',
    '688041': '海光信息',
    '688065': '凯赛生物',
    '688111': '金山办公',
    '688126': '沪硅产业',
    '688169': '石头科技',
    '688180': '君实生物',
    '688187': '时代电气',
    '688223': '晶科能源',
    '688229': '博众精工',
    '688256': '寒武纪',
    '688299': '长阳科技',
    '688363': '华熙生物',
    '688396': '华润微',
    '688561': '奇安信',
    '688599': '天合光能',
    '688981': '中芯国际',
    
    # 中小板（部分已合并到主板）
    '002001': '新和成',
    '002027': '分众传媒',
    '002050': '三花智控',
    '002129': '中环股份',
    '002230': '科大讯飞',
    '002236': '大华股份',
    '002241': '歌尔股份',
    '002271': '东方雨虹',
    '002352': '顺丰控股',
    '002410': '广联达',
    '002415': '海康威视',
    '002439': '启明星辰',
    '002460': '赣锋锂业',
    '002475': '立讯精密',
    '002493': '荣盛石化',
    '002594': '比亚迪',
    '002601': '龙佰集团',
    '002714': '牧原股份',
    '002938': '鹏鼎控股',
}


class StockInfoFetcher:
    """股票信息获取器"""
    
    def __init__(self):
        self._stock_info_cache = STOCK_NAMES_MAP.copy()
        logger.info(f"已加载 {len(self._stock_info_cache)} 只内置股票信息")
    
    def get_stock_name(self, stock_code: str) -> Optional[str]:
        """
        根据股票代码获取股票名称
        
        Args:
            stock_code: 6位股票代码
            
        Returns:
            股票名称，如果未找到返回 "股票{code}"
        """
        # 先从缓存中查找
        name = self._stock_info_cache.get(stock_code)
        
        if name:
            return name
        
        # 如果未找到，尝试从akshare获取
        try:
            import akshare as ak
            logger.info(f"从akshare查询股票 {stock_code}...")
            df = ak.stock_individual_info_em(symbol=stock_code)
            if not df.empty:
                name = df[df['item'] == '股票简称']['value'].values[0]
                # 添加到缓存
                self._stock_info_cache[stock_code] = name
                logger.info(f"成功获取: {stock_code} - {name}")
                return name
        except Exception as e:
            logger.warning(f"从akshare获取股票 {stock_code} 失败: {e}")
        
        # 如果都失败，返回默认名称
        default_name = f"股票{stock_code}"
        logger.info(f"使用默认名称: {stock_code} - {default_name}")
        return default_name
    
    def get_multiple_stock_names(self, stock_codes: list) -> Dict[str, str]:
        """
        批量获取股票名称
        
        Args:
            stock_codes: 股票代码列表
            
        Returns:
            {股票代码: 股票名称} 的字典
        """
        result = {}
        for code in stock_codes:
            name = self.get_stock_name(code)
            result[code] = name
        return result
    
    def add_stock_name(self, stock_code: str, stock_name: str):
        """手动添加股票名称到缓存"""
        self._stock_info_cache[stock_code] = stock_name
        logger.info(f"手动添加: {stock_code} - {stock_name}")


# 创建全局实例
_stock_fetcher = None

def get_stock_fetcher() -> StockInfoFetcher:
    """获取股票信息获取器的单例"""
    global _stock_fetcher
    if _stock_fetcher is None:
        _stock_fetcher = StockInfoFetcher()
    return _stock_fetcher


# 便捷函数
def get_stock_name(stock_code: str) -> Optional[str]:
    """
    获取股票名称
    
    Args:
        stock_code: 6位股票代码
        
    Returns:
        股票名称
    """
    return get_stock_fetcher().get_stock_name(stock_code)


def get_multiple_stock_names(stock_codes: list) -> Dict[str, str]:
    """
    批量获取股票名称
    
    Args:
        stock_codes: 股票代码列表
        
    Returns:
        {股票代码: 股票名称} 的字典
    """
    return get_stock_fetcher().get_multiple_stock_names(stock_codes)


if __name__ == '__main__':
    # 测试
    print("测试股票信息获取...")
    
    # 测试单个股票
    test_codes = ['000001', '600519', '300750', '688111', '002594', '999999']
    
    for code in test_codes:
        name = get_stock_name(code)
        print(f"{code}: {name}")
    
    print("\n批量获取测试:")
    names = get_multiple_stock_names(test_codes)
    for code, name in names.items():
        print(f"{code}: {name}")
