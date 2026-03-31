# 库存预测分析系统 - 实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 构建一个前后端分离的库存预测分析Web应用，支持多仓库多物料的库存预测和下单建议。

**Architecture:** 后端采用FastAPI分层架构（路由层→服务层→模型层），前端采用Vue3组件化架构。预测算法使用策略模式便于扩展。数据存储使用CSV文件，与代码分离。

**Tech Stack:** FastAPI, Python, Vue.js 3, Element Plus, ECharts, Pandas

---

## Phase 1: 后端基础框架

### Task 1: 创建后端项目结构

**Files:**
- Create: `backend/requirements.txt`
- Create: `backend/app/__init__.py`
- Create: `backend/app/config.py`
- Create: `backend/app/main.py`

- [ ] **Step 1: 创建requirements.txt**

```txt
fastapi==0.109.0
uvicorn==0.27.0
pandas==2.1.4
numpy==1.26.3
pydantic==2.5.3
python-multipart==0.0.6
```

- [ ] **Step 2: 创建app/__init__.py**

```python
# 库存预测分析系统 - 后端服务
```

- [ ] **Step 3: 创建config.py配置文件**

```python
from pydantic_settings import BaseSettings
from pathlib import Path


class Settings(BaseSettings):
    # 数据目录
    DATA_DIR: str = str(Path(__file__).parent.parent.parent / "data")

    # 服务器配置
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000

    # CORS配置
    CORS_ORIGINS: list = ["http://localhost:5173", "http://localhost:3000"]

    class Config:
        env_file = ".env"


settings = Settings()
```

- [ ] **Step 4: 创建main.py入口文件**

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings

app = FastAPI(
    title="库存预测分析系统",
    description="基于历史出货数据的库存预测和下单建议系统",
    version="1.0.0"
)

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"message": "库存预测分析系统 API", "version": "1.0.0"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
```

- [ ] **Step 5: 测试后端启动**

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

访问 http://localhost:8000/docs 确认API文档可访问。

---

### Task 2: 创建数据模型

**Files:**
- Create: `backend/app/models/__init__.py`
- Create: `backend/app/models/material.py`
- Create: `backend/app/models/prediction.py`

- [ ] **Step 1: 创建models/__init__.py**

```python
from app.models.material import MaterialInfo
from app.models.prediction import PredictionResult, ComparisonResult

__all__ = ["MaterialInfo", "PredictionResult", "ComparisonResult"]
```

- [ ] **Step 2: 创建material.py物料模型**

```python
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
```

- [ ] **Step 3: 创建prediction.py预测结果模型**

```python
from pydantic import BaseModel
from typing import Optional


class OrderSuggestion(BaseModel):
    """下单建议"""
    need_order: bool           # 是否需要下单
    order_date: Optional[str]  # 建议下单日期
    order_quantity: Optional[int]  # 下单数量


class PredictionResult(BaseModel):
    """预测结果模型"""
    warehouse: str                     # 仓库
    material: str                      # 物料
    moq: int                           # 最小订货量
    leadtime: int                      # 前置时间
    safety_factor: float               # 安全库存系数
    current_stock: float               # 当前库存
    safety_stock: float                # 安全库存
    predictions: list[float]           # 未来N天预测出货量
    predicted_stocks: list[float]      # 预测库存变化
    order_suggestion: OrderSuggestion  # 下单建议


class ComparisonData(BaseModel):
    """对比数据点"""
    date: str
    actual: Optional[float]     # 实际出货
    predicted: Optional[float]  # 预测出货
    error: Optional[float]      # 误差


class ComparisonMetrics(BaseModel):
    """对比统计指标"""
    mean_error: float           # 平均误差
    std_error: float            # 误差标准差
    mape: float                 # 平均绝对百分比误差
    accuracy_rate: float        # 准确率


class ComparisonResult(BaseModel):
    """对比分析结果"""
    warehouse: str
    material: str
    data: list[ComparisonData]  # 对比数据列表
    metrics: ComparisonMetrics  # 统计指标


class OverviewItem(BaseModel):
    """总览表单项"""
    warehouse: str
    material: str
    current_stock: float
    safety_stock: float
    need_order: bool
    order_date: Optional[str]
    order_quantity: Optional[int]
    leadtime: int
    moq: int
```

- [ ] **Step 4: 验证模型导入**

```bash
cd backend
python -c "from app.models import MaterialInfo, PredictionResult, ComparisonResult; print('Models imported successfully')"
```

---

### Task 3: 创建数据加载服务

**Files:**
- Create: `backend/app/services/__init__.py`
- Create: `backend/app/services/data_loader.py`

- [ ] **Step 1: 创建services/__init__.py**

```python
from app.services.data_loader import DataLoader

__all__ = ["DataLoader"]
```

- [ ] **Step 2: 创建data_loader.py数据加载服务**

```python
import pandas as pd
from pathlib import Path
from typing import Optional
from app.config import settings


class DataLoader:
    """数据加载服务 - 从CSV文件加载物料和出货数据"""

    def __init__(self, data_dir: Optional[str] = None):
        self._data_dir = Path(data_dir) if data_dir else Path(settings.DATA_DIR)
        self._materials_df: Optional[pd.DataFrame] = None
        self._shipments_df: Optional[pd.DataFrame] = None

    def reload(self) -> dict:
        """重新加载CSV数据"""
        try:
            self._materials_df = pd.read_csv(
                self._data_dir / "物料信息表.csv",
                encoding='gbk'
            )
            self._shipments_df = pd.read_csv(
                self._data_dir / "仓库出货量.csv",
                encoding='gbk'
            )
            return {
                "success": True,
                "message": "数据加载成功",
                "materials_count": len(self._materials_df),
                "shipments_count": len(self._shipments_df)
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"数据加载失败: {str(e)}"
            }

    def get_materials(self) -> list[dict]:
        """获取所有物料信息"""
        if self._materials_df is None:
            self.reload()
        return self._materials_df.to_dict('records')

    def get_material(self, material_name: str) -> Optional[dict]:
        """获取单个物料信息"""
        materials = self.get_materials()
        for m in materials:
            if m['物料'] == material_name:
                return {
                    'material': m['物料'],
                    'moq': int(m['MOQ']),
                    'leadtime': int(m['leadtime']),
                    'safety_factor': float(m['安全库存系数'])
                }
        return None

    def get_warehouses(self) -> list[str]:
        """获取所有仓库名称"""
        if self._shipments_df is None:
            self.reload()
        return self._shipments_df['仓库'].unique().tolist()

    def get_shipments(self, warehouse: str, material: str) -> list[dict]:
        """获取指定仓库物料的出货历史"""
        if self._shipments_df is None:
            self.reload()
        filtered = self._shipments_df[
            (self._shipments_df['仓库'] == warehouse) &
            (self._shipments_df['物料'] == material)
        ]
        return filtered.to_dict('records')

    def get_shipment_quantities(self, warehouse: str, material: str) -> list[float]:
        """获取出货量列表（仅数值，用于预测计算）"""
        shipments = self.get_shipments(warehouse, material)
        return [float(s['出货量']) for s in shipments]

    def get_all_warehouse_materials(self) -> list[tuple[str, str]]:
        """获取所有仓库-物料组合"""
        if self._shipments_df is None:
            self.reload()
        pairs = self._shipments_df[['仓库', '物料']].drop_duplicates()
        return [(row['仓库'], row['物料']) for _, row in pairs.iterrows()]


# 全局数据加载器实例
_data_loader: Optional[DataLoader] = None


def get_data_loader() -> DataLoader:
    """获取数据加载器单例"""
    global _data_loader
    if _data_loader is None:
        _data_loader = DataLoader()
        _data_loader.reload()
    return _data_loader
```

- [ ] **Step 3: 测试数据加载**

```bash
cd backend
python -c "
from app.services.data_loader import DataLoader
dl = DataLoader('D:/TRAE Projects/safty_material/data')
result = dl.reload()
print(result)
print('Materials:', dl.get_materials())
print('Warehouses:', dl.get_warehouses())
print('Sample shipments:', dl.get_shipments('南京仓', '西米')[:3])
"
```

---

### Task 4: 创建预测算法模块

**Files:**
- Create: `backend/app/services/predictor.py`

- [ ] **Step 1: 创建predictor.py预测算法（策略模式）**

```python
from abc import ABC, abstractmethod
from typing import List
import numpy as np


class PredictionStrategy(ABC):
    """预测算法抽象基类"""

    @abstractmethod
    def predict(self, history_data: List[float], window: int) -> List[float]:
        """
        预测未来window天的出货量

        Args:
            history_data: 历史出货数据
            window: 预测窗口（天数）

        Returns:
            预测的未来window天出货量列表
        """
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """算法名称"""
        pass


class MovingAverageStrategy(PredictionStrategy):
    """移动平均预测算法"""

    def __init__(self, period: int = 4):
        """
        Args:
            period: 移动平均周期（默认4天）
        """
        self.period = period

    @property
    def name(self) -> str:
        return f"移动平均({self.period}天)"

    def predict(self, history_data: List[float], window: int) -> List[float]:
        """
        使用移动平均法预测未来出货量

        对未来第i天，使用最近period+i-1天的数据进行预测
        """
        predictions = []
        data = list(history_data)

        for i in range(window):
            # 计算移动平均
            start_idx = max(0, len(data) - self.period)
            recent_data = data[start_idx:]
            avg = sum(recent_data) / len(recent_data)
            predictions.append(avg)
            # 将预测值加入数据，用于后续预测
            data.append(avg)

        return predictions


class Predictor:
    """预测器 - 支持策略切换"""

    def __init__(self, strategy: PredictionStrategy = None):
        self._strategy = strategy or MovingAverageStrategy()

    def set_strategy(self, strategy: PredictionStrategy):
        """设置预测策略"""
        self._strategy = strategy

    def predict(self, history_data: List[float], window: int) -> List[float]:
        """执行预测"""
        if len(history_data) < self._strategy.period:
            # 数据不足时，使用全部数据的平均值
            avg = sum(history_data) / len(history_data)
            return [avg] * window
        return self._strategy.predict(history_data, window)

    def calculate_errors(
        self,
        history_data: List[float],
        window: int
    ) -> List[float]:
        """
        计算历史预测误差

        对历史数据进行回溯预测，计算每天的预测误差
        """
        errors = []
        min_data_length = window + self._strategy.period

        if len(history_data) < min_data_length:
            return errors

        # 从第(window + period)天开始计算误差
        for i in range(min_data_length - 1, len(history_data)):
            # 使用之前的数据预测当天
            train_data = history_data[:i]
            actual = history_data[i]

            # 预测当天（取第一个预测值）
            predictions = self.predict(train_data, window)
            predicted = predictions[0] if predictions else 0

            error = actual - predicted
            errors.append(error)

        return errors

    def calculate_safety_stock(
        self,
        history_data: List[float],
        safety_factor: float,
        leadtime: int
    ) -> float:
        """
        计算安全库存

        安全库存 = 误差标准差 × 安全库存系数 × leadtime
        """
        errors = self.calculate_errors(history_data, leadtime)

        if len(errors) < 2:
            # 误差数据不足，使用历史数据标准差
            std = np.std(history_data) if len(history_data) > 1 else 0
        else:
            std = np.std(errors)

        return std * safety_factor * leadtime


# 默认预测器实例
_default_predictor: Predictor = None


def get_predictor() -> Predictor:
    """获取默认预测器"""
    global _default_predictor
    if _default_predictor is None:
        _default_predictor = Predictor()
    return _default_predictor
```

- [ ] **Step 2: 测试预测算法**

```bash
cd backend
python -c "
from app.services.predictor import MovingAverageStrategy, Predictor

# 测试数据
data = [100, 120, 110, 130, 115, 125, 118, 122, 108, 135]

predictor = Predictor()
predictions = predictor.predict(data, 4)
print('预测未来4天:', predictions)

errors = predictor.calculate_errors(data, 4)
print('历史误差:', errors)

safety = predictor.calculate_safety_stock(data, 1.65, 4)
print('安全库存:', safety)
"
```

---

### Task 5: 创建库存计算和下单建议服务

**Files:**
- Create: `backend/app/services/inventory_calculator.py`
- Create: `backend/app/services/order_advisor.py`

- [ ] **Step 1: 创建inventory_calculator.py库存计算服务**

```python
from typing import List, Dict, Any
import copy


class InventoryCalculator:
    """库存计算服务 - 模拟库存变化"""

    def simulate_inventory(
        self,
        initial_stock: float,
        predicted_outbound: List[float],
        incoming_orders: Dict[int, float] = None
    ) -> List[float]:
        """
        模拟库存变化

        Args:
            initial_stock: 初始库存
            predicted_outbound: 预测的每日出货量
            incoming_orders: 预期到货 {天数索引: 到货量}

        Returns:
            每日库存列表
        """
        incoming_orders = incoming_orders or {}
        stocks = []
        current_stock = initial_stock

        for day, outbound in enumerate(predicted_outbound):
            # 当日到货
            incoming = incoming_orders.get(day, 0)
            current_stock = current_stock - outbound + incoming
            stocks.append(current_stock)

        return stocks

    def find_first_stockout(
        self,
        stocks: List[float],
        safety_stock: float
    ) -> int:
        """
        找到首次低于安全库存的天数索引

        Returns:
            首次低于安全库存的索引，如果未低于返回-1
        """
        for i, stock in enumerate(stocks):
            if stock < safety_stock:
                return i
        return -1


# 默认实例
_calculator = InventoryCalculator()


def get_inventory_calculator() -> InventoryCalculator:
    return _calculator
```

- [ ] **Step 2: 创建order_advisor.py下单建议服务**

```python
from typing import List, Dict, Any, Optional
from app.services.predictor import Predictor, get_predictor
from app.services.inventory_calculator import InventoryCalculator, get_inventory_calculator


class OrderAdvisor:
    """下单建议服务 - 综合预测和库存计算，给出下单建议"""

    def __init__(
        self,
        predictor: Predictor = None,
        calculator: InventoryCalculator = None
    ):
        self._predictor = predictor or get_predictor()
        self._calculator = calculator or get_inventory_calculator()

    def analyze(
        self,
        history_data: List[float],
        initial_stock: float,
        moq: int,
        leadtime: int,
        safety_factor: float
    ) -> Dict[str, Any]:
        """
        综合分析并给出下单建议

        Args:
            history_data: 历史出货数据
            initial_stock: 当前库存
            moq: 最小订货量
            leadtime: 前置时间
            safety_factor: 安全库存系数

        Returns:
            分析结果字典
        """
        # 1. 预测未来leadtime天的出货量
        predictions = self._predictor.predict(history_data, leadtime)

        # 2. 计算安全库存
        safety_stock = self._predictor.calculate_safety_stock(
            history_data, safety_factor, leadtime
        )

        # 3. 模拟库存变化（假设不下单）
        predicted_stocks = self._calculator.simulate_inventory(
            initial_stock, predictions
        )

        # 4. 判断是否需要下单
        first_stockout_idx = self._calculator.find_first_stockout(
            predicted_stocks, safety_stock
        )

        need_order = first_stockout_idx >= 0
        order_date = None
        order_quantity = None

        if need_order:
            # 建议下单日期：在首次低于安全库存的leadtime天前下单
            order_date_idx = max(0, first_stockout_idx - leadtime)
            order_date = f"第{order_date_idx + 1}天"
            order_quantity = moq

        return {
            "predictions": predictions,
            "predicted_stocks": predicted_stocks,
            "safety_stock": safety_stock,
            "need_order": need_order,
            "order_date": order_date,
            "order_quantity": order_quantity,
            "first_stockout_day": first_stockout_idx + 1 if need_order else None
        }

    def get_full_prediction(
        self,
        history_data: List[float],
        initial_stock: float,
        moq: int,
        leadtime: int,
        safety_factor: float
    ) -> Dict[str, Any]:
        """
        获取完整预测结果（包含下单后的库存模拟）
        """
        # 基础分析
        analysis = self.analyze(
            history_data, initial_stock, moq, leadtime, safety_factor
        )

        # 如果需要下单，重新模拟库存（考虑下单到货）
        if analysis["need_order"]:
            incoming_orders = {
                leadtime: moq  # leadtime天后到货
            }
            analysis["predicted_stocks_with_order"] = self._calculator.simulate_inventory(
                initial_stock, analysis["predictions"], incoming_orders
            )
        else:
            analysis["predicted_stocks_with_order"] = analysis["predicted_stocks"]

        return analysis


# 默认实例
_advisor = None


def get_order_advisor() -> OrderAdvisor:
    global _advisor
    if _advisor is None:
        _advisor = OrderAdvisor()
    return _advisor
```

- [ ] **Step 3: 更新services/__init__.py**

```python
from app.services.data_loader import DataLoader, get_data_loader
from app.services.predictor import Predictor, get_predictor
from app.services.inventory_calculator import InventoryCalculator, get_inventory_calculator
from app.services.order_advisor import OrderAdvisor, get_order_advisor

__all__ = [
    "DataLoader", "get_data_loader",
    "Predictor", "get_predictor",
    "InventoryCalculator", "get_inventory_calculator",
    "OrderAdvisor", "get_order_advisor"
]
```

- [ ] **Step 4: 测试下单建议服务**

```bash
cd backend
python -c "
from app.services import get_data_loader, get_order_advisor

dl = get_data_loader()
advisor = get_order_advisor()

# 获取南京仓西米的出货数据
quantities = dl.get_shipment_quantities('南京仓', '西米')
material = dl.get_material('西米')

print('物料信息:', material)
print('历史出货数据量:', len(quantities))

# 分析
result = advisor.get_full_prediction(
    history_data=quantities,
    initial_stock=200,
    moq=material['moq'],
    leadtime=material['leadtime'],
    safety_factor=material['safety_factor']
)

print('预测出货:', result['predictions'])
print('安全库存:', result['safety_stock'])
print('需要下单:', result['need_order'])
print('建议下单日期:', result['order_date'])
print('下单数量:', result['order_quantity'])
"
```

---

## Phase 2: 后端API接口

### Task 6: 创建物料和仓库API

**Files:**
- Create: `backend/app/routers/__init__.py`
- Create: `backend/app/routers/material.py`

- [ ] **Step 1: 创建routers/__init__.py**

```python
from app.routers.material import router as material_router

__all__ = ["material_router"]
```

- [ ] **Step 2: 创建material.py物料API**

```python
from fastapi import APIRouter, HTTPException
from typing import List
from app.services.data_loader import get_data_loader
from app.models.material import MaterialInfo, MaterialWithStock

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
    pairs = dl.get_all_warehouse_materials()
    return [{"warehouse": w, "material": m} for w, m in pairs]
```

- [ ] **Step 3: 更新main.py注册路由**

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers.material import router as material_router

app = FastAPI(
    title="库存预测分析系统",
    description="基于历史出货数据的库存预测和下单建议系统",
    version="1.0.0"
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


@app.get("/")
async def root():
    return {"message": "库存预测分析系统 API", "version": "1.0.0"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
```

- [ ] **Step 4: 测试物料API**

```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

访问 http://localhost:8000/docs 测试：
- GET /api/materials
- GET /api/warehouses
- POST /api/materials/reload

---

### Task 7: 创建总览表API

**Files:**
- Create: `backend/app/routers/overview.py`

- [ ] **Step 1: 创建overview.py总览API**

```python
from fastapi import APIRouter
from typing import List, Optional
from app.services.data_loader import get_data_loader
from app.services.order_advisor import get_order_advisor
from app.models.prediction import OverviewItem

router = APIRouter(prefix="/api", tags=["总览"])

# 默认初始库存配置（后续可从配置文件读取）
DEFAULT_INITIAL_STOCK = 200


@router.get("/overview", response_model=List[OverviewItem])
async def get_overview(initial_stock: Optional[float] = None):
    """
    获取总览表 - 所有仓库物料的下单建议

    Args:
        initial_stock: 可选的初始库存参数，用于模拟
    """
    dl = get_data_loader()
    advisor = get_order_advisor()

    initial_stock = initial_stock or DEFAULT_INITIAL_STOCK
    results = []

    for warehouse, material_name in dl.get_all_warehouse_materials():
        # 获取物料信息
        material = dl.get_material(material_name)
        if not material:
            continue

        # 获取出货历史
        quantities = dl.get_shipment_quantities(warehouse, material_name)
        if not quantities:
            continue

        # 分析
        analysis = advisor.analyze(
            history_data=quantities,
            initial_stock=initial_stock,
            moq=material['moq'],
            leadtime=material['leadtime'],
            safety_factor=material['safety_factor']
        )

        results.append(OverviewItem(
            warehouse=warehouse,
            material=material_name,
            current_stock=initial_stock,
            safety_stock=round(analysis['safety_stock'], 2),
            need_order=analysis['need_order'],
            order_date=analysis['order_date'],
            order_quantity=analysis['order_quantity'],
            leadtime=material['leadtime'],
            moq=material['moq']
        ))

    # 排序：需要下单的排在前面
    results.sort(key=lambda x: (not x.need_order, x.order_date or ""))

    return results
```

- [ ] **Step 2: 更新main.py注册路由**

在main.py中添加：

```python
from app.routers.overview import router as overview_router

# 在 app.include_router(material_router) 后添加
app.include_router(overview_router)
```

- [ ] **Step 3: 测试总览API**

```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

访问 http://localhost:8000/docs 测试 GET /api/overview

---

### Task 8: 创建预测详情API

**Files:**
- Create: `backend/app/routers/prediction.py`

- [ ] **Step 1: 创建prediction.py预测详情API**

```python
from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from app.services.data_loader import get_data_loader
from app.services.order_advisor import get_order_advisor
from app.services.predictor import get_predictor
from app.models.prediction import PredictionResult, ComparisonResult, OrderSuggestion

router = APIRouter(prefix="/api", tags=["预测分析"])

DEFAULT_INITIAL_STOCK = 200


@router.get("/prediction/{warehouse}/{material}", response_model=PredictionResult)
async def get_prediction(
    warehouse: str,
    material: str,
    initial_stock: Optional[float] = Query(None, description="初始库存，用于模拟")
):
    """
    获取单个仓库物料的预测详情
    """
    dl = get_data_loader()
    advisor = get_order_advisor()

    # 验证物料
    material_info = dl.get_material(material)
    if not material_info:
        raise HTTPException(status_code=404, detail=f"物料 {material} 不存在")

    # 获取出货数据
    quantities = dl.get_shipment_quantities(warehouse, material)
    if not quantities:
        raise HTTPException(status_code=404, detail=f"未找到 {warehouse} - {material} 的出货数据")

    # 分析
    initial_stock = initial_stock or DEFAULT_INITIAL_STOCK
    analysis = advisor.get_full_prediction(
        history_data=quantities,
        initial_stock=initial_stock,
        moq=material_info['moq'],
        leadtime=material_info['leadtime'],
        safety_factor=material_info['safety_factor']
    )

    return PredictionResult(
        warehouse=warehouse,
        material=material,
        moq=material_info['moq'],
        leadtime=material_info['leadtime'],
        safety_factor=material_info['safety_factor'],
        current_stock=initial_stock,
        safety_stock=round(analysis['safety_stock'], 2),
        predictions=[round(p, 2) for p in analysis['predictions']],
        predicted_stocks=[round(s, 2) for s in analysis['predicted_stocks']],
        order_suggestion=OrderSuggestion(
            need_order=analysis['need_order'],
            order_date=analysis['order_date'],
            order_quantity=analysis['order_quantity']
        )
    )


@router.get("/prediction/{warehouse}/{material}/compare", response_model=ComparisonResult)
async def get_comparison(
    warehouse: str,
    material: str
):
    """
    获取预测vs实际对比分析
    """
    dl = get_data_loader()
    predictor = get_predictor()

    # 验证物料
    material_info = dl.get_material(material)
    if not material_info:
        raise HTTPException(status_code=404, detail=f"物料 {material} 不存在")

    # 获取出货数据
    shipments = dl.get_shipments(warehouse, material)
    quantities = dl.get_shipment_quantities(warehouse, material)

    if not quantities:
        raise HTTPException(status_code=404, detail=f"未找到 {warehouse} - {material} 的出货数据")

    leadtime = material_info['leadtime']

    # 计算历史预测误差
    errors = predictor.calculate_errors(quantities, leadtime)

    # 构建对比数据
    comparison_data = []
    min_data_length = leadtime + predictor._strategy.period

    for i, shipment in enumerate(shipments):
        if i < min_data_length - 1:
            # 数据不足，无法计算预测
            comparison_data.append({
                "date": shipment['日期'],
                "actual": float(shipment['出货量']),
                "predicted": None,
                "error": None
            })
        else:
            # 有足够的预测数据
            error_idx = i - (min_data_length - 1)
            error = errors[error_idx] if error_idx < len(errors) else None
            predicted = float(shipment['出货量']) - error if error is not None else None

            comparison_data.append({
                "date": shipment['日期'],
                "actual": float(shipment['出货量']),
                "predicted": round(predicted, 2) if predicted else None,
                "error": round(error, 2) if error else None
            })

    # 计算统计指标
    valid_errors = [e for e in errors if e is not None]
    if valid_errors:
        import numpy as np
        mean_error = np.mean(valid_errors)
        std_error = np.std(valid_errors)

        # 计算MAPE
        actual_values = [s['出货量'] for s in shipments[min_data_length-1:]]
        mape_values = []
        for i, (actual, error) in enumerate(zip(actual_values, valid_errors)):
            if actual != 0:
                mape_values.append(abs(error) / actual * 100)
        mape = np.mean(mape_values) if mape_values else 0
        accuracy_rate = max(0, 100 - mape)
    else:
        mean_error = 0
        std_error = 0
        mape = 0
        accuracy_rate = 100

    return ComparisonResult(
        warehouse=warehouse,
        material=material,
        data=comparison_data,
        metrics={
            "mean_error": round(mean_error, 2),
        "std:code:prediction.py:compute_accuracy
        accuracy_rate = max(0, 100 - mape)

        metrics = {
            "mean_error": round(mean_error, 2),
            "std_error": round(std_error, 2),
            "mape": round(mape, 2),
            "accuracy_rate": round(accuracy_rate, 2)
        }
    else:
        metrics = {
            "mean_error": 0,
            "std_error": 0,
            "mape": 0,
            "accuracy_rate": 0
        }

    from app.models.prediction import ComparisonData, ComparisonMetrics

    return ComparisonResult(
        warehouse=warehouse,
        material=material,
        data=[ComparisonData(**d) for d in comparison_data],
        metrics=ComparisonMetrics(**metrics)
    )


@router.post("/simulation")
async def run_simulation(
    warehouse: str,
    material: str,
    initial_stock: float = Query(..., description="初始库存"),
    safety_factor: Optional[float] = Query(None, description="安全库存系数（可选）")
):
    """
    参数调整模拟
    """
    dl = get_data_loader()
    advisor = get_order_advisor()

    # 获取物料信息
    material_info = dl.get_material(material)
    if not material_info:
        raise HTTPException(status_code=404, detail=f"物料 {material} 不存在")

    # 使用传入的参数或默认值
    safety_factor = safety_factor or material_info['safety_factor']

    # 获取出货数据
    quantities = dl.get_shipment_quantities(warehouse, material)
    if not quantities:
        raise HTTPException(status_code=404, detail=f"未找到 {warehouse} - {material} 的出货数据")

    # 分析
    analysis = advisor.get_full_prediction(
        history_data=quantities,
        initial_stock=initial_stock,
        moq=material_info['moq'],
        leadtime=material_info['leadtime'],
        safety_factor=safety_factor
    )

    return {
        "warehouse": warehouse,
        "material": material,
        "initial_stock": initial_stock,
        "safety_factor": safety_factor,
        "safety_stock": round(analysis['safety_stock'], 2),
        "predictions": [round(p, 2) for p in analysis['predictions']],
        "predicted_stocks": [round(s, 2) for s in analysis['predicted_stocks']],
        "predicted_stocks_with_order": [round(s, 2) for s in analysis['predicted_stocks_with_order']],
        "need_order": analysis['need_order'],
        "order_date": analysis['order_date'],
        "order_quantity": analysis['order_quantity']
    }
```

- [ ] **Step 2: 更新main.py注册路由**

在main.py中添加：

```python
from app.routers.prediction import router as prediction_router

# 在已有 include_router 后添加
app.include_router(prediction_router)
```

- [ ] **Step 3: 测试预测API**

```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

测试：
- GET /api/prediction/南京仓/西米
- GET /api/prediction/南京仓/西米/compare
- POST /api/simulation?warehouse=南京仓&material=西米&initial_stock=300

---

## Phase 3: 前端开发

### Task 9: 创建前端项目

**Files:**
- Create: `frontend/package.json`
- Create: `frontend/vite.config.js`
- Create: `frontend/index.html`
- Create: `frontend/src/main.js`
- Create: `frontend/src/App.vue`

- [ ] **Step 1: 初始化前端项目**

```bash
cd "D:\TRAE Projects\safty_material"
npm create vite@latest frontend -- --template vue
cd frontend
npm install
npm install vue-router@4 axios echarts element-plus
```

- [ ] **Step 2: 配置vite.config.js**

```javascript
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true
      }
    }
  }
})
```

- [ ] **Step 3: 配置main.js**

```javascript
import { createApp } from 'vue'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import App from './App.vue'
import router from './router'

const app = createApp(App)
app.use(ElementPlus)
app.use(router)
app.mount('#app')
```

- [ ] **Step 4: 创建App.vue**

```vue
<template>
  <div id="app">
    <el-container>
      <el-header>
        <h1>库存预测分析系统</h1>
        <el-button type="primary" @click="reloadData" :loading="loading">
          重新加载数据
        </el-button>
      </el-header>
      <el-main>
        <router-view />
      </el-main>
    </el-container>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { reloadMaterials } from './api'
import { ElMessage } from 'element-plus'

const loading = ref(false)

const reloadData = async () => {
  loading.value = true
  try {
    await reloadMaterials()
    ElMessage.success('数据重新加载成功')
    window.location.reload()
  } catch (error) {
    ElMessage.error('数据加载失败: ' + error.message)
  } finally {
    loading.value = false
  }
}
</script>

<style>
#app {
  font-family: Arial, sans-serif;
  min-height: 100vh;
}

.el-header {
  background-color: #409EFF;
  color: white;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 20px;
}

.el-header h1 {
  margin: 0;
  font-size: 20px;
}
</style>
```

- [ ] **Step 5: 测试前端启动**

```bash
cd frontend
npm run dev
```

访问 http://localhost:5173 确认页面可访问。

---

### Task 10: 创建API封装和路由

**Files:**
- Create: `frontend/src/api/index.js`
- Create: `frontend/src/router/index.js`

- [ ] **Step 1: 创建api/index.js**

```javascript
import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 10000
})

// 物料管理
export const getMaterials = () => api.get('/materials')
export const reloadMaterials = () => api.post('/materials/reload')
export const getWarehouses = () => api.get('/warehouses')
export const getWarehouseMaterials = () => api.get('/warehouse-materials')

// 总览
export const getOverview = (initialStock) => {
  const params = initialStock ? { initial_stock: initialStock } : {}
  return api.get('/overview', { params })
}

// 预测详情
export const getPrediction = (warehouse, material, initialStock) => {
  const params = initialStock ? { initial_stock: initialStock } : {}
  return api.get(`/prediction/${warehouse}/${material}`, { params })
}

export const getComparison = (warehouse, material) => {
  return api.get(`/prediction/${warehouse}/${material}/compare`)
}

// 模拟
export const runSimulation = (warehouse, material, initialStock, safetyFactor) => {
  const params = { warehouse, material, initial_stock: initialStock }
  if (safetyFactor) params.safety_factor = safetyFactor
  return api.post('/simulation', null, { params })
}

export default api
```

- [ ] **Step 2: 创建router/index.js**

```javascript
import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'
import Detail from '../views/Detail.vue'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home
  },
  {
    path: '/detail/:warehouse/:material',
    name: 'Detail',
    component: Detail
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
```

---

### Task 11: 创建总览页面

**Files:**
- Create: `frontend/src/views/Home.vue`
- Create: `frontend/src/components/OverviewTable.vue`

- [ ] **Step 1: 创建views/Home.vue**

```vue
<template>
  <div class="home">
    <overview-table :data="overviewData" :loading="loading" @view-detail="goToDetail" />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import OverviewTable from '../components/OverviewTable.vue'
import { getOverview } from '../api'

const router = useRouter()
const overviewData = ref([])
const loading = ref(false)

const fetchData = async () => {
  loading.value = true
  try {
    const response = await getOverview()
    overviewData.value = response.data
  } catch (error) {
    console.error('获取总览数据失败:', error)
  } finally {
    loading.value = false
  }
}

const goToDetail = (warehouse, material) => {
  router.push(`/detail/${warehouse}/${material}`)
}

onMounted(() => {
  fetchData()
})
</script>

<style scoped>
.home {
  padding: 20px;
}
</style>
```

- [ ] **Step 2: 创建components/OverviewTable.vue**

```vue
<template>
  <div class="overview-table">
    <el-table :data="data" v-loading="loading" stripe style="width: 100%">
      <el-table-column prop="warehouse" label="仓库" width="120" />
      <el-table-column prop="material" label="物料" width="120" />
      <el-table-column prop="current_stock" label="当前库存(kg)" width="120">
        <template #default="{ row }">
          {{ row.current_stock.toFixed(1) }}
        </template>
      </el-table-column>
      <el-table-column prop="safety_stock" label="安全库存(kg)" width="120">
        <template #default="{ row }">
          {{ row.safety_stock.toFixed(1) }}
        </template>
      </el-table-column>
      <el-table-column label="下单建议" width="180">
        <template #default="{ row }">
          <el-tag v-if="row.need_order" type="danger">
            建议 {{ row.order_date }} 下单
          </el-tag>
          <el-tag v-else type="success">暂无需下单</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="order_quantity" label="下单数量(kg)" width="120">
        <template #default="{ row }">
          {{ row.order_quantity || '-' }}
        </template>
      </el-table-column>
      <el-table-column prop="leadtime" label="Lead Time(天)" width="130" />
      <el-table-column prop="moq" label="MOQ(kg)" width="100" />
      <el-table-column label="操作" width="100">
        <template #default="{ row }">
          <el-button type="primary" size="small" @click="$emit('view-detail', row.warehouse, row.material)">
            详情
          </el-button>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script setup>
defineProps({
  data: {
    type: Array,
    default: () => []
  },
  loading: {
    type: Boolean,
    default: false
  }
})

defineEmits(['view-detail'])
</script>

<style scoped>
.overview-table {
  background: white;
  padding: 20px;
  border-radius: 4px;
}
</style>
```

---

### Task 12: 创建详情页面

**Files:**
- Create: `frontend/src/views/Detail.vue`
- Create: `frontend/src/components/StockChart.vue`
- Create: `frontend/src/components/ComparisonChart.vue`
- Create: `frontend/src/components/ParamAdjust.vue`

- [ ] **Step 1: 创建views/Detail.vue**

```vue
<template>
  <div class="detail" v-loading="loading">
    <div class="header">
      <el-button @click="goBack">← 返回总览</el-button>
      <h2>{{ warehouse }} - {{ material }}</h2>
    </div>

    <!-- 物料基本信息 -->
    <el-card class="info-card">
      <template #header>
        <span>物料基本信息</span>
      </template>
      <el-row :gutter="20">
        <el-col :span="6">
          <div class="info-item">
            <span class="label">MOQ:</span>
            <span class="value">{{ predictionData.moq }} kg</span>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="info-item">
            <span class="label">Lead Time:</span>
            <span class="value">{{ predictionData.leadtime }} 天</span>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="info-item">
            <span class="label">安全库存系数:</span>
            <span class="value">{{ predictionData.safety_factor }}</span>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="info-item">
            <span class="label">当前库存:</span>
            <span class="value">{{ predictionData.current_stock?.toFixed(1) }} kg</span>
          </div>
        </el-col>
      </el-row>
      <el-row :gutter="20" style="margin-top: 15px;">
        <el-col :span="6">
          <div class="info-item">
            <span class="label">安全库存:</span>
            <span class="value">{{ predictionData.safety_stock?.toFixed(1) }} kg</span>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="info-item">
            <span class="label">下单建议:</span>
            <el-tag :type="predictionData.order_suggestion?.need_order ? 'danger' : 'success'">
              {{ predictionData.order_suggestion?.need_order ? '建议下单' : '暂无需下单' }}
            </el-tag>
          </div>
        </el-col>
        <el-col :span="6" v-if="predictionData.order_suggestion?.need_order">
          <div class="info-item">
            <span class="label">建议下单日期:</span>
            <span class="value">{{ predictionData.order_suggestion?.order_date }}</span>
          </div>
        </el-col>
        <el-col :span="6" v-if="predictionData.order_suggestion?.need_order">
          <div class="info-item">
            <span class="label">下单数量:</span>
            <span class="value">{{ predictionData.order_suggestion?.order_quantity }} kg</span>
          </div>
        </el-col>
      </el-row>
    </el-card>

    <!-- 参数调整 -->
    <param-adjust
      :default-stock="predictionData.current_stock"
      :default-factor="predictionData.safety_factor"
      @simulate="handleSimulate"
    />

    <!-- 库存预测曲线 -->
    <el-card class="chart-card">
      <template #header>
        <span>库存预测曲线</span>
      </template>
      <stock-chart
        :predictions="predictionData.predictions"
        :stocks="predictionData.predicted_stocks"
        :safety-stock="predictionData.safety_stock"
        :leadtime="predictionData.leadtime"
      />
    </el-card>

    <!-- 预测vs实际对比 -->
    <el-card class="chart-card">
      <template #header>
        <span>预测 vs 实际对比</span>
      </template>
      <comparison-chart :data="comparisonData" />
    </el-card>

    <!-- 统计指标 -->
    <el-card class="metrics-card">
      <template #header>
        <span>预测准确率统计</span>
      </template>
      <el-row :gutter="20">
        <el-col :span="6">
          <div class="metric-item">
            <div class="metric-value">{{ comparisonData.metrics?.mean_error?.toFixed(2) }}</div>
            <div class="metric-label">平均误差 (kg)</div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="metric-item">
            <div class="metric-value">{{ comparisonData.metrics?.std_error?.toFixed(2) }}</div>
            <div class="metric-label">误差标准差 (kg)</div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="metric-item">
            <div class="metric-value">{{ comparisonData.metrics?.mape?.toFixed(2) }}%</div>
            <div class="metric-label">MAPE</div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="metric-item">
            <div class="metric-value">{{ comparisonData.metrics?.accuracy_rate?.toFixed(1) }}%</div>
            <div class="metric-label">准确率</div>
          </div>
        </el-col>
      </el-row>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getPrediction, getComparison, runSimulation } from '../api'
import StockChart from '../components/StockChart.vue'
import ComparisonChart from '../components/ComparisonChart.vue'
import ParamAdjust from '../components/ParamAdjust.vue'

const route = useRoute()
const router = useRouter()

const warehouse = ref(route.params.warehouse)
const material = ref(route.params.material)
const loading = ref(false)

const predictionData = ref({})
const comparisonData = ref({ metrics: {} })

const fetchData = async () => {
  loading.value = true
  try {
    const [predRes, compRes] = await Promise.all([
      getPrediction(warehouse.value, material.value),
      getComparison(warehouse.value, material.value)
    ])
    predictionData.value = predRes.data
    comparisonData.value = compRes.data
  } catch (error) {
    console.error('获取数据失败:', error)
  } finally {
    loading.value = false
  }
}

const handleSimulate = async (initialStock, safetyFactor) => {
  loading.value = true
  try {
    const response = await runSimulation(
      warehouse.value,
      material.value,
      initialStock,
      safetyFactor
    )
    predictionData.value = {
      ...predictionData.value,
      ...response.data,
      current_stock: initialStock,
      safety_factor: safetyFactor || predictionData.value.safety_factor
    }
  } catch (error) {
    console.error('模拟失败:', error)
  } finally {
    loading.value = false
  }
}

const goBack = () => {
  router.push('/')
}

onMounted(() => {
  fetchData()
})
</script>

<style scoped>
.detail {
  padding: 20px;
}

.header {
  display: flex;
  align-items: center;
  gap: 20px;
  margin-bottom: 20px;
}

.header h2 {
  margin: 0;
}

.info-card, .chart-card, .metrics-card {
  margin-bottom: 20px;
}

.info-item {
  display: flex;
  gap: 10px;
}

.info-item .label {
  color: #666;
}

.info-item .value {
  font-weight: bold;
}

.metric-item {
  text-align: center;
  padding: 15px;
}

.metric-value {
  font-size: 24px;
  font-weight: bold;
  color: #409EFF;
}

.metric-label {
  font-size: 14px;
  color: #666;
  margin-top: 5px;
}
</style>
```

- [ ] **Step 2: 创建components/StockChart.vue**

```vue
<template>
  <div ref="chartRef" style="width: 100%; height: 400px;"></div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import * as echarts from 'echarts'

const props = defineProps({
  predictions: {
    type: Array,
    default: () => []
  },
  stocks: {
    type: Array,
    default: () => []
  },
  safetyStock: {
    type: Number,
    default: 0
  },
  leadtime: {
    type: Number,
    default: 0
  }
})

const chartRef = ref(null)
let chart = null

