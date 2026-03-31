from pydantic import BaseModel
from typing import Optional


class OrderSuggestion(BaseModel):
    """下单建议"""
    need_order: bool           # 是否需要下单
    order_date: Optional[str]  # 建议下单日期
    order_quantity: Optional[int]  # 下单数量


class PredictionResult(BaseModel):
    """预测结果模型"""
    warehouse: str                     # 仓库
    material: str                      # 物料
    moq: int                           # 最小订货量
    leadtime: int                      # 前置时间
    safety_factor: float               # 安全库存系数
    current_stock: float               # 当前库存
    safety_stock: float                # 安全库存
    predictions: list[float]           # 未来N天预测出货量
    predicted_stocks: list[float]      # 预测库存变化
    order_suggestion: OrderSuggestion  # 下单建议


class ComparisonData(BaseModel):
    """对比数据点"""
    date: str
    actual: Optional[float]     # 实际出货
    predicted: Optional[float]  # 预测出货
    error: Optional[float]      # 误差


class ComparisonMetrics(BaseModel):
    """对比统计指标"""
    mean_error: float           # 平均误差
    std_error: float            # 误差标准差
    mape: float                 # 平均绝对百分比误差
    accuracy_rate: float        # 准确率


class ComparisonResult(BaseModel):
    """对比分析结果"""
    warehouse: str
    material: str
    data: list[ComparisonData]  # 对比数据列表
    metrics: ComparisonMetrics  # 统计指标


class OverviewItem(BaseModel):
    """总览表单项"""
    warehouse: str
    material: str
    current_stock: float
    safety_stock: float
    need_order: bool
    order_date: Optional[str]
    order_quantity: Optional[int]
    leadtime: int
    moq: int
