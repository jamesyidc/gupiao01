"""
数据库模型定义
"""
from sqlalchemy import create_engine, Column, Integer, String, Float, Date, DateTime, ForeignKey, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime

Base = declarative_base()


class Stock(Base):
    """股票基本信息表"""
    __tablename__ = 'stocks'
    
    id = Column(Integer, primary_key=True)
    code = Column(String(10), unique=True, nullable=False, index=True)  # 股票代码
    name = Column(String(50), nullable=False)  # 股票名称
    market = Column(String(10))  # 市场: SH/SZ
    created_at = Column(DateTime, default=datetime.now)
    
    # 关系
    daily_prices = relationship("DailyPrice", back_populates="stock")
    limit_up_records = relationship("LimitUpRecord", back_populates="stock")


class Theme(Base):
    """题材表"""
    __tablename__ = 'themes'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False, index=True)  # 题材名称
    description = Column(String(500))  # 题材描述
    created_at = Column(DateTime, default=datetime.now)
    
    # 关系
    limit_up_records = relationship("LimitUpRecord", back_populates="theme")


class DailyPrice(Base):
    """股票日线数据表"""
    __tablename__ = 'daily_prices'
    
    id = Column(Integer, primary_key=True)
    stock_id = Column(Integer, ForeignKey('stocks.id'), nullable=False)
    trade_date = Column(Date, nullable=False, index=True)  # 交易日期
    open_price = Column(Float)  # 开盘价
    close_price = Column(Float, nullable=False)  # 收盘价
    high_price = Column(Float)  # 最高价
    low_price = Column(Float)  # 最低价
    volume = Column(Float)  # 成交量
    amount = Column(Float)  # 成交额
    change_percent = Column(Float)  # 涨跌幅
    
    # 关系
    stock = relationship("Stock", back_populates="daily_prices")
    
    # 复合索引
    __table_args__ = (
        Index('idx_stock_date', 'stock_id', 'trade_date'),
    )


class LimitUpRecord(Base):
    """涨停记录表"""
    __tablename__ = 'limit_up_records'
    
    id = Column(Integer, primary_key=True)
    stock_id = Column(Integer, ForeignKey('stocks.id'), nullable=False)
    theme_id = Column(Integer, ForeignKey('themes.id'), nullable=False)
    trade_date = Column(Date, nullable=False, index=True)  # 涨停日期
    limit_up_time = Column(String(10))  # 封板时间
    open_count = Column(Integer, default=0)  # 打开次数
    reason = Column(String(500))  # 涨停原因
    turnover_rate = Column(Float)  # 换手率
    
    # 关系
    stock = relationship("Stock", back_populates="limit_up_records")
    theme = relationship("Theme", back_populates="limit_up_records")
    
    # 复合索引
    __table_args__ = (
        Index('idx_theme_date', 'theme_id', 'trade_date'),
        Index('idx_stock_theme_date', 'stock_id', 'theme_id', 'trade_date'),
    )


class OperationLog(Base):
    """操作日志表"""
    __tablename__ = 'operation_logs'
    
    id = Column(Integer, primary_key=True)
    operation_type = Column(String(50), nullable=False)  # 操作类型：add/delete/update
    operation_time = Column(DateTime, default=datetime.now, index=True)  # 操作时间
    target_type = Column(String(50))  # 目标类型：limit_up_record/stock/theme
    target_id = Column(Integer)  # 目标ID
    details = Column(String(1000))  # 操作详情JSON
    ip_address = Column(String(50))  # IP地址
    
    __table_args__ = (
        Index('idx_operation_time', 'operation_time'),
    )


class Database:
    """数据库管理类"""
    
    def __init__(self, db_url='sqlite:///stock_analysis.db'):
        self.engine = create_engine(db_url, echo=False)
        self.Session = sessionmaker(bind=self.engine)
        
    def create_tables(self):
        """创建所有表"""
        Base.metadata.create_all(self.engine)
        
    def get_session(self):
        """获取数据库会话"""
        return self.Session()
    
    def drop_tables(self):
        """删除所有表（慎用）"""
        Base.metadata.drop_all(self.engine)


# 全局数据库实例
db = Database()
