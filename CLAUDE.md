# 库存预测分析系统

## 项目简介

库存预测分析系统是一个面向物控人员的Web应用，用于管理多仓库多物料的库存预测和下单决策。

**核心功能：**
- 基于历史出货数据预测未来LeadTime期间的出货量
- 计算安全库存，判断是否需要下单
- 提供可视化的预测分析和对比功能

## 技术栈

| 组件 | 技术 |
|------|------|
| 后端 | FastAPI + Python |
| 前端 | Vue.js 3 + Element Plus + ECharts |
| 数据存储 | CSV文件 |

## 项目结构

```
safty_material/
├── backend/                 # 后端服务 (FastAPI)
│   ├── app/
│   │   ├── main.py         # 入口文件
│   │   ├── config.py       # 配置管理
│   │   ├── routers/        # API路由
│   │   ├── services/       # 业务逻辑
│   │   ├── models/         # 数据模型
│   │   └── utils/          # 工具函数
│   └── requirements.txt
│
├── frontend/                # 前端服务 (Vue.js)
│   ├── src/
│   │   ├── api/            # API调用
│   │   ├── components/     # 组件
│   │   ├── views/          # 页面
│   │   └── router/         # 路由
│   └── package.json
│
├── data/                    # 数据目录
│   ├── 仓库出货量.csv
│   └── 物料信息表.csv
│
└── docs/                    # 文档目录
    └── superpowers/specs/   # 设计文档
```

## 开发指南

### 后端启动

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### 前端启动

```bash
cd frontend
npm install
npm run dev
```

### API文档

启动后端后访问：http://localhost:8000/docs

## 核心算法

### 预测算法

当前使用**移动平均法**，预测窗口为LeadTime天数。

```python
# 预测公式
预测值 = AVERAGE(前N天出货量)
```

### 安全库存计算

```python
# 安全库存公式
安全库存 = STDEV(预测误差) × 安全库存系数 × LeadTime
```

### 下单判断逻辑

1. 预测未来LeadTime天的库存变化
2. 若某天库存低于安全库存，建议下单
3. 每次下单数量为MOQ

## 数据格式

### 物料信息表 (物料信息表.csv)

| 字段 | 说明 |
|------|------|
| 物料 | 物料名称 |
| MOQ | 最小订货量 (kg) |
| leadtime | 前置时间 (天) |
| 安全库存系数 | 安全系数 (如1.65对应95%置信度) |

### 仓库出货量 (仓库出货量.csv)

| 字段 | 说明 |
|------|------|
| 仓库 | 仓库名称 |
| 物料 | 物料名称 |
| 日期 | 出货日期 |
| 出货量 | 当日出货量 (kg) |

## 功能规划

### 一期功能
- [x] 总览表（仓库/物料/建议下单日期/下单数量）
- [x] 单物料详情页
- [x] 预测vs实际对比分析
- [x] 参数调整功能

### 二期功能
- [ ] 仪表盘总览
- [ ] API数据对接
- [ ] 算法优化扩展

## 注意事项

1. **数据代码分离**：数据文件存放在 `data/` 目录，与代码完全分离
2. **预测算法可替换**：采用策略模式设计，方便后期替换算法
3. **参数扩展性**：数据结构已预留仓库-物料维度的参数扩展能力
