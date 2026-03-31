# 库存预测分析系统

基于历史出货数据的库存预测和下单建议Web应用。

## 快速启动

双击运行 `start.bat` 即可同时启动前后端服务。

或手动启动：

### 后端
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### 前端
```bash
cd frontend
npm install
npm run dev
```

## 访问地址

| 服务 | 地址 |
|------|------|
| 前端页面 | http://localhost:5173 |
| 后端API | http://localhost:8000 |
| API文档 | http://localhost:8000/docs |

## 功能模块

- **总览表**: 展示所有仓库物料的下单建议
- **详情页**: 单物料的预测详情和对比分析
- **参数调整**: 支持调整初始库存和安全库存系数进行模拟

## 项目结构

```
safty_material/
├── backend/          # FastAPI后端
├── frontend/         # Vue3前端
├── data/             # 数据文件（CSV）
├── docs/             # 设计文档
└── start.bat         # 启动脚本
```
