from fastapi import APIRouter, HTTPException
from typing import List
from app.services.data_loader import get_data_loader
from app.models.material import MaterialInfo

router = APIRouter(prefix="/api", tags=["物料管理"])


@router.get("/materials", response_model=List[MaterialInfo])
async def get_materials():
    """获取所有物料信息"""
    dl = get_data_loader()
    materials = dl.get_materials()
    return [
        MaterialInfo(
            material=m['物料'],
            moq=int(m['MOQ']),
            leadtime=int(m['leadtime']),
            safety_factor=float(m['安全库存系数'])
        )
        for m in materials
    ]


@router.post("/materials/reload")
async def reload_materials():
    """重新加载物料信息"""
    dl = get_data_loader()
    result = dl.reload()
    if not result["success"]:
        raise HTTPException(status_code=500, detail=result["message"])
    return result


@router.get("/warehouses", response_model=List[str])
async def get_warehouses():
    """获取所有仓库"""
    dl = get_data_loader()
    return dl.get_warehouses()


@router.get("/warehouse-materials")
async def get_warehouse_materials():
    """获取所有仓库-物料组合"""
    dl = get_data_loader()
    return dl.get_all_warehouse_materials()
