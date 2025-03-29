#!/usr/bin/env python3
import os
import yaml
from datetime import datetime
import glob

def ensure_dir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

def process_yaml_files():
    """处理 meta-rules-dat 仓库中的 YAML 文件"""
    # 处理 geosite 规则
    geosite_path = "meta-rules-dat/geo/geosite"
    if os.path.exists(geosite_path):
        ensure_dir("geosite")
        for yaml_file in glob.glob(os.path.join(geosite_path, "*.yaml")):
            category = os.path.splitext(os.path.basename(yaml_file))[0]
            print(f"处理 geosite/{category} 规则...")
            try:
                with open(yaml_file, "r") as f:
                    data = yaml.safe_load(f)
                with open(f"geosite/{category}.list", "w") as f:
                    for domain in data.get("payload", []):
                        if ":" in domain:  # 处理带属性的域名
                            domain = domain.split(":")[0]
                        f.write(f"DOMAIN-SUFFIX,{domain}\n")
            except Exception as e:
                print(f"处理 geosite/{category} 规则时出错: {e}")
    
    # 处理 geoip 规则
    geoip_path = "meta-rules-dat/geo/geoip"
    if os.path.exists(geoip_path):
        ensure_dir("geoip")
        for yaml_file in glob.glob(os.path.join(geoip_path, "*.yaml")):
            category = os.path.splitext(os.path.basename(yaml_file))[0]
            print(f"处理 geoip/{category} 规则...")
            try:
                with open(yaml_file, "r") as f:
                    data = yaml.safe_load(f)
                with open(f"geoip/{category}.list", "w") as f:
                    for ip in data.get("payload", []):
                        f.write(f"IP-CIDR,{ip}\n")
            except Exception as e:
                print(f"处理 geoip/{category} 规则时出错: {e}")

def main():
    print(f"开始生成规则 - {datetime.now()}")
    
    if not os.path.exists("meta-rules-dat"):
        print("错误: meta-rules-dat 子模块未初始化")
        print("请运行: git submodule update --init --recursive")
        return
    
    print("处理规则数据...")
    process_yaml_files()
    
    print(f"规则生成完成 - {datetime.now()}")

if __name__ == "__main__":
    main() 