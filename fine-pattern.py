import tkinter as tk
from tkinter import scrolledtext, messagebox
from openai import OpenAI

class SimpleChineseMedicineAssistant:
    def __init__(self, root):
        self.root = root
        self.root.title("简易中医助手")
        self.root.geometry("700x600")
        self.root.configure(bg="#f0f5f9")
        
        # 初始化OpenAI客户端
        self.client = OpenAI(
            base_url="http://34.13.73.248:3888/v1",
            api_key="sk-Oer4C1HqYxkYdgRWjOQGfY2EmBYwdwU618nl8Hhzj9bQW6c4"
        )
        
        self.create_ui()
        
    def create_ui(self):
        # 标题
        tk.Label(
            self.root, 
            text="简易中医诊疗助手", 
            font=("SimHei", 14, "bold"),
            bg="#f0f5f9",
            fg="#1e3a8a"
        ).pack(pady=10)
        
        # 症状输入
        tk.Label(
            self.root, 
            text="请描述您的症状：", 
            font=("SimHei", 12),
            bg="#f0f5f9"
        ).pack(anchor=tk.W, padx=20)
        
        self.symptom_input = scrolledtext.ScrolledText(
            self.root, 
            height=4, 
            font=("SimHei", 12),
            wrap=tk.WORD
        )
        self.symptom_input.pack(fill=tk.X, padx=20, pady=5)
        
        # 按钮
        btn_frame = tk.Frame(self.root, bg="#f0f5f9")
        btn_frame.pack(pady=10)
        
        tk.Button(
            btn_frame, 
            text="获取诊疗建议", 
            command=self.get_advice,
            font=("SimHei", 12),
            bg="#3b82f6",
            fg="white",
            padx=15
        ).pack(side=tk.LEFT, padx=10)
        
        tk.Button(
            btn_frame, 
            text="清空", 
            command=self.clear_input,
            font=("SimHei", 12),
            bg="#64748b",
            fg="white",
            padx=15
        ).pack(side=tk.LEFT)
        
        # 结果展示
        tk.Label(
            self.root, 
            text="诊疗建议：", 
            font=("SimHei", 12),
            bg="#f0f5f9"
        ).pack(anchor=tk.W, padx=20, pady=5)
        
        self.result_text = scrolledtext.ScrolledText(
            self.root, 
            height=15, 
            font=("SimHei", 12),
            wrap=tk.WORD
        )
        self.result_text.pack(fill=tk.BOTH, expand=True, padx=20, pady=5)
        
    def clear_input(self):
        self.symptom_input.delete(1.0, tk.END)
        self.result_text.delete(1.0, tk.END)
        
    def get_advice(self):
        symptom = self.symptom_input.get(1.0, tk.END).strip()
        if not symptom:
            messagebox.showwarning("提示", "请输入症状描述")
            return
            
        try:
            # 显示加载状态
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(tk.END, "正在分析，请稍候...")
            self.root.update()
            
            # 调用AI生成建议
            prompt = f"""请根据以下症状，从中医角度给出简要诊疗建议：
症状：{symptom}
建议应包含：可能的证型、推荐药材（3-5味）、简单用法
注意：仅作参考，不替代专业医师诊断"""
            
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}]
            )
            
            # 显示结果
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(tk.END, response.choices[0].message.content)
            
        except Exception as e:
            messagebox.showerror("错误", f"处理失败：{str(e)}")
            self.result_text.delete(1.0, tk.END)

if __name__ == "__main__":
    root = tk.Tk()
    app = SimpleChineseMedicineAssistant(root)
    root.mainloop()