#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import subprocess
import json
import tempfile
import os

def test_export():
    # 创建临时文件来保存导出的JSON
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as temp_file:
        temp_filename = temp_file.name
    
    try:
        # 使用winget export命令导出已安装的软件包信息
        cmd = ["winget", "export", "--include-versions", "-o", temp_filename, "--source", "winget"]
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
        print(f"Stdout: {result.stdout}")
        print(f"Stderr: {result.stderr}")
        
        if result.returncode == 0:
            # 读取导出的JSON文件
            if os.path.exists(temp_filename):
                with open(temp_filename, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                print("\nJSON data structure:")
                print(f"Keys: {list(data.keys())}")
                
                if 'Sources' in data:
                    print(f"Number of sources: {len(data['Sources'])}")
                    for i, source in enumerate(data['Sources']):
                        print(f"Source {i}: {source.get('SourceDetails', {})}")
                        if 'Packages' in source:
                            print(f"  Number of packages: {len(source['Packages'])}")
                            # 显示前几个包作为示例
                            for j, package in enumerate(source['Packages'][:3]):
                                print(f"    Package {j}: {package}")
                else:
                    print("No 'Sources' key found in JSON")
            else:
                print("Export file was not created")
        else:
            print(f"Export failed with return code: {result.returncode}")
            
    finally:
        # 清理临时文件
        if os.path.exists(temp_filename):
            os.unlink(temp_filename)

if __name__ == "__main__":
    test_export()