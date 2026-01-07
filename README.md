# 投资跟踪系统 (Investment Tracking System)

一个用于跟踪和展示投资组合、股票、ETF指标的Web系统。

## 功能特性

- 📊 高股息股票追踪
- 🏢 券商龙头股票监控
- 📈 ETF布局方案展示
- 💼 投资组合配置管理
- 📉 实时指标展示

## 技术栈

- 后端: Python Flask
- 前端: HTML + Tailwind CSS + Vue.js
- 数据: JSON文件

## 快速开始

1. 安装依赖:
```bash
pip install -r requirements.txt
```

2. 运行服务器:
```bash
python backend/app.py
```

3. 访问系统:
打开浏览器访问 http://localhost:5000

## 项目结构

```
stockmoniter/
├── backend/          # Flask后端
│   ├── app.py       # 主应用
│   └── routes.py    # API路由
├── frontend/        # 前端文件
│   ├── static/      # 静态资源
│   └── templates/   # HTML模板
└── data/            # 数据文件
    └── stocks.json  # 股票和ETF数据
```
