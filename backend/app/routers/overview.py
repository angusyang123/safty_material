"""
总览表API路由

功能：
- 获取所有仓库物料的下单建议总览
- 支持模拟不同初始库存参数
"""

from fastapi import APIRouter
from typing import List, Optional
from app.services.data_loader import get_data_loader
from app.services.order_advisor import get_order_advisor
from app.models.prediction import OverviewItem

router = APIRouter(prefix="/api", tags=["总览"])

# 默认初始库存配置
DEFAULT_INITIAL_STOCKS = {
    ("南京仓", "西米"): 2000,
    ("南京仓", "麻薯"): 2000,
    ("北京仓", "西米"): 2000,
    ("北京仓", "麻薯"): 2000,
}


@router.get("/overview", response_model=List[OverviewItem])
async def get_overview(initial_stock: Optional[float] = None):
    """
    获取总览表 - 所有仓库物料的下单建议

    Args:
        initial_stock: 可选的初始库存参数，用于模拟（应用于所有物料）
    """
    dl = get_data_loader()
    advisor = get_order_advisor()

    results = []

    for item in dl.get_all_warehouse_materials():
        warehouse = item['warehouse']
        material_name = item['material']

        # 获取物料信息
        material = dl.get_material(material_name)
        if not material:
            continue

        # 获取出货历史
        quantities = dl.get_shipment_quantities(warehouse, material_name)
        if not quantities:
            continue

        # 获取初始库存
        stock = initial_stock if initial_stock is not None else DEFAULT_INITIAL_STOCKS.get(
            (warehouse, material_name), 2000
        )

        # 分析
        analysis = advisor.analyze(
            history_data=quantities,
            initial_stock=stock,
            moq=int(material['MOQ']),
            leadtime=int(material['leadtime']),
            safety_factor=float(material['安全库存系数'])
        )

        results.append(OverviewItem(
            warehouse=warehouse,
            material=material_name,
            current_stock=stock,
            safety_stock=analysis['safety_stock'],
            need_order=analysis['need_order'],
            order_date=analysis['first_order_day'],
            order_quantity=analysis['first_order_quantity'],
            leadtime=int(material['leadtime']),
            moq=int(material['MOQ'])
        ))

    # 排序：需要下单的排在前面
    results.sort(key=lambda x: (not x.need_order, x.order_date or ""))

    return results
