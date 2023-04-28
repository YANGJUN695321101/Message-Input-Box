import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QTextEdit, QComboBox
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
from PyQt5.QtCore import QByteArray, QBuffer
import openai
import asyncio
from PyQt5.QtCore import QThreadPool, QRunnable, pyqtSlot
from PyQt5.QtCore import QMetaObject
from PyQt5.QtCore import QThreadPool, QRunnable, pyqtSlot, Q_ARG
from openai import ChatCompletion
import aiohttp


api_key=openai.api_key
openai.api_key = "s"




class GenerateReplyTask(QRunnable):
    def __init__(self, message, chat_window):
        super().__init__()
        self.message = message
        self.chat_window = chat_window

    @pyqtSlot()
    @pyqtSlot()
    def run(self):
        try:
            print("Starting GenerateReplyTask...")
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            response = loop.run_until_complete(self.chat_window.async_generate_reply(self.message))
            print(f"Generated response: {response}")
            QMetaObject.invokeMethod(
            self.chat_window,
            "display_message",
            Qt.QueuedConnection,
            pyqtSlot(str, str, str, bool)(response),
        )

        except Exception as e:
                print(f"Error in GenerateReplyTask: {e}")
                self.chat_window.display_message('GPT-3.5-turbo', '抱歉，无法生成回复。', 'D:\\DESK\\GPT-3.5\\ABC.png', is_user=False)


class ChatWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setGeometry(100, 100, 800, 600)
        self.setWindowTitle('微信聊天')

        self.chat_widget = QWidget()
        self.setCentralWidget(self.chat_widget)

        self.main_layout = QVBoxLayout()
        self.chat_widget.setLayout(self.main_layout)

        self.chat_history = QTextEdit()
        self.chat_history.setReadOnly(True)
        self.main_layout.addWidget(self.chat_history)

        input_layout = QHBoxLayout()

        self.input_text = QLineEdit()
        input_layout.addWidget(self.input_text)

        send_button = QLabel('发送')
        send_button.mousePressEvent = lambda event: self.send_message(event)
        input_layout.addWidget(send_button)

        self.main_layout.addLayout(input_layout)
        self.show()

    def send_message(self, event):
        try:
            message = self.input_text.text()
            if message:
                self.display_message('我', message, 'D:\\DESK\\GPT-3.5\\ABC.png', is_user=True)
                self.input_text.clear()
                self.generate_reply(message)
        except Exception as e:
            print(f"Error: {e}")

    def generate_reply(self, message):
        task = GenerateReplyTask(message, self)
        QThreadPool.globalInstance().start(task)

    async def async_generate_reply(self, message):
        try:
            async with aiohttp.ClientSession() as session:
                response = await session.post(
                    "https://api.openai.com/v1/engines/gpt-3.5-turbo/completions",
                    headers={"Authorization": f"Bearer {api_key}"},
                    json={
                        "messages": [
                            {"role": "system", "content": "You are a helpful assistant."},
                            {"role": "user", "content": message}
                        ],
                        "max_tokens": 100,
                        "n": 1,
                        "temperature": 0.8,
                    },
                )
                response_json = await response.json()
            return response_json["choices"][0]["message"]["content"]
        except Exception as e:
            print(f"Error in async_generate_reply: {e}")
            return "抱歉，无法生成回复。"




    def display_message(self, username, message, avatar_path, is_user=True, *args):
        pixmap = QPixmap(avatar_path)
        pixmap = pixmap.scaled(40, 40, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        buffer = QBuffer(QByteArray())
        buffer.open(QBuffer.WriteOnly)
        pixmap.toImage().save(buffer, 'PNG')
        base64_data = buffer.data().toBase64().data().decode()
        avatar_margin = "margin-right: 20px;" if is_user else "margin-left: 20px;"
        avatar_html = f'''
        <div style="display: inline-block; vertical-align: top; {avatar_margin} margin-top: 5px;"> 
            <img src="data:image/png;base64,{base64_data}" width="{pixmap.width()}" height="{pixmap.height()}" style="border-radius: 20px; border: none;"/>
        </div>
        '''

        bubble_color = '#e6e6e6' if is_user else '#66ccff'
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
        self.chat_history.ensureCursorVisible()  # 修改此行

        
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ChatWindow()
    sys.exit(app.exec_())
