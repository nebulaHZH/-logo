import os
from PIL import Image
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import threading


class AddLogo:
    def __init__(self, images_path: str = 'images', logo_path: str = './logo.png', save_path: str = 'images_logo'):
        self.images_path = images_path
        self.logo_path = logo_path
        if not os.path.exists(save_path):
            paths = save_path.split('/')
            for i in range(len(paths)):
                path = '/'.join(paths[:i+1])
                if not os.path.exists(path):
                    os.mkdir(path)

        self.save_path = save_path
        # 获取原始图片列表
        self.images_list = self.get_images_path(self.images_path)
        # 获取logo图片
        self.logo = Image.open(self.logo_path)

    def process_all(self, progress_callback=None, cancel_flag=None):
        """处理所有图片的便捷方法"""
        results = []
        for i in range(len(self)):
            if cancel_flag and cancel_flag():
                return None  # 如果取消，返回None
                
            try:
                res = self[i]
                results.append(res)
                if progress_callback:
                    progress_callback(i + 1, len(self))  # 调用进度回调
            except Exception as e:
                print(e)
        return results

    def __len__(self):
        return len(self.images_list)

    def __getitem__(self, index):
        
        current_image_path = self.images_list[index]
        
        # 把第一个路径替换成保存的路径
        save_path = current_image_path.replace(self.images_path, self.save_path)
        # 去掉最后一个斜杠的文件名
        save_path = save_path.replace(save_path.split('/')[-1], '')
        if not os.path.exists(save_path):
            paths = save_path.split('/')
            for i in range(len(paths)):
                if paths[i].endswith('.jpg') or paths[i].endswith('.png'):
                    break
                
                path = '/'.join(paths[:i+1])
                if not os.path.exists(path):
                    os.mkdir(path)

        # 获取列表中的图片
        background = Image.open(current_image_path)
    
        # 将 logo 图片放在图片的左上角
        background.paste(self.logo, (2, 2), mask=self.logo)

        # 将图片保存到加images_logo 目录下
        save_path = current_image_path.replace(self.images_path, self.save_path)
        background.save(save_path) 

        return self.images_list[index]

    # 递归获取文件夹下所有的图片路径
    def get_images_path(self, path):
        images_list = []
        for (root, dirs, files) in os.walk(path):
            for file in files:
                if file.endswith(('.jpg', '.png', '.jpeg')):
                    path = os.path.join(root.replace('\\', '/'), file)
                    path = path.replace('\\', '/')
                    images_list.append(path)
        return images_list

class AddLogoGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("给图片添加logo")
        
        # 创建变量存储路径
        self.images_path = tk.StringVar(value='images/')
        self.logo_path = tk.StringVar(value='logo.png')
        self.save_path = tk.StringVar(value='images_logo/')
        self.processing = False  # 处理状态
        self.canceled = False  # 取消标志
        
        # 创建界面元素
        self.create_widgets()
    
    def create_widgets(self):
        # 输入/选择文件夹
        tk.Label(self.root, text="图片文件夹：").grid(row=0, column=0, padx=5, pady=5)
        tk.Entry(self.root, textvariable=self.images_path, width=50).grid(row=0, column=1, padx=5, pady=5)
        tk.Button(self.root, text="浏览", command=self.select_images_folder).grid(row=0, column=2, padx=5, pady=5)
        
        # 选择logo图片
        tk.Label(self.root, text="Logo图片：").grid(row=1, column=0, padx=5, pady=5)
        tk.Entry(self.root, textvariable=self.logo_path, width=50).grid(row=1, column=1, padx=5, pady=5)
        tk.Button(self.root, text="浏览", command=self.select_logo_file).grid(row=1, column=2, padx=5, pady=5)
        
        # 选择保存路径
        tk.Label(self.root, text="保存路径：").grid(row=2, column=0, padx=5, pady=5)
        tk.Entry(self.root, textvariable=self.save_path, width=50).grid(row=2, column=1, padx=5, pady=5)
        tk.Button(self.root, text="浏览", command=self.select_save_folder).grid(row=2, column=2, padx=5, pady=5)
        
        # 状态显示
        self.status_frame = tk.Frame(self.root)
        self.status_frame.grid(row=3, column=0, columnspan=3, padx=5, pady=5, sticky="we")
        
        self.status_label = tk.Label(self.status_frame, text="等待开始...")
        self.status_label.pack(side=tk.LEFT, expand=True, fill=tk.X)
        
        self.progress_bar = ttk.Progressbar(self.status_frame, mode='determinate')
        self.progress_bar.pack(side=tk.RIGHT, fill=tk.X, expand=True)
        
        # 按钮框架
        btn_frame = tk.Frame(self.root)
        btn_frame.grid(row=4, column=0, columnspan=3, pady=10)
        
        # 执行按钮
        self.process_button = tk.Button(btn_frame, text="添加Logo", command=self.start_processing)
        self.process_button.pack(side=tk.LEFT, padx=5)
        
        # 取消按钮（默认禁用）
        self.cancel_button = tk.Button(btn_frame, text="取消", command=self.cancel_processing, state=tk.DISABLED)
        self.cancel_button.pack(side=tk.LEFT, padx=5)
    
    def select_images_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.images_path.set(folder)
    
    def select_logo_file(self):
        file = filedialog.askopenfilename(filetypes=[("Image Files", "*.png *.jpg *.jpeg")])
        if file:
            self.logo_path.set(file)
    
    def select_save_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.save_path.set(folder)
    
    def start_processing(self):
        try:
            # 启动处理线程
            self.processing = True
            self.canceled = False
            self.update_status("正在处理中...", 0, 0)
            self.process_button.config(state=tk.DISABLED)
            self.cancel_button.config(state=tk.NORMAL)
            
            # 在新线程中处理
            thread = threading.Thread(target=self.process_images)
            thread.start()
        except Exception as e:
            messagebox.showerror("错误", f"启动处理时发生错误: {str(e)}")
    
    def cancel_processing(self):
        self.canceled = True
        self.update_status("取消处理...", 0, 0)
    
    def update_status(self, status, current, total):
        self.status_label.config(text=status)
        if total > 0:
            self.progress_bar['maximum'] = total
            self.progress_bar['value'] = current
        else:
            self.progress_bar['value'] = 0
    
    def process_images(self):
        try:
            # 创建AddLogo实例
            add_logo = AddLogo(
                images_path=self.images_path.get(),
                logo_path=self.logo_path.get(),
                save_path=self.save_path.get()
            )
            
            # 定义进度回调函数
            def update_progress(current, total):
                if self.processing:
                    self.root.after(100, lambda: self.update_status(f"正在处理图片 {current}/{total}", current, total))
            
            # 定义取消检查函数
            def check_canceled():
                return self.canceled
            
            # 处理所有图片
            processed = add_logo.process_all(update_progress, check_canceled)
            
            # 更新完成后的状态
            if self.canceled:
                self.root.after(100, lambda: messagebox.showinfo("已取消", "图片处理已取消"))
            elif processed is not None:
                self.root.after(100, lambda: messagebox.showinfo("完成", f"成功处理{len(processed)}张图片！"))
        except Exception as e:
            self.root.after(100, lambda: messagebox.showerror("错误", f"发生错误: {str(e)}"))
        finally:
            self.root.after(100, self.reset_ui)
    
    def reset_ui(self):
        self.processing = False
        self.process_button.config(state=tk.NORMAL)
        self.cancel_button.config(state=tk.DISABLED)
        self.update_status("等待开始...", 0, 0)