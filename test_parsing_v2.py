#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import subprocess

def test_parsing():
    # 获取winget列表输出
    result = subprocess.run(
        ["winget", "list", "--source", "winget"],
        capture_output=True, 
        text=True, 
        encoding='utf-8',
        errors='ignore',
        timeout=30
    )
    
    if result.returncode == 0:
        output = result.stdout.strip() if result.stdout else ""
        if output:
            lines = output.split('\n')
            if len(lines) > 2:
                # 分析标题行来确定列位置
                header_line = lines[0] if len(lines) > 0 else ""
                
                # 找到各列标题的起始位置
                name_pos = header_line.find("Name")
                id_pos = header_line.find("Id")
                version_pos = header_line.find("Version")
                available_pos = header_line.find("Available")
                
                print(f"Header line: {repr(header_line)}")
                print(f"Name position: {name_pos}")
                print(f"Id position: {id_pos}")
                print(f"Version position: {version_pos}")
                print(f"Available position: {available_pos}")
                
                # 测试解析几行数据
                print("\nParsing sample data lines:")
                count = 0
                for line in lines[2:]:  # 从第三行开始解析
                    line = line.rstrip() if line else ""
                    if line and not line.startswith('-') and not line.startswith('Name'):
                        print(f"\nLine: {repr(line)}")
                        
                        # Name列
                        name = ""
                        if name_pos >= 0:
                            end_pos = id_pos if id_pos > name_pos else len(line)
                            if end_pos > name_pos:
                                name = line[name_pos:end_pos].strip()
                        print(f"  Name: {repr(name)}")
                        
                        # Id列
                        package_id = ""
                        if id_pos >= 0:
                            start_pos = id_pos
                            end_pos = version_pos if version_pos > id_pos else len(line)
                            if end_pos > start_pos:
                                package_id = line[start_pos:end_pos].strip()
                        print(f"  Id: {repr(package_id)}")
                        
                        # Version列
                        version = ""
                        if version_pos >= 0:
                            start_pos = version_pos
                            end_pos = available_pos if available_pos > version_pos else len(line)
                            if end_pos > start_pos:
                                version = line[start_pos:end_pos].strip()
                        print(f"  Version: {repr(version)}")
                        
                        # Available列
                        available = ""
                        if available_pos >= 0:
                            start_pos = available_pos
                            if start_pos < len(line):
                                available = line[start_pos:].strip()
                        print(f"  Available: {repr(available)}")
                        
                        count += 1
                        if count >= 5:  # 只显示前5个包
                            break

if __name__ == "__main__":
    test_parsing()