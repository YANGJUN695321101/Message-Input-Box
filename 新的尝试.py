
import asyncio
import json
import sys

import httpx
import openai
import PyQt5
from openai import ChatCompletion
from PyQt5.QtCore import (QBuffer, QByteArray, QRunnable,
                          QSortFilterProxyModel, QStandardItemModel, Qt,
                          QThreadPool, pyqtSignal, pyqtSlot)
from PyQt5.QtGui import QPixmap, QStandardItem, QStandardItemModel
from PyQt5.QtWidgets import (QApplication, QComboBox, QCompleter, QFileDialog,
                             QHBoxLayout, QLabel, QLineEdit, QListView,
                             QMainWindow, QPushButton, QSplitter,
                             QStandardItemModel, QTabWidget, QTextEdit,
                             QVBoxLayout, QWidget)

print(PyQt5.__version__)
openai.api_key = ""

class GenerateReplyTask(QRunnable):
    def __init__(self, message, chat_window, api_key):
        super().__init__()
        self.message = message
        self.chat_window = chat_window
        self.api_key = api_key

    @pyqtSlot()
    def run(self):
        try:
            print("Starting GenerateReplyTask...")
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            response = loop.run_until_complete(self.chat_window.async_generate_reply(self.message))
            print(f"Generated response: {response}")
            self.chat_window.new_message_signal.emit("GPT-3.5-turbo", response, "D:\\DESK\\GPT-3.5\\DEF.png", False)
        except Exception as e:
            print(f"Error in GenerateReplyTask: {e}")
            self.chat_window.new_message_signal.emit('GPT-3.5-turbo', '抱歉，无法生成回复。', 'D:\\DESK\\GPT-3.5\\ABC.png', False)

class ChatWindow(QMainWindow):
    new_message_signal = pyqtSignal(str, str, str, bool)

    def __init__(self):
        super().__init__()
        self.setWindowTitle('微信聊天仿制版')
        self.setGeometry(100, 100, 800, 600)

        self.main_splitter = QSplitter(Qt.Horizontal)
        self.setCentralWidget(self.main_splitter)

        # 联系人列表
        self.contacts_list_view = QListView()
        self.contacts_model = QStandardItemModel(self)
        self.contacts_list_view.setModel(self.contacts_model)
        self.main_splitter.addWidget(self.contacts_list_view)

        # 聊天窗口
        self.chat_widget = QWidget()
        self.chat_layout = QVBoxLayout()
        self.chat_widget.setLayout(self.chat_layout)

        # 聊天记录
        self.chat_history = QTextEdit()
        self.chat_history.setReadOnly(True)
        self.chat_layout.addWidget(self.chat_history)

        # 创建下拉列表
        self.commands_combo = QComboBox()
        self.chat_layout.addWidget(self.commands_combo)

        # 输入框和发送按钮
        self.input_layout = QHBoxLayout()
        self.chat_layout.addLayout(self.input_layout)

        self.input_text = QLineEdit()
        self.input_layout.addWidget(self.input_text)

        self.send_button = QPushButton("发送")
        self.input_layout.addWidget(self.send_button)

        self.main_splitter.addWidget(self.chat_widget)

        # 创建选项卡部件
        self.tab_widget = QTabWidget()

        # 创建聊天选项卡
        self.chat_tab = QWidget()
        self.chat_tab_layout = QVBoxLayout()
        self.chat_tab.setLayout(self.chat_tab_layout)
        self.tab_widget.addTab(self.chat_tab, "聊天")

        # 将聊天记录和输入布局添加到聊天选项卡
        self.chat_tab_layout.addWidget(self.chat_history)
        self.chat_tab_layout.addLayout(self.input_layout)

        # 创建设置选项卡
        self.settings_tab = QWidget()
        self.settings_tab_layout = QVBoxLayout()
        self.settings_tab.setLayout(self.settings_tab_layout)
        self.tab_widget.addTab(self.settings_tab, "设置")

        # 在设置选项卡中创建API密钥输入框和保存按钮
        self.settings_top_layout = QHBoxLayout()
        self.settings_tab_layout.addLayout(self.settings_top_layout)

        # 创建API密钥输入框
        self.api_key_input = QLineEdit()
        self.api_key_input.setPlaceholderText("请输入KEY并保存")
        self.settings_top_layout.addWidget(self.api_key_input)
        self.api_key_input.setEchoMode(QLineEdit.Password)

        # 创建保存按钮
        save_button = QPushButton("保存")
        save_button.clicked.connect(self.save_api_key)
        self.settings_top_layout.addWidget(save_button)

        # 创建一个按钮和一个QLabel来显示用户头像
        self.user_avatar_label = QLabel()
        self.user_avatar_label.setFixedSize(100, 100)
        self.user_avatar_path = 'D:\\DESK\\GPT-3.5\\ABC.png'  # 将用户头像路径设置为默认值
        self.update_user_avatar(self.user_avatar_path)  # 显示用户头像
        self.settings_tab_layout.addWidget(self.user_avatar_label)

        # 创建选择头像按钮
        select_avatar_button = QPushButton("选择头像")
        select_avatar_button.clicked.connect(self.select_avatar)
        self.settings_tab_layout.addWidget(select_avatar_button)

        # 将选项卡部件添加到主布局中
        self.chat_layout.addWidget(self.tab_widget)

            # 创建指令编辑文本框
        self.commands_editor = QTextEdit()
        self.settings_tab_layout.addWidget(self.commands_editor)

        # 创建保存指令集按钮
        save_commands_button = QPushButton("保存指令集")
        save_commands_button.clicked.connect(self.save_commands)
        self.settings_tab_layout.addWidget(save_commands_button)

        # 创建新建指令集按钮
        new_commands_button = QPushButton("新建指令集")
        new_commands_button.clicked.connect(self.new_commands)
        self.settings_tab_layout.addWidget(new_commands_button)

        # 将下拉列表添加到布局中
        self.main_layout.insertWidget(1, self.commands_combo)

        # 设置窗口属性
        self.api_key = openai.api_key
        self.setGeometry(100, 100, 800, 600)
        self.setWindowTitle('微信聊天')

        self.show()



    def select_avatar(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        file_path, _ = QFileDialog.getOpenFileName(self, "选择头像", "", "Images (*.png *.xpm *.jpg);;All Files (*)", options=options)
        if file_path:
            self.user_avatar_path = file_path
            self.update_user_avatar(self.user_avatar_path)

    def update_user_avatar(self, avatar_path):
        pixmap = QPixmap(avatar_path)
        pixmap = pixmap.scaled(100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.user_avatar_label.setPixmap(pixmap)

        
    def add_commands(self):
        commands = [
            # 在此处添加您的指令
            "Command_1",
            "Command_2",
            "Command_3",
        ]

        for command in commands:
            item = QStandardItem(command)
            self.commands_model.appendRow(item)

    def new_commands(self):
        new_key = "小红书文案编辑师（这是给您的示例）"
        new_value = (
            "我想让你充当小红书文案编辑师，提供有小红书的营销文案。"
            "你应该只提供有关小红书的营销文案而不是解决其他问题。"
            
        
        "你提供的文案应该是有亲和力带有营销属性并且带有emoji表情的文案。”"
            "我的第一个要求是“写一份苹果耳机的营销文案”"
        )
        
      

        self.commands_editor.setPlainText(f'key: {new_key}\nvalue: {new_value}')  # 同步新建指令到指令编辑文本框
    def save_commands(self):
        # 从指令编辑器中获取当前的指令键和值
        editor_content = self.commands_editor.toPlainText().split('\n')
        current_key = editor_content[0].split(': ')[1].strip()
        current_value = editor_content[1].split(': ')[1].strip()

        # 更新 commands_data 列表中的指令值或添加新指令
        commands_data = []
        existing_keys = []
        for i in range(self.commands_combo.count()):
            item_data = self.commands_combo.itemData(i)
            key = item_data['key']
            existing_keys.append(key)
            value = item_data['value']
            if key == current_key:
                value = current_value
            command_obj = {'key': key, 'value': value}
            commands_data.append(command_obj)

        if current_key not in existing_keys:
            command_obj = {'key': current_key, 'value': current_value}
            commands_data.append(command_obj)
            self.commands_combo.addItem(current_key, command_obj)

        # 将更新后的 commands_data 列表保存到文件中
        try:
            with open('D:\\DESK\\GPT-3.5\\GPTPrompt11.json', 'w', encoding='utf-8') as f:
                json.dump(commands_data, f)
            print("指令集已保存。")
        except Exception as e:
            print(f"保存指令集时出错: {e}")



    def load_commands_from_file(self, file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                commands = json.load(f)

            for command in commands:
                self.commands_combo.addItem(command['key'], command)

            self.completer.setModel(self.commands_combo.model())
        except Exception as e:
            print(f"Error loading commands from file: {e}")

    def insert_command(self, index):
        if index > 0:
            command = self.commands_combo.itemData(index)
            key = command['key']
            value = command['value']
            self.input_text.setText(value)
            self.commands_editor.setPlainText(f'key: {key}\nvalue: {value}')  # 同步指令编辑文本框
            self.commands_combo.setCurrentIndex(index)



    def send_message(self, event):
        try:
            message = self.input_text.text()
            if message:
                self.display_message('我', message, self.user_avatar_path, True)

                self.input_text.clear()
                self.generate_reply(message)
        except Exception as e:
            print(f"Error: {e}")

    def generate_reply(self, message):
        task = GenerateReplyTask(message, self, api_key=openai.api_key)
        QThreadPool.globalInstance().start(task)
    def save_api_key(self):
            try:
                new_api_key = self.api_key_input.text()
                if new_api_key:
                    self.api_key = new_api_key
                    openai.api_key = new_api_key
                    print("API key updated.")
                else:
                    print("No API key entered.")
            except Exception as e:
                print(f"Error saving API key: {e}")


    async def async_generate_reply(self, message):
        try:
            print(f"Sending message to GPT-3.5-turbo: {message}")

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers={"Authorization": f"Bearer {self.api_key}"},
                    json={
                        "model": "gpt-3.5-turbo",
                        "messages": [
                            {"role": "system", "content": "You are a helpful assistant."},
                            {"role": "user", "content": message},
                        ],
                        "max_tokens": 1024,
                        "n": 1,
                        "stop": None,
                        "temperature": 0.8,
                    },
                )
            response_data = response.json()
            print(f"Response data: {response_data}")
            result = response_data["choices"][0]["message"]["content"].strip()
            print(f"Received response from GPT-3.5-turbo: {result}")
            return result
        except Exception as e:
            print(f"Error in async_generate_reply: {e}")
            return "抱歉，无法生成回复。"

    def display_message(self, username, message, avatar_path, is_user=True):
        pixmap = QPixmap(avatar_path)
        pixmap = pixmap.scaled(40, 40, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        buffer = QBuffer(QByteArray())
        buffer.open(QBuffer.WriteOnly)
        pixmap.toImage().save(buffer, 'PNG')
        base64_data = buffer.data().toBase64().data().decode()
        avatar_margin = "margin-right: 20px;" if not is_user else "margin-left: 20px;"
        avatar_html = f'''
        <div style="display: inline-block; vertical-align: top; {avatar_margin} margin-top: 5px;"> 
            <img src="data:image/png;base64,{base64_data}" width="{pixmap.width()}" height="{pixmap.height()}" style="border-radius: 20px; border: none;"/>
        </div>
        '''

        bubble_color = '#ec8d63' if is_user else '#406ae3'
        bubble_style = f'''
            <div style="
                display: inline-block;
                background-color: {bubble_color};
                border-radius: 10px;
                padding: 10px;
                max-width: 400px;
                word-wrap: break-word;
                margin-top: 10px;
            ">
                {message}
            </div>
        '''

        if is_user:
            html = f'''
                <div style="display: flex; flex-direction: row-reverse; margin-bottom: 20px;">
                    {avatar_html}
                    {bubble_style}
                </div>
            '''
        else:
            html = f'''
                <div style="display: flex; flex-direction: row; margin-bottom: 20px;">
                    {avatar_html}
                    {bubble_style}
                </div>
            '''
        self.chat_history.setHtml(self.chat_history.toHtml() + html)
        self.chat_history.ensureCursorVisible()




if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ChatWindow()
    sys.exit(app.exec_())  
