"""
预测算法模块

功能：
- 移动平均预测算法
- 计算历史预测误差
- 计算安全库存（公式：标准差 × 系数 × √LeadTime）

核心修改：
- 安全库存公式使用 √LeadTime
- 误差计算只取最近30天
"""

import math
from typing import List
import numpy as np


class Predictor:
    """
    预测器类

    使用移动平均法预测未来出货量，并计算安全库存
    """

    def __init__(self, period: int = 4):
        """
        初始化预测器

        Args:
            period: 移动平均周期，默认4天
        """
        self.period = period

    def predict(self, history_data: List[float], days: int) -> List[float]:
        """
        预测未来N天的出货量

        使用移动平均法：预测值 = AVERAGE(最近period天出货量)

        Args:
            history_data: 历史出货数据列表
            days: 需要预测的天数

        Returns:
            预测的未来N天出货量列表

        Example:
            >>> predictor = Predictor(period=4)
            >>> predictor.predict([184, 181, 181, 178], 5)
            [181.0, 181.0, 181.0, 181.0, 181.0]
        """
        if not history_data:
            return [0.0] * days

        # 计算移动平均值
        recent_data = history_data[-self.period:] if len(history_data) >= self.period else history_data
        avg = np.mean(recent_data)

        # 返回预测列表
        return [float(avg)] * days

    def calculate_errors(
        self,
        history_data: List[float],
        leadtime: int,
        max_days: int = 30
    ) -> List[float]:
        """
        计算历史预测误差

        误差 = 实际值 - 预测值
        只保留最近max_days天的误差

        Args:
            history_data: 历史出货数据
            leadtime: 前置时间（用于确定开始计算误差的位置）
            max_days: 最多保留多少天的误差，默认30天

        Returns:
            误差列表
        """
        # 需要至少 (leadtime + period) 天数据才能计算误差
        min_length = leadtime + self.period
        if len(history_data) < min_length:
            return []

        errors = []
        # 从第min_length天开始计算误差
        for i in range(min_length - 1, len(history_data)):
            # 使用之前的数据预测当天
            train_data = history_data[:i]
            actual = history_data[i]

            # 预测当天的值
            predicted = self.predict(train_data, 1)[0]
            error = actual - predicted
            errors.append(error)

        # 只保留最近max_days天的误差
        return errors[-max_days:] if len(errors) > max_days else errors

    def calculate_safety_stock(
        self,
        history_data: List[float],
        safety_factor: float,
        leadtime: int,
        max_error_days: int = 30
    ) -> float:
        """
        计算安全库存

        【核心公式】
        安全库存 = 标准差 × 安全库存系数 × √LeadTime

        Args:
            history_data: 历史出货数据
            safety_factor: 安全库存系数（如1.65对应95%置信度）
            leadtime: 前置时间（天）
            max_error_days: 计算误差标准差时使用的最近天数

        Returns:
            安全库存值

        Example:
            >>> predictor = Predictor(period=4)
            >>> # 假设误差标准差为39.2
            >>> safety_stock = predictor.calculate_safety_stock(
            ...     history_data, safety_factor=1.65, leadtime=5
            ... )
            >>> # 安全库存 ≈ 39.2 × 1.65 × √5 ≈ 144.5
        """
        # 计算误差
        errors = self.calculate_errors(history_data, leadtime, max_error_days)

        # 计算标准差
        if len(errors) < 2:
            # 误差数据不足，使用历史数据标准差
            recent_data = history_data[-max_error_days:] if len(history_data) > max_error_days else history_data
            std = np.std(recent_data) if len(recent_data) > 1 else 0
        else:
            std = np.std(errors)

        # 【核心公式】安全库存 = 标准差 × 系数 × √LeadTime
        safety_stock = std * safety_factor * math.sqrt(leadtime)

        return float(safety_stock)


# 默认预测器实例
_predictor_instance: Predictor = None


def get_predictor(period: int = 4) -> Predictor:
    """
    获取预测器实例

    Args:
        period: 移动平均周期

    Returns:
        Predictor实例
    """
    global _predictor_instance
    if _predictor_instance is None:
        _predictor_instance = Predictor(period)
    return _predictor_instance
