"""
A tool to use winget with gui.
"""
import importlib.metadata
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
WinGet GUI - 类似AppStore的Windows包管理器图形界面
基于PySide6开发
"""

import sys
import subprocess
import json
import threading
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QGridLayout, QLabel, QLineEdit, QPushButton, QListView, 
    QTreeView, QTableView, QTextEdit, QProgressBar, QMessageBox,
    QTabWidget, QGroupBox, QScrollArea, QFrame, QSplitter, QSizePolicy
)
from PySide6.QtCore import Qt, QAbstractListModel, QModelIndex, QRunnable, QThreadPool, Signal, QObject
from PySide6.QtGui import QPixmap, QIcon, QStandardItemModel, QStandardItem


class PackageModel(QAbstractListModel):
    """软件包数据模型"""
    
    def __init__(self, packages=None):
        super().__init__()
        self.packages = packages or []
    
    def rowCount(self, parent=None):
        """返回行数"""
        if parent is None:
            parent = QModelIndex()
        elif parent.isValid():
            return 0
        return len(self.packages)
    
    def data(self, index, role=None):
        """返回数据"""
        if not index.isValid() or index.row() >= len(self.packages):
            return None
            
        package = self.packages[index.row()]
        
        if role == Qt.ItemDataRole.DisplayRole:
            return f"{package.get('Name', 'Unknown')} - {package.get('Version', 'Unknown')}"
        elif role == Qt.ItemDataRole.ToolTipRole:
            return f"{package.get('Description', '')}\nPublisher: {package.get('Publisher', 'Unknown')}"
        
        return None
    
    def get_package(self, index):
        """获取指定索引的软件包"""
        if 0 <= index < len(self.packages):
            return self.packages[index]
        return None
    
    def clear(self):
        """清空所有软件包"""
        self.beginResetModel()
        self.packages.clear()
        self.endResetModel()
    
    def add_packages(self, packages):
        """添加软件包到模型"""
        if not packages:
            return
        self.beginInsertRows(QModelIndex(), len(self.packages), len(self.packages) + len(packages) - 1)
        self.packages.extend(packages)
        self.endInsertRows()


class WorkerSignals(QObject):
    """工作线程信号"""
    finished = Signal()
    error = Signal(str)
    result = Signal(object)


class Worker(QRunnable):
    """工作线程"""
    
    def __init__(self, fn, *args, **kwargs):
        super().__init__()
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()
    
    def run(self):
        try:
            result = self.fn(*self.args, **self.kwargs)
            self.signals.result.emit(result)
        except Exception as e:
            self.signals.error.emit(str(e))
        finally:
            self.signals.finished.emit()


class WinGetGUI(QMainWindow):
    """WinGet GUI主窗口"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("WinGet GUI - Windows包管理器")
        self.setGeometry(100, 100, 1200, 800)
        
        # 当前选中的软件包
        self.current_package = None
        self.current_installed_package = None
        
        # 初始化线程池
        self.threadpool = QThreadPool()
        
        # 状态栏
        self.status_bar = self.statusBar()
        self.status_bar.showMessage("就绪")
        
        # 创建UI
        self.init_ui()
        
        # 检查WinGet是否可用
        self.check_winget_availability()
    
    def init_ui(self):
        """初始化用户界面"""
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建主布局
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        # 创建标签页
        tab_widget = QTabWidget()
        
        main_layout.addWidget(tab_widget)
        
        # 搜索标签页
        search_tab = self.create_search_tab()
        tab_widget.addTab(search_tab, "搜索")
        
        # 已安装标签页
        installed_tab = self.create_installed_tab()
        tab_widget.addTab(installed_tab, "已安装")
        
        # 设置标签页
        settings_tab = self.create_settings_tab()
        tab_widget.addTab(settings_tab, "设置")

    def create_search_tab(self):
        """创建搜索标签页"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # 搜索区域
        search_group = QGroupBox("搜索软件包")
        
        search_layout = QHBoxLayout(search_group)
        search_layout.setContentsMargins(10, 10, 10, 10)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("输入软件名称或关键词...")
        self.search_input.returnPressed.connect(self.search_packages)
        
        self.search_button = QPushButton("搜索")
        self.search_button.clicked.connect(self.search_packages)
        
        search_layout.addWidget(QLabel("搜索:"))
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(self.search_button)
        
        # 结果区域
        result_group = QGroupBox("搜索结果")
        
        result_layout = QVBoxLayout(result_group)
        result_layout.setContentsMargins(10, 10, 10, 10)
        
        # 软件包列表和详情区域
        detail_splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # 软件包列表
        self.package_list = QListView()
        
        self.package_model = PackageModel()
        self.package_list.setModel(self.package_model)
        self.package_list.clicked.connect(self.on_package_selected)
        
        # 软件包详情区域
        self.detail_widget = QWidget()
        detail_layout = QVBoxLayout(self.detail_widget)
        detail_layout.setContentsMargins(10, 10, 10, 10)
        
        # 详情标题
        detail_title = QLabel("软件详情")
        detail_title.setStyleSheet("font-size: 16px; font-weight: bold; margin-bottom: 10px;")
        detail_layout.addWidget(detail_title)
        
        # 详情内容
        self.detail_label = QLabel("请选择一个软件包查看详细信息")
        self.detail_label.setWordWrap(True)
        self.detail_label.setStyleSheet("""
            QLabel {
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 10px;
                min-height: 100px;
            }
        """)
        detail_layout.addWidget(self.detail_label)
        
        # 操作按钮
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        self.install_button = QPushButton("安装")
        self.install_button.clicked.connect(self.install_package)
        self.install_button.setEnabled(False)
        
        button_layout.addWidget(self.install_button)
        button_layout.addStretch()
        
        detail_layout.addLayout(button_layout)
        
        detail_splitter.addWidget(self.package_list)
        detail_splitter.addWidget(self.detail_widget)
        detail_splitter.setSizes([400, 500])
        
        result_layout.addWidget(detail_splitter)
        
        layout.addWidget(search_group)
        layout.addWidget(result_group)
        
        return widget
    
    def create_installed_tab(self):
        """创建已安装标签页"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # 已安装软件区域
        installed_group = QGroupBox("已安装的软件包")
        
        installed_layout = QVBoxLayout(installed_group)
        installed_layout.setContentsMargins(10, 10, 10, 10)
        
        # 使用表格视图替代列表视图
        self.installed_table = QTableView()
        self.installed_table.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
        self.installed_table.setSelectionMode(QTableView.SelectionMode.SingleSelection)
        
        # 创建表格模型
        self.installed_model = QStandardItemModel(0, 4)  # 4列：Name, Id, Version, Available
        self.installed_model.setHorizontalHeaderLabels(["软件名", "软件ID", "已安装版本", "当前最新版本"])
        self.installed_table.setModel(self.installed_model)
        
        # 连接选择信号
        self.installed_table.clicked.connect(self.on_installed_package_selected)
        
        # 按钮区域
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        self.refresh_button = QPushButton("刷新")
        self.refresh_button.clicked.connect(self.refresh_installed_packages)
        
        self.uninstall_button = QPushButton("卸载")
        self.uninstall_button.clicked.connect(self.uninstall_package)
        self.uninstall_button.setEnabled(False)
        
        self.update_button = QPushButton("更新")
        self.update_button.clicked.connect(self.update_package)
        self.update_button.setEnabled(False)
        
        button_layout.addWidget(self.refresh_button)
        button_layout.addWidget(self.uninstall_button)
        button_layout.addWidget(self.update_button)
        button_layout.addStretch()
        
        installed_layout.addWidget(self.installed_table)
        installed_layout.addLayout(button_layout)
        
        layout.addWidget(installed_group)
        
        # 初始化已安装软件列表
        self.refresh_installed_packages()
        
        return widget
    
    def create_settings_tab(self):
        """创建设置标签页"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # 标题
        title_label = QLabel("设置")
        title_label.setStyleSheet("font-size: 20px; font-weight: bold; margin-bottom: 20px;")
        layout.addWidget(title_label)
        
        # WinGet信息
        info_group = QGroupBox("WinGet信息")
        
        info_layout = QVBoxLayout(info_group)
        info_layout.setContentsMargins(15, 15, 15, 15)
        
        self.info_label = QLabel("正在检查WinGet...")
        self.info_label.setWordWrap(True)
        info_layout.addWidget(self.info_label)
        
        layout.addWidget(info_group)
        
        # 应用信息
        app_group = QGroupBox("应用信息")
        
        app_layout = QVBoxLayout(app_group)
        app_layout.setContentsMargins(15, 15, 15, 15)
        
        app_info = QLabel("WinGet GUI - Windows包管理器图形界面\n版本: 1.0\n基于PySide6开发")
        app_info.setWordWrap(True)
        app_layout.addWidget(app_info)
        
        layout.addWidget(app_group)
        layout.addStretch()
        
        return widget
    
    def check_winget_availability(self):
        """检查WinGet是否可用"""
        def check_winget():
            try:
                result = subprocess.run(
                    ["winget", "--version"], 
                    capture_output=True, 
                    text=True, 
                    timeout=10
                )
                return result.stdout.strip() if result.returncode == 0 else "WinGet不可用"
            except FileNotFoundError:
                return "未找到WinGet命令，请确保已安装Windows包管理器"
            except Exception as e:
                return f"检查WinGet时出错: {str(e)}"
        
        # 在线程中运行
        worker = Worker(check_winget)
        worker.signals.result.connect(self.on_winget_check_result)
        self.threadpool.start(worker)
        
        self.status_bar.showMessage("正在检查WinGet...")
    
    def on_winget_check_result(self, result):
        """处理WinGet检查结果"""
        self.info_label.setText(result)
        self.status_bar.showMessage(result)
    
    def on_package_selected(self, index):
        """当选择软件包时"""
        package = self.package_model.get_package(index.row())
        if package:
            self.current_package = package
            # 显示软件包详情
            details = f"<b>名称:</b> {package.get('Name', 'Unknown')}<br>"
            details += f"<b>版本:</b> {package.get('Version', 'Unknown')}<br>"
            details += f"<b>发布者:</b> {package.get('Publisher', 'Unknown')}<br>"
            details += f"<b>ID:</b> {package.get('Id', 'Unknown')}<br>"
            details += f"<b>描述:</b> {package.get('Description', '无描述')}<br>"
            
            self.detail_label.setText(details)
            self.install_button.setEnabled(True)
        else:
            self.current_package = None
            self.detail_label.setText("请选择一个软件包查看详细信息")
            self.install_button.setEnabled(False)
    
    def on_installed_package_selected(self, index):
        """当选中已安装的软件包时"""
        # 获取选中的行
        row = index.row()
        if row >= 0:
            # 从模型中获取软件包信息
            name_item = self.installed_model.item(row, 0)
            id_item = self.installed_model.item(row, 1)
            
            if name_item and id_item:
                self.current_installed_package = {
                    "Name": name_item.text(),
                    "Id": id_item.text()
                }
                self.uninstall_button.setEnabled(True)
                self.update_button.setEnabled(True)
            else:
                self.current_installed_package = None
                self.uninstall_button.setEnabled(False)
                self.update_button.setEnabled(False)
        else:
            self.current_installed_package = None
            self.uninstall_button.setEnabled(False)
            self.update_button.setEnabled(False)
    
    def search_packages(self):
        """搜索软件包"""
        query = self.search_input.text().strip()
        if not query:
            QMessageBox.warning(self, "警告", "请输入搜索关键词")
            return
        
        # 清空之前的结果
        self.package_model.clear()
        self.detail_label.setText("请选择一个软件包查看详细信息")
        self.install_button.setEnabled(False)
        
        self.status_bar.showMessage(f"正在搜索 '{query}'...")
        
        def do_search():
            try:
                # 使用普通格式获取搜索结果（不使用--json参数）
                cmd = ["winget", "search", query, "--source", "winget"]
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
                    # 解析文本格式输出
                    output = result.stdout.strip() if result.stdout else ""
                    if output:
                        lines = output.split('\n')
                        if len(lines) > 2:  # 确保有内容（跳过标题行）
                            packages = []
                            # 跳过前两行（标题和分隔线）
                            for line in lines[2:]:
                                line = line.strip() if line else ""
                                if line:  # 跳过空行
                                    # 尝试分割包信息
                                    # 格式通常是: Name Id Version Source
                                    parts = line.split()
                                    if len(parts) >= 3:
                                        # 对于搜索结果，格式通常是 Name Id Version Source
                                        package = {
                                            "Name": parts[0] if len(parts) > 0 else "Unknown",
                                            "Id": parts[1] if len(parts) > 1 else "Unknown",
                                            "Version": parts[2] if len(parts) > 2 else "Unknown",
                                            "Publisher": "Unknown",  # 搜索结果不直接提供发布者
                                            "Description": ""
                                        }
                                        packages.append(package)
                                    elif len(parts) == 2:
                                        # 只有名称和ID
                                        package = {
                                            "Name": parts[0],
                                            "Id": parts[1],
                                            "Version": "Unknown",
                                            "Publisher": "Unknown",
                                            "Description": ""
                                        }
                                        packages.append(package)
                            return packages
                    return []
                else:
                    return f"搜索失败: {result.stderr}"
            except subprocess.TimeoutExpired:
                return "搜索超时"
            except Exception as e:
                import traceback
                return f"搜索时出错: {str(e)}\n{traceback.format_exc()}"
        
        # 在线程中运行
        worker = Worker(do_search)
        worker.signals.result.connect(self.on_search_result)
        worker.signals.error.connect(self.on_search_error)
        self.threadpool.start(worker)
    
    def on_search_result(self, result):
        """处理搜索结果"""
        if isinstance(result, str):
            # 错误信息
            QMessageBox.critical(self, "错误", result)
            self.status_bar.showMessage("搜索失败")
        else:
            # 成功获取软件包列表
            self.package_model.add_packages(result)
            self.status_bar.showMessage(f"找到 {len(result)} 个软件包")
    
    def on_search_error(self, error):
        """处理搜索错误"""
        QMessageBox.critical(self, "错误", f"搜索时发生错误: {error}")
        self.status_bar.showMessage("搜索失败")
    
    def install_package(self):
        """安装软件包"""
        if not self.current_package:
            QMessageBox.warning(self, "警告", "请选择要安装的软件包")
            return
        
        package_id = self.current_package.get('Id')
        if not package_id:
            QMessageBox.warning(self, "警告", "无法获取软件包ID")
            return
        
        reply = QMessageBox.question(
            self, 
            "确认安装", 
            f"确定要安装 {self.current_package.get('Name')} 吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.status_bar.showMessage(f"正在安装 {self.current_package.get('Name')}...")
            
            def do_install():
                try:
                    # 使用winget安装命令
                    result = subprocess.run(
                        ["winget", "install", "--id", package_id, "--source", "winget", "-h"], 
                        capture_output=True, 
                        text=True, 
                        timeout=300  # 5分钟超时
                    )
                    
                    package_name = "Unknown"
                    if self.current_package is not None:
                        package_name = self.current_package.get('Name', 'Unknown')
                    
                    if result.returncode == 0:
                        return f"成功安装 {package_name}"
                    else:
                        return f"安装失败: {result.stderr}"
                except subprocess.TimeoutExpired:
                    return "安装超时"
                except Exception as e:
                    return f"安装时出错: {str(e)}"
            
            # 在线程中运行
            worker = Worker(do_install)
            worker.signals.result.connect(self.on_install_result)
            worker.signals.error.connect(self.on_install_error)
            self.threadpool.start(worker)
    
    def on_install_result(self, result):
        """处理安装结果"""
        QMessageBox.information(self, "安装结果", result)
        self.status_bar.showMessage(result)
        # 刷新已安装列表
        self.refresh_installed_packages()
    
    def on_install_error(self, error):
        """处理安装错误"""
        QMessageBox.critical(self, "错误", f"安装时发生错误: {error}")
        self.status_bar.showMessage("安装失败")
    
    def refresh_installed_packages(self):
        """刷新已安装软件包列表"""
        # 清空之前的列表
        self.installed_model.removeRows(0, self.installed_model.rowCount())
        self.uninstall_button.setEnabled(False)
        self.update_button.setEnabled(False)
        
        self.status_bar.showMessage("正在获取已安装的软件包...")
        
        def get_installed():
            try:
                # 获取winget列表输出
                cmd = ["winget", "list", "--source", "winget"]
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
                    # 解析文本格式输出
                    output = result.stdout.strip() if result.stdout else ""
                    if output:
                        lines = output.split('\n')
                        
                        # 查找实际的标题行（包含Name的行）
                        header_line_index = -1
                        header_line = ""
                        for i, line in enumerate(lines):
                            if "Name" in line and "Id" in line and "Version" in line:
                                header_line_index = i
                                header_line = line
                                break
                        
                        if header_line_index >= 0:
                            packages = []
                            
                            # 查找各列的位置
                            name_pos = header_line.find("Name")
                            id_pos = header_line.find("Id")
                            version_pos = header_line.find("Version")
                            available_pos = header_line.find("Available")
                            
                            # 从标题行之后开始解析数据行
                            for i in range(header_line_index + 2, len(lines)):
                                line = lines[i].rstrip()
                                if line and not line.startswith('-') and "Name" not in line:
                                    # 使用列位置解析数据
                                    name = ""
                                    package_id = ""
                                    version = ""
                                    available = ""
                                    
                                    # Name列
                                    if name_pos >= 0 and len(line) > name_pos:
                                        end_pos = id_pos if id_pos > name_pos and id_pos < len(line) else len(line)
                                        if end_pos > name_pos:
                                            name = line[name_pos:end_pos].strip()
                                    
                                    # Id列
                                    if id_pos >= 0 and len(line) > id_pos:
                                        start_pos = id_pos
                                        end_pos = version_pos if version_pos > id_pos and version_pos < len(line) else len(line)
                                        if end_pos > start_pos:
                                            package_id = line[start_pos:end_pos].strip()
                                    
                                    # Version列
                                    if version_pos >= 0 and len(line) > version_pos:
                                        start_pos = version_pos
                                        end_pos = available_pos if available_pos > version_pos and available_pos < len(line) else len(line)
                                        if end_pos > start_pos:
                                            version = line[start_pos:end_pos].strip()
                                    
                                    # Available列
                                    if available_pos >= 0 and len(line) > available_pos:
                                        start_pos = available_pos
                                        available = line[start_pos:].strip()
                                    
                                    # 只有当至少有名称时才添加包
                                    if name and name.strip():
                                        package = {
                                            "Name": name,
                                            "Id": package_id,
                                            "Version": version,
                                            "Available": available
                                        }
                                        packages.append(package)
                            
                            return packages
                    return []
                else:
                    error_msg = f"获取已安装软件包失败:\n返回码: {result.returncode}\n错误信息: {result.stderr}"
                    if result.returncode == 1603:
                        error_msg += "\n可能是权限问题，请以管理员身份运行程序。"
                    elif result.returncode == -1073741515:
                        error_msg += "\n可能是WinGet未正确安装。"
                    return error_msg
                    
            except subprocess.TimeoutExpired:
                return "获取超时"
            except Exception as e:
                import traceback
                return f"获取已安装软件包时出错: {str(e)}\n{traceback.format_exc()}"
        
        # 在线程中运行
        worker = Worker(get_installed)
        worker.signals.result.connect(self.on_installed_result)
        worker.signals.error.connect(self.on_installed_error)
        self.threadpool.start(worker)

    def on_installed_result(self, result):
        """处理已安装软件包结果"""
        if isinstance(result, str):
            # 错误信息
            QMessageBox.critical(self, "错误", result)
            self.status_bar.showMessage("获取已安装软件包失败")
        else:
            # 成功获取软件包列表，填充表格
            self.installed_model.removeRows(0, self.installed_model.rowCount())
            
            for package in result:
                row = self.installed_model.rowCount()
                self.installed_model.insertRow(row)
                
                # 添加数据到表格
                self.installed_model.setItem(row, 0, QStandardItem(package.get("Name", "Unknown")))
                self.installed_model.setItem(row, 1, QStandardItem(package.get("Id", "Unknown")))
                self.installed_model.setItem(row, 2, QStandardItem(package.get("Version", "Unknown")))
                self.installed_model.setItem(row, 3, QStandardItem(package.get("Available", "")))
            
            # 调整列宽
            self.installed_table.resizeColumnsToContents()
            self.installed_table.horizontalHeader().setStretchLastSection(True)
            
            self.status_bar.showMessage(f"已安装 {len(result)} 个软件包")

    def on_installed_error(self, error):
        """处理已安装软件包错误"""
        QMessageBox.critical(self, "错误", f"获取已安装软件包时发生错误: {error}")
        self.status_bar.showMessage("获取已安装软件包失败")
    
    def uninstall_package(self):
        """卸载软件包"""
        if not hasattr(self, 'current_installed_package') or not self.current_installed_package:
            QMessageBox.warning(self, "警告", "请选择要卸载的软件包")
            return
        
        package_id = self.current_installed_package.get('Id')
        if not package_id:
            QMessageBox.warning(self, "警告", "无法获取软件包ID")
            return
        
        reply = QMessageBox.question(
            self, 
            "确认卸载", 
            f"确定要卸载 {self.current_installed_package.get('Name')} 吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.status_bar.showMessage(f"正在卸载 {self.current_installed_package.get('Name')}...")
            
            def do_uninstall():
                try:
                    # 使用winget卸载命令
                    result = subprocess.run(
                        ["winget", "uninstall", "--id", package_id, "--source", "winget", "-h"], 
                        capture_output=True, 
                        text=True, 
                        timeout=300  # 5分钟超时
                    )
                    
                    package_name = "Unknown"
                    if self.current_installed_package is not None:
                        package_name = self.current_installed_package.get('Name', 'Unknown')
                    
                    if result.returncode == 0:
                        return f"成功卸载 {package_name}"
                    else:
                        return f"卸载失败: {result.stderr}"
                except subprocess.TimeoutExpired:
                    return "卸载超时"
                except Exception as e:
                    return f"卸载时出错: {str(e)}"
            
            # 在线程中运行
            worker = Worker(do_uninstall)
            worker.signals.result.connect(self.on_uninstall_result)
            worker.signals.error.connect(self.on_uninstall_error)
            self.threadpool.start(worker)
    
    def on_uninstall_result(self, result):
        """处理卸载结果"""
        QMessageBox.information(self, "卸载结果", result)
        self.status_bar.showMessage(result)
        # 刷新已安装列表
        self.refresh_installed_packages()
    
    def on_uninstall_error(self, error):
        """处理卸载错误"""
        QMessageBox.critical(self, "错误", f"卸载时发生错误: {error}")
        self.status_bar.showMessage("卸载失败")
    
    def update_package(self):
        """更新软件包"""
        if not hasattr(self, 'current_installed_package') or not self.current_installed_package:
            QMessageBox.warning(self, "警告", "请选择要更新的软件包")
            return
        
        package_id = self.current_installed_package.get('Id')
        if not package_id:
            QMessageBox.warning(self, "警告", "无法获取软件包ID")
            return
        
        reply = QMessageBox.question(
            self, 
            "确认更新", 
            f"确定要更新 {self.current_installed_package.get('Name')} 吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.status_bar.showMessage(f"正在更新 {self.current_installed_package.get('Name')}...")
            
            def do_update():
                try:
                    # 使用winget更新命令
                    result = subprocess.run(
                        ["winget", "upgrade", "--id", package_id, "--source", "winget", "-h"], 
                        capture_output=True, 
                        text=True, 
                        timeout=300  # 5分钟超时
                    )
                    
                    package_name = "Unknown"
                    if self.current_installed_package is not None:
                        package_name = self.current_installed_package.get('Name', 'Unknown')
                    
                    if result.returncode == 0:
                        return f"成功更新 {package_name}"
                    else:
                        return f"更新失败: {result.stderr}"
                except subprocess.TimeoutExpired:
                    return "更新超时"
                except Exception as e:
                    return f"更新时出错: {str(e)}"
            
            # 在线程中运行
            worker = Worker(do_update)
            worker.signals.result.connect(self.on_update_result)
            worker.signals.error.connect(self.on_update_error)
            self.threadpool.start(worker)
    
    def on_update_result(self, result):
        """处理更新结果"""
        QMessageBox.information(self, "更新结果", result)
        self.status_bar.showMessage(result)
        # 刷新已安装列表
        self.refresh_installed_packages()
    
    def on_update_error(self, error):
        """处理更新错误"""
        QMessageBox.critical(self, "错误", f"更新时发生错误: {error}")
        self.status_bar.showMessage("更新失败")



def main():
    # Linux desktop environments use an app's .desktop file to integrate the app
    # in to their application menus. The .desktop file of this app will include
    # the StartupWMClass key, set to app's formal name. This helps associate the
    # app's windows to its menu item.
    #
    # For association to work, any windows of the app must have WMCLASS property
    # set to match the value set in app's desktop file. For PySide6, this is set
    # with setApplicationName().

    # Find the name of the module that was used to start the app
    app_module = sys.modules["__main__"].__package__
    if app_module:
        try:
            # Retrieve the app's metadata
            metadata = importlib.metadata.metadata(app_module)
            QApplication.setApplicationName(metadata["Formal-Name"])
        except Exception:
            # If metadata is not available, set a default application name
            QApplication.setApplicationName("WinGetGUI")
    else:
        # If app_module is not available, set a default application name
        QApplication.setApplicationName("WinGetGUI")

    app = QApplication(sys.argv)
    
    # 设置应用程序信息
    app.setApplicationName("WinGet GUI")
    app.setApplicationVersion("1.0")
    
    # 创建并显示主窗口
    window = WinGetGUI()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

