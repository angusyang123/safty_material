# 库存预测分析系统 - 设计文档

> 创建日期: 2026-03-30
> 版本: v1.0
> 状态: 待审核

## 一、项目概述

### 1.1 项目背景

物控人员需要管理多个仓库的多种物料，基于历史出货数据预测未来需求，在合适的时间向厂商下单，避免缺货同时提高库存周转率。

### 1.2 核心目标

- 基于历史出货数据预测未来LeadTime期间的出货量
- 计算安全库存，判断是否需要下单
- 提供可视化的预测分析和对比功能

### 1.3 目标用户

物控人员：负责管理仓库物料货量，执行下单决策

---

## 二、功能范围

### 2.1 一期功能

| 功能模块 | 说明 |
|----------|------|
| 总览表 | 展示所有仓库-物料的建议下单日期和数量 |
| 单物料详情页 | 某个仓库-物料的详细预测分析 |
| 预测vs实际对比 | 历史预测准确率分析 |
| 参数调整 | 支持调整初始库存、安全库存系数等参数进行模拟 |
| 数据重新加载 | CSV文件修改后可重新加载 |

### 2.2 二期功能（预留）

| 功能模块 | 说明 |
|----------|------|
| 仪表盘总览 | 多仓库多物料的可视化仪表盘 |
| API数据对接 | 自动从WMS/ERP系统同步出货数据 |
| 算法优化 | 提供多种预测算法选择 |

---

## 三、技术架构

### 3.1 技术选型

| 组件 | 技术 | 理由 |
|------|------|------|
| 后端框架 | FastAPI | 现代、异步、自动API文档、类型提示 |
| 前端框架 | Vue.js 3 | 组件化、生态丰富、模块化友好 |
| 数据存储 | CSV文件 | 按用户要求，预留扩展能力 |
| 图表展示 | ECharts | 功能强大、中文文档完善 |
| UI组件库 | Element Plus | Vue3生态主流组件库 |

### 3.2 架构模式

**前后端完全分离**

- 前后端独立部署，各自运行
- 通过RESTful API通信
- 职责清晰分离，便于维护扩展

---

## 四、项目结构

```
safty_material/
├── backend/                          # 后端服务
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                   # FastAPI 入口
│   │   ├── config.py                 # 配置管理
│   │   ├── routers/                  # API路由层
│   │   │   ├── __init__.py
│   │   │   ├── material.py           # 物料信息接口
│   │   │   ├── warehouse.py          # 仓库出货数据接口
│   │   │   ├── prediction.py         # 预测分析接口
│   │   │   └── overview.py           # 总览表接口
│   │   ├── services/                 # 业务逻辑层
│   │   │   ├── __init__.py
│   │   │   ├── data_loader.py        # 数据加载服务
│   │   │   ├── predictor.py          # 预测算法（策略模式）
│   │   │   ├── inventory_calculator.py  # 库存计算服务
│   │   │   └── order_advisor.py      # 下单建议服务
│   │   ├── models/                   # 数据模型层
│   │   │   ├── __init__.py
│   │   │   ├── material.py           # 物料模型
│   │   │   ├── warehouse.py          # 仓库模型
│   │   │   └── prediction.py         # 预测结果模型
│   │   └── utils/                    # 工具函数
│   │       └── __init__.py
│   └── requirements.txt
│
├── frontend/                         # 前端服务
│   ├── public/
│   ├── src/
│   │   ├── api/                      # API调用层
│   │   ├── components/               # 组件
│   │   │   ├── OverviewTable.vue     # 总览表
│   │   │   ├── MaterialDetail.vue    # 物料详情页
│   │   │   ├── PredictionChart.vue   # 预测图表
│   │   │   ├── ComparisonChart.vue   # 对比分析图表
│   │   │   └── ParamAdjust.vue       # 参数调整
│   │   ├── views/                    # 页面视图
│   │   ├── router/                   # 路由配置
│   │   └── App.vue
│   └── package.json
│
├── data/                             # 数据目录（与代码分离）
│   ├── 仓库出货量.csv
│   ├── 物料信息表.csv
│   └── config/                       # 参数配置文件
│
├── docs/                             # 文档目录
│   └── superpowers/specs/            # 设计文档
│
└── CLAUDE.md                         # 项目说明文档
```

---

## 五、核心模块设计

### 5.1 预测模块（策略模式）

```python
# 预测算法抽象接口
class PredictionStrategy(ABC):
    @abstractmethod
    def predict(self, history_data: list, window: int) -> list:
        """预测未来window天的出货量"""
        pass

# 移动平均算法（一期实现）
class MovingAverageStrategy(PredictionStrategy):
    def predict(self, history_data: list, window: int) -> list:
        # 实现移动平均预测逻辑
        pass

# 预测器（可注入不同策略）
class Predictor:
    def __init__(self, strategy: PredictionStrategy):
        self._strategy = strategy

    def set_strategy(self, strategy: PredictionStrategy):
        self._strategy = strategy  # 方便后期替换算法

    def predict(self, history_data: list, window: int) -> list:
        return self._strategy.predict(history_data, window)
```

### 5.2 库存计算模块

**核心计算流程：**

1. **预测出货**：基于历史数据预测未来leadtime天的出货量
2. **计算误差**：实际出货 - 预测出货
3. **安全库存**：`STDEV(误差) × 安全库存系数 × leadtime`
4. **库存模拟**：逐日模拟库存变化 `当日库存 = 上日库存 - 出库 + 到货`
5. **下单判断**：若leadtime天后库存低于安全库存，建议下单MOQ

### 5.3 数据加载模块

```python
class DataLoader:
    def __init__(self, data_dir: str):
        self._data_dir = data_dir
        self._materials = None
        self._shipments = None

    def reload(self):
        """重新加载CSV数据"""
        self._materials = pd.read_csv(f"{self._data_dir}/物料信息表.csv")
        self._shipments = pd.read_csv(f"{self._data_dir}/仓库出货量.csv")

    def get_materials(self) -> list:
        return self._materials.to_dict('records')

    def get_shipments(self, warehouse: str, material: str) -> list:
        # 返回指定仓库物料的出货历史
        pass
```

---

## 六、API接口设计

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/materials` | GET | 获取物料列表 |
| `/api/materials/reload` | POST | 重新加载物料信息 |
| `/api/warehouses` | GET | 获取仓库列表 |
| `/api/overview` | GET | 获取总览表（建议下单列表） |
| `/api/prediction/{warehouse}/{material}` | GET | 获取单物料预测详情 |
| `/api/prediction/compare/{warehouse}/{material}` | GET | 预测vs实际对比分析 |
| `/api/simulation` | POST | 参数调整模拟 |

---

## 七、前端页面设计

### 7.1 页面路由

| 路由 | 页面 | 说明 |
|------|------|------|
| `/` | 总览页 | 展示所有物料的下单建议表 |
| `/detail/:warehouse/:material` | 详情页 | 单物料的预测详情和对比分析 |

### 7.2 总览页功能

- 表格展示所有仓库-物料组合
- 字段：仓库、物料、建议下单日期、下单数量、当前库存、操作
- 状态标识：需要下单（高亮）、暂无需下单
- 点击"详情"跳转到单物料详情页
- "重新加载"按钮刷新数据

### 7.3 详情页功能

- 物料基本信息展示（MOQ、LeadTime、安全库存系数、当前库存、安全库存）
- 参数调整面板（初始库存、安全库存系数）
- 库存预测曲线图（库存量、安全库存线、预测区间）
- 预测vs实际对比图
- 准确率统计指标

---

## 八、数据结构

### 8.1 物料信息模型

```python
class MaterialInfo:
    material: str          # 物料名称
    moq: int              # 最小订货量
    leadtime: int         # 前置时间（天）
    safety_factor: float  # 安全库存系数
```

### 8.2 出货记录模型

```python
class ShipmentRecord:
    warehouse: str    # 仓库名称
    material: str     # 物料名称
    date: str         # 日期
    quantity: int     # 出货量
```

### 8.3 预测结果模型

```python
class PredictionResult:
    warehouse: str              # 仓库
    material: str               # 物料
    predictions: list[float]    # 未来N天预测值
    safety_stock: float         # 安全库存
    current_stock: float        # 当前库存
    order_suggestion: dict      # 下单建议
    # order_suggestion = {
    #     "need_order": True,
    #     "order_date": "2024-03-05",
    #     "order_quantity": 80
    # }
```

### 8.4 对比分析结果模型

```python
class ComparisonResult:
    dates: list[str]           # 日期列表
    actual: list[float]        # 实际出货
    predicted: list[float]     # 预测出货
    errors: list[float]        # 误差
    metrics: dict              # 统计指标
    # metrics = {
    #     "mean_error": 12.5,
    #     "std_error": 8.3,
    #     "accuracy_rate": 87.2
    # }
```

---

## 九、依赖配置

### 9.1 后端依赖 (requirements.txt)

```
fastapi==0.109.0
uvicorn==0.27.0
pandas==2.1.4
numpy==1.26.3
pydantic==2.5.3
python-multipart==0.0.6
```

### 9.2 前端依赖 (package.json)

```json
{
  "dependencies": {
    "vue": "^3.4.0",
    "vue-router": "^4.2.0",
    "axios": "^1.6.0",
    "echarts": "^5.4.0",
    "element-plus": "^2.5.0"
  }
}
```

---

## 十、开发计划

### 阶段1: 基础框架搭建
- 后端项目结构创建
- 前端项目结构创建
- 数据加载模块实现
- 基础API框架搭建

### 阶段2: 核心算法实现
- 移动平均预测算法
- 安全库存计算
- 库存模拟计算
- 下单建议逻辑

### 阶段3: API接口开发
- 物料信息接口
- 总览表接口
- 预测详情接口
- 参数模拟接口

### 阶段4: 前端页面开发
- 总览页面
- 详情页面
- ECharts图表组件
- 参数调整功能

### 阶段5: 联调测试
- 前后端联调
- 数据验证
- 问题修复

---

## 十一、扩展性设计

| 扩展点 | 说明 |
|--------|------|
| 预测算法 | 策略模式，新增算法只需实现`PredictionStrategy`接口 |
| 数据源 | `DataLoader`可扩展为从API获取数据 |
| 仓库-物料参数 | 数据结构已预留，可支持不同仓库的leadtime差异 |
| 前端组件 | 组件化设计，可复用扩展 |
