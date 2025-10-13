#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import subprocess

def debug_winget_output():
    print("Debugging winget list output...")
    
    # 获取winget列表输出
    result = subprocess.run(
        ["winget", "list", "--source", "winget"],
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
        output = result.stdout.strip() if result.stdout else ""
        if output:
            lines = output.split('\n')
            print(f"Total lines: {len(lines)}")
            
            # 查找实际的标题行（包含Name的行）
            header_line_index = -1
            header_line = ""
            for i, line in enumerate(lines):
                if "Name" in line and "Id" in line and "Version" in line:
                    header_line_index = i
                    header_line = line
                    break
            
            if header_line_index >= 0:
                print(f"\nHeader line found at index {header_line_index}: {repr(header_line)}")
                
                # 查找各列的位置
                name_pos = header_line.find("Name")
                id_pos = header_line.find("Id")
                version_pos = header_line.find("Version")
                available_pos = header_line.find("Available")
                
                print(f"Name position: {name_pos}")
                print(f"Id position: {id_pos}")
                print(f"Version position: {version_pos}")
                print(f"Available position: {available_pos}")
                
                # 尝试解析几行数据
                print("\nTrying to parse data lines:")
                parsed_count = 0
                # 从标题行之后开始解析
                for i in range(header_line_index + 2, min(header_line_index + 7, len(lines))):
                    line = lines[i].rstrip()
                    if line and not line.startswith('-') and "Name" not in line:
                        print(f"\nLine {i}: {repr(line)}")
                        
                        # 尝试提取数据
                        if len(line) > name_pos and name_pos >= 0:
                            # Name
                            end_pos = id_pos if id_pos > name_pos and id_pos < len(line) else len(line)
                            name = line[name_pos:end_pos].strip()
                            print(f"  Name: {repr(name)}")
                            
                            # Id
                            if id_pos >= 0 and id_pos < len(line):
                                start_pos = id_pos
                                end_pos = version_pos if version_pos > id_pos and version_pos < len(line) else len(line)
                                if end_pos > start_pos:
                                    package_id = line[start_pos:end_pos].strip()
                                    print(f"  Id: {repr(package_id)}")
                                    
                                    # Version
                                    if version_pos >= 0 and version_pos < len(line):
                                        start_pos = version_pos
                                        end_pos = available_pos if available_pos > version_pos and available_pos < len(line) else len(line)
                                        if end_pos > start_pos:
                                            version = line[start_pos:end_pos].strip()
                                            print(f"  Version: {repr(version)}")
                                            
                                            # Available
                                            if available_pos >= 0 and available_pos < len(line):
                                                start_pos = available_pos
                                                available = line[start_pos:].strip()
                                                print(f"  Available: {repr(available)}")
                        
                        parsed_count += 1
                        if parsed_count >= 3:
                            break
            else:
                print("Header line not found!")
                
                # 显示前20行以帮助调试
                print("\nFirst 20 lines:")
                for i, line in enumerate(lines[:20]):
                    print(f"{i}: {repr(line)}")
        else:
            print("No output received")
    else:
        print("Command failed")

if __name__ == "__main__":
    debug_winget_output()