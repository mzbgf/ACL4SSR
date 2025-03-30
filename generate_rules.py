#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import yaml
import glob
import shutil
import hashlib
import json
from datetime import datetime
from typing import Dict, List, Optional

def ensure_dir(directory):
    """确保目录存在，如果不存在则创建"""
    if not os.path.exists(directory):
        os.makedirs(directory)

def clean_output_dirs():
    """清理输出目录"""
    print("清理输出目录...")
    for dir_name in ['geosite', 'geoip']:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"已删除 {dir_name} 目录")
        ensure_dir(dir_name)
        print(f"已创建 {dir_name} 目录")

def calculate_file_hash(file_path: str) -> str:
    """计算文件的 SHA-256 哈希值"""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def load_hash_file() -> Dict[str, str]:
    """加载规则文件的哈希值记录"""
    hash_file = "rule_hashes.json"
    if os.path.exists(hash_file):
        with open(hash_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_hash_file(hashes: Dict[str, str]):
    """保存规则文件的哈希值记录"""
    with open("rule_hashes.json", 'w', encoding='utf-8') as f:
        json.dump(hashes, f, indent=2)

def check_updates() -> Dict[str, List[str]]:
    """检查规则更新情况"""
    updates = {
        'modified': [],
        'added': [],
        'removed': []
    }
    
    # 加载之前的哈希值记录
    old_hashes = load_hash_file()
    new_hashes = {}
    
    # 检查 geosite 规则
    for yaml_file in glob.glob("meta-rules-dat/geo/geosite/*.yaml"):
        file_hash = calculate_file_hash(yaml_file)
        new_hashes[yaml_file] = file_hash
        
        if yaml_file not in old_hashes:
            updates['added'].append(yaml_file)
        elif old_hashes[yaml_file] != file_hash:
            updates['modified'].append(yaml_file)
    
    # 检查 geoip 规则
    for yaml_file in glob.glob("meta-rules-dat/geo/geoip/*.yaml"):
        file_hash = calculate_file_hash(yaml_file)
        new_hashes[yaml_file] = file_hash
        
        if yaml_file not in old_hashes:
            updates['added'].append(yaml_file)
        elif old_hashes[yaml_file] != file_hash:
            updates['modified'].append(yaml_file)
    
    # 检查删除的文件
    for old_file in old_hashes:
        if old_file not in new_hashes:
            updates['removed'].append(old_file)
    
    # 保存新的哈希值记录
    save_hash_file(new_hashes)
    
    return updates

def generate_update_report(updates: Dict[str, List[str]]):
    """生成更新报告"""
    report = []
    report.append(f"规则更新报告 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append("=" * 50)
    
    if updates['modified']:
        report.append("\n修改的文件:")
        for file in updates['modified']:
            report.append(f"- {file}")
    
    if updates['added']:
        report.append("\n新增的文件:")
        for file in updates['added']:
            report.append(f"- {file}")
    
    if updates['removed']:
        report.append("\n删除的文件:")
        for file in updates['removed']:
            report.append(f"- {file}")
    
    if not any(updates.values()):
        report.append("\n没有发现更新")
    
    # 保存报告
    with open("update_report.txt", 'w', encoding='utf-8') as f:
        f.write('\n'.join(report))
    
    # 打印报告
    print('\n'.join(report))

def process_yaml_files():
    """处理 YAML 格式的规则文件"""
    # 处理 geosite 规则
    geosite_base = "meta-rules-dat/geo/geosite"
    geosite_output = "geosite"
    
    print(f"处理 geosite 规则...")
    for yaml_file in glob.glob(f"{geosite_base}/*.yaml"):
        try:
            with open(yaml_file, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
                if not data or 'payload' not in data:
                    print(f"警告：{yaml_file} 文件格式不正确或为空")
                    continue
                    
                # 生成输出文件名
                base_name = os.path.splitext(os.path.basename(yaml_file))[0]
                output_file = f"{geosite_output}/{base_name}.list"
                
                # 写入规则
                with open(output_file, 'w', encoding='utf-8') as out:
                    for item in data['payload']:
                        if isinstance(item, str):
                            # 处理带属性的域名，例如 "example.com:cn"
                            domain = item.split(':')[0] if ':' in item else item
                            out.write(f"DOMAIN-SUFFIX,{domain}\n")
                print(f"已生成 {output_file}")
        except Exception as e:
            print(f"处理 {yaml_file} 时出错: {e}")
    
    # 处理 geoip 规则
    geoip_base = "meta-rules-dat/geo/geoip"
    geoip_output = "geoip"
    
    print(f"处理 geoip 规则...")
    for yaml_file in glob.glob(f"{geoip_base}/*.yaml"):
        try:
            with open(yaml_file, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
                if not data or 'payload' not in data:
                    print(f"警告：{yaml_file} 文件格式不正确或为空")
                    continue
                    
                # 生成输出文件名
                base_name = os.path.splitext(os.path.basename(yaml_file))[0]
                output_file = f"{geoip_output}/{base_name}.list"
                
                # 写入规则
                with open(output_file, 'w', encoding='utf-8') as out:
                    for item in data['payload']:
                        if isinstance(item, str):
                            out.write(f"IP-CIDR,{item}\n")
                print(f"已生成 {output_file}")
        except Exception as e:
            print(f"处理 {yaml_file} 时出错: {e}")

def main():
    """主函数"""
    print(f"开始生成规则 - {datetime.now()}")
    
    if not os.path.exists("meta-rules-dat"):
        print("错误：meta-rules-dat 子模块不存在")
        print("请运行: git submodule update --init --recursive")
        return
    
    # 检查更新
    print("\n检查规则更新...")
    updates = check_updates()
    generate_update_report(updates)
    
    # 清理输出目录
    clean_output_dirs()
    
    # 处理规则文件
    process_yaml_files()
    
    print(f"\n规则生成完成 - {datetime.now()}")

if __name__ == "__main__":
    main() 