import openai
import os
import tkinter as tk
from tkinter import ttk, scrolledtext

openai.api_key = "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"

HISTORY_FILE = "chat_history.txt"

def load_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r") as f:
            return f.read()
    return ""

def save_history(history):
    with open(HISTORY_FILE, "w") as f:
        f.write(history)

def send_message(message, engine):
    history = load_history()
    response = openai.Completion.create(
        engine=engine,
        prompt=f"{history}用户: {message}\nAI:",
        temperature=0.7,
        max_tokens=1024,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )

    reply = response.choices[0].text.strip()
    history += f"用户: {message}\nAI: {reply}\n"
    save_history(history)
    return reply

def on_send_message(*args):
    message = message_entry.get()
    engine = engine_combobox.get()
    if message and engine:
        message_entry.delete(0, tk.END)
        conversation_text.insert(tk.END, f"你: {message}\n")
        reply = send_message(message, engine)
        conversation_text.insert(tk.END, f"GPT: {reply}\n")
        conversation_text.see(tk.END)
def on_new_conversation():
    def create_new_conversation():
        nonlocal new_conversation_window
        new_name = new_conversation_entry.get()
        if new_name:
            global HISTORY_FILE
            HISTORY_FILE = f"{new_name}.txt"
            conversation_text.delete(1.0, tk.END)
            new_conversation_window.destroy()

    new_conversation_window = tk.Toplevel(root)
    new_conversation_window.title("新对话")

    new_conversation_label = ttk.Label(new_conversation_window, text="输入新对话的名称：")
    new_conversation_label.grid(row=0, column=0, padx=10, pady=(10, 0), sticky=(tk.W, tk.E, tk.N, tk.S))

    new_conversation_entry = ttk.Entry(new_conversation_window, width=20)
    new_conversation_entry.grid(row=1, column=0, padx=10, pady=(5, 10), sticky=(tk.W, tk.E, tk.N, tk.S))
    new_conversation_entry.focus()

    new_conversation_button = ttk.Button(new_conversation_window, text="创建", command=create_new_conversation)
    new_conversation_button.grid(row=2, column=0, padx=10, pady=(0, 10), sticky=(tk.W, tk.E, tk.N, tk.S))

    new_conversation_window.bind("<Return>", lambda event: create_new_conversation())


       
        
        

root = tk.Tk()
root.title("AI机器人3聊天")

main_frame = ttk.Frame(root, padding="10")
main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

conversation_text = scrolledtext.ScrolledText(main_frame, wrap=tk.WORD, width=80, height=20)
conversation_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), columnspan=2)

message_entry = ttk.Entry(main_frame, width=60)
message_entry.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10), pady=(10, 0))
message_entry.focus()

send_button = ttk.Button(main_frame, text="发送", command=on_send_message)
send_button.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 0))

engine_list = ["AI机器人3-达芬奇版", "AI机器人3-居里版", "AI机器人3-巴贝奇版", "AI机器人3-埃达版"]

engine_combobox = ttk.Combobox(main_frame, values=engine_list, state="readonly")
engine_combobox.set(engine_list[0])
engine_combobox.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 0))

root.bind("<Return>", on_send_message)

root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)
main_frame.columnconfigure(0, weight=1)
main_frame.rowconfigure(0, weight=1)
new_conversation_button = ttk.Button(main_frame, text="新对话", command=on_new_conversation)
new_conversation_button.grid(row=2, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 0))

root.mainloop()
