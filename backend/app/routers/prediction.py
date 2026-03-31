"""
预测数据管理API路由

功能：
1. POST /api/prediction/generate - 生成预测CSV文件
2. GET /api/prediction/read - 读取预测CSV文件
3. POST /api/order/generate - 生成下单建议CSV文件
4. GET /api/order/read - 读取下单建议CSV文件
5. GET /api/inventory/chart - 获取图表数据

设计原则：后端生成CSV，前端读取CSV展示
"""

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import FileResponse
from typing import Optional
from pathlib import Path
import pandas as pd
import numpy as np
import math
from datetime import datetime, timedelta

from app.services.data_loader import get_data_loader
from app.services.predictor import get_predictor

router = APIRouter(prefix="/api", tags=["预测数据管理"])

# 输出目录
OUTPUT_DIR = Path(__file__).parent.parent.parent.parent / "output"
OUTPUT_DIR.mkdir(exist_ok=True)


@router.post("/prediction/generate")
async def generate_prediction(
    warehouse: str,
    material: str,
    initial_stock: float = Query(2000, description="初始库存(kg)"),
    predict_days: int = Query(60, description="预测天数"),
    start_date: Optional[str] = Query(None, description="预测开始日期(YYYY-MM-DD)")
):
    """
    生成预测数据CSV文件

    生成的CSV包含：日期、预测出货量、安全库存
    用户可以编辑此文件调整预测数据
    """
    dl = get_data_loader()
    predictor = get_predictor()

    # 验证物料
    material_info = dl.get_material(material)
    if not material_info:
        raise HTTPException(status_code=404, detail=f"物料 {material} 不存在")

    # 获取历史数据
    quantities = dl.get_shipment_quantities(warehouse, material)
    if not quantities:
        raise HTTPException(status_code=404, detail=f"未找到 {warehouse} - {material} 的出货数据")

    # 参数
    moq = int(material_info['MOQ'])
    leadtime = int(material_info['leadtime'])
    safety_factor = float(material_info['安全库存系数'])

    # 计算预测
    predictions = predictor.predict(quantities, predict_days)

    # 计算安全库存
    safety_stock = predictor.calculate_safety_stock(quantities, safety_factor, leadtime)

    # 确定开始日期
    if start_date:
        current_date = datetime.strptime(start_date, "%Y-%m-%d")
    else:
        current_date = datetime.now()

    # 生成日期列表
    dates = [(current_date + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(predict_days)]

    # 创建DataFrame
    df = pd.DataFrame({
        "日期": dates,
        "预测出货量(kg)": [round(p, 2) for p in predictions],
        "安全库存(kg)": round(safety_stock, 2)
    })

    # 保存CSV
    filename = f"预测数据_{warehouse}_{material}.csv"
    filepath = OUTPUT_DIR / filename
    df.to_csv(filepath, index=False, encoding='gbk')

    return {
        "success": True,
        "message": "预测数据已生成",
        "file_path": str(filepath),
        "file_name": filename,
        "warehouse": warehouse,
        "material": material,
        "predict_days": predict_days,
        "initial_stock": initial_stock,
        "moq": moq,
        "leadtime": leadtime,
        "safety_factor": safety_factor,
        "safety_stock": round(safety_stock, 2),
        "avg_prediction": round(np.mean(predictions), 2),
        "total_prediction": round(sum(predictions), 2)
    }


@router.get("/prediction/read")
async def read_prediction(warehouse: str, material: str):
    """读取预测数据CSV文件"""
    filename = f"预测数据_{warehouse}_{material}.csv"
    filepath = OUTPUT_DIR / filename

    if not filepath.exists():
        raise HTTPException(status_code=404, detail=f"预测数据文件不存在，请先生成预测数据")

    df = pd.read_csv(filepath, encoding='gbk')

    return {
        "success": True,
        "data": df.to_dict('records'),
        "summary": {
            "total_days": len(df),
            "avg_prediction": round(df["预测出货量(kg)"].mean(), 2),
            "total_prediction": round(df["预测出货量(kg)"].sum(), 2),
            "safety_stock": df["安全库存(kg)"].iloc[0] if len(df) > 0 else 0
        }
    }


@router.post("/order/generate")
async def generate_order_suggestion(
    warehouse: str,
    material: str,
    initial_stock: float = Query(2000, description="初始库存(kg)"),
    moq: Optional[int] = Query(None, description="最小订货量"),
    leadtime: Optional[int] = Query(None, description="前置时间(天)")
):
    """
    根据预测数据CSV生成下单建议CSV

    读取用户可能编辑过的预测CSV，生成下单建议
    """
    # 读取预测数据
    pred_filename = f"预测数据_{warehouse}_{material}.csv"
    pred_filepath = OUTPUT_DIR / pred_filename

    if not pred_filepath.exists():
        raise HTTPException(status_code=404, detail="请先生成预测数据")

    pred_df = pd.read_csv(pred_filepath, encoding='gbk')
    predictions = pred_df["预测出货量(kg)"].tolist()
    dates = pred_df["日期"].tolist()
    safety_stock = pred_df["安全库存(kg)"].iloc[0]

    # 获取物料信息
    dl = get_data_loader()
    material_info = dl.get_material(material)
    if not material_info:
        raise HTTPException(status_code=404, detail=f"物料 {material} 不存在")

    moq = moq or int(material_info['MOQ'])
    leadtime = leadtime or int(material_info['leadtime'])

    # 模拟库存并生成下单建议
    arrival_plan = {}
    order_plan = {}
    temp_stock = initial_stock

    for day, prediction in enumerate(predictions, start=1):
        stock_after = temp_stock - prediction
        if stock_after <= safety_stock:
            arrival_day = day
            order_day = arrival_day - leadtime
            if order_day >= 1 and order_day not in order_plan:
                order_plan[order_day] = moq
                arrival_plan[arrival_day] = moq
                temp_stock = stock_after + moq
            else:
                temp_stock = stock_after
        else:
            temp_stock = stock_after

    # 生成详细数据
    results = []
    current_stock = initial_stock

    for day, (date, prediction) in enumerate(zip(dates, predictions), start=1):
        yesterday_stock = current_stock
        stock_after_shipment = yesterday_stock - prediction
        arrival_qty = arrival_plan.get(day, 0)
        ending_stock = stock_after_shipment + arrival_qty
        is_order_day = day in order_plan
        order_qty = order_plan.get(day, 0)

        results.append({
            "日期": date,
            "初始库存(kg)": round(yesterday_stock, 2),
            "预测出货(kg)": round(prediction, 2),
            "出货后库存(kg)": round(stock_after_shipment, 2),
            "到货量(kg)": arrival_qty,
            "结束库存(kg)": round(ending_stock, 2),
            "安全库存(kg)": round(safety_stock, 2),
            "是否下单": "是" if is_order_day else "否",
            "下单数量(kg)": order_qty
        })

        current_stock = ending_stock

    # 保存CSV
    df = pd.DataFrame(results)
    filename = f"下单建议_{warehouse}_{material}.csv"
    filepath = OUTPUT_DIR / filename
    df.to_csv(filepath, index=False, encoding='gbk')

    return {
        "success": True,
        "message": "下单建议已生成",
        "file_path": str(filepath),
        "file_name": filename,
        "summary": {
            "total_days": len(df),
            "order_count": len(order_plan),
            "order_dates": [f"第{d}天" for d in sorted(order_plan.keys())],
            "order_quantities": [order_plan[d] for d in sorted(order_plan.keys())],
            "total_order_qty": sum(order_plan.values()),
            "min_stock": round(df["结束库存(kg)"].min(), 2),
            "final_stock": round(df["结束库存(kg)"].iloc[-1], 2)
        }
    }


@router.get("/order/read")
async def read_order_suggestion(warehouse: str, material: str):
    """读取下单建议CSV文件"""
    filename = f"下单建议_{warehouse}_{material}.csv"
    filepath = OUTPUT_DIR / filename

    if not filepath.exists():
        raise HTTPException(status_code=404, detail=f"下单建议文件不存在，请先生成")

    df = pd.read_csv(filepath, encoding='gbk')

    # 提取下单记录
    orders = df[df["是否下单"] == "是"][["日期", "下单数量(kg)"]].to_dict('records')

    return {
        "success": True,
        "data": df.to_dict('records'),
        "orders": orders,
        "summary": {
            "total_days": len(df),
            "order_count": len(orders),
            "min_stock": round(df["结束库存(kg)"].min(), 2),
            "final_stock": round(df["结束库存(kg)"].iloc[-1], 2)
        }
    }


@router.get("/material/info")
async def get_material_info_api(material: str):
    """
    获取物料信息

    返回物料的MOQ、LeadTime、安全库存系数等信息
    """
    dl = get_data_loader()
    material_info = dl.get_material(material)
    if not material_info:
        raise HTTPException(status_code=404, detail=f"物料 {material} 不存在")

    return {
        "success": True,
        "material": material,
        "moq": int(material_info['MOQ']),
        "leadtime": int(material_info['leadtime']),
        "safety_factor": float(material_info['安全库存系数'])
    }


@router.get("/inventory/chart")
async def get_inventory_chart_data(
    warehouse: str,
    material: str,
    history_days: int = Query(30, description="显示历史天数")
):
    """
    获取图表展示数据

    返回包含历史30天 + 预测数据的完整图表数据
    用于前端组合图展示：
    - 柱：历史出货量（蓝色）、预测出货量（黄色）、预测进货量（红色）
    - 折线：预测库存、安全库存线
    """
    dl = get_data_loader()

    # 获取历史数据
    shipments = dl.get_shipments(warehouse, material)
    if not shipments:
        raise HTTPException(status_code=404, detail=f"未找到 {warehouse} - {material} 的出货数据")

    # 取最近N天历史
    recent_shipments = shipments[-history_days:] if len(shipments) > history_days else shipments

    # 读取预测数据
    pred_filename = f"预测数据_{warehouse}_{material}.csv"
    pred_filepath = OUTPUT_DIR / pred_filename
    predict_data = []
    if pred_filepath.exists():
        pred_df = pd.read_csv(pred_filepath, encoding='gbk')
        predict_data = pred_df.to_dict('records')

    # 读取下单建议
    order_filename = f"下单建议_{warehouse}_{material}.csv"
    order_filepath = OUTPUT_DIR / order_filename
    order_data = []
    if order_filepath.exists():
        order_df = pd.read_csv(order_filepath, encoding='gbk')
        order_data = order_df.to_dict('records')

    # 组装历史数据
    history_dates = [s['日期'] for s in recent_shipments]
    history_outbound = [s['出货量'] for s in recent_shipments]

    # 组装预测数据
    predict_dates = [d['日期'] for d in predict_data]
    predict_outbound = [d['预测出货量(kg)'] for d in predict_data]
    safety_stock = predict_data[0]['安全库存(kg)'] if predict_data else 0

    # 预测进货量和库存
    predict_inbound = [o['到货量(kg)'] for o in order_data] if order_data else []
    predict_stock = [o['结束库存(kg)'] for o in order_data] if order_data else []

    return {
        "success": True,
        "history": {
            "dates": history_dates,
            "outbound": history_outbound
        },
        "predict": {
            "dates": predict_dates,
            "outbound": predict_outbound,
            "inbound": predict_inbound,
            "stock": predict_stock,
            "safety_stock": safety_stock
        },
        "all_dates": history_dates + predict_dates
    }
