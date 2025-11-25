import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os
import glob
import threading
import time
import subprocess
import pyautogui
import psutil

class XPSDataExtractor:
    def __init__(self, root):
        self.root = root
        self.root.title("XPS数据提取工具 - 全文件格式版 + CasaXPS智能导航")
        self.root.geometry("1000x1250")
        
        # CasaXPS路径配置
        self.casaxps_path = r"E:/Academic/FYP/XPS/Casa/Casa2326PR1-0/CasaXPS.exe"
        self.convert_button_pos = (95, 85)  # Convert按钮坐标
        
        self.setup_ui()
        
    def setup_ui(self):
        """设置用户界面"""
        main_frame = ttk.Frame(self.root, padding="20") 
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 标题
        title_label = ttk.Label(main_frame, text="XPS数据提取工具 - 全文件格式版 + CasaXPS智能导航", 
                               font=('Arial', 14, 'bold'))
        title_label.pack(pady=(0, 15))
        
        # 说明文本
        info_text = """专用文件格式处理说明：
• 支持所有文件格式（文本文件、数据文件等）
• 自动检测列标题：Binding Energy(eV) 和 Intensity(cps)
• 跳过文件头部的元数据信息
• 输出格式：仅包含两列数据（Binding Energy + Intensity），TAB分隔
• 智能导航：使用Alt+↑回到根目录，Alt+←导航，然后逐级导航到目标文件夹"""
        
        info_label = ttk.Label(main_frame, text=info_text, justify=tk.LEFT, 
                              background='#e8f4fd', relief='solid', padding=10)
        info_label.pack(pady=(0, 20), fill=tk.X)
        
        # CasaXPS配置区域
        casaxps_frame = ttk.LabelFrame(main_frame, text="CasaXPS配置", padding=10)
        casaxps_frame.pack(fill=tk.X, pady=(0, 15))
        
        casaxps_config_frame = ttk.Frame(casaxps_frame)
        casaxps_config_frame.pack(fill=tk.X)
        
        ttk.Label(casaxps_config_frame, text="CasaXPS路径:").pack(side=tk.LEFT)
        
        self.casaxps_path_var = tk.StringVar(value=self.casaxps_path)
        casaxps_entry = ttk.Entry(casaxps_config_frame, textvariable=self.casaxps_path_var, 
                                 width=60, state='readonly')
        casaxps_entry.pack(side=tk.LEFT, padx=(5, 10), fill=tk.X, expand=True)
        
        ttk.Button(casaxps_config_frame, text="浏览", 
                  command=self.browse_casaxps).pack(side=tk.RIGHT)
        
        # Convert按钮坐标配置
        convert_pos_frame = ttk.Frame(casaxps_frame)
        convert_pos_frame.pack(fill=tk.X, pady=(5, 0))
        
        ttk.Label(convert_pos_frame, text="Convert按钮坐标:").pack(side=tk.LEFT)
        
        self.convert_x_var = tk.StringVar(value="95")
        self.convert_y_var = tk.StringVar(value="85")
        
        ttk.Entry(convert_pos_frame, textvariable=self.convert_x_var, width=5).pack(side=tk.LEFT, padx=(5, 0))
        ttk.Label(convert_pos_frame, text="X").pack(side=tk.LEFT, padx=(2, 0))
        ttk.Entry(convert_pos_frame, textvariable=self.convert_y_var, width=5).pack(side=tk.LEFT, padx=(2, 0))
        ttk.Label(convert_pos_frame, text="Y").pack(side=tk.LEFT, padx=(2, 5))
        
        ttk.Button(convert_pos_frame, text="测试坐标", 
                  command=self.test_convert_position).pack(side=tk.LEFT, padx=(5, 0))
        
        # CasaXPS选项
        casaxps_options_frame = ttk.Frame(casaxps_frame)
        casaxps_options_frame.pack(fill=tk.X, pady=(5, 0))
        
        self.auto_process_casaxps = tk.BooleanVar(value=True)
        ttk.Checkbutton(casaxps_options_frame, text="自动调用CasaXPS处理dat文件", 
                       variable=self.auto_process_casaxps).pack(side=tk.LEFT)
        
        self.close_casaxps = tk.BooleanVar(value=True)
        ttk.Checkbutton(casaxps_options_frame, text="处理完成后关闭CasaXPS", 
                       variable=self.close_casaxps).pack(side=tk.LEFT, padx=(20, 0))
        
        # 文件夹选择区域
        folder_frame = ttk.Frame(main_frame)
        folder_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(folder_frame, text="选择XPS数据文件夹:").pack(anchor=tk.W)
        
        folder_select_frame = ttk.Frame(folder_frame)
        folder_select_frame.pack(fill=tk.X, pady=(5, 0))
        
        self.folder_path = tk.StringVar()
        self.folder_entry = ttk.Entry(folder_select_frame, textvariable=self.folder_path, 
                                     font=('Arial', 9))
        self.folder_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        ttk.Button(folder_select_frame, text="浏览文件夹", 
                  command=self.browse_folder).pack(side=tk.RIGHT)
        
        # 处理选项区域
        options_frame = ttk.LabelFrame(main_frame, text="处理选项", padding=10)
        options_frame.pack(fill=tk.X, pady=(0, 15))
        
        # 文件类型选择
        filetype_frame = ttk.Frame(options_frame)
        filetype_frame.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(filetype_frame, text="文件类型:").pack(side=tk.LEFT)
        
        self.file_type = tk.StringVar(value="all")
        file_types = [
            ("所有文件 (*.*)", "all"),
            ("文本文件 (*.txt)", "txt"),
            ("数据文件 (*.dat;*.csv)", "data"),
            ("自定义扩展名", "custom")
        ]
        
        for text, value in file_types:
            ttk.Radiobutton(filetype_frame, text=text, 
                           variable=self.file_type, value=value,
                           command=self.toggle_custom_entry).pack(side=tk.LEFT, padx=(10, 0))
        
        # 自定义扩展名输入框
        self.custom_frame = ttk.Frame(options_frame)
        self.custom_frame.pack(fill=tk.X, pady=(5, 0))
        
        ttk.Label(self.custom_frame, text="自定义扩展名:").pack(side=tk.LEFT)
        self.custom_ext = tk.StringVar(value="*.xyz")
        self.custom_entry = ttk.Entry(self.custom_frame, textvariable=self.custom_ext, width=20)
        self.custom_entry.pack(side=tk.LEFT, padx=(5, 0))
        ttk.Label(self.custom_frame, text="(如: *.xyz, *.data, 多个用分号分隔)").pack(side=tk.LEFT, padx=(5, 0))
        
        # 文件过滤选项
        filter_frame = ttk.Frame(options_frame)
        filter_frame.pack(fill=tk.X, pady=(5, 0))
        
        self.skip_folders = tk.BooleanVar(value=True)
        ttk.Checkbutton(filter_frame, text="跳过子文件夹", 
                       variable=self.skip_folders).pack(side=tk.LEFT, padx=(0, 10))
        
        self.skip_binary = tk.BooleanVar(value=True)
        ttk.Checkbutton(filter_frame, text="跳过二进制文件", 
                       variable=self.skip_binary).pack(side=tk.LEFT)
        
        # 分隔符选项
        delimiter_frame = ttk.Frame(options_frame)
        delimiter_frame.pack(fill=tk.X, pady=(5, 0))
        
        ttk.Label(delimiter_frame, text="分隔符:").pack(side=tk.LEFT)
        
        self.delimiter_var = tk.StringVar(value="tab")
        ttk.Radiobutton(delimiter_frame, text="制表符 (Tab)", 
                       variable=self.delimiter_var, value="tab").pack(side=tk.LEFT, padx=(10, 0))
        ttk.Radiobutton(delimiter_frame, text="自动检测", 
                       variable=self.delimiter_var, value="auto").pack(side=tk.LEFT, padx=(10, 0))
        
        # 输出格式选项
        output_frame = ttk.Frame(options_frame)
        output_frame.pack(fill=tk.X, pady=(5, 0))
        
        ttk.Label(output_frame, text="输出格式:").pack(side=tk.LEFT)
        
        self.include_header = tk.BooleanVar(value=False)
        ttk.Checkbutton(output_frame, text="包含列标题", 
                       variable=self.include_header).pack(side=tk.LEFT, padx=(10, 0))
        
        # 进度区域
        progress_frame = ttk.Frame(main_frame)
        progress_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(progress_frame, text="处理进度:").pack(anchor=tk.W)
        
        self.progress = ttk.Progressbar(progress_frame, mode='determinate')
        self.progress.pack(fill=tk.X, pady=(5, 0))
        
        self.progress_label = ttk.Label(progress_frame, text="等待开始...")
        self.progress_label.pack(anchor=tk.W)
        
        # 日志区域
        log_frame = ttk.LabelFrame(main_frame, text="处理日志", padding=10)
        log_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        # 创建带滚动条的文本框
        log_text_frame = ttk.Frame(log_frame)
        log_text_frame.pack(fill=tk.BOTH, expand=True)
        
        self.log_text = tk.Text(log_text_frame, height=12, wrap=tk.WORD, font=('Consolas', 9))
        scrollbar = ttk.Scrollbar(log_text_frame, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)
        
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 按钮区域
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)
        
        ttk.Button(button_frame, text="开始处理", 
                  command=self.start_processing).pack(side=tk.RIGHT, padx=(10, 0))
        
        ttk.Button(button_frame, text="清空日志", 
                  command=self.clear_log).pack(side=tk.RIGHT, padx=(10, 0))
        
        ttk.Button(button_frame, text="打开结果文件夹", 
                  command=self.open_result_folder).pack(side=tk.LEFT)
        
        # 初始化界面状态
        self.toggle_custom_entry()
        
        # 设置pyautogui安全设置
        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = 1.0
    
    def browse_casaxps(self):
        """浏览选择CasaXPS.exe路径"""
        file_selected = filedialog.askopenfilename(
            title="选择CasaXPS.exe文件",
            filetypes=[("Executable files", "*.exe"), ("All files", "*.*")]
        )
        if file_selected:
            self.casaxps_path_var.set(file_selected)
            self.casaxps_path = file_selected
    
    def test_convert_position(self):
        """测试Convert按钮坐标"""
        try:
            x = int(self.convert_x_var.get())
            y = int(self.convert_y_var.get())
            self.convert_button_pos = (x, y)
            
            self.log(f"🎯 测试Convert按钮坐标: ({x}, {y})")
            self.log("⚠️ 请确保CasaXPS窗口可见且未被遮挡")
            
            # 倒计时
            for i in range(3, 0, -1):
                self.log(f"⏰ {i}秒后测试点击...")
                self.root.update()
                time.sleep(1)
            
            # 移动鼠标到指定位置
            pyautogui.moveTo(x, y, duration=1)
            time.sleep(1)
            
            # 点击测试
            pyautogui.click()
            self.log("✅ 已执行点击测试，请检查CasaXPS是否打开了Convert对话框")
            
        except ValueError:
            messagebox.showerror("错误", "请输入有效的坐标数字")
        except Exception as e:
            self.log(f"❌ 坐标测试失败: {e}")
    
    def toggle_custom_entry(self):
        """切换自定义扩展名输入框的可用状态"""
        if self.file_type.get() == "custom":
            self.custom_entry.configure(state='normal')
        else:
            self.custom_entry.configure(state='disabled')
    
    def browse_folder(self):
        """浏览选择文件夹"""
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.folder_path.set(folder_selected)
            self.log(f"📁 已选择文件夹: {folder_selected}")
    
    def log(self, message):
        """添加日志信息"""
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()
    
    def clear_log(self):
        """清空日志"""
        self.log_text.delete(1.0, tk.END)
    
    def open_result_folder(self):
        """打开结果文件夹"""
        folder_path = self.folder_path.get()
        if folder_path and os.path.exists(folder_path):
            try:
                if os.name == 'nt':  # Windows
                    os.startfile(folder_path)
                else:  # MacOS or Linux
                    os.system(f'open "{folder_path}"' if os.name == 'posix' else f'xdg-open "{folder_path}"')
            except:
                self.log("⚠️ 无法打开文件夹，请手动访问")
        else:
            messagebox.showwarning("警告", "请先选择有效的文件夹")
    
    def is_binary_file(self, file_path):
        """检测文件是否为二进制文件"""
        try:
            with open(file_path, 'rb') as f:
                chunk = f.read(1024)
                if b'\0' in chunk:  # 二进制文件通常包含空字节
                    return True
        except:
            return True
        return False
    
    def get_file_patterns(self):
        """根据选择的文件类型获取匹配模式"""
        file_type = self.file_type.get()
        
        if file_type == "all":
            return ["*"]  # 匹配所有文件
        elif file_type == "txt":
            return ["*.txt"]
        elif file_type == "data":
            return ["*.dat", "*.csv", "*.data"]
        elif file_type == "custom":
            custom_patterns = self.custom_ext.get().split(';')
            return [pattern.strip() for pattern in custom_patterns if pattern.strip()]
        
        return ["*"]  # 默认匹配所有文件
    
    def get_all_files(self, folder_path):
        """获取文件夹中的所有文件（根据选项过滤）"""
        patterns = self.get_file_patterns()
        all_files = []
        
        if self.skip_folders.get():
            # 只搜索当前文件夹，不搜索子文件夹
            for pattern in patterns:
                if pattern == "*":
                    # 获取所有文件
                    files = [f for f in os.listdir(folder_path) 
                            if os.path.isfile(os.path.join(folder_path, f))]
                    all_files.extend([os.path.join(folder_path, f) for f in files])
                else:
                    # 使用glob匹配模式
                    files = glob.glob(os.path.join(folder_path, pattern))
                    all_files.extend(files)
        else:
            # 搜索所有子文件夹
            for pattern in patterns:
                if pattern == "*":
                    # 获取所有文件（包括子文件夹）
                    for root, dirs, files in os.walk(folder_path):
                        for file in files:
                            all_files.append(os.path.join(root, file))
                else:
                    # 使用glob递归匹配
                    files = glob.glob(os.path.join(folder_path, "**", pattern), recursive=True)
                    all_files.extend(files)
        
        # 去重并排序
        all_files = list(set(all_files))
        all_files.sort()
        
        # 过滤掉文件夹（确保只处理文件）
        all_files = [f for f in all_files if os.path.isfile(f)]
        
        # 如果启用二进制文件过滤，跳过二进制文件
        if self.skip_binary.get():
            text_files = []
            for file_path in all_files:
                if not self.is_binary_file(file_path):
                    text_files.append(file_path)
                else:
                    self.log(f"⚠️ 跳过二进制文件: {os.path.basename(file_path)}")
            return text_files
        
        return all_files
    
    def detect_delimiter(self, line):
        """检测分隔符类型"""
        if '\t' in line and len(line.split('\t')) >= 4:
            return '\t'  # 制表符分隔
        elif ' ' in line and len(line.split()) >= 4:
            return ' '   # 空格分隔
        return '\t'  # 默认制表符
    
    def parse_xps_file(self, file_path):
        """解析XPS数据文件"""
        try:
            # 检查文件大小，避免处理过大文件
            file_size = os.path.getsize(file_path)
            if file_size > 10 * 1024 * 1024:  # 10MB限制
                return None, f"文件过大 ({file_size/1024/1024:.1f}MB)，跳过处理"
            
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
            
            self.log(f"  读取到 {len(lines)} 行内容，文件大小: {file_size/1024:.1f}KB")
            
            # 查找包含列标题的行
            header_line_index = -1
            energy_col = -1
            intensity_col = -1
            delimiter = '\t'  # 默认使用制表符
            
            for i, line in enumerate(lines):
                # 检测分隔符
                if self.delimiter_var.get() == 'auto' and i < min(10, len(lines)):
                    detected_delimiter = self.detect_delimiter(line)
                    if detected_delimiter:
                        delimiter = detected_delimiter
                
                # 查找列标题行
                if 'Binding Energy(eV)' in line and 'Intensity(cps)' in line:
                    header_line_index = i
                    self.log(f"  找到标题行: 第{i+1}行")
                    
                    # 使用检测到的分隔符分割
                    columns = line.strip().split(delimiter)
                    self.log(f"  检测到分隔符: {'制表符' if delimiter == '\t' else '空格'}")
                    
                    # 查找列索引
                    for j, col in enumerate(columns):
                        if 'Binding Energy(eV)' in col:
                            energy_col = j
                            self.log(f"  Binding Energy列索引: {j}")
                        elif 'Intensity(cps)' in col:
                            intensity_col = j
                            self.log(f"  Intensity列索引: {j}")
                    
                    break
            
            if header_line_index == -1:
                # 如果没有找到标准标题，尝试其他可能的标题格式
                for i, line in enumerate(lines):
                    if any(keyword in line for keyword in ['Binding Energy', 'Intensity']):
                        columns = line.strip().split(delimiter)
                        if len(columns) >= 3:  # 至少有3列
                            header_line_index = i
                            energy_col = 1  # 通常第二列是Binding Energy
                            intensity_col = 2  # 通常第三列是Intensity
                            self.log(f"  使用备用标题行: 第{i+1}行")
                            break
            
            if header_line_index == -1 or energy_col == -1 or intensity_col == -1:
                return None, "未找到Binding Energy和Intensity列标题"
            
            # 提取数据
            data_lines = []
            valid_data_count = 0
            
            for i, line in enumerate(lines[header_line_index + 1:], header_line_index + 2):
                line = line.strip()
                if not line:
                    continue
                
                # 跳过注释行和元数据行
                if line.startswith('#') or any(keyword in line for keyword in 
                    ['Dataset', 'Dwell', 'sweeps', 'Transmission', 'Kinetic Energy']):
                    continue
                
                # 使用检测到的分隔符分割
                parts = line.split(delimiter)
                
                # 检查是否是有效数据行
                if len(parts) > max(energy_col, intensity_col):
                    try:
                        # 尝试转换为浮点数
                        energy_val = float(parts[energy_col])
                        intensity_val = float(parts[intensity_col])
                        
                        data_lines.append(f"{energy_val:.6f}\t{intensity_val:.6f}")
                        valid_data_count += 1
                        
                    except (ValueError, IndexError) as e:
                        # 如果转换失败，跳过这行
                        continue
            
            if valid_data_count == 0:
                return None, "未找到有效数据"
            
            self.log(f"  成功提取 {valid_data_count} 行数据")
            return data_lines, "成功"
            
        except Exception as e:
            return None, f"读取文件时出错: {str(e)}"
    
    def is_process_running(self, process_name):
        """检查进程是否在运行"""
        for proc in psutil.process_iter(['name']):
            if proc.info['name'] and process_name.lower() in proc.info['name'].lower():
                return True
        return False
    
    def close_casaxps_process(self):
        """关闭CasaXPS进程"""
        try:
            for proc in psutil.process_iter(['name', 'pid']):
                if proc.info['name'] and 'casaxps' in proc.info['name'].lower():
                    proc.terminate()
                    self.log("🔴 已关闭CasaXPS进程")
                    time.sleep(1)
                    break
        except Exception as e:
            self.log(f"⚠️ 关闭CasaXPS时出错: {e}")
    
    def split_path_into_parts(self, path):
        """将路径分解为可导航的部分"""
        try:
            # 标准化路径
            path = os.path.normpath(path)
            
            # 分解路径
            parts = []
            current_path = path
            
            while True:
                # 获取当前路径和父路径
                current_dir = os.path.basename(current_path)
                parent_path = os.path.dirname(current_path)
                
                # 如果当前目录不为空，添加到列表
                if current_dir:
                    parts.insert(0, current_dir)
                
                # 如果到达根目录，添加驱动器号（Windows）或根目录（Linux/Mac）
                if parent_path == current_path or not parent_path:
                    # 添加驱动器号（如C:）或根目录
                    if os.name == 'nt':  # Windows
                        drive = path.split(':')[0] + ':' if ':' in path else 'C:'
                        parts.insert(0, drive)
                    else:  # Linux/Mac
                        parts.insert(0, '/')
                    break
                    
                current_path = parent_path
            
            return parts
            
        except Exception as e:
            self.log(f"  ❌ 路径分解失败: {e}")
            # 返回默认路径
            if os.name == 'nt':
                return ['C:', 'Users', 'Public']
            else:
                return ['/', 'home']
    
    def navigate_to_file_first_time(self, dat_file):
        """第一个文件：完整导航到目标文件"""
        try:
            file_name = os.path.basename(dat_file)
            file_dir = os.path.dirname(dat_file)
            
            self.log(f"  🗺️ 完整导航到: {file_dir}")
            self.log(f"  📄 目标文件: {file_name}")
            
            # 步骤1: 多次按Alt+↑回到根目录
            self.log("  ⬆️ 按10次Alt+↑回到根目录...")
            for i in range(10):  # 按10次，确保回到根目录
                pyautogui.hotkey('alt', 'up')
                time.sleep(0.2)
            
            time.sleep(1)
            
            # 步骤2: 按一次Alt+←
            self.log("  ⬅️ 按一次Alt+←...")
            pyautogui.hotkey('alt', 'left')
            time.sleep(0.5)
            
            # 步骤3: 分解路径并逐级导航
            path_parts = self.split_path_into_parts(file_dir)
            self.log(f"  📂 路径分解: {' -> '.join(path_parts)}")
            
            # 逐级进入文件夹
            for part in path_parts:
                if part:  # 跳过空的部分
                    self.log(f"  📁 进入文件夹: {part}")
                    pyautogui.write(part)
                    time.sleep(0.5)
                    pyautogui.press('enter')
                    time.sleep(0.5)
            
            # 步骤4: 输入文件名并打开
            self.log(f"  📄 输入文件名: {file_name}")
            pyautogui.write(file_name)
            time.sleep(0.5)
            pyautogui.press('enter')
            time.sleep(1)  # 等待文件打开和处理
            
            return True
            
        except Exception as e:
            self.log(f"  ❌ 完整导航失败: {e}")
            return False
    
    def open_file_quickly(self, dat_file):
        """后续文件：快速打开（假设已经在正确的文件夹）"""
        try:
            file_name = os.path.basename(dat_file)
            
            self.log(f"  ⚡ 快速打开: {file_name}")
            
            # 直接输入文件名
            pyautogui.write(file_name)
            time.sleep(0.5)
            pyautogui.press('enter')
            time.sleep(0.5)  # 等待文件打开和处理
            
            return True
            
        except Exception as e:
            self.log(f"  ❌ 快速打开失败: {e}")
            return False
    
    def automate_casaxps_smart_navigation(self, dat_files):
        """智能导航方法：使用Alt+↑回到根目录，然后逐级导航"""
        try:
            self.log("\n🧭 使用智能导航方法处理CasaXPS...")
            
            # 检查CasaXPS路径
            if not os.path.exists(self.casaxps_path):
                self.log("❌ CasaXPS路径不存在")
                return False
            
            # 关闭可能正在运行的CasaXPS实例
            if self.is_process_running('casaxps'):
                self.log("⚠️ 检测到CasaXPS正在运行，尝试关闭...")
                self.close_casaxps_process()
            
            # 启动CasaXPS
            self.log("🟢 启动CasaXPS...")
            process = subprocess.Popen([self.casaxps_path])
            time.sleep(1)  # 等待软件完全启动
            
            # 激活CasaXPS窗口
            time.sleep(0.5)
            pyautogui.click(500, 300)
            time.sleep(0.5)
            
            # 处理每个dat文件
            success_count = 0
            first_file_processed = False
            
            for i, dat_file in enumerate(dat_files):
                self.log(f"📊 处理文件 [{i+1}/{len(dat_files)}]: {os.path.basename(dat_file)}")
                
                try:
                    # 激活CasaXPS窗口
                    pyautogui.click(500, 300)
                    time.sleep(0.5)
                    
                    # 点击Convert按钮
                    x, y = self.convert_button_pos
                    self.log(f"  🎯 点击Convert按钮: 坐标({x}, {y})")
                    pyautogui.click(x, y)
                    time.sleep(0.5)  # 等待Convert对话框打开
                    
                    if not first_file_processed:
                        # 第一个文件：需要完整导航
                        if self.navigate_to_file_first_time(dat_file):
                            success_count += 1
                            first_file_processed = True
                            self.log(f"  ✅ 第一个文件导航成功: {os.path.basename(dat_file)}")
                        else:
                            self.log(f"  ❌ 第一个文件导航失败: {os.path.basename(dat_file)}")
                    else:
                        # 后续文件：直接输入文件名
                        if self.open_file_quickly(dat_file):
                            success_count += 1
                            self.log(f"  ✅ 快速打开成功: {os.path.basename(dat_file)}")
                        else:
                            self.log(f"  ❌ 快速打开失败: {os.path.basename(dat_file)}")
                    
                except Exception as e:
                    self.log(f"  ❌ 处理失败: {os.path.basename(dat_file)} - {e}")
                    continue
            
            self.log(f"✅ 智能导航处理完成: {success_count}/{len(dat_files)} 个文件成功")
            
            # 关闭CasaXPS
            if self.close_casaxps.get():
                self.close_casaxps_gracefully()
            
            return success_count > 0
            
        except Exception as e:
            self.log(f"❌ 智能导航失败: {e}")
            # 尝试关闭进程
            try:
                if 'process' in locals():
                    process.terminate()
            except:
                pass
            return False
    
    def close_casaxps_gracefully(self):
        """优雅关闭CasaXPS"""
        try:
            self.log("🔴 关闭CasaXPS...")
            
            # 尝试正常关闭
            pyautogui.hotkey('alt', 'f4')
            time.sleep(1)
            
            # 处理可能的保存提示
            try:
                # 如果有保存提示，选择不保存
                pyautogui.press('n')  # 按N选择不保存
                time.sleep(1)
            except:
                pass
            
            # 如果进程还在运行，强制终止
            if self.is_process_running('casaxps'):
                self.close_casaxps_process()
            
            self.log("✅ CasaXPS已关闭")
            
        except Exception as e:
            self.log(f"⚠️ 关闭CasaXPS时出错: {e}")
    
    def process_files(self):
        """处理文件夹中的所有文件"""
        folder_path = self.folder_path.get()
        if not folder_path or not os.path.exists(folder_path):
            messagebox.showerror("错误", "请选择有效的文件夹路径")
            return
        
        # 获取所有文件
        files = self.get_all_files(folder_path)
        
        if not files:
            messagebox.showwarning("警告", "在选择的文件夹中未找到符合条件的文件")
            return
        
        self.log(f"🔍 找到 {len(files)} 个文件，开始处理...")
        total_steps = len(files) + (len(files) if self.auto_process_casaxps.get() else 0)
        self.progress['maximum'] = total_steps
        self.progress['value'] = 0
        
        success_count = 0
        error_count = 0
        skipped_count = 0
        dat_files = []  # 保存生成的dat文件路径
        
        # 第一步：提取数据并生成dat文件
        for i, file_path in enumerate(files):
            filename = os.path.basename(file_path)
            file_ext = os.path.splitext(filename)[1]
            self.log(f"\n📄 处理文件 [{i+1}/{len(files)}]: {filename} (扩展名: {file_ext})")
            
            # 提取数据
            data_lines, message = self.parse_xps_file(file_path)
            
            if data_lines is not None:
                # 创建新的.dat文件
                base_name = os.path.splitext(filename)[0]
                output_path = os.path.join(folder_path, f"{base_name}.dat")
                
                try:
                    with open(output_path, 'w', encoding='utf-8') as f:
                        # 根据用户选择决定是否包含标题行
                        if self.include_header.get():
                            f.write("# Binding Energy(eV)\tIntensity(cps)\n")
                        # 只写入数据行
                        for line in data_lines:
                            f.write(line + '\n')
                    
                    header_status = "含标题" if self.include_header.get() else "无标题"
                    self.log(f"   ✅ 成功创建: {base_name}.dat ({header_status})")
                    self.log(f"   📊 数据量: {len(data_lines)} 行")
                    success_count += 1
                    dat_files.append(output_path)
                except Exception as e:
                    self.log(f"   ❌ 创建文件失败: {str(e)}")
                    error_count += 1
            else:
                if "跳过" in message:
                    self.log(f"   ⚠️ {message}")
                    skipped_count += 1
                else:
                    self.log(f"   ❌ 提取失败: {message}")
                    error_count += 1
            
            # 更新进度
            self.progress['value'] = i + 1
            self.progress_label['text'] = f"数据提取: {i+1}/{len(files)} - 成功: {success_count}, 失败: {error_count}, 跳过: {skipped_count}"
            self.root.update_idletasks()
        
        # 第二步：使用智能导航方法处理CasaXPS
        if self.auto_process_casaxps.get() and dat_files:
            self.log(f"\n🔄 开始CasaXPS智能导航处理 {len(dat_files)} 个dat文件...")
            
            # 显示确认信息
            confirm_message = (
                f"即将使用智能导航方法处理 {len(dat_files)} 个dat文件。\n\n"
                f"导航流程：\n"
                f"1. 第一个文件：按10次Alt+↑回到根目录，然后按一次Alt+←，再逐级导航到目标文件夹\n"
                f"2. 后续文件：直接输入文件名（CasaXPS会记住文件夹位置）\n\n"
                f"重要提示：\n"
                f"• 请确保CasaXPS窗口可见\n"
                f"• 不要操作鼠标键盘\n"
                f"• 处理需要较长时间，请耐心等待\n\n"
                f"是否继续？"
            )
            
            confirm = messagebox.askyesno("CasaXPS智能导航处理", confirm_message)
            
            if confirm:
                # 在新线程中运行智能导航
                casa_thread = threading.Thread(target=self.automate_casaxps_smart_navigation, args=(dat_files,))
                casa_thread.daemon = True
                casa_thread.start()
                
                # 显示处理进度
                casa_start_time = time.time()
                timeout = 600  # 10分钟超时
                
                while casa_thread.is_alive():
                    elapsed = time.time() - casa_start_time
                    if elapsed > timeout:
                        self.log("⏰ CasaXPS处理超时，强制结束")
                        break
                    
                    # 更新进度显示
                    progress_value = len(files) + min(int(elapsed/10), len(dat_files))
                    self.progress['value'] = progress_value
                    self.progress_label['text'] = f"CasaXPS智能导航中... 已用时: {int(elapsed)}秒"
                    self.root.update_idletasks()
                    
                    time.sleep(1)
                
                # 等待线程结束
                casa_thread.join(timeout=1)
        
        # 显示最终结果
        result_message = f"处理完成！\n\n数据提取结果:\n成功: {success_count} 个文件\n失败: {error_count} 个文件\n跳过: {skipped_count} 个文件"
        
        if self.auto_process_casaxps.get() and dat_files:
            result_message += f"\n\nCasaXPS处理:\n已处理: {len(dat_files)} 个dat文件"
        
        result_message += f"\n\n输出文件保存在: {folder_path}"
        
        messagebox.showinfo("处理完成", result_message)
        
        self.log(f"\n🎉 所有处理完成！")
        self.log(f"✅ 数据提取成功: {success_count} 个文件")
        self.log(f"❌ 数据提取失败: {error_count} 个文件")
        self.log(f"⚠️  数据提取跳过: {skipped_count} 个文件")
        
        if self.auto_process_casaxps.get() and dat_files:
            self.log(f"🧭 CasaXPS智能导航处理: {len(dat_files)} 个dat文件")
        
        # 重置进度条
        self.progress['value'] = 0
        self.progress_label['text'] = "等待开始..."
    
    def start_processing(self):
        """开始处理文件"""
        if not self.folder_path.get():
            messagebox.showerror("错误", "请先选择文件夹")
            return
        
        # 检查是否需要安装额外库
        try:
            import pyautogui
            import psutil
        except ImportError as e:
            self.log(f"❌ 缺少必要的库: {e}")
            install_confirm = messagebox.askyesno(
                "安装依赖库",
                "需要安装pyautogui和psutil库来自动化CasaXPS。\n是否立即安装？"
            )
            if install_confirm:
                self.install_required_packages()
            return
        
        # 更新Convert按钮坐标
        try:
            x = int(self.convert_x_var.get())
            y = int(self.convert_y_var.get())
            self.convert_button_pos = (x, y)
            self.log(f"🎯 使用Convert按钮坐标: ({x}, {y})")
        except ValueError:
            messagebox.showerror("错误", "请输入有效的坐标数字")
            return
        
        # 在新线程中处理文件
        thread = threading.Thread(target=self.process_files)
        thread.daemon = True
        thread.start()
    
    def install_required_packages(self):
        """安装必要的Python包"""
        try:
            import subprocess
            import sys
            
            self.log("📦 开始安装必要的库...")
            
            # 安装pyautogui
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pyautogui"])
            self.log("✅ pyautogui安装完成")
            
            # 安装psutil
            subprocess.check_call([sys.executable, "-m", "pip", "install", "psutil"])
            self.log("✅ psutil安装完成")
            
            # 重新导入库
            global pyautogui, psutil
            import pyautogui
            import psutil
            
            self.log("✅ 所有必要库安装完成，请重新启动程序")
            messagebox.showinfo("安装完成", "必要的库已安装完成，请重新启动程序。")
            
        except Exception as e:
            self.log(f"❌ 安装失败: {e}")
            messagebox.showerror("安装错误", f"安装必要的库时出错: {e}")

def main():
    root = tk.Tk()
    app = XPSDataExtractor(root)
    root.mainloop()

if __name__ == "__main__":
    main()