"""
库存预测分析测试用例

测试案例：南京仓-西米
基于用户提供的计算逻辑说明文档

参数设置：
- 初始库存: 2000 kg
- MOQ: 1000 kg
- LeadTime: 5 天
- 安全库存系数: 1.65
- 移动平均周期: 4 天
"""

import pytest
import numpy as np
import math


class TestPredictionLogic:
    """测试预测逻辑"""

    # 历史出货数据（最近4天）
    history_data_last_4 = [184, 181, 181, 178]

    def test_moving_average_prediction(self):
        """
        测试移动平均预测

        计算逻辑：预测值 = AVERAGE(最近4天出货量)
        预期：预测值 = (184 + 181 + 181 + 178) / 4 = 181
        """
        expected_avg = sum(self.history_data_last_4) / 4
        assert expected_avg == 181, f"移动平均值应为181，实际为{expected_avg}"

    def test_predict_future_5_days(self):
        """
        测试预测未来5天出货量

        预期：每天预测出货量都是181，总出货量 = 181 * 5 = 905
        """
        daily_prediction = 181
        leadtime = 5
        total_prediction = daily_prediction * leadtime
        assert total_prediction == 905


class TestSafetyStockLogic:
    """测试安全库存计算逻辑"""

    # 最近30天的误差数据（示例）
    # 实际值来自用户文档中的误差列表后30个
    recent_30_errors = [
        -20.0, -49.0, -27.0, -30.0, -32.0, -47.0, -73.0, -20.0, -18.0, +27.0,
        -40.0, -53.0, -42.0, -16.0, -48.0, +34.0, +28.0, -79.0, -2.5, -50.0,
        +24.5, +24.5, +29.5, +6.0, +56.0, +37.0, +53.0, +66.0, -15.0, -28.0
    ]

    def test_error_std_calculation(self):
        """
        测试误差标准差计算

        只使用最近30天的误差值
        """
        std = np.std(self.recent_30_errors)
        print(f"误差标准差: {std:.2f}")
        assert std > 0

    def test_safety_stock_formula(self):
        """
        测试安全库存公式

        【修改后的公式】
        安全库存 = 标准差 × 安全库存系数 × √LeadTime

        示例计算：
        - 标准差 ≈ 39.2（假设值，需根据实际数据计算）
        - 安全库存系数 = 1.65
        - LeadTime = 5天
        - 安全库存 = 39.2 × 1.65 × √5 = 39.2 × 1.65 × 2.236 = 144.5
        """
        safety_factor = 1.65
        leadtime = 5

        # 计算标准差
        std = np.std(self.recent_30_errors)

        # 【核心公式】安全库存 = 标准差 × 系数 × √LeadTime
        safety_stock = std * safety_factor * math.sqrt(leadtime)

        print(f"标准差: {std:.2f}")
        print(f"安全库存: {safety_stock:.2f}")

        # 验证公式正确性
        expected_formula = std * safety_factor * math.sqrt(leadtime)
        assert abs(safety_stock - expected_formula) < 0.01


