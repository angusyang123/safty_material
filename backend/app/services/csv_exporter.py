"""
CSV数据导出服务

功能：
- 导出预测数据到CSV
- 导出库存模拟数据到CSV
- 导出下单建议到CSV
- 导出综合分析报告

输出目录：项目根目录/output/
"""

import os
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path
import pandas as pd


class CSVExporter:
    """
    CSV数据导出器

    将预测分析结果导出为CSV文件
    """

    def __init__(self, output_dir: str = None):
        """
        初始化导出器

        Args:
            output_dir: 输出目录，默认为项目根目录下的output文件夹
        """
        if output_dir is None:
            project_root = Path(__file__).parent.parent.parent.parent
            output_dir = str(project_root / "output")
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def export_full_report(
        self,
        warehouse: str,
        material: str,
        moq: int,
        leadtime: int,
        safety_factor: float,
        current_stock: float,
        safety_stock: float,
        daily_data: List[Dict[str, Any]],
        order_summary: Dict[str, Any],
        predictions: List[float] = None,
        history_data: List[float] = None,
        filename: str = None
    ) -> str:
        """
        导出完整分析报告

        Args:
            warehouse: 仓库名称
            material: 物料名称
            moq: 最小订货量
            leadtime: 前置时间
            safety_factor: 安全库存系数
            current_stock: 当前库存
            safety_stock: 安全库存
            daily_data: 每日库存数据（来自模拟结果）
            order_summary: 下单建议汇总
            predictions: 预测出货量列表（可选）
            history_data: 历史出货数据（可选）
            filename: 文件名（可选）

        Returns:
            导出文件路径
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"完整报告_{warehouse}_{material}_{timestamp}.csv"

        filepath = self.output_dir / filename

        with open(filepath, 'w', encoding='gbk') as f:
            # === 汇总信息 ===
            f.write("=== 汇总信息 ===\n")
            summary_data = [
                {"项目": "仓库", "值": warehouse},
                {"项目": "物料", "值": material},
                {"项目": "MOQ(kg)", "值": moq},
                {"项目": "前置时间(天)", "值": leadtime},
                {"项目": "安全库存系数", "值": safety_factor},
                {"项目": "当前库存(kg)", "值": round(current_stock, 2)},
                {"项目": "安全库存(kg)", "值": round(safety_stock, 2)},
                {"项目": "是否需要下单", "值": "是" if order_summary.get("总下单次数", 0) > 0 else "否"},
                {"项目": "总下单次数", "值": order_summary.get("总下单次数", 0)},
                {"项目": "总下单量(kg)", "值": order_summary.get("总下单量", 0)},
                {"项目": "最低库存(kg)", "值": round(order_summary.get("最低库存", 0), 2)},
            ]
            pd.DataFrame(summary_data).to_csv(f, index=False)
            f.write("\n")

            # === 下单建议详情 ===
            if order_summary.get("下单日期"):
                f.write("=== 下单建议详情 ===\n")
                order_detail = pd.DataFrame({
                    "下单日期": order_summary["下单日期"],
                    "下单数量(kg)": order_summary["下单数量"]
                })
                order_detail.to_csv(f, index=False)
                f.write("\n")

            # === 每日库存模拟 ===
            f.write("=== 每日库存模拟 ===\n")
            if isinstance(daily_data, pd.DataFrame):
                daily_data.to_csv(f, index=False)
            else:
                pd.DataFrame(daily_data).to_csv(f, index=False)
            f.write("\n")

            # === 预测出货量 ===
            if predictions:
                f.write("=== 预测出货量 ===\n")
                pred_df = pd.DataFrame({
                    "天数": range(1, len(predictions) + 1),
                    "预测出货量(kg)": [round(p, 2) for p in predictions]
                })
                pred_df.to_csv(f, index=False)
                f.write("\n")

            # === 历史出货数据 ===
            if history_data:
                f.write("=== 历史出货数据 ===\n")
                hist_df = pd.DataFrame({
                    "序号": range(1, len(history_data) + 1),
                    "出货量(kg)": history_data
                })
                hist_df.to_csv(f, index=False)

        return str(filepath)

    def export_overview(
        self,
        overview_data: List[Dict[str, Any]],
        filename: str = None
    ) -> str:
        """
        导出总览表

        Args:
            overview_data: 总览数据列表
            filename: 文件名（可选）

        Returns:
            导出文件路径
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"总览表_{timestamp}.csv"

        filepath = self.output_dir / filename
        df = pd.DataFrame(overview_data)
        df.to_csv(filepath, index=False, encoding='gbk')

        return str(filepath)

    def export_daily_detail(
        self,
        daily_data: List[Dict[str, Any]],
        warehouse: str,
        material: str,
        filename: str = None
    ) -> str:
        """
        导出每日库存详情

        Args:
            daily_data: 每日数据列表
            warehouse: 仓库名称
            material: 物料名称
            filename: 文件名（可选）

        Returns:
            导出文件路径
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"每日库存_{warehouse}_{material}_{timestamp}.csv"

        filepath = self.output_dir / filename
        df = pd.DataFrame(daily_data)
        df.to_csv(filepath, index=False, encoding='gbk')

        return str(filepath)


# 全局实例
_exporter_instance: Optional[CSVExporter] = None


def get_csv_exporter(output_dir: str = None) -> CSVExporter:
    """获取CSV导出器实例"""
    global _exporter_instance
    if _exporter_instance is None:
        _exporter_instance = CSVExporter(output_dir)
    return _exporter_instance
