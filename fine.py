import tkinter as tk
from tkinter import scrolledtext, ttk
import json
import os
import re
import sys
import time
from openai import OpenAI
import pickle as pkl

class TraditionalChineseMedicineGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("本草纲目中医诊疗助手")
        self.root.geometry("900x700")
        self.root.configure(bg="#f0f5f9")
        
        # 初始化OpenAI客户端
        self.init_openai_client()
        
        # 加载本草纲目数据库
        self.load_bencao_database()
        
        # 创建UI组件
        self.create_widgets()
        
    def init_openai_client(self):
        API_KEY = r"sk-Oer4C1HqYxkYdgRWjOQGfY2EmBYwdwU618nl8Hhzj9bQW6c4"  # 请替换为实际API密钥
        self.client = OpenAIClient(
            base_url=r"http://34.13.73.248:3888/v1",
            api_key=API_KEY
        )
    
    def load_bencao_database(self):
        try:
            with open(r'resource/BenCaoGangMu.pkl', 'rb') as fr:
                self.DB = pkl.load(fr)
            self.update_status("本草纲目数据库加载成功")
        except Exception as e:
            self.update_status(f"数据库加载失败: {str(e)}")
            self.DB = None
    
    def create_widgets(self):
        # 顶部标题
        title_label = tk.Label(
            self.root, 
            text="本草纲目中医智能诊疗系统", 
            font=("SimHei", 16, "bold"),
            bg="#f0f5f9",
            fg="#1e3a8a"
        )
        title_label.pack(pady=10)
        
        # 输入区域
        input_frame = tk.Frame(self.root, bg="#f0f5f9")
        input_frame.pack(fill=tk.X, padx=20, pady=5)
        
        tk.Label(
            input_frame, 
            text="请输入您的症状：", 
            font=("SimHei", 12),
            bg="#f0f5f9"
        ).pack(anchor=tk.W)
        
        self.symptom_input = scrolledtext.ScrolledText(
            input_frame, 
            height=3, 
            font=("SimHei", 12),
            wrap=tk.WORD,
            bd=2,
            relief=tk.SUNKEN
        )
        self.symptom_input.pack(fill=tk.X, pady=5)
        
        # 按钮区域
        button_frame = tk.Frame(self.root, bg="#f0f5f9")
        button_frame.pack(pady=10)
        
        self.analyze_btn = tk.Button(
            button_frame, 
            text="开始诊疗分析", 
            command=self.start_analysis,
            font=("SimHei", 12),
            bg="#3b82f6",
            fg="white",
            padx=15,
            pady=5,
            relief=tk.RAISED
        )
        self.analyze_btn.pack(side=tk.LEFT, padx=10)
        
        self.clear_btn = tk.Button(
            button_frame, 
            text="清空内容", 
            command=self.clear_all,
            font=("SimHei", 12),
            bg="#64748b",
            fg="white",
            padx=15,
            pady=5,
            relief=tk.RAISED
        )
        self.clear_btn.pack(side=tk.LEFT, padx=10)
        
        # 状态标签
        self.status_var = tk.StringVar()
        self.status_var.set("请输入症状并点击开始诊疗分析")
        status_label = tk.Label(
            self.root, 
            textvariable=self.status_var, 
            font=("SimHei", 10),
            bg="#f0f5f9",
            fg="#dc2626",
            anchor=tk.W,
            wraplength=860
        )
        status_label.pack(fill=tk.X, padx=20)
        
        # 结果展示区域
        result_frame = tk.Frame(self.root, bg="#f0f5f9")
        result_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=5)
        
        # 创建标签页
        self.tab_control = ttk.Notebook(result_frame)
        
        self.tab_disease = ttk.Frame(self.tab_control)
        self.tab_herbs = ttk.Frame(self.tab_control)
        self.tab_prescription = ttk.Frame(self.tab_control)
        self.tab_review = ttk.Frame(self.tab_control)
        self.tab_final = ttk.Frame(self.tab_control)
        
        self.tab_control.add(self.tab_disease, text="疾病识别")
        self.tab_control.add(self.tab_herbs, text="药材检索")
        self.tab_control.add(self.tab_prescription, text="初步药方")
        self.tab_control.add(self.tab_review, text="药方审核")
        self.tab_control.add(self.tab_final, text="最终药方")
        
        # 为每个标签页添加文本区域
        self.create_tab_content(self.tab_disease, "disease")
        self.create_tab_content(self.tab_herbs, "herbs")
        self.create_tab_content(self.tab_prescription, "prescription")
        self.create_tab_content(self.tab_review, "review")
        self.create_tab_content(self.tab_final, "final")
        
        self.tab_control.pack(expand=1, fill="both")
    
    def create_tab_content(self, tab, name):
        text_widget = scrolledtext.ScrolledText(
            tab, 
            font=("SimHei", 11),
            wrap=tk.WORD,
            bd=2,
            relief=tk.SUNKEN
        )
        text_widget.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        setattr(self, f"{name}_text", text_widget)
    
    def update_status(self, message):
        self.status_var.set(message)
        self.root.update_idletasks()
    
    def clear_all(self):
        self.symptom_input.delete(1.0, tk.END)
        self.disease_text.delete(1.0, tk.END)
        self.herbs_text.delete(1.0, tk.END)
        self.prescription_text.delete(1.0, tk.END)
        self.review_text.delete(1.0, tk.END)
        self.final_text.delete(1.0, tk.END)
        self.update_status("请输入症状并点击开始诊疗分析")
    
    def start_analysis(self):
        requirement = self.symptom_input.get(1.0, tk.END).strip()
        if not requirement:
            self.update_status("请先输入症状描述")
            return
        
        if not self.DB:
            self.update_status("数据库未加载，无法进行分析")
            return
        
        try:
            self.update_status("正在进行疾病识别...")
            
            # 疾病识别
            possible_disease = self.disease_identify(requirement)
            self.disease_text.insert(tk.END, "识别出的可能疾病（古代名称）：\n")
            for i, disease in enumerate(possible_disease, 1):
                self.disease_text.insert(tk.END, f"{i}. {disease}\n")
            
            # 药材检索
            self.update_status("正在检索相关药材...")
            retrieved_item = self.retrieve_herb(possible_disease)
            if retrieved_item:
                for idx, (k, v) in enumerate(retrieved_item.items(), 1):
                    self.herbs_text.insert(tk.END, f"参考 {idx}：\n")
                    herb = v[0].split("·")[-1].strip()
                    self.herbs_text.insert(tk.END, f"药物：{herb}\n")
                    for idx2, e in enumerate(v[-1], 1):
                        self.herbs_text.insert(tk.END, f"使用方法或疗效 {idx2}：{e}\n")
                    self.herbs_text.insert(tk.END, "\n")
            else:
                self.herbs_text.insert(tk.END, "没有找到对应药草")
            
            # 生成初步药方
            self.update_status("正在生成初步药方...")
            task2 = requirement + "\n我从本草纲目搜集了一些相关的药物供你参考。请注意，我搜集回来的可能有噪声。请你仔细辨别。你开的方子，可以是一些已知的方剂。如果是新设计的，请包含每种药物的用量。\n"
            
            c = ''
            for idx, t in enumerate(retrieved_item.values()):
                c += f"参考 {idx + 1}\n"
                herb = t[0].split("·")[-1].strip()
                c += f"药物： {herb}\n"
                for idx2, e in enumerate(t[-1]):
                    f = f'使用方法或疗效{idx2+1}：{e}\n'
                    c += f
                c += '\n\n'
            
            task2 += c + '请一步一步思考'
            results = self.client.chat(task2, model="gpt-4o-mini")
            self.prescription_text.insert(tk.END, results)
            
            # 药方审核
            self.update_status("正在审核药方...")
            task3 = '你的任务是审核开出的药方是否合理。如不合理，请指出不合理的地方。\n\n诉求： ' + requirement + '\n\n之前的药方：' + results
            results2 = self.client.chat(task3, model="gpt-4o-mini")
            self.review_text.insert(tk.END, results2)
            
            # 生成最终药方
            self.update_status("正在生成最终药方...")
            message_dict = [
                {
                    "role": "system",
                    "content": "你是一个经验丰富的中医"
                },
                {
                    "role": "user",
                    "content": task2
                },
                {
                    "role": "assistant",
                    "content": results
                },
                {
                    "role": "user",
                    "content": results2 + '\n\n请再次开具药方'
                }  
            ]
            
            final_result = self.client.chat_msg(message_dict=message_dict, model="gpt-4o-mini")
            self.final_text.insert(tk.END, final_result)
            
            self.update_status("诊疗分析完成")
            
        except Exception as e:
            self.update_status(f"分析过程出错: {str(e)}")
            print(f"错误详情: {e}")
    
    def disease_identify(self, requirement):
        task1 = """
        我正在设计中药药方。请你帮我提取出下面需求中的疾病。
        我会参考本草纲目，因此你需要把疾病尽可能用古代医学典籍的方法表述出来。
        如果有多个可能的名字,返回多行
        不要标点
        最多返回五个
        每个疾病尽可能简短

        需求：
        """
        task1 += requirement
        possible_diseases_str = self.client.chat(task1)
        possible_disease = []
        for d in possible_diseases_str.split('\n'):
            if d.strip() != '':
                possible_disease.append(d.strip())
        return possible_disease[:5]  # 确保最多5个
    
    def retrieve_herb(self, possible_disease):
        retrieved_item = {}
        for disease in possible_disease:
            for k, values in self.DB.items():
                selected_treatment = []
                treatment = values.get(r'主治', None)
                if treatment is None:
                    continue
                for e in treatment:
                    if disease in e:
                        selected_treatment.append(e)
                if len(selected_treatment) > 0:
                    if k in retrieved_item:
                        continue
                    retrieved_item[k] = (values['题目'], selected_treatment)
        return retrieved_item


class OpenAIClient:
    def __init__(self, base_url: str, api_key: str):
        self.client = OpenAI(base_url=base_url, api_key=api_key)

    def chat_msg(self, message_dict, model="gpt-4o-mini"):
        completion = self.client.chat.completions.create(
            model=model,
            messages=message_dict,
        )
        return completion.choices[0].message.content

    def chat(self, message, model="gpt-4o-mini", system_prompt: str = "你是一个经验丰富的中医。"):
        if model == "openai/o1-mini":
            completion = self.client.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "user",
                        "content": message,
                    },
                ],
            )
        else:
            completion = self.client.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "system",
                        "content": system_prompt,
                    },
                    {
                        "role": "user",
                        "content": message,
                    },
                ],
            )
        
        return completion.choices[0].message.content


if __name__ == "__main__":
    root = tk.Tk()
    app = TraditionalChineseMedicineGUI(root)
    root.mainloop()