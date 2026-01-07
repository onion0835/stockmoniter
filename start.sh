#!/bin/bash

echo "================================================"
echo "  投资跟踪系统 - Investment Tracking System"
echo "================================================"
echo ""

# 检查Python是否安装
if ! command -v python3 &> /dev/null; then
    echo "错误: 未找到Python3，请先安装Python 3.7+"
    exit 1
fi

echo "✓ Python已安装"

# 检查依赖
echo "正在检查依赖..."
pip install -r requirements.txt -q

if [ $? -eq 0 ]; then
    echo "✓ 依赖安装成功"
else
    echo "错误: 依赖安装失败"
    exit 1
fi

echo ""
echo "正在启动服务器..."
echo "服务器地址: http://localhost:5000"
echo "按 Ctrl+C 停止服务器"
echo ""

# 启动Flask服务器
python backend/app.py
