#!/bin/bash

# 检查并创建虚拟环境
if [ ! -d "venv" ]; then
    echo "创建虚拟环境..."
    python3 -m venv venv
fi

# 激活虚拟环境
source venv/bin/activate

# 安装依赖
echo "安装依赖..."
pip install -r requirements.txt

# 更新子模块
echo "更新子模块..."
git submodule update --init --recursive

# 运行规则生成脚本
echo "运行规则生成脚本..."
python3 generate_rules.py

# 检查输出
echo "检查输出文件..."
ls -l geosite/ geoip/

# 显示示例规则内容
echo "显示示例规则内容..."
echo "=== geosite/cn.list ==="
head -n 5 geosite/cn.list
echo "=== geoip/cn.list ==="
head -n 5 geoip/cn.list 