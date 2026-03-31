from pydantic import BaseModel
from typing import Optional


class MaterialInfo(BaseModel):
    """物料信息模型"""
    material: str              # 物料名称
    moq: int                   # 最小订货量
    leadtime: int              # 前置时间（天）
    safety_factor: float       # 安全库存系数

    class Config:
        json_schema_extra = {
            "example": {
                "material": "麻薯",
                "moq": 100,
                "leadtime": 10,
                "safety_factor": 1.65
            }
        }


class MaterialWithStock(MaterialInfo):
    """带库存信息的物料模型"""
    warehouse: str             # 仓库名称
    current_stock: float       # 当前库存

    class Config:
        json_schema_extra = {
            "example": {
                "material": "麻薯",
                "moq": 100,
                "leadtime": 10,
                "safety_factor": 1.65,
                "warehouse": "南京仓",
                "current_stock": 200
            }
        }
