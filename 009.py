import os
import sys


from PyQt5.QtCore import QFileInfo, QRect, QRectF, QSize, Qt
from PyQt5.QtGui import (QBrush, QColor, QFont, QIcon, QMovie, QPainter,
                         QPainterPath, QPen, QPixmap)
from PyQt5.QtWidgets import (QAction, QApplication, QDialog, QFileDialog,
                             QHBoxLayout, QInputDialog, QLabel, QLineEdit,
                             QListView, QListWidget, QListWidgetItem,
                             QMainWindow, QMenu, QPushButton, QTextEdit,
                             QVBoxLayout, QWidget,QPlainTextEdit)


from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QPushButton
from PyQt5.QtWidgets import QApplication, QMainWindow
import sys
from MessageInputBox import MessageInputBox
class MessageInputBox(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        self.text_input = QPlainTextEdit(self)
        self.send_button = QPushButton("Send", self)

        layout.addWidget(self.text_input)
        layout.addWidget(self.send_button)

        self.setLayout(layout)
# 自定义圆角矩形 QLabel 子类
class RoundedRectLabel(QLabel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # 设置圆角矩形
        rect = QRect(0, 0, self.width(), self.height())
        rounded_rect = QPainterPath()
        rounded_rect.addRoundedRect(rect, 10, 10)  # 设置圆角半径

        # 用圆角矩形裁剪 QPainter
        painter.setClipPath(rounded_rect)

        # 绘制 QLabel 的原始内容
        super().paintEvent(event)


# 用户资料对话框类
class ProfileDialog(QDialog):
    def __init__(self, parent, contact_data, is_user=True):
        super().__init__(parent)
        
        self.setWindowTitle("用户资料" if is_user else "AI资料")
        self.contact_data = contact_data
        self.is_user = is_user

        layout = QVBoxLayout()

        self.avatar_label = QLabel(self)
        self.set_avatar(contact_data['user_avatar' if is_user else 'ai_avatar'])
        layout.addWidget(self.avatar_label)

        self.name_label = QLabel(contact_data['user_name' if is_user else 'ai_name'], self)
        layout.addWidget(self.name_label)

        change_avatar_button = QPushButton("更改头像", self)
        change_avatar_button.clicked.connect(self.change_avatar)
        layout.addWidget(change_avatar_button)

        change_name_button = QPushButton("更改名称", self)
        change_name_button.clicked.connect(self.change_name)
        layout.addWidget(change_name_button)

        self.setLayout(layout)

    # 设置头像
    def set_avatar(self, file_name, size=None):
        if size is None:
            size = QSize(100, 100)

        _, file_extension = os.path.splitext(file_name)
        if file_extension.lower() == ".gif":
            movie = QMovie(file_name)
            movie.setScaledSize(size)
            self.avatar_label.setMovie(movie)
            movie.start()
        else:
            self.avatar_label.setPixmap(QPixmap(file_name).scaled(size.width(), size.height(), Qt.KeepAspectRatio))

    # 更改名称
    def change_name(self):
        old_name = self.contact_data['user_name' if self.is_user else 'ai_name']
        new_name, ok_pressed = QInputDialog.getText(self, "更改名称", "请输入新的名称:", text=old_name)
        if ok_pressed and new_name != '':
            self.contact_data['user_name' if self.is_user else 'ai_name'] = new_name
            self.name_label.setText(new_name)

    # 更改头像
    def change_avatar(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        file_name, _ = QFileDialog.getOpenFileName(
            self, "选择头像", "", "Images (*.png *.xpm *.jpg *.bmp *.gif);;All Files (*)", options=options
        )
        if file_name:
            self.set_avatar(file_name)
            self.contact_data["user_avatar" if self.is_user else "ai_avatar"] = file_name

# 主窗口类
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setGeometry(100, 100, 800, 600)
        self.setWindowTitle('仿微信聊天')

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        main_layout = QHBoxLayout()
        self.central_widget.setLayout(main_layout)

        left_layout = QVBoxLayout()

        # 用户头像
        self.user_avatar = RoundedRectLabel()
        self.user_avatar.setPixmap(QPixmap("D:\\DESK\\GPT-3.5\\ABC.png").scaled(50, 50, Qt.KeepAspectRatio))
        self.user_avatar_movie = QMovie("D:\\DESK\\GPT-3.5\\ABC.gif")  # 更改为您的GIF路径
        self.user_avatar.setMovie(self.user_avatar_movie)
        self.user_avatar_movie.start()
        left_layout.addWidget(self.user_avatar)

        # 用户名称
        self.user_name_label = RoundedRectLabel()
        self.user_name_label.setText("用户")
        self.user_name_label.setAlignment(Qt.AlignCenter)
        self.user_name_label.setAutoFillBackground(True)
        palette = self.user_name_label.palette()
        palette.setColor(self.user_name_label.backgroundRole(), QColor(0, 0, 255, 128))
        self.user_name_label.setPalette(palette)
        left_layout.addWidget(self.user_name_label)

        # AI头像
        self.ai_avatar = RoundedRectLabel()
        self.ai_avatar.setPixmap(QPixmap("D:\\DESK\\GPT-3.5\\DEF.png").scaled(50, 50, Qt.KeepAspectRatio))
        self.ai_avatar_movie = QMovie("D:\\DESK\\GPT-3.5\\DEF.gif")  # 更改为您的GIF路径
        self.ai_avatar.setMovie(self.ai_avatar_movie)
        self.ai_avatar_movie.start()
        left_layout.addWidget(self.ai_avatar)


        # AI名称
        self.ai_name_label = RoundedRectLabel()
        self.ai_name_label.setText("AI")
        self.ai_name_label.setAlignment(Qt.AlignCenter)
        self.ai_name_label.setAutoFillBackground(True)
        palette = self.ai_name_label.palette()
        palette.setColor(self.ai_name_label.backgroundRole(), QColor(0, 0, 255, 128))
        self.ai_name_label.setPalette(palette)
        left_layout.addWidget(self.ai_name_label)
            # 用户头像和名称组合
        self.user_avatar_name_container = QWidget()
        user_avatar_name_layout = QHBoxLayout()
        self.user_avatar_name_container.setLayout(user_avatar_name_layout)
        user_avatar_name_layout.addWidget(self.user_avatar)
        user_avatar_name_layout.addWidget(self.user_name_label)
        left_layout.addWidget(self.user_avatar_name_container)

        # AI头像和名称组合
        self.ai_avatar_name_container = QWidget()
        ai_avatar_name_layout = QHBoxLayout()
        self.ai_avatar_name_container.setLayout(ai_avatar_name_layout)
        ai_avatar_name_layout.addWidget(self.ai_avatar)
        ai_avatar_name_layout.addWidget(self.ai_name_label)
        left_layout.addWidget(self.ai_avatar_name_container)
        # 更新 `update_avatars` 函数以使用 `RoundedRectLabel` 作为名称标签
        def update_avatars(self, item):
            current_contact = item.text()
            user_avatar_path = self.contact_data[current_contact]['user_avatar']
            ai_avatar_path = self.contact_data[current_contact]['ai_avatar']
            chat_history = self.contact_data[current_contact]['chat_history']
            user_name = self.contact_data[current_contact]['user_name']
            ai_name = self.contact_data[current_contact]['ai_name']
            contact_item = self.contact_list.item(self.contact_list.row(item))
            ai_avatar = QPixmap(ai_avatar_path)

            # 更新用户头像
            _, user_avatar_extension = os.path.splitext(user_avatar_path)
            if user_avatar_extension.lower() == ".gif":
                self.user_avatar_movie.setFileName(user_avatar_path)
                self.user_avatar_movie.start()
                self.user_avatar.setMovie(self.user_avatar_movie)
            else:
                self.user_avatar_movie.stop()
                self.user_avatar.setPixmap(QPixmap(user_avatar_path).scaled(50, 50, Qt.KeepAspectRatio))

            # 更新 AI 头像
            _, ai_avatar_extension = os.path.splitext(ai_avatar_path)
            if ai_avatar_extension.lower() == ".gif":
                self.ai_avatar_movie.setFileName(ai_avatar_path)
                self.ai_avatar_movie.setScaledSize(QSize(50, 50))
                self.ai_avatar_movie.start()
            else:
                self.ai_avatar_movie.stop()
                self.ai_avatar.setPixmap(QPixmap(ai_avatar_path).scaled(50, 50, Qt.KeepAspectRatio))

            # 更新联系人列表项图标
            if ai_avatar_extension.lower() == ".gif":
                contact_item.setIcon(QIcon(self.ai_avatar_movie.currentPixmap()))
            else:
                contact_item.setIcon(QIcon(ai_avatar.scaled(50, 50, Qt.KeepAspectRatio)))

            # 更新聊天历史记录和名称标签
            self.chat_history.setPlainText(chat_history)
            self.user_name_label.setText(user_name)
            self.ai_name_label.setText(ai_name)

        # 联系人列表
        self.contact_list = QListWidget()
        self.contact_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.contact_list.customContextMenuRequested.connect(self.contact_context_menu)
        left_layout.addWidget(self.contact_list)

        # 新建聊天卡按钮
        add_contact_button = QPushButton('新建聊天卡', self)
        add_contact_button.clicked.connect(self.add_contact)
        left_layout.addWidget(add_contact_button)

        # 联系人数据
        self.contact_data = {}
        for i in range(1, 11):
            contact_name = f"联系人 {i}"
            contact_item = QListWidgetItem(contact_name)
            contact_item.setIcon(QIcon(QPixmap("D:\\DESK\\GPT-3.5\\ABC.png")))
            self.contact_list.addItem(contact_item)
            self.contact_data[contact_name] = {
                'user_avatar': "D:\\DESK\\GPT-3.5\\ABC.png",
                'ai_avatar': "D:\\DESK\\GPT-3.5\\DEF.png",
                'chat_history': "",
                'user_name': f"用户 {i}",
                'ai_name': f"AI {i}",
            }

        # 连接联系人变更事件
        self.contact_list.currentItemChanged.connect(self.update_avatars)

        main_layout.addLayout(left_layout)

        # 右侧布局
        right_layout = QVBoxLayout()

        # 聊天记录
        self.chat_history = QTextEdit()
        self.chat_history.setReadOnly(True)
        right_layout.addWidget(self.chat_history)

        # 输入框
        self.input_text = QLineEdit()
        right_layout.addWidget(self.input_text)

        # 发送按钮
        send_button = QPushButton('发送')
        send_button.clicked.connect(self.send_message)
        right_layout.addWidget(send_button)

        main_layout.addLayout(right_layout)

        self.show()

    def show_contact_context_menu(self, position):
        context_menu = QMenu()

        # 添加用于修改用户和 AI 头像和名称的操作
        change_user_avatar_action = QAction("修改用户头像", self)
        change_user_avatar_action.triggered.connect(self.change_user_avatar)
        context_menu.addAction(change_user_avatar_action)

        change_ai_avatar_action = QAction("修改 AI 头像", self)
        change_ai_avatar_action.triggered.connect(self.change_ai_avatar)
        context_menu.addAction(change_ai_avatar_action)

        change_user_name_action = QAction("修改用户名称", self)
        change_user_name_action.triggered.connect(self.change_user_name)
        context_menu.addAction(change_user_name_action)

        change_ai_name_action = QAction("修改 AI 名称", self)
        change_ai_name_action.triggered.connect(self.change_ai_name)
        context_menu.addAction(change_ai_name_action)

        # 添加用于修改联系人窗口名称的操作
        change_window_name_action = QAction("修改窗口名称", self)
        change_window_name_action.triggered.connect(self.change_window_name)
        context_menu.addAction(change_window_name_action)

        context_menu.exec_(self.contact_list.mapToGlobal(position))

    def edit_user_avatar(self):
        self.show_user_profile(None)

    def edit_user_name(self):
        current_contact = self.contact_list.currentItem().text()
        profile_dialog = ProfileDialog(self, self.contact_data[current_contact], is_user=True)
        profile_dialog.change_name()

    def edit_ai_avatar(self):
        self.show_ai_profile(None)

    def edit_ai_name(self):
        current_contact = self.contact_list.currentItem().text()
        profile_dialog = ProfileDialog(self, self.contact_data[current_contact], is_user=False)
        profile_dialog.change_name()

    def contact_context_menu(self, position):
        menu = QMenu()
        edit_name_action = QAction("修改名称", self)
        edit_name_action.triggered.connect(self.edit_contact_name)
        menu.addAction(edit_name_action)

        edit_avatar_action = QAction("修改头像", self)
        edit_avatar_action.triggered.connect(self.edit_contact_avatar)
        menu.addAction(edit_avatar_action)

        menu.exec_(self.contact_list.mapToGlobal(position))

    def edit_contact_name(self):
        current_contact = self.contact_list.currentItem().text()
        old_name = current_contact
        new_name, ok_pressed = QInputDialog.getText(self, "更改名称", "请输入新的名称:", text=old_name)
        if ok_pressed and new_name != '':
            self.contact_data[new_name] = self.contact_data.pop(old_name)
            self.contact_list.currentItem().setText(new_name)

    def edit_contact_avatar(self):
        current_contact = self.contact_list.currentItem().text()
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        file_name, _ = QFileDialog.getOpenFileName(self, "选择头像", "", "Images (*.png *.xpm *.jpg *.bmp *.gif);;All Files (*)", options=options)
        if file_name:
            self.contact_data[current_contact]['ai_avatar'] = file_name
            self.contact_list.currentItem().setIcon(QIcon(QPixmap(file_name)))
            self.update_avatars(self.contact_list.currentItem())

        

    def send_message(self):
        message = self.input_text.text()
        current_contact = self.contact_list.currentItem().text()
        self.contact_data[current_contact]['chat_history'] += f"我: {message}\n"
        self.chat_history.append(f"我: {message}")
        self.input_text.clear()

    def update_avatars(self, item):
        current_contact = item.text()
        user_avatar_path = self.contact_data[current_contact]['user_avatar']
        ai_avatar_path = self.contact_data[current_contact]['ai_avatar']
        chat_history = self.contact_data[current_contact]['chat_history']
        user_name = self.contact_data[current_contact]['user_name']
        ai_name = self.contact_data[current_contact]['ai_name']
        contact_item = self.contact_list.item(self.contact_list.row(item))
        ai_avatar = QPixmap(ai_avatar_path)

        # Update user avatar
        _, user_avatar_extension = os.path.splitext(user_avatar_path)
        if user_avatar_extension.lower() == ".gif":
            self.user_avatar_movie.setFileName(user_avatar_path)
            self.user_avatar_movie.start()
            self.user_avatar.setMovie(self.user_avatar_movie)
        else:
            self.user_avatar_movie.stop()
            self.user_avatar.setPixmap(QPixmap(user_avatar_path).scaled(50, 50, Qt.KeepAspectRatio))

        # Update AI avatar
        _, ai_avatar_extension = os.path.splitext(ai_avatar_path)
        if ai_avatar_extension.lower() == ".gif":
            self.ai_avatar_movie.setFileName(ai_avatar_path)
            self.ai_avatar_movie.setScaledSize(QSize(50, 50))
            self.ai_avatar_movie.start()
        else:
            self.ai_avatar_movie.stop()
            self.ai_avatar.setPixmap(QPixmap(ai_avatar_path).scaled(50, 50, Qt.KeepAspectRatio))

        # Update contact list item icon
        if ai_avatar_extension.lower() == ".gif":
            contact_item.setIcon(QIcon(self.ai_avatar_movie.currentPixmap()))
        else:
            contact_item.setIcon(QIcon(ai_avatar.scaled(50, 50, Qt.KeepAspectRatio)))

        # Update chat history and name labels
        self.chat_history.setPlainText(chat_history)
        self.user_name_label.setText(user_name)
        self.ai_name_label.setText(ai_name)

        

    def show_user_profile(self, event):
        current_item = self.contact_list.currentItem()
        if current_item is not None:
            current_contact = current_item.text()
            profile_dialog = ProfileDialog(self, self.contact_data[current_contact], is_user=True)
            profile_dialog.exec_()

    def show_ai_profile(self, event):
        current_item = self.contact_list.currentItem()
        if current_item is not None:
            current_contact = current_item.text()
            profile_dialog = ProfileDialog(self, self.contact_data[current_contact], is_user=False)
            profile_dialog.exec_()

    def add_contact(self):
        contact_name, ok_pressed = QInputDialog.getText(self, "新建聊天卡", "请输入联系人名称:")
        if ok_pressed and contact_name != '':
            contact_item = QListWidgetItem(contact_name)
            contact_item.setIcon(QIcon(QPixmap("D:\\DESK\\GPT-3.5\\ABC.png")))
            self.contact_list.addItem(contact_item)
            self.contact_data[contact_name] = {
                'user_avatar': "D:\\DESK\\GPT-3.5\\ABC.png",
                'ai_avatar': "D:\\DESK\\GPT-3.5\\DEF.png",
                'chat_history': "",
                'user_name': f"用户 {contact_name}",
                'ai_name': f"AI {contact_name}",
            }
    def send_message(self):
        message = self.input_text.text()
        current_contact = self.contact_list.currentItem().text()
        self.contact_data[current_contact]['chat_history'] += f"我: {message}\n"
        self.chat_history.append(f"我: {message}")
        
        # 模拟AI回复
        ai_response = f"AI {current_contact}: 回复 '{message}'"
        self.contact_data[current_contact]['chat_history'] += ai_response + "\n"
        self.chat_history.append(ai_response)
        
        # 同步AI头像
        ai_avatar_path = self.contact_data[current_contact]['ai_avatar']
        self.ai_avatar.setPixmap(QPixmap(ai_avatar_path).scaled(50, 50, Qt.KeepAspectRatio))
        
        self.input_text.clear()
        


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = QMainWindow()
    input_box = MessageInputBox(window)
    window.setCentralWidget(input_box)
    window.show()
    sys.exit(app.exec_())
