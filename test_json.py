#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import subprocess
import json

def test_json_parsing():
    # 使用winget list命令获取已安装的软件包信息（JSON格式）
    cmd = ["winget", "list", "--source", "winget", "--format", "json"]
    print(f"Executing command: {' '.join(cmd)}")
    
    result = subprocess.run(
        cmd,
        capture_output=True, 
        text=True, 
        encoding='utf-8',
        errors='ignore',
        timeout=30
    )
    
    print(f"Return code: {result.returncode}")
    print(f"Stdout length: {len(result.stdout)}")
    print(f"Stderr: {result.stderr}")
    
    if result.returncode == 0:
        # 解析JSON输出
        output = result.stdout.strip() if result.stdout else ""
        if output:
            try:
                data = json.loads(output)
                print("\nJSON data structure:")
                print(f"Keys: {list(data.keys())}")
                
                if 'Packages' in data:
                    print(f"Number of packages: {len(data['Packages'])}")
                    # 显示前几个包作为示例
                    for i, package in enumerate(data['Packages'][:3]):
                        print(f"Package {i}:")
                        print(f"  Name: {package.get('Name', 'Unknown')}")
                        print(f"  Id: {package.get('Id', 'Unknown')}")
                        print(f"  Version: {package.get('Version', 'Unknown')}")
                        print(f"  AvailableVersion: {package.get('AvailableVersion', 'Unknown')}")
                else:
                    print("No 'Packages' key found in JSON")
            except json.JSONDecodeError as e:
                print(f"JSON解析错误: {str(e)}")
                print("Output preview:")
                print(output[:500])
        else:
            print("No output received")
    else:
        print(f"Command failed with return code: {result.returncode}")

if __name__ == "__main__":
    test_json_parsing()