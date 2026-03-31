"""
下单建议服务模块

功能：
- 整合预测、安全库存计算、库存模拟
- 生成完整的下单建议报告

核心流程：
1. 预测未来LeadTime天的出货量
2. 计算安全库存（标准差 × 系数 × √LeadTime）
3. 模拟库存变化
4. 判断何时需要下单
"""

from typing import List, Dict, Any, Optional
import pandas as pd

from app.services.predictor import Predictor, get_predictor
from app.services.inventory_calculator import InventoryCalculator, get_inventory_calculator


class OrderAdvisor:
    """
    下单建议服务

    整合预测和库存计算，给出完整的下单建议
    """

    def __init__(
        self,
        predictor: Predictor = None,
        calculator: InventoryCalculator = None
    ):
        """
        初始化下单建议服务

        Args:
            predictor: 预测器实例
            calculator: 库存计算器实例
        """
        self._predictor = predictor or get_predictor()
        self._calculator = calculator or get_inventory_calculator()

    def analyze(
        self,
        history_data: List[float],
        initial_stock: float,
        moq: int,
        leadtime: int,
        safety_factor: float,
        simulate_days: int = None
    ) -> Dict[str, Any]:
        """
        综合分析并给出下单建议

        Args:
            history_data: 历史出货数据
            initial_stock: 当前库存
            moq: 最小订货量
            leadtime: 前置时间
            safety_factor: 安全库存系数
            simulate_days: 模拟天数，默认为leadtime的2倍

        Returns:
            分析结果字典，包含：
            - predictions: 预测出货量列表
            - safety_stock: 安全库存
            - daily_data: 每日库存详情DataFrame
            - order_summary: 下单建议汇总
            - need_order: 是否需要下单
            - first_order_day: 首次下单天数
            - first_order_quantity: 首次下单数量
        """
        # 默认模拟leadtime的2倍天数
        if simulate_days is None:
            simulate_days = leadtime * 2

        # 1. 预测未来出货量
        predictions = self._predictor.predict(history_data, simulate_days)

        # 2. 计算安全库存
        safety_stock = self._predictor.calculate_safety_stock(
            history_data, safety_factor, leadtime
        )

        # 3. 模拟库存变化
        daily_df = self._calculator.simulate_inventory(
            initial_stock=initial_stock,
            daily_predictions=predictions,
            safety_stock=safety_stock,
            moq=moq,
            leadtime=leadtime,
            simulate_days=simulate_days
        )

        # 4. 提取下单建议
        order_summary = self._calculator.get_order_summary(daily_df)

        # 5. 判断是否需要下单
        need_order = order_summary["总下单次数"] > 0
        first_order_day = None
        first_order_quantity = None

        if need_order and order_summary["下单日期"]:
            first_order_day = order_summary["下单日期"][0]
            first_order_quantity = order_summary["下单数量"][0]

        return {
            "predictions": predictions,
            "safety_stock": round(safety_stock, 2),
            "daily_data": daily_df,
            "order_summary": order_summary,
            "need_order": need_order,
            "first_order_day": first_order_day,
            "first_order_quantity": first_order_quantity,
            "predicted_total_outbound": round(sum(predictions[:leadtime]), 2),
            "predicted_remaining_stock": round(daily_df["结束库存(kg)"].iloc[leadtime - 1], 2)
        }

    def get_full_prediction(
        self,
        history_data: List[float],
        initial_stock: float,
        moq: int,
        leadtime: int,
        safety_factor: float
    ) -> Dict[str, Any]:
        """
        获取完整预测结果（用于API返回）

        Args:
            history_data: 历史出货数据
            initial_stock: 当前库存
            moq: 最小订货量
            leadtime: 前置时间
            safety_factor: 安全库存系数

        Returns:
            完整预测结果
        """
        analysis = self.analyze(
            history_data=history_data,
            initial_stock=initial_stock,
            moq=moq,
            leadtime=leadtime,
            safety_factor=safety_factor
        )

        # 转换DataFrame为字典列表
        daily_data_list = analysis["daily_data"].to_dict('records')

        return {
            "predictions": analysis["predictions"][:leadtime],
            "predicted_stocks": analysis["daily_data"]["结束库存(kg)"].tolist()[:leadtime],
            "safety_stock": analysis["safety_stock"],
            "need_order": analysis["need_order"],
            "order_date": analysis["first_order_day"],
            "order_quantity": analysis["first_order_quantity"],
            "daily_data": daily_data_list,
            "order_summary": analysis["order_summary"]
        }


# 默认实例
_advisor_instance: OrderAdvisor = None


def get_order_advisor() -> OrderAdvisor:
    """获取下单建议服务实例"""
    global _advisor_instance
    if _advisor_instance is None:
        _advisor_instance = OrderAdvisor()
    return _advisor_instance
