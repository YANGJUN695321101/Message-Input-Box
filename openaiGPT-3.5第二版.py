import tkinter as tk
import json
from tkinter import ttk
import openai
from tkinter import StringVar
global template_combobox
template_combobox = None
global chat_template_combobox
chat_template_combobox = None
#设置OpenAI API密钥为 None
openai.api_key = None
#定义一个函数，用于加载提示模板
def load_prompt_templates(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        templates = json.load(file)
    return templates
#加载提示模板
prompt_templates = load_prompt_templates("D:\\DESK\\GPT-3.5\\ChatGPTPromptTemplate.json")
#定义一个函数，用于向GPT-3发送问题并获取回答
def ask_gpt3(question):
    if not openai.api_key:
        return "请先在设置中输入您的OpenAI API密钥。"

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": question},
        ]
    )
    return response.choices[0].message['content']
# 定义一个函数，用于将问题提交给GPT-3，并将问题和回答显示在聊天框中
def submit_question(chat_text, entry):
    question = entry.get()
    if question.strip():
        answer = ask_gpt3(question)
        chat_text.insert(tk.END, f"您: {question}\n")
        chat_text.insert(tk.END, f"GPT-3.5-turbo助手: {answer}\n")
        chat_text.yview(tk.END)
        entry.delete(0, tk.END)
#定义一个函数，用于保存用户输入的API密钥
def save_key():
    key = key_entry.get()
    if key.strip():
        openai.api_key = key
#定义一个函数，用于创建聊天页面
def create_chat_page(notebook):
    template_search_var = StringVar()
    chat_frame = tk.Frame(notebook)
    notebook.add(chat_frame, text=f"聊天 {notebook.index('end') + 1}")
    chat_text = tk.Text(chat_frame, wrap=tk.WORD)
    chat_text.grid(row=0, column=0, sticky=tk.NSEW)
    scrollbar = tk.Scrollbar(chat_frame)
    scrollbar.config(command=chat_text.yview)
    chat_text.config(yscrollcommand=scrollbar.set)
    scrollbar.grid(row=0, column=1, sticky=tk.NS)
    entry_frame = tk.Frame(chat_frame)
    entry_frame.grid(row=1, column=0, columnspan=2, sticky=tk.EW)
    def insert_template():
        selected_template_name = template_combobox.get()
        for template in prompt_templates:
            if template['key'] == selected_template_name:
                entry.delete(0, tk.END)
                entry.insert(0, template['value'].format(query=""))
                break
    global template_combobox
    template_combobox = AutocompleteCombobox(entry_frame, values=[template['key'] for template in prompt_templates])
    template_combobox.pack(side=tk.LEFT, padx=5)
    template_combobox["values"] = [template["key"] for template in prompt_templates]
    template_combobox.set(template_combobox["values"][0])

    template_button = tk.Button(entry_frame, text="插入指令", command=insert_template)
    template_button.pack(side=tk.RIGHT, padx=5)

    entry = tk.Entry(entry_frame, width=50)
    entry.pack(side=tk.LEFT, padx=5, pady=10, fill=tk.X, expand=True)
    submit_button = tk.Button(entry_frame, text="发送", command=lambda: submit_question(chat_text, entry))
    submit_button.pack(side=tk.RIGHT, padx=5, pady=10)
    chat_frame.columnconfigure(0, weight=1)
   
    chat_frame.rowconfigure(0, weight=1)
    entry_frame.columnconfigure(0, weight=1)
#创建并设置Tkinter根窗口
root = tk.Tk()
root.title("GPT-3.5-turbo助手")
# 设置UI样式
style = ttk.Style()
style.configure('TNotebook', tabposition='nw')
style.configure('TNotebook.Tab', padding=[5, 5], font=('Helvetica', 10, 'bold'))
style.configure('TButton', font=('Helvetica', 10, 'bold'))
style.configure('TLabel', font=('Helvetica', 10, 'bold'))
style.configure('TEntry', font=('Helvetica', 10))
#定义一个自动完成组合框类
class AutocompleteCombobox(ttk.Combobox):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._completion_list = kwargs["values"]
        self.set_completion_list(self._completion_list)
        self.bind("<KeyRelease>", self.handle_key_release)

    def set_completion_list(self, completion_list):
        self._completion_list = sorted(completion_list, key=str.lower)

    def handle_key_release(self, event):
        value = self.get()
        if value == "":
            self["values"] = self._completion_list
        else:
            search = [item for item in self._completion_list if item.lower().startswith(value.lower())]
            if search:  # 只有当搜索结果非空时才更改组合框的值
                self["values"] = search

        self.event_generate("<<ComboboxSelected>>")
       
