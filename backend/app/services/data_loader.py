"""
数据加载服务模块

功能：
- 从CSV文件加载物料信息和出货数据
- 支持重新加载(reload)功能
- 支持获取物料列表、单个物料信息
- 支持获取仓库列表
- 支持获取指定仓库物料的出货历史

文件说明：
- 物料信息表：物料, MOQ, leadtime, 安全库存系数
- 出货数据：仓库, 物料, 日期, 出货量
"""

import os
import pandas as pd
from typing import Optional, List, Dict, Any
from pathlib import Path


class DataLoader:
    """
    数据加载器类

    用于从CSV文件加载和管理物料信息和出货数据
    """

    def __init__(self, data_dir: str):
        """
        初始化数据加载器

        Args:
            data_dir: 数据文件所在目录路径
        """
        self.data_dir = Path(data_dir)
        self.materials_df: Optional[pd.DataFrame] = None
        self.shipments_df: Optional[pd.DataFrame] = None
        self._loaded = False

    def reload(self) -> Dict[str, Any]:
        """
        重新加载CSV数据

        Returns:
            包含加载状态和统计信息的字典
        """
        try:
            # 加载物料信息表
            material_file = self.data_dir / "物料信息表.csv"
            if not material_file.exists():
                return {
                    "success": False,
                    "error": f"物料信息表不存在: {material_file}"
                }

            self.materials_df = pd.read_csv(
                material_file,
                encoding='gbk',
                dtype={
                    '物料': str,
                    'MOQ': int,
                    'leadtime': int,
                    '安全库存系数': float
                }
            )

            # 加载出货数据
            shipment_file = self.data_dir / "仓库出货量.csv"
            if not shipment_file.exists():
                return {
                    "success": False,
                    "error": f"出货数据表不存在: {shipment_file}"
                }

            self.shipments_df = pd.read_csv(
                shipment_file,
                encoding='gbk',
                dtype={
                    '仓库': str,
                    '物料': str,
                    '日期': str,
                    '出货量': int
                }
            )

            self._loaded = True

            return {
                "success": True,
                "materials_count": len(self.materials_df),
                "shipments_count": len(self.shipments_df),
                "warehouses_count": len(self.shipments_df['仓库'].unique()),
                "materials_list": self.materials_df['物料'].tolist()
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def get_materials(self) -> List[Dict[str, Any]]:
        """
        获取所有物料信息

        Returns:
            物料信息列表，每个元素为包含物料属性的字典
        """
        if not self._loaded or self.materials_df is None:
            return []

        return self.materials_df.to_dict('records')

    def get_material(self, material_name: str) -> Optional[Dict[str, Any]]:
        """
        获取单个物料信息

        Args:
            material_name: 物料名称

        Returns:
            物料信息字典，如果不存在则返回None
        """
        if not self._loaded or self.materials_df is None:
            return None

        result = self.materials_df[self.materials_df['物料'] == material_name]
        if len(result) == 0:
            return None

        return result.iloc[0].to_dict()

    def get_warehouses(self) -> List[str]:
        """
        获取所有仓库名称

        Returns:
            仓库名称列表
        """
        if not self._loaded or self.shipments_df is None:
            return []

        return self.shipments_df['仓库'].unique().tolist()

    def get_shipments(
        self,
        warehouse: Optional[str] = None,
        material: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        获取出货历史

        Args:
            warehouse: 仓库名称（可选，用于筛选）
            material: 物料名称（可选，用于筛选）

        Returns:
            出货记录列表，每个元素为包含出货信息的字典
        """
        if not self._loaded or self.shipments_df is None:
            return []

        df = self.shipments_df.copy()

        if warehouse:
            df = df[df['仓库'] == warehouse]
        if material:
            df = df[df['物料'] == material]

        return df.to_dict('records')

    def get_shipment_quantities(
        self,
        warehouse: str,
        material: str
    ) -> List[int]:
        """
        获取指定仓库物料的出货量列表

        Args:
            warehouse: 仓库名称
            material: 物料名称

        Returns:
            出货量列表（按日期排序）
        """
        if not self._loaded or self.shipments_df is None:
            return []

        df = self.shipments_df[
            (self.shipments_df['仓库'] == warehouse) &
            (self.shipments_df['物料'] == material)
        ].copy()

        # 按日期排序
        df = df.sort_values('日期')

        return df['出货量'].tolist()

    def get_all_warehouse_materials(self) -> List[Dict[str, str]]:
        """
        获取所有仓库-物料组合

        Returns:
            仓库-物料组合列表，每个元素包含warehouse和material字段
        """
        if not self._loaded or self.shipments_df is None:
            return []

        unique_combos = self.shipments_df[['仓库', '物料']].drop_duplicates()
        return unique_combos.rename(
            columns={'仓库': 'warehouse', '物料': 'material'}
        ).to_dict('records')


# 全局单例实例
_data_loader_instance: Optional[DataLoader] = None


def get_data_loader(data_dir: Optional[str] = None) -> DataLoader:
    """
    获取数据加载器单例实例

    Args:
        data_dir: 数据目录路径（首次调用时需要提供）

    Returns:
        DataLoader实例
    """
    global _data_loader_instance

    if _data_loader_instance is None:
        if data_dir is None:
            # 默认使用项目根目录下的data目录
            project_root = Path(__file__).parent.parent.parent.parent
            data_dir = str(project_root)
        _data_loader_instance = DataLoader(data_dir)

    return _data_loader_instance
