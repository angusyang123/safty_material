"""
库存计算服务模块

功能：
- 模拟库存变化
- 判断到货时机
- 计算下单日期
- 生成每日库存报告

核心逻辑：
- 到货判断：昨日库存 - 今日出货 <= 安全库存 → 需要到货
- 下单日期：到货日期 - LeadTime
"""

from typing import List, Dict, Any, Optional
import pandas as pd
import numpy as np


class InventoryCalculator:
    """
    库存计算器

    负责模拟库存变化和计算下单建议
    """

    def simulate_inventory(
        self,
        initial_stock: float,
        daily_predictions: List[float],
        safety_stock: float,
        moq: int,
        leadtime: int,
        simulate_days: int = None
    ) -> pd.DataFrame:
        """
        模拟库存变化并生成下单建议

        【核心逻辑】
        1. 当日库存 = 昨日库存 - 今日出货 + 今日到货
        2. 判断到货：昨日库存 - 今日出货 <= 安全库存 → 需要到货
        3. 下单日期：到货日期 - LeadTime

        Args:
            initial_stock: 初始库存（kg）
            daily_predictions: 每日预测出货量列表
            safety_stock: 安全库存（kg）
            moq: 最小订货量（kg）
            leadtime: 前置时间（天）
            simulate_days: 模拟天数，默认使用daily_predictions的长度

        Returns:
            DataFrame包含每日库存详情：
            - 天数: 第N天
            - 预测出货: 当日预测出货量
            - 初始库存: 当日开始时的库存
            - 到货量: 当日到货数量
            - 结束库存: 当日结束时的库存
            - 安全库存: 安全库存线
            - 是否需要到货: 是否触发到货条件
            - 是否下单: 是否建议下单
            - 下单数量: 建议下单数量

        Example:
            >>> calc = InventoryCalculator()
            >>> df = calc.simulate_inventory(
            ...     initial_stock=2000,
            ...     daily_predictions=[181]*20,
            ...     safety_stock=204.5,
            ...     moq=1000,
            ...     leadtime=5
            ... )
        """
        if simulate_days is None:
            simulate_days = len(daily_predictions)

        # 扩展预测列表
        predictions = daily_predictions[:]
        while len(predictions) < simulate_days:
            predictions.append(predictions[-1] if predictions else 0)

        # 初始化结果列表
        results = []
        current_stock = initial_stock

        # 记录已规划的下单（避免重复下单）
        planned_orders = set()

        for day in range(1, simulate_days + 1):
            prediction = predictions[day - 1]

            # 昨日库存
            yesterday_stock = current_stock

            # 今日出货前的库存
            stock_before_shipment = yesterday_stock

            # 计算出货后的库存（不含到货）
            stock_after_shipment = stock_before_shipment - prediction

            # 判断是否需要到货
            need_arrival = stock_after_shipment <= safety_stock

            # 计算到货日期和下单日期
            arrival_day = day if need_arrival else None
            order_day = arrival_day - leadtime if need_arrival else None

            # 检查是否已经规划过这个订单
            if order_day and order_day >= 1 and order_day not in planned_orders:
                planned_orders.add(order_day)
                arrival_qty = moq
                is_order_day = (order_day == day)
            else:
                arrival_qty = 0
                is_order_day = False
                need_arrival = False  # 如果不能下单，则不需要到货

            # 计算结束库存
            ending_stock = stock_after_shipment + arrival_qty

            # 记录结果
            results.append({
                "天数": day,
                "预测出货(kg)": round(prediction, 2),
                "初始库存(kg)": round(yesterday_stock, 2),
                "出货后库存(kg)": round(stock_after_shipment, 2),
                "到货量(kg)": arrival_qty,
                "结束库存(kg)": round(ending_stock, 2),
                "安全库存(kg)": round(safety_stock, 2),
                "是否低于安全库存": stock_after_shipment <= safety_stock,
                "是否下单": is_order_day,
                "下单数量(kg)": moq if is_order_day else 0,
                "建议下单日期": f"第{order_day}天" if is_order_day else ""
            })

            # 更新库存
            current_stock = ending_stock

        return pd.DataFrame(results)

    def get_order_summary(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        从模拟结果中提取下单建议汇总

        Args:
            df: simulate_inventory返回的DataFrame

        Returns:
            汇总信息字典
        """
        # 找出所有下单日期
        order_days = df[df["是否下单"] == True]["天数"].tolist()
        order_quantities = df[df["是否下单"] == True]["下单数量(kg)"].tolist()

        return {
            "总下单次数": len(order_days),
            "下单日期": [f"第{d}天" for d in order_days],
            "下单数量": order_quantities,
            "总下单量": sum(order_quantities),
            "最低库存": float(df["结束库存(kg)"].min()),
            "最终库存": float(df["结束库存(kg)"].iloc[-1])
        }

    def find_first_arrival_day(
        self,
        initial_stock: float,
        daily_predictions: List[float],
        safety_stock: float
    ) -> int:
        """
        找到首次需要到货的天数

        Args:
            initial_stock: 初始库存
            daily_predictions: 每日预测出货量
            safety_stock: 安全库存

        Returns:
            首次需要到货的天数（从1开始），如果不需要返回-1
        """
        current_stock = initial_stock

        for day, prediction in enumerate(daily_predictions, start=1):
            current_stock = current_stock - prediction
            if current_stock <= safety_stock:
                return day

        return -1


# 默认实例
_calculator_instance: InventoryCalculator = None


def get_inventory_calculator() -> InventoryCalculator:
    """获取库存计算器实例"""
    global _calculator_instance
    if _calculator_instance is None:
        _calculator_instance = InventoryCalculator()
    return _calculator_instance