const initChart = () => {
  if (!chartRef.value) return

  chart = echarts.init(chartRef.value)

  const days = props.predictions.map((_, i) => `第${i + 1}天`)
  const safetyLine = Array(props.predictions.length).fill(props.safetyStock)

  const option = {
    tooltip: {
      trigger: 'axis'
    },
    legend: {
      data: ['预测出货量', '预测库存', '安全库存线']
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: days
    },
    yAxis: {
      type: 'value',
      name: '数量 (kg)'
    },
    series: [
      {
        name: '预测出货量',
        type: 'bar',
        data: props.predictions,
        itemStyle: {
          color: '#409EFF'
        }
      },
      {
        name: '预测库存',
        type: 'line',
        data: props.stocks,
        itemStyle: {
          color: '#67C23A'
        },
        lineStyle: {
          width: 3
        }
      },
      {
        name: '安全库存线',
        type: 'line',
        data: safetyLine,
        itemStyle: {
          color: '#F56C6C'
        },
        lineStyle: {
          type: 'dashed',
          width: 2
        },
        symbol: 'none'
      }
    ]
  }

  chart.setOption(option)
}

watch(() => [props.predictions, props.stocks, props.safetyStock], () => {
  if (chart) {
    initChart()
  }
}, { deep: true })

onMounted(() => {
  initChart()
})
</script>
```

- [ ] **Step 3: 创建components/ComparisonChart.vue**

```vue
<template>
  <div ref="chartRef" style="width: 100%; height: 400px;"></div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import * as echarts from 'echarts'

const props = defineProps({
  data: {
    type: Object,
    default: () => ({ data: [], metrics: {} })
  }
})

const chartRef = ref(null)
let chart = null

const initChart = () => {
  if (!chartRef.value) return

  chart = echarts.init(chartRef.value)

  const validData = (props.data.data || []).filter(d => d.predicted !== null)
  const dates = validData.map(d => d.date)
  const actuals = validData.map(d => d.actual)
  const predicteds = validData.map(d => d.predicted)

  const option = {
    tooltip: {
      trigger: 'axis'
    },
    legend: {
      data: ['实际出货', '预测出货']
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: dates,
      axisLabel: {
        rotate: 45
      }
    },
    yAxis: {
      type: 'value',
      name: '出货量 (kg)'
    },
    series: [
      {
        name: '实际出货',
        type: 'line',
        data: actuals,
        itemStyle: {
          color: '#409EFF'
        }
      },
      {
        name: '预测出货',
        type: 'line',
        data: predicteds,
        itemStyle: {
          color: '#E6A23C'
        },
        lineStyle: {
          type: 'dashed'
        }
      }
    ]
  }

  chart.setOption(option)
}

watch(() => props.data, () => {
  if (chart) {
    initChart()
  }
}, { deep: true })

onMounted(() => {
  initChart()
})
</script>
```

- [ ] **Step 4: 创建components/ParamAdjust.vue**

```vue
<template>
  <el-card class="param-adjust">
    <template #header>
      <span>参数调整（模拟计算）</span>
    </template>
    <el-form :inline="true" :model="form">
      <el-form-item label="初始库存 (kg)">
        <el-input-number v-model="form.initialStock" :min="0" :step="10" />
      </el-form-item>
      <el-form-item label="安全库存系数">
        <el-input-number v-model="form.safetyFactor" :min="0.1" :max="5" :step="0.1" :precision="2" />
      </el-form-item>
      <el-form-item>
        <el-button type="primary" @click="handleSimulate">模拟计算</el-button>
      </el-form-item>
    </el-form>
  </el-card>
</template>

<script setup>
import { ref, watch } from 'vue'

const props = defineProps({
  defaultStock: {
    type: Number,
    default: 200
  },
  defaultFactor: {
    type: Number,
    default: 1.65
  }
})

const emit = defineEmits(['simulate'])

const form = ref({
  initialStock: props.defaultStock || 200,
  safetyFactor: props.defaultFactor || 1.65
})

watch(() => [props.defaultStock, props.defaultFactor], () => {
  form.value.initialStock = props.defaultStock || 200
  form.value.safetyFactor = props.defaultFactor || 1.65
})

const handleSimulate = () => {
  emit('simulate', form.value.initialStock, form.value.safetyFactor)
}
</script>

<style scoped>
.param-adjust {
  margin-bottom: 20px;
}
</style>
```

---

## Phase 4: 联调测试

### Task 13: 创建配置文件和启动脚本

**Files:**
- Create: `data/config/settings.json`
- Create: `start.bat`

- [ ] **Step 1: 创建data/config/settings.json**

```json
{
  "default_initial_stock": 200,
  "warehouse_material_stocks": {
    "南京仓_西米": 200,
    "南京仓_麻薯": 350,
    "北京仓_西米": 180,
    "北京仓_麻薯": 300
  }
}
```

- [ ] **Step 2: 创建启动脚本start.bat**

```batch
@echo off
echo Starting Inventory Prediction System...
echo.
echo Starting Backend...
start cmd /k "cd backend && uvicorn app.main:app --reload --port 8000"
echo.
echo Starting Frontend...
start cmd /k "cd frontend && npm run dev"
echo.
echo Backend API: http://localhost:8000/docs
echo Frontend: http://localhost:5173
echo.
pause
```

- [ ] **Step 3: 整体测试**

1. 启动后端和前端
2. 访问 http://localhost:5173
3. 测试总览表数据加载
4. 点击详情测试详情页
5. 测试参数调整模拟功能
6. 测试重新加载数据功能

---

## Checklist

### 功能验收

- [ ] 后端API正常运行，/docs可访问
- [ ] 前端页面正常显示
- [ ] 总览表正确显示所有仓库物料的下单建议
- [ ] 详情页正确显示预测曲线
- [ ] 详情页正确显示预测vs实际对比图
- [ ] 参数调整模拟功能正常
- [ ] 重新加载数据功能正常

### 代码质量

- [ ] 后端代码结构清晰，分层合理
- [ ] 前端组件化，可复用
- [ ] 预测算法采用策略模式，可扩展
- [ ] 数据与代码分离
