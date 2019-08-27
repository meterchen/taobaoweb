# coding=utf-8

import sys, os
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtWebEngineWidgets import QWebEngineView

import fdb

import sqlite3

import platform
import winreg

import paramiko


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__()

        # 窗口最大化
        #self.showMaximized()

        tb = self.addToolBar("tool")
        start=QAction("START",self)
        tb.addAction(start)
        tb.actionTriggered[QAction].connect(self.opendb)

        self.setWindowTitle("db_converter")

        self.btn = QPushButton("START CONVERT")
        self.btn.clicked.connect(self.opendb)
        self.layout_h = QHBoxLayout()
        self.layout_h.addWidget(self.btn)
        self.layout_h.addStretch()

        self.logt = QTextEdit()

        self.layout_v = QVBoxLayout()
        self.layout_v.addLayout(self.layout_h)
        self.layout_v.addWidget(self.logt)

        main_frame= QWidget()
        main_frame.setLayout(self.layout_v)
        self.setCentralWidget(main_frame)

        self.setWindowState(Qt.WindowMaximized)

    def query_fdb(self, database, store):
        self.logt.append(database)
        con = fdb.connect(host='127.0.0.1', database=database, user='sysdba', password='masterkey', charset="utf8")
        # con = fdb.connect(host='127.0.0.1', database=database, user='sysdba', password='masterkey',charset = 'UTF8')

        cur = con.cursor()

        # con_fb = fdb.connect(host='127.0.0.1', database='/Users/meterchen/test/APPITEM.DAT', user='sysdba',
        #                     password='masterkey', charset='UTF8')
        # con = fdb.connect(host='10.0.0.20', database='/home/pi/APPITEM.DAT', user='sysdba', password='masterkey',charset = 'UTF8')
        # cur_fb = con_fb1.cursor()

        # 已删除宝贝除外
        sql_select = '''select NUM_IID,OUTER_ID,CLIENT_NAVIGATION_TYPE from ITEM 
                                where (CLIENT_IS_DELETE  is NULL or CLIENT_IS_DELETE =0)'''

        # 显示全部内容
        cur.execute(sql_select)

        item = cur.fetchall()

        con.close()

        num_iid = []
        for t in item:
            t = list(t)
            if t[2] == 2:
                t.append("出售")
            elif t[2] == 3:
                t.append("仓库")
            elif t[2] == 5:
                t.append("回收")
            else:
                continue      #bugfix 本地宝贝

            # 加上店名
            t.append(store)
            t.append("AAAA")
            num_iid.append(t)

        # print(num_iid)
        return num_iid

    def opendb(self):
        if platform.system() == "Windows":
            self.logt.append("windows platform")
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                                 "SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\App Paths\\Workbench.exe")
            base_dir = winreg.QueryValueEx(key, "")[0]
            base_dir = os.path.dirname(base_dir)
            self.logt.append(base_dir)
        else:
            base_dir = QFileDialog.getExistingDirectory(self, "选取文件夹", "C:/Program Files/Taobaoassistant")
        # print(directory1)

        # base_dir = "/Volumes/BOOTCAMP/Program Files/TaobaoAssistant/users/"
        # base_dir = "/Users/meterchen/test/users/"
        num_iid = self.query_fdb(base_dir + "/users/希希小元/" + "APPITEM.DAT", store="企业店")
        num_iid += self.query_fdb(base_dir + "/users/醉美彤彤/" + "APPITEM.DAT", store="彤彤店")
        num_iid += self.query_fdb(base_dir + "/users/meterchen/" + "APPITEM.DAT", store="女童店")
        num_iid += self.query_fdb(base_dir + "/users/爱跳的憨豆/" + "APPITEM.DAT", store="憨豆店")

        con_sq3 = sqlite3.connect("seyryan_np.db")
        cur_sq3 = con_sq3.cursor()

        sql_drop = "DROP TABLE if exists ITEM "  # 若表存在则删除
        cur_sq3.execute(sql_drop)

        sql_create = '''create table ITEM(NUM_IID BIGINT PRIMARY KEY, 
                                        OUTER_ID VARCHAR(96),
                                        CLIENT_NAVIGATION_TYPE SMALLINT,
                                        STOCK_STATUS VARCHAR(96),
                                        STORE_NAME VARCHAR(96),
                                        POSITION VARCHAR(96)
                                        )'''
        cur_sq3.execute(sql_create)

        for t in num_iid:
            sql_insert = "insert into ITEM values(%d,'%s',%d,'%s','%s','%s')" % (t[0], t[1], t[2], t[3], t[4], t[5])
            cur_sq3.execute(sql_insert)

        # 建立索引
        sql_index = "CREATE INDEX IDX_OUTER_ID ON ITEM(OUTER_ID)"
        cur_sq3.execute(sql_index)

        con_sq3.commit()

        con_sq3.close()

        self.logt.append("转换完成！")


        transport = paramiko.Transport(('192.168.5.26', 22))
        transport.connect(username="pi", password='raspberry')
        sftp = paramiko.SFTPClient.from_transport(transport)
        #sftp.mkdir("/home/pi/Documents/sss")
        # 将location.py 上传至服务器 /tmp/test.py
        sftp.put('C:\\Users\\meterchen\Desktop\\taobaoweb\\seyryan_np.db', '/home/pi/Documents/flaskDemo/database/seyryan_np.db')
        # 将remove_path 下载到本地 local_path
        # sftp.get('/root/oldgirl.txt', 'fromlinux.txt')

        transport.close()
        self.logt.append("上传完成！")

        # 实例化一个transport对象
        transport = paramiko.Transport(('192.168.5.26', 22))
        # 建立连接
        transport.connect(username="pi", password='raspberry')
        # 将sshclient的对象的transport指定为以上的transport
        ssh = paramiko.SSHClient()
        ssh._transport = transport
        # 执行命令，和传统方法一样
        stdin, stdout, stderr = ssh.exec_command('cd /home/pi/Documents/flaskDemo/database;./migratedb.sh')

        self.logt.append(stdout.read().decode())
        # 关闭连接
        transport.close()

        # prefix = "https://item.taobao.com/item.htm?id="

        # url = prefix + str(num_iid[0][0])

        # self.view.load(QUrl(url))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    form = MainWindow()
    form.show()
    sys.exit(app.exec_())
