from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.config import settings
from app.routers.material import router as material_router
from app.routers.overview import router as overview_router
from app.routers.prediction import router as prediction_router
from app.services.data_loader import get_data_loader


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时加载数据
    dl = get_data_loader()
    result = dl.reload()
    if result["success"]:
        print(f"数据加载成功: {result['materials_count']} 个物料, {result['shipments_count']} 条出货记录")
    else:
        print(f"数据加载失败: {result.get('error', '未知错误')}")
    yield
    # 关闭时清理（如果需要）


app = FastAPI(
    title="库存预测分析系统",
    description="基于历史出货数据的库存预测和下单建议系统",
    version="1.0.0",
    lifespan=lifespan
)

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(material_router)
app.include_router(overview_router)
app.include_router(prediction_router)


@app.get("/")
async def root():
    return {"message": "库存预测分析系统 API", "version": "1.0.0"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