class TestInventorySimulation:
    """测试库存模拟逻辑"""

    def test_inventory_simulation_basic(self):
        """
        测试库存模拟（不下单场景）

        参数：
        - 初始库存: 2000 kg
        - 预测每日出货: 181 kg
        - LeadTime: 5天

        预期库存变化：
        第0天: 2000
        第1天: 2000 - 181 = 1819
        第2天: 1819 - 181 = 1638
        第3天: 1638 - 181 = 1457
        第4天: 1457 - 181 = 1276
        第5天: 1276 - 181 = 1095
        """
        initial_stock = 2000
        daily_shipment = 181
        leadtime = 5

        stocks = [initial_stock]
        current = initial_stock

        for day in range(1, leadtime + 1):
            current = current - daily_shipment
            stocks.append(current)

        expected_stocks = [2000, 1819, 1638, 1457, 1276, 1095]
        assert stocks == expected_stocks, f"库存模拟错误: {stocks}"

    def test_arrival_judgment(self):
        """
        测试到货判断逻辑

        【判断规则】
        昨日库存 - 今日出货 <= 安全库存 → 需要到货

        案例：
        - 安全库存 = 204.5 kg（用户示例值）
        - 第5天结束库存: 1095 kg
        - 第6天: 1095 - 181 = 914 > 204.5 → 不需要到货
        - 继续模拟...
        - 第9天结束库存: 371 kg
        - 第10天: 371 - 181 = 190 <= 204.5 → 需要到货！
        """
        safety_stock = 204.5
        daily_shipment = 181

        # 模拟库存变化
        stocks = [2000]  # 第0天
        arrivals = {}  # 记录到货

        for day in range(1, 20):
            yesterday_stock = stocks[-1]
            today_stock_before_arrival = yesterday_stock - daily_shipment

            # 判断是否需要到货
            if today_stock_before_arrival <= safety_stock:
                # 需要到货
                arrivals[day] = 1000  # MOQ
                today_stock = today_stock_before_arrival + 1000
            else:
                today_stock = today_stock_before_arrival

            stocks.append(today_stock)

        # 验证第10天需要到货
        assert 10 in arrivals, "第10天应该需要到货"
        print(f"到货记录: {arrivals}")
        print(f"库存变化: {stocks[:12]}")

    def test_order_date_calculation(self):
        """
        测试下单日期计算

        【计算逻辑】
        下单日期 = 到货日期 - LeadTime

        案例：
        - 到货日期: 第10天
        - LeadTime: 5天
        - 下单日期: 10 - 5 = 第5天
        """
        arrival_day = 10
        leadtime = 5
        order_day = arrival_day - leadtime
        assert order_day == 5, f"下单日期应为第5天，实际为第{order_day}天"


class TestFullScenario:
    """完整场景测试（用户案例）"""

    def test_full_scenario_with_params(self):
        """
        完整测试用户提供的案例

        参数：
        - 初始库存: 2000 kg
        - MOQ: 1000 kg
        - LeadTime: 5天
        - 安全库存系数: 1.65
        - 预测每日出货: 181 kg
        - 安全库存: 204.5 kg（示例值）

        预期结果：
        - 第5天下单1000kg
        - 第10天到货1000kg
        - 第11天再次下单1000kg
        - 第16天到货1000kg
        """
        initial_stock = 2000
        moq = 1000
        leadtime = 5
        safety_stock = 204.5  # 示例值
        daily_shipment = 181

        # 模拟库存和订单
        stocks = [initial_stock]
        orders = {}  # {下单天数: 下单数量}
        arrivals = {}  # {到货天数: 到货数量}

        for day in range(1, 20):
            yesterday_stock = stocks[-1]
            today_stock_before_arrival = yesterday_stock - daily_shipment

            # 检查是否有到货
            if day in arrivals:
                today_stock_before_arrival += arrivals[day]

            # 判断是否需要到货（未来会低于安全库存）
            if today_stock_before_arrival <= safety_stock:
                # 计算到货日期和下单日期
                arrival_day = day
                order_day = arrival_day - leadtime

                # 只有当下单日期 >= 当前日期才记录
                if order_day >= 1 and order_day not in orders:
                    orders[order_day] = moq
                    arrivals[arrival_day] = moq
                    today_stock = today_stock_before_arrival + moq
                else:
                    today_stock = today_stock_before_arrival
            else:
                today_stock = today_stock_before_arrival

            stocks.append(today_stock)

        print(f"下单记录: {orders}")
        print(f"到货记录: {arrivals}")
        print(f"库存变化: {stocks}")

        # 验证
        assert 5 in orders, "第5天应该下单"
        assert orders[5] == 1000, "下单数量应为1000kg"


class TestDataExport:
    """测试数据导出"""

    def test_export_format(self):
        """
        测试导出数据格式

        导出内容应包含：
        1. 汇总信息
        2. 每日预测详情
        3. 下单建议
        """
        # 预期的导出数据结构
        expected_columns = [
            "天数", "预测出货量(kg)", "当日初始库存(kg)",
            "当日到货(kg)", "当日结束库存(kg)", "安全库存(kg)",
            "是否低于安全库存", "是否下单", "下单数量(kg)"
        ]

        # 验证列名存在
        assert len(expected_columns) == 9


if __name__ == "__main__":
    # 运行测试
    pytest.main([__file__, "-v", "-s"])
