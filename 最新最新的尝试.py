import sys
import asyncio
import json
import sys

import httpx
import openai
import PyQt5
import sys
from PyQt5.QtCore import Qt, pyqtSlot

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QIcon, QPixmap
from PyQt5.QtWidgets import (QAction, QApplication, QHBoxLayout, QInputDialog,
                             QLabel, QLineEdit, QListWidget, QListWidgetItem,
                             QMainWindow, QMenu, QMessageBox, QPushButton,
                             QSizePolicy, QSpacerItem, QTextEdit, QVBoxLayout,
                             QWidget, QTabWidget, QFormLayout, QCheckBox, QFileDialog)

from PyQt5.QtWidgets import QMenu, QAction

class Contact:
    def __init__(self, name, avatar_path, introduction):
        self.name = name
        self.avatar = QPixmap(avatar_path).scaled(50, 50, Qt.KeepAspectRatio)
        self.introduction = introduction


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setWindowTitle("仿微信")
        self.setGeometry(100, 100, 800, 600)

        self.setup_ui()

    def setup_ui(self):
        main_widget = QWidget()
        main_layout = QHBoxLayout(main_widget)

        # 左侧布局
        left_layout = QVBoxLayout()

        # 添加选项卡部件
        self.tabs = QTabWidget()
        left_layout.addWidget(self.tabs)

        # 聊天选项卡
        chat_tab = QWidget()
        chat_tab_layout = QVBoxLayout(chat_tab)

        # 用户头像和AI头像显示框
        self.user_avatar = QLabel()
        self.user_avatar.setPixmap(QPixmap("D:/DESK/GPT-3.5/ABC.png").scaled(50, 50, Qt.KeepAspectRatio))
        self.ai_avatar = QLabel()
        self.ai_avatar.setPixmap(QPixmap("D:/DESK/GPT-3.5/DEF.png").scaled(50, 50, Qt.KeepAspectRatio))

        # 用户名和AI名称
        self.username_label = QLabel("用户名")
        self.ai_name_label = QLabel("AI名称")

        self.username_label.setFont(QFont("Microsoft YaHei", 10))
        self.ai_name_label.setFont(QFont("Microsoft YaHei", 10))

        # 添加头像和名称到聊天选项卡布局
        chat_tab_layout.addWidget(self.user_avatar)
        chat_tab_layout.addWidget(self.username_label)
        chat_tab_layout.addWidget(self.ai_avatar)
        chat_tab_layout.addWidget(self.ai_name_label)

        # 联系人搜索框
        self.contact_search = QLineEdit()
        self.contact_search.setPlaceholderText("搜索联系人")
        chat_tab_layout.addWidget(self.contact_search)

        # 联系人列表
        self.contact_list = QListWidget()
        chat_tab_layout.addWidget(self.contact_list)

        # 添加联系人按钮
        self.add_contact_button = QPushButton("添加联系人")
        self.add_contact_button.clicked.connect(self.add_contact)
        chat_tab_layout.addWidget(self.add_contact_button)

        self.tabs.addTab(chat_tab, "聊天")

        # 设置选项卡
        settings_tab = QWidget()
        settings_tab_layout = QFormLayout(settings_tab)

        # 在此处添加设置选项卡内容
        self.setting_option = QCheckBox("启用某个设置")
        settings_tab_layout.addRow("设置选项：", self.setting_option)

        self.tabs.addTab(settings_tab, "设置")

        main_layout.addLayout(left_layout)

        # 右侧布局
        right_layout = QVBoxLayout()

        # 聊天窗口
        self.chat_window = QTextEdit()
        self.chat_window.setReadOnly(True)
        right_layout.addWidget(self.chat_window)

        # 输入框
        self.input_box = QTextEdit()
        right_layout.addWidget(self.input_box)

        bottom_layout = QHBoxLayout()

        # 空白区域，使得发送按钮在右边
        spacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        bottom_layout.addItem(spacer)

        # 发送按钮
        self.send_button = QPushButton("发送")
        self.send_button.clicked.connect(self.send_message)
        bottom_layout.addWidget(self.send_button)
        right_layout.addLayout(bottom_layout)

        main_layout.addLayout(right_layout)

        self.setCentralWidget(main_widget)

        # 添加联系人列表右键菜单
        self.contact_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.contact_list.customContextMenuRequested.connect(self.show_contact_menu)

    def show_contact_menu(self, position):
        # 创建一个菜单并将其关联到当前对象
        menu = QMenu(self)

        # 创建各个操作项
        modify_contact = QAction("修改联系人", self)
        delete_contact = QAction("删除联系人", self)
        modify_ai_engine = QAction("修改 AI 引擎", self)

        # 将操作项添加到菜单中
        menu.addAction(modify_contact)
        menu.addAction(delete_contact)
        menu.addSeparator()
        menu.addAction(modify_ai_engine)

        # 显示菜单并获取选中的操作项
        action = menu.exec_(self.mapToGlobal(position))

        # 根据选中的操作项执行相应的函数
        if action == modify_contact:
            self.modify_contact_info()
        elif action == delete_contact:
            self.remove_contact()
        elif action == modify_ai_engine:
            self.change_ai_engine()


        # 在鼠标位置显示右键菜单
        action = menu.exec_(self.contact_list.mapToGlobal(position))

    @pyqtSlot()
    def change_user_avatar(self):
        avatar_path, _ = QFileDialog.getOpenFileName(self, "选择用户头像", "", "图片文件 (*.png *.jpg *.bmp)")
        if avatar_path:
            self.user_avatar.setPixmap(QPixmap(avatar_path).scaled(50, 50, Qt.KeepAspectRatio))

    @pyqtSlot()
    def change_ai_avatar(self):
        avatar_path, _ = QFileDialog.getOpenFileName(self, "选择AI头像", "", "图片文件 (*.png *.jpg *.bmp)")
        if avatar_path:
            self.ai_avatar.setPixmap(QPixmap(avatar_path).scaled(50, 50, Qt.KeepAspectRatio))

    @pyqtSlot()
    def change_username(self):
        new_username, ok = QInputDialog.getText(self, "更改用户名", "请输入新的用户名:")
        if ok and new_username:
            self.username_label.setText(new_username)

    @pyqtSlot()
    def change_ai_name(self):
        new_ai_name, ok = QInputDialog.getText(self, "更改AI名称", "请输入新的AI名称:")
        if ok and new_ai_name:
            self.ai_name_label.setText(new_ai_name)

        # 在鼠标位置显示右键菜单
        action = menu.exec_(self.contact_list.mapToGlobal(position))

        # 选择执行对应的操作
        if action == modify_contact:
            self.modify_contact_info()
        elif action == delete_contact:
            self.remove_contact()
        elif action == modify_ai_engine:
            self.change_ai_engine()

    def add_contact(self):
        # 添加联系人
        name, ok = QInputDialog.getText(self, "添加联系人", "请输入联系人名称：")
        if ok and name:
            item = QListWidgetItem(name)
            self.contact_list.addItem(item)
            contact = Contact(name, "D:/DESK/GPT-3.5/DEF.png", "这里是联系人简介")
            item.setData(Qt.UserRole, contact)


    def modify_contact_info(self):
        # 修改联系人信息
        current_item = self.contact_list.currentItem()
        if current_item:
            new_name, ok = QInputDialog.getText(self, "修改联系人", "请输入新的联系人名称：", QLineEdit.Normal, current_item.text())
            if ok and new_name:
                current_item.setText(new_name)
                contact = self.contact_list.itemData(self.contact_list.row(current_item))
                contact.name = new_name 
    def remove_contact(self):
        # 删除联系人
        current_item = self.contact_list.currentItem()
        if current_item:
            reply = QMessageBox.question(self, "删除联系人", "您确定要删除此联系人吗？", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.Yes:
                row = self.contact_list.row(current_item)
                self.contact_list.takeItem(row)

    def change_ai_engine(self):
        # 更换 AI 引擎
        pass

    def send_message(self):
        # 发送消息
        message = self.input_box.toPlainText()
        if message:
            self.chat_window.append("我: " + message)
            self.input_box.clear()
            # 这里可以调用 GPT-3.5 Turbo 模型生成回复

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