#创建并添加一个notebook小部件
notebook = ttk.Notebook(root)
notebook.pack(padx=20, pady=20, fill=tk.BOTH, expand=True)
#创建并添加一个设置页面
settings_frame = tk.Frame(notebook)
notebook.add(settings_frame, text="设置")

key_label = tk.Label(settings_frame, text="请输入您的OpenAI API密钥：", font=("Helvetica", 12))
key_label.grid(row=0, column=0, pady=10, sticky=tk.W)

key_entry = tk.Entry(settings_frame, width=50, show="*")
key_entry.grid(row=0, column=1, pady=10, sticky=tk.W)

save_button = tk.Button(settings_frame, text="保存", command=save_key)
save_button.grid(row=0, column=2, padx=10, pady=10, sticky=tk.W)
settings_frame.columnconfigure(0, weight=1)
settings_frame.columnconfigure(1, weight=1)
settings_frame.columnconfigure(2, weight=1)
settings_frame.rowconfigure(2, weight=1)
#定义函数用于保存、备份和恢复提示模板
def save_template():
    with open("D:\\DESK\\GPT-3.5\\ChatGPTPromptTemplate.json", "w", encoding="utf-8") as file:
        json.dump(prompt_templates, file)

def backup_template():
    with open("D:\\DESK\\GPT-3.5\\ChatGPTPromptTemplate_backup.json", "w", encoding="utf-8") as file:
        json.dump(prompt_templates, file)

def restore_template():
    global prompt_templates
    with open("D:\\DESK\\GPT-3.5\\ChatGPTPromptTemplate_backup.json", "r", encoding="utf-8") as file:
        prompt_templates = json.load(file)
    template_combobox["values"] = [template['key'] for template in prompt_templates]
    template_edit_combobox["values"] = [template['key'] for template in prompt_templates]

# 定义一个函数，用于创建新的提示模板
def create_new_template():
    
    global prompt_templates
    global template_combobox
    new_key = "小红书文案编辑师"
    new_value = (
        "我想让你充当小红书文案编辑师，提供有小红书的营销文案。"
        "你应该只提供有关小红书的营销文案而不是解决其他问题。"
        
       
    "你提供的文案应该是有亲和力带有营销属性并且带有emoji表情的文案。”"
        "我的第一个要求是“写一份苹果耳机的营销文案”"
    )
    new_template = {"key": new_key, "value": new_value}
    prompt_templates.append(new_template)
   
    template_combobox["values"] = [template['key'] for template in prompt_templates]
    template_edit_combobox["values"] = [template['key'] for template in prompt_templates]  # 新增这一行代码

    template_edit_combobox.set(new_key)
    edit_template()





# 更改模板编辑文本框的大小
#在设置页面上创建并添加提示模板编辑文本框和相关按钮
template_edit_text = tk.Text(settings_frame, wrap=tk.WORD, width=60, height=10)
template_edit_text.grid(row=2, column=0, columnspan=3, pady=10, sticky=tk.NSEW)

save_template_button = tk.Button(settings_frame, text="保存指令", command=save_template)
save_template_button.grid(row=3, column=0, pady=10, sticky=tk.W)

backup_template_button = tk.Button(settings_frame, text="备份指令", command=backup_template)
backup_template_button.grid(row=3, column=2, pady=10, sticky=tk.W)

restore_template_button = tk.Button(settings_frame, text="恢复指令", command=restore_template)
restore_template_button.grid(row=3, column=1, pady=10, sticky=tk.W)
new_template_button = tk.Button(settings_frame, text="新建指令", command=create_new_template)
new_template_button.grid(row=1, column=2, pady=10, sticky=tk.W)


#创建并添加模板编辑组合框及其相关按钮
template_edit_combobox = AutocompleteCombobox(settings_frame, values=[template['key'] for template in prompt_templates])
template_edit_combobox.grid(row=1, column=0, pady=10, sticky=tk.W)


def edit_template():
    selected_template_name = template_edit_combobox.get()
    for template in prompt_templates:
        if template['key'] == selected_template_name:
            template_edit_text.delete(1.0, tk.END)
            template_edit_text.insert(tk.END, json.dumps(template, ensure_ascii=False, indent=4))


    
# 将编辑指令按钮移动到下拉选项框的右边同一水平高度
edit_template_button = tk.Button(settings_frame, text="编辑指令", command=edit_template)
edit_template_button.grid(row=1, column=1, pady=10, sticky=tk.W)


# 创建并添加新建聊天按钮
new_chat_button = tk.Button(root, text="新建聊天", command=lambda: create_chat_page(notebook))
new_chat_button.pack(pady=10, fill=tk.X)

# 创建初始聊天页面
create_chat_page(notebook)
#配置根窗口的列和行权重
root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)

# 启动Tkinter主循环
root.mainloop()

