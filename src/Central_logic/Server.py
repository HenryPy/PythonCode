from configparser import ConfigParser
import serial.tools.list_ports
from PyQt5.QtGui import QCursor
from PyQt5.QtCore import pyqtSignal, QDateTime, QTimer, Qt
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox, QLabel, QMenu, QAction
from Central import Ui_mainWindow
import sys
import socket
import threading
import time
import operator


class ZhongKong(QMainWindow, Ui_mainWindow):
    # 当前所有测试机的30码
    dict_yuan = {}
    # IP地址与测试机绑定
    bind_csj = {'1': '192.168.0.1', '2': '192.168.0.2', '3': '192.168.0.3', '4': '192.168.0.4'}
    # 储存所有连接的客户端的socket,k=ip,v=socket
    # dict_socket = {'ip1':'socket1','ip2':'socket2','ip3':'socket3','ip4':'socket4'}
    dict_socket = {}
    # 机械手上产品码,双爪情况下最多为2个
    code_jxs = []
    # 机械手收到30码时,即将去往的站
    sta_num = 1
    # 自定义信号->此处应该自定义QThread类
    sendxx_plc = pyqtSignal(str)
    send_signal = pyqtSignal(str)

    # 初始化
    def __init__(self, parent=None, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.setupUi(self)
        self.actiondakaipeizhiwenjian.triggered.connect(self.clicked)
        self.actionlianjixieshou_I.triggered.connect(self.jxs_conn)
        self.actioncaozuojixies.triggered.connect(self.clicked)
        self.actionxunhuanjieshoujxs.triggered.connect(self.clicked)
        self.actionmianbanxieru.triggered.connect(self.clicked)
        self.actiondakaiwangkou.triggered.connect(self.clicked)
        self.actionwangkoufasong.triggered.connect(self.clicked)
        self.actiondakaipeizhiwenjian_2.triggered.connect(self.clicked)
        self.actionlianPlc_T.triggered.connect(self.plc_conn)
        self.actioncaozuoPLC_O.triggered.connect(self.clicked)
        self.actionshoudongPLC.triggered.connect(self.send_plc)
        self.actionjiechuPlc.triggered.connect(self.jiechu_Plc)
        self.actionCanshushezhi_P.triggered.connect(self.clicked)
        self.actionjinzhi_N.triggered.connect(self.clicked)
        self.actionxunyu_Y.triggered.connect(self.clicked)
        self.actiondakaishujukufuwuqi.triggered.connect(self.clicked)
        self.actionguanbishujukufuwuqi.triggered.connect(self.clicked)
        self.actionlianjieshujuku_L.triggered.connect(self.clicked)
        self.actionduankaishujuku_C.triggered.connect(self.clicked)
        self.actionpanduan_Y.triggered.connect(self.clicked)
        self.actionbupanduan_N.triggered.connect(self.clicked)
        self.actionyicitongguo_O.triggered.connect(self.clicked)
        self.actionchankandangqianzhuangtai_S.triggered.connect(self.clicked)
        self.actionjilu_R.triggered.connect(self.clicked)
        self.actionshegnchengdejieguo_G.triggered.connect(self.clicked)
        self.actionpeizhicanshulujing_M.triggered.connect(self.clicked)
        self.actionzhegnchangshenchan_N.triggered.connect(self.clicked)
        self.actionshouliaomoshi_C.triggered.connect(self.clicked)
        self.actionshi_Y.triggered.connect(self.clicked)
        self.actionfou_N.triggered.connect(self.clicked)
        self.actionzhongkongjima_P.triggered.connect(self.clicked)
        self.actionchongxinsaoma_I.triggered.connect(self.clicked)
        self.actionqiyong_U.triggered.connect(self.clicked)
        self.actionjinyong_N.triggered.connect(self.clicked)
        self.actionchakanbangzhu_V.triggered.connect(self.clicked)
        self.save_buton.clicked.connect(self.save_peizhi)
        self.dakai_plc.clicked.connect(self.plc_conn)
        self.dakai_jxxs.clicked.connect(self.jxs_conn)
        self.chaxun_30ma.clicked.connect(self.display_30ma)
        self.chaxun_socket.clicked.connect(self.socket_display)
        self.chaxun_peizhi.clicked.connect(self.config_display)
        self.set_default()
        self.signal_slot()
        self.thread_server_start()
        self.statusShowTime()
        # 创建单个菜单并返回当前值
        self.frame_2.setContextMenuPolicy(Qt.CustomContextMenu)
        self.frame_2.customContextMenuRequested.connect(lambda: self.create_rightmenu(1))
        self.frame_3.setContextMenuPolicy(Qt.CustomContextMenu)
        self.frame_3.customContextMenuRequested.connect(lambda: self.create_rightmenu(2))
        self.frame_4.setContextMenuPolicy(Qt.CustomContextMenu)
        self.frame_4.customContextMenuRequested.connect(lambda: self.create_rightmenu(3))
        self.frame_5.setContextMenuPolicy(Qt.CustomContextMenu)
        self.frame_5.customContextMenuRequested.connect(lambda: self.create_rightmenu(4))
        # 创建整体菜单并返回当前值
        self.tab.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tab.customContextMenuRequested.connect(self.tab_rightmenu)
        self.pushButton_ceshi.clicked.connect(lambda: self.you_chanpin(4))
        self.pushButton_ceshi_2.clicked.connect(lambda: self.wu_chanpin(4))
        # 隐藏主窗口边界
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.pushButton_close.pressed.connect(self.close)
        self.pushButton_min.pressed.connect(self.showMinimized)

    # 鼠标点击事件
    def mousePressEvent(self, evt):
        # 获取鼠标当前的坐标
        self.mouse_x = evt.globalX()
        self.mouse_y = evt.globalY()

        # 获取窗体当前坐标
        self.origin_x = self.x()
        self.origin_y = self.y()

    # 鼠标移动事件
    def mouseMoveEvent(self, evt):
        # 计算鼠标移动的x，y位移
        move_x = evt.globalX() - self.mouse_x
        move_y = evt.globalY() - self.mouse_y
        # 计算窗体更新后的坐标：更新后的坐标 = 原本的坐标 + 鼠标的位移
        dest_x = self.origin_x + move_x
        dest_y = self.origin_y + move_y
        # 移动窗体
        self.move(dest_x, dest_y)

    # frame菜单槽函数
    def create_rightmenu(self, sta):
        self.groupBox_menu = QMenu(self)
        self.actionA = QAction(U'状态更新', self)
        self.groupBox_menu.addAction(self.actionA)
        self.actionB = QAction(u'屏蔽本站', self)
        self.groupBox_menu.addAction(self.actionB)
        self.actionC = QAction(u'解除屏蔽', self)
        self.groupBox_menu.addAction(self.actionC)
        self.actionD = QAction(u'初始化', self)
        self.groupBox_menu.addAction(self.actionD)
        self.actionE = QAction(u'赋值->1N', self)
        self.groupBox_menu.addAction(self.actionE)
        self.actionF = QAction(u'赋值->2N', self)
        self.groupBox_menu.addAction(self.actionF)
        self.actionG = QAction(u'赋值->3N', self)
        self.groupBox_menu.addAction(self.actionG)
        self.actionH = QAction(u'赋值->OK', self)
        self.groupBox_menu.addAction(self.actionH)
        self.groupBox_menu.popup(QCursor.pos())
        self.actionA.triggered.connect(lambda: self.caidan_1(sta))
        self.actionB.triggered.connect(lambda: self.caidan_2(sta))
        self.actionC.triggered.connect(lambda: self.caidan_3(sta))
        self.actionD.triggered.connect(lambda: self.caidan_4(sta))
        self.actionE.triggered.connect(lambda: self.caidan_5(sta, '1N'))
        self.actionF.triggered.connect(lambda: self.caidan_5(sta, '2N'))
        self.actionG.triggered.connect(lambda: self.caidan_5(sta, '3N'))
        self.actionH.triggered.connect(lambda: self.caidan_5(sta, 'OK'))

    # tab右键菜单
    def tab_rightmenu(self):
        self.tab_menu = QMenu(self)
        self.actionA = QAction(U'全部初始化', self)
        self.tab_menu.addAction(self.actionA)
        self.actionB = QAction(u'解除PLC报警', self)
        self.tab_menu.addAction(self.actionB)
        self.actionC = QAction(u'功能2', self)
        self.tab_menu.addAction(self.actionC)
        self.actionD = QAction(u'功能3', self)
        self.tab_menu.addAction(self.actionD)
        self.tab_menu.popup(QCursor.pos())
        self.actionA.triggered.connect(self.quan_chushi)
        self.actionB.triggered.connect(self.jiechu_Plc)
        self.actionC.triggered.connect(self.clicked)
        self.actionD.triggered.connect(self.clicked)

    # 状态更新->给客户端发送CG
    def caidan_1(self, sta):
        ip = '192.168.0.{}'.format(sta)
        if ip in self.dict_socket:
            socket = self.dict_socket[ip]
            self.send_to_client(socket, 'CG!')
        else:
            self.mianban_xianshi('{}客户端不存在!'.format(sta))

    # 屏蔽当前站
    def caidan_2(self, sta):
        self.ping_bi(sta)

    # 解除屏蔽
    def caidan_3(self, sta):
        self.re_pingbi(sta)
        self.jiechu_Plc()

    # 赋值给不同的站
    def caidan_5(self, sta, msg):

        self.mianban_xianshi('给{}站赋值{}'.format(sta, msg))

    # 初始化->更新面板状态
    def caidan_4(self, sta):
        self.mianban_xianshi('{}站初始化'.format(sta))

    # 将报警写入本地
    def alarm_write(self, msg):
        time1 = QDateTime.currentDateTime()
        time_display = time1.toString('MM/dd hh:mm:ss ')
        str_msg = str(msg)
        try:
            # with open('{}:\Alarm.txt'.format(app_path), 'a') as stream:
            with open('.\Alarm.txt', 'a') as stream:
                stream.write(time_display + str_msg + ' ' + '\n')
        except Exception as e:
            self.sendxx_plc.emit(str(e))

    # 将日志写入本地
    def log_write(self, msg):
        time1 = QDateTime.currentDateTime()
        time_display = time1.toString('MM/dd hh:mm:ss ')
        str_msg = str(msg)
        try:
            # with open('{}:\Alarm.txt'.format(app_path), 'a') as stream:
            with open('.\Log.txt', 'a') as stream:
                stream.write(time_display + str_msg + ' ' + '\n')
        except Exception as e:
            self.sendxx_plc.emit(str(e))

    # 打印到面板定义为函数
    def mianban_xianshi(self, data):
        str_data = str(data)
        time1 = QDateTime.currentDateTime()
        time_display = time1.toString('MM/dd hh:mm:ss ')
        try:
            self.sendxx_plc.emit(time_display + str_data)
            self.log_write(data)
        except Exception as e:
            self.sendxx_plc.emit(str(e))

    # 开机后判断有多少客户端在线,就重置dict_yuan,初始化时候调用
    def client_num(self):
        # bind_csj = {1: '192.168.0.1', 2: '192.168.0.2', 3: '192.168.0.3', 4: '192.168.0.4'}
        # dict_socket = {'192.168.0.1':'socket1','192.168.0.2':'socket2','192.168.0.3':'socket3','IP4':'socket4'}
        for k, v in self.bind_csj.items():
            for i, j in self.dict_socket.items():
                if v == i:
                    str_num = int(k)
                    if str_num not in self.dict_yuan:
                        self.dict_yuan[str_num] = ':100000' + str(str_num) + '000000000000000000000!'

    # 全部初始化:给所有的终端发送CG
    def quan_chushi(self):
        for i in self.dict_socket.values():
            self.send_to_client(i, 'CG!')

    # 点击屏蔽后删除dict_yuan里的码,点击屏蔽时要传入一个当前站
    def ping_bi(self, sta_num):
        ip = '192.168.0.{}'.format(sta_num)
        in_sta_num = int(sta_num)
        new_socket = self.dict_socket[ip]
        if ip in self.dict_socket:
            if sta_num in self.dict_yuan.keys():
                del self.dict_yuan[sta_num]
                data1 = '屏蔽{}号终端'.format(sta_num)
                self.mianban_xianshi(data1)
                # 需要额外触发PLC报警
                self.send_plc()
                self.xianshi_pingb(in_sta_num)
                self.send_to_client(new_socket, '0000PB')
            else:
                self.mianban_xianshi('屏蔽失败!')
        else:
            self.mianban_xianshi('{}测试机不在线!'.format(sta_num))

    # 解除屏蔽,重新加载dict_yuan里的码,解除屏蔽时也要传入一个当前站
    def re_pingbi(self, sta_num):
        ip = '192.168.0.{}'.format(sta_num)
        in_sta_num = int(sta_num)
        new_socket = self.dict_socket[ip]
        if ip in self.dict_socket:
            if sta_num not in self.dict_yuan.keys():
                value = ":000000" + str(sta_num) + '000000000000000000000!'
                self.dict_yuan[sta_num] = value
                data1 = '{}号终端解除屏蔽'.format(sta_num)
                self.mianban_xianshi(data1)
                self.jiechu_pingb(in_sta_num)
                self.send_to_client(new_socket, '0000JCPB')
            else:
                self.mianban_xianshi('解除屏蔽失败!')
        else:
            self.mianban_xianshi('{}测试机不在线!'.format(sta_num))

    # 功能开发中
    def clicked(self):
        QMessageBox.information(self, "功能开发中", "功能开发中!")

    # 点击按钮后开始执行子线程,并连接信号与槽
    def signal_slot(self):
        self.sendxx_plc.connect(self.handleDisplay)
        self.send_signal.connect(self.handle_data_display)

    # 监视文本框追加消息
    def handleDisplay(self, msg):
        self.textEdit.append(msg)
        self.textEdit.setStyleSheet('color:rgb(0, 0, 255)')

    # 数据文本框追加消息
    def handle_data_display(self, msg):
        self.textEdit_2.append(msg)
        self.textEdit.setStyleSheet('color:rgb(0, 0, 255)')

    # 退出询问
    def closeEvent(self, event):
        reply = QMessageBox.question(self, '退出询问', '是否确认退出？', QMessageBox.Yes, QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.server_socket.shutdown(socket.SHUT_RDWR) # 这里可能是套接字关闭错误导致
            self.server_socket.close()
            event.accept()
        else:
            event.ignore()

    # 获取系统当前时间
    def showCurrentTime(self, timeLabel):
        time = QDateTime.currentDateTime()
        timeDisplay = time.toString('yyyy/MM/dd hh:mm:ss dddd')
        timeLabel.setText(timeDisplay)

    # 面板时间显示->此处用QTimer属于多线程
    def statusShowTime(self):
        self.timer = QTimer()
        self.timeLabel = QLabel()
        self.message = QLabel('承制单位:自动化设备开发处')
        self.statusbar.addPermanentWidget(self.timeLabel, 400)
        self.statusbar.addPermanentWidget(self.message, 0)
        # 这个通过调用槽函数来刷新时间
        self.timer.timeout.connect(lambda: self.showCurrentTime(self.timeLabel))
        # 每隔1000MS刷新一次
        self.timer.start(1000)

    # 30位通讯码生成
    def return_30ma(self):
        # 为保证机台号有顺序,对字典排序
        sort_dict_yuan = dict(sorted(self.dict_yuan.items(), key=operator.itemgetter(0)))  # 按照key值升序
        for i in sort_dict_yuan.keys():
            # 如果无料没没开,就报警
            if sort_dict_yuan[i][1] == sort_dict_yuan[i][10] == sort_dict_yuan[i][19] == '0':

                self.mianban_xianshi('请检查测试机门状态!')
            else:
                if self.comboBox_danshxue.currentText() == '单穴':
                    # if self.radioButton_dan.isChecked():
                    # 如果测试完成
                    if sort_dict_yuan[i][21] == '0':
                        if len(self.code_jxs) == 0:
                            self.sta_num = i
                            return sort_dict_yuan[i]
                        else:
                            if self.code_jxs[0][7] != str(i):
                                self.sta_num = i
                                return sort_dict_yuan[i]
                elif self.comboBox_danshxue.currentText() == '双穴':
                    # elif self.radioButton_shuang.isChecked():
                    # 如果两个都测试完成
                    if sort_dict_yuan[i][21:23] == '00':
                        if len(self.code_jxs) == 0:
                            self.sta_num = i
                            return sort_dict_yuan[i]
                        else:
                            if self.code_jxs[0][7] != str(i):
                                self.sta_num = i
                                return sort_dict_yuan[i]

    # 连接机械手,可以设置开机自动连接,可以设置点击连接
    def jxs_conn(self):
        com_0 = self.comboBox_com_jxs.currentText()
        bo_te = self.comboBox_botelv_jxs.currentText()
        bo_telv = int(bo_te)
        jiao_yan = self.comboBox_jiaoyan_jxs.currentText()
        shu_1 = self.comboBox_shujuwei_jxs.currentText()
        shu_2 = int(shu_1)
        ting_0 = self.comboBox_tingzhiwei_jxs.currentText()
        ting_1 = int(ting_0)
        try:
            self.ser_jxs = serial.Serial(port='{}'.format(com_0), baudrate=bo_telv,
                                         bytesize=shu_2, parity='{}'.format(jiao_yan),
                                         stopbits=ting_1, timeout=0.1)
            self.thread_receive_jxs()
            self.mianban_xianshi('机械手串口打开成功！')
        except Exception as e:
            self.mianban_xianshi(str(e))

    # 给机械手发送30码,前提是通讯已连接
    def send_jxs30(self):
        try:
            data = self.return_30ma()
            send_ = data.encode('UTF-8')
            self.ser_jxs.write(send_)
            send_data = 'To:' + send_.decode('UTF-8')
            self.mianban_xianshi(send_data)
        except:
            pass

    # 接收机械手sl数据,前提是通讯已连接,根据设置发送不同的指令
    def send_sl(self):
        if self.comboBox_shifousl.currentText() == '不收料':
            # if self.radioButton_no.isChecked():
            data = ':0!'.encode('UTF-8')
            self.ser_jxs.write(data)
            send_data = 'To:' + data.decode('UTF-8')
            self.mianban_xianshi(send_data)
        elif self.comboBox_shifousl.currentText() == '收料':
            # elif self.radioButtonshou.isChecked():
            data = ':1!'.encode('UTF-8')
            self.ser_jxs.write(data)
            send_data = 'To:' + data.decode('UTF-8')
            self.mianban_xianshi(send_data)

    # 循环读取机械手数据,这个开机就要运行,启动前保证机械手连接已打开
    def receive_jxs(self):
        try:
            while True:
                # return the number of input buffer
                n = self.ser_jxs.inWaiting()
                if n:
                    # 确认机械手当前的位置,便于给对应的机械手发信息
                    str_num = str(self.sta_num)
                    # bind_csj = {'001': '192.168.0.1', '002': '192.168.0.2', '003': '192.168.0.3', '004': '192.168.0.4'}
                    # 机械手收到30码时,即将去往的站 sta_num = 0,初始默认是 O
                    co_od = self.bind_csj[str_num]
                    a = self.ser_jxs.readline()
                    send_data = 'Fr robot:' + a.decode('UTF-8')
                    self.mianban_xianshi(send_data)
                    re_data = a.decode('utf-8')
                    # 询问结果就引入当前函数
                    if re_data == 'JG!':
                        self.send_jxs30()
                    # 发送CG给测试机,还要等收到后再写入这个函数
                    # dict_socket = {'ip1':'socket1','ip2':'socket2','ip3':'socket3','ip4':'socket4'}
                    elif re_data == 'KM!':
                        try:
                            self.send_to_client(self.dict_socket[co_od], 'KM!')
                        except Exception as e:
                            self.sendxx_plc.emit(str(e))
                    # 发送CG给终端,通过终端发给测试机,测试机回复后生成新的30码,直接返回给机械手此时的30码,如果再次收到的30码还是关门,则重复此动作
                    # 此时会回复1^0
                    elif re_data == 'CG!':
                        try:
                            self.send_to_client(self.dict_socket[co_od], 'CG!')
                            # 发送当前站的30码给机械手
                            data = self.dict_yuan[self.sta_num]
                            send_ = data.encode('UTF-8')
                            self.ser_jxs.write(send_)
                            send_data = 'To robot:' + send_.decode('UTF-8')
                            self.mianban_xianshi(send_data)
                        except Exception as e:
                            self.sendxx_plc.emit(str(e))
                    # 表示机械手已经取完测试机料,如果当前测试机上是2N产品,就存入code_jxs = [],并将当前测试机码初始化
                    elif re_data == 'QW!':
                        # 双穴的情况 -->机械手取到1个2N的,会再流水线上取一个待测;机械手取到同一台机两个2N,同时取出
                        # 机械手每次取2N的都会是同一个爪,也就是第一次的爪
                        if self.comboBox_danshxue.currentText() == '双穴':
                            # if self.radioButton_shuang.isChecked():
                            # 如果当前测试机是->:0 000 002 1N 1   002 002 2N 1 0 00 0 0 0000!
                            if self.dict_yuan[self.sta_num][8:10] == '1N' and self.dict_yuan[self.sta_num][
                                                                              17:19] == '2N':
                                # 如果机械手上没有料:
                                if len(self.code_jxs) == 0:
                                    quwan_30 = self.dict_yuan[self.sta_num][0:2] + '000000000' + self.dict_yuan[
                                                                                                     self.sta_num][
                                                                                                 11:]
                                    self.code_jxs.append(quwan_30)
                                    self.dict_yuan[self.sta_num] = self.dict_yuan[self.sta_num][
                                                                   0:11] + '00000' + str_num + '000' + self.dict_yuan[
                                                                                                           self.sta_num][
                                                                                                       20:]
                            # 如果当前测试机是->:0 002 002 2N 1 000 002 1N 1 0 00 0 0 0000!
                            elif self.dict_yuan[self.sta_num][8:10] == '2N' and self.dict_yuan[self.sta_num][
                                                                                17:19] == '1N':
                                # 如果机械手上没有料:
                                if len(self.code_jxs) == 0:
                                    quwan_30 = self.dict_yuan[self.sta_num][0:11] + '000000000' + self.dict_yuan[
                                                                                                      self.sta_num][
                                                                                                  20:]
                                    self.code_jxs.append(quwan_30)
                                    self.dict_yuan[self.sta_num] = self.dict_yuan[self.sta_num][0:2] + '000000000' + \
                                                                   self.dict_yuan[self.sta_num][11:]
                            # 如果当前测试机是->:0 002 002 2N 1 000 002 2N 1 0 00 0 0 0000!
                            elif self.dict_yuan[self.sta_num][8:10] == '2N' and self.dict_yuan[self.sta_num][
                                                                                17:19] == '2N':
                                # 如果机械手上没有料:
                                if len(self.code_jxs) == 0:
                                    self.code_jxs.append(self.dict_yuan[self.sta_num])
                                    self.dict_yuan[self.sta_num] = ':1000000000000000000000000000!'
                            # 如果当前测试机是->:0 002 002 1N 1 000 002 1N 1 0 00 0 0 0000!
                            elif self.dict_yuan[self.sta_num][8:10] == '1N' and self.dict_yuan[self.sta_num][
                                                                                17:19] == '1N':
                                pass
                            # 如果当前测试机是->:0 001 002 3N 1 000 002 OK 1 0 00 0 0 0000! /0 000 002 OK 1 001 002 3N 1 0 00 0 0 0000!
                            elif (self.dict_yuan[self.sta_num][8:10] == '3N' and self.dict_yuan[self.sta_num][
                                                                                 17:19] == 'OK') or (
                                    self.dict_yuan[self.sta_num][8:10] == 'OK' and self.dict_yuan[self.sta_num][
                                                                                   17:19] == '3N'):
                                self.dict_yuan[self.sta_num] = ':1000000000000000000000000000!'
                        # 单穴的情况 -->此处1N状态需要保留,因为接收到的NG需要在1N基础上修改
                        elif self.comboBox_danshxue.currentText() == '单穴':
                            # elif self.radioButton_dan.isChecked():
                            # 如果是-->:0 002 002 2N 1 000 000 00 0 0 00 0 0 0000!
                            if self.dict_yuan[self.sta_num][8:10] == '2N':
                                self.code_jxs.append(self.dict_yuan[self.sta_num])
                                self.dict_yuan[self.sta_num] = ':1000000000000000000000000000!'
                            # 机械手会发送一个取完,这时将测试机当前站改为上一站,并改为测试中
                            elif self.dict_yuan[self.sta_num][8:10] == '1N':
                                self.dict_yuan[self.sta_num] = self.dict_yuan[self.sta_num][0:4] + \
                                                               self.dict_yuan[self.sta_num][7] + self.dict_yuan[
                                                                                                     self.sta_num][
                                                                                                 5:21] + '1' + \
                                                               self.dict_yuan[self.sta_num][22:]
                            elif self.dict_yuan[self.sta_num][8:10] == 'OK' or self.dict_yuan[self.sta_num][
                                                                               8:10] == '3N':
                                self.dict_yuan[self.sta_num] = ':1000000000000000000000000000!'
                    # 表示机械手已经将产品放到测试机,如果机械手上有产品,就将这个值给到测试机,如果机械手上没产品,说明是放的新产品,则不执行
                    elif re_data == 'FW!:GM!':
                        sta_code = int(self.sta_num)
                        # 如果是单穴
                        if self.comboBox_danshxue.currentText() == '单穴':
                            # if self.radioButton_dan.isChecked():
                            try:
                                # 如果机械手上产品和本站不相同时执行:
                                if self.code_jxs:
                                    if self.code_jxs[0][7] != str(self.sta_num):
                                        # 如果机械手上有2N产品
                                        if len(self.code_jxs) != 0:
                                            # 将机械手上2N料放入当前测试机,并删除机械手上料号
                                            self.dict_yuan[self.sta_num] = self.code_jxs[0]
                                            del self.code_jxs[0]
                                # 向这台测试机的终端发送GM,可以关闭测试机的门
                                self.send_to_client(self.dict_socket[co_od], 'GM!')
                                # 将测试机状态置为 有料,测试中
                                self.dict_yuan[self.sta_num] = self.dict_yuan[self.sta_num][0:10] + '1' \
                                                               + self.dict_yuan[self.sta_num][11:21] + '1' \
                                                               + self.dict_yuan[self.sta_num][22:30]

                                # 还要更新产品有无状态
                                self.del_test_result(sta_code)
                            except Exception as e:
                                self.sendxx_plc.emit(str(e))
                        # 如果是双穴
                        elif self.comboBox_danshxue.currentText() == '双穴':
                            # elif self.radioButton_shuang.isChecked():
                            try:
                                # 如果机械手上有2N产品
                                if len(self.code_jxs) != 0:
                                    # :0 002 002 2N 1 000 002 2N 1 0 00 0 0 0000!
                                    if self.code_jxs[0][17:19] == '2N' and self.code_jxs[0][8:10] == '2N':
                                        # 如果当前测试机2个穴都是空的
                                        if self.dict_yuan[self.sta_num][10] == '0' and self.dict_yuan[self.sta_num][
                                            19] == '0':
                                            self.dict_yuan[self.sta_num] = self.dict_yuan[self.sta_num][0:2] + \
                                                                           self.code_jxs[0][2:21] + '11' + \
                                                                           self.dict_yuan[
                                                                               self.sta_num][
                                                                           23:]
                                            del self.code_jxs[0]
                                        # 先放下哪个就把机械手哪个爪置为0,另一个爪不变
                                        # 如果当前测试机1穴是空的
                                        elif self.dict_yuan[self.sta_num][10] == '0':
                                            # 把左爪的放入测试机1穴
                                            self.dict_yuan[self.sta_num] = self.dict_yuan[self.sta_num][0:2] + \
                                                                           self.code_jxs[0][2:11] + self.dict_yuan[
                                                                                                        self.sta_num][
                                                                                                    11:21] + '11' + \
                                                                           self.dict_yuan[self.sta_num][23:]
                                            # 把机械手上右爪的2N倒到左爪上
                                            self.code_jxs[0] = self.code_jxs[0][:2] + self.code_jxs[0][
                                                                                      11:20] + '000000000' + \
                                                               self.code_jxs[
                                                                   0][20:]
                                        # 如果当前测试机2穴是空的
                                        elif self.dict_yuan[self.sta_num][19] == '0':
                                            # 把左爪的放入测试机2穴
                                            self.dict_yuan[self.sta_num] = self.dict_yuan[self.sta_num][:11] + \
                                                                           self.code_jxs[0][2:11] + \
                                                                           self.dict_yuan[self.sta_num][20] + '11' + \
                                                                           self.dict_yuan[self.sta_num][23:]
                                            # 把机械手上右爪的2N倒到左爪上
                                            self.code_jxs[0] = self.code_jxs[0][:2] + self.code_jxs[0][
                                                                                      11:20] + '000000000' + \
                                                               self.code_jxs[
                                                                   0][20:]
                                    # # :0 000 000 00 1 000 002 2N 1 0 00 0 0 0000!
                                    # elif self.code_jxs[0][17:19] == '2N':
                                    #     # 如果1穴无料
                                    #     if self.dict_yuan[self.sta_num][10] == '0':
                                    #         # 机械手2N料放1穴,二穴码不变
                                    #         self.dict_yuan[self.sta_num] = self.dict_yuan[self.sta_num][0:2] + \
                                    #                                        self.code_jxs[0][11:20] + self.dict_yuan[
                                    #                                                                      self.sta_num][
                                    #                                                                  11:21] + '11' + \
                                    #                                        self.dict_yuan[self.sta_num][23:]
                                    #         del self.code_jxs[0]
                                    #     # 如果2穴无料
                                    #     elif self.dict_yuan[self.sta_num][19] == '0':
                                    #         # 机械手2N料放2穴,一穴码不变
                                    #         self.dict_yuan[self.sta_num] = self.dict_yuan[self.sta_num][0:11] + \
                                    #                                        self.code_jxs[0][11:20] + self.dict_yuan[
                                    #                                                                      self.sta_num][
                                    #                                                                  11:21] + '11' + \
                                    #                                        self.dict_yuan[self.sta_num][23:]
                                    #         del self.code_jxs[0]
                                    # :0 002 002 2N 1 000 000 00 1 0 00 0 0 0000!
                                    # 如果机械手左爪是2N料
                                    elif self.code_jxs[0][8:10] == '2N':
                                        # 如果当前测试机1穴是空的
                                        if self.dict_yuan[self.sta_num][10] == '0':
                                            # 机械手2N料放1穴,二穴码不变
                                            self.dict_yuan[self.sta_num] = self.dict_yuan[self.sta_num][0:2] + \
                                                                           self.code_jxs[0][2:11] + self.dict_yuan[
                                                                                                        self.sta_num][
                                                                                                    11:21] + '11' + \
                                                                           self.dict_yuan[self.sta_num][23:]
                                            del self.code_jxs[0]
                                        # 如果当前测试机2穴是空的
                                        elif self.dict_yuan[self.sta_num][19] == '0':
                                            # 机械手2N料放2穴,一穴码不变
                                            self.dict_yuan[self.sta_num] = self.dict_yuan[self.sta_num][0:11] + \
                                                                           self.code_jxs[0][2:11] + self.dict_yuan[
                                                                                                        self.sta_num][
                                                                                                    11:21] + '11' + \
                                                                           self.dict_yuan[self.sta_num][23:]
                                            del self.code_jxs[0]
                                self.send_to_client(self.dict_socket[co_od], 'GM!')
                                # 将测试机状态置为 有料,测试中
                                self.dict_yuan[self.sta_num] = self.dict_yuan[self.sta_num][0:10] + '1' + \
                                                               self.dict_yuan[
                                                                   self.sta_num][
                                                               11:19] + '1' + \
                                                               self.dict_yuan[self.sta_num][20] + '11' + self.dict_yuan[
                                                                                                             self.sta_num][
                                                                                                         23:30]
                            except Exception as e:
                                self.sendxx_plc.emit(str(e))
                    # 收到后发送给终端GM指令,并且将当前测试机置为有料,和正在测试中
                    elif re_data == 'GM!':
                        sta_code = int(self.sta_num)
                        if self.comboBox_danshxue.currentText() == '单穴':
                            # if self.radioButton_dan.isChecked():
                            try:
                                # 用[21]=1表示一穴测试中 =0表示测试完 [22]=1表示一穴测试中 =0表示测试完
                                self.send_to_client(self.dict_socket[co_od], 'GM!')
                                self.dict_yuan[self.sta_num] = self.dict_yuan[self.sta_num][0:10] + '1' \
                                                               + self.dict_yuan[self.sta_num][11:21] + '1' \
                                                               + self.dict_yuan[self.sta_num][22:30]
                                self.del_test_result(sta_code)
                            except Exception as e:
                                self.sendxx_plc.emit(str(e))
                        elif self.comboBox_danshxue.currentText() == '双穴':
                            # elif self.radioButton_shuang.isChecked():
                            try:
                                # 用[21]=1表示一穴测试中 =0表示测试完 [22]=1表示一穴测试中 =0表示测试完
                                self.send_to_client(self.dict_socket[co_od], 'GM!')
                                self.dict_yuan[self.sta_num] = self.dict_yuan[self.sta_num][0:10] + '1' + \
                                                               self.dict_yuan[
                                                                   self.sta_num][
                                                               11:19] + '1' + \
                                                               self.dict_yuan[self.sta_num][20] + '11' + self.dict_yuan[
                                                                                                             self.sta_num][
                                                                                                         23:30]
                            except Exception as e:
                                self.sendxx_plc.emit(str(e))
                    elif re_data == 'SL!':
                        try:
                            self.send_sl()
                        except Exception as e:
                            self.sendxx_plc.emit(str(e))
        except Exception as e:
            self.sendxx_plc.emit(str(e))

    # 线程启动循环接收机械手信息
    def thread_receive_jxs(self):
        threading.Thread(target=self.receive_jxs, daemon=True).start()

    # 打开PLC串口
    def plc_conn(self):
        com_0 = self.comboBox_com_plc.currentText()
        bo_te = self.comboBox_botelv_plc.currentText()
        bo_telv = int(bo_te)
        jiao_yan = self.comboBox_jiaoyan_plc.currentText()
        shu_1 = self.comboBox_shujuwei_plc.currentText()
        shu_2 = int(shu_1)
        ting_0 = self.comboBox_tingzhiwei_plc.currentText()
        ting_1 = int(ting_0)
        try:
            self.ser_plc = serial.Serial(port='{}'.format(com_0), baudrate=bo_telv,
                                         bytesize=shu_2, parity='{}'.format(jiao_yan),
                                         stopbits=ting_1, timeout=0.1)
            self.thread_receive_plc()
            self.mianban_xianshi('PLC串口打开成功！')
        except Exception as e:
            self.mianban_xianshi(str(e))

    # 触发PLC报警
    def send_plc(self):
        try:
            if self.ser_plc.isOpen():
                bao_jing = self.lineEdit_toPlcMa.text() or '014501Y0000177'
                data_0 = '' + '{}'.format(bao_jing) + ''
                data = data_0.encode('UTF-8')
                self.ser_plc.write(data)
                send_data = 'To PLC:' + data.decode('UTF-8')
                self.mianban_xianshi(send_data)
        except Exception as e:
            self.sendxx_plc.emit(str(e))

    # 解除PLC报警
    def jiechu_Plc(self):
        try:
            if self.ser_plc.isOpen():
                data_0 = '014501Y0000076'
                data = data_0.encode('UTF-8')
                self.ser_plc.write(data)
                send_data = 'To PLC:' + data.decode('UTF-8')
                self.mianban_xianshi(send_data)
        except Exception as e:
            self.sendxx_plc.emit(str(e))

    # 循环读取PLC信息,要用线程执行,启动前保证PLC已经连接
    def receive_plc(self):
        try:
            while True:
                num = self.ser_plc.inWaiting()
                if num:
                    data = self.ser_plc.readline()
                    str_data = 'Fr PLC:' + data.decode('utf-8')
                    self.mianban_xianshi(str_data)
        except Exception as e:
            self.sendxx_plc.emit(str(e))

    # 线程接收PLC信息,只能点击一次这个函数
    def thread_receive_plc(self):
        threading.Thread(target=self.receive_plc, daemon=True).start()

    # 启动socket服务器,同时更新面板连接状态
    def server_start(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, True)  # 端口复用
        self.server_socket.bind(("", 8888))
        self.server_socket.listen(128)
        self.mianban_xianshi('服务器已开启')
        while True:
            new_client, ip_port = self.server_socket.accept()
            sta = ip_port[0][-1]
            in_sta = int(sta)
            str_ip_port = str(ip_port[0])
            self.dict_socket[str_ip_port] = new_client
            self.lianjie_zhaungtai(in_sta)
            sub_thread = threading.Thread(target=self.client_repay, args=(ip_port, new_client), daemon=True)
            sub_thread.start()

    # 接收处理终端信息 :01^0123456789AB^001^002^OK!  1^1  1^0^0
    def client_repay(self, ip_port, new_client):
        str_ip_port = str(ip_port[0])
        # 根据终端的IP地址选出当前的Socket
        for k, v in self.bind_csj.items():
            if str_ip_port == v:
                str_sta = k
        data = '终端{}连接'.format(str_sta) + ',当前在线:{}台'.format(len(self.dict_socket))
        # data = time_display + '客户端{}连接'.format(ip_port[0]) + '当前在线:{}台'.format(len(self.num_csj))
        self.mianban_xianshi(data)
        # 初始化30码,保证有几台终端,有几个测试码
        self.client_num()
        while True:
            try:
                data_0 = new_client.recv(1024)
            except:
                try:
                    int_1 = int(str_ip_port[-1])
                    # 清空面板显示
                    self.qingkong_lianjie(int_1)
                    # 将dict_socket里的ip地址删除,因为len(dict_socket)是当前在线终端数
                    del self.dict_socket[str_ip_port]
                    data2 = '终端{}异常断开'.format(str_sta) + ',当前在线:{}台'.format(len(self.dict_socket))
                    # 将dict_yuan里的对应码删除,避免客户端退出后还返回其30码
                    del self.dict_yuan[int_1]
                    self.mianban_xianshi(data2)
                    break
                except Exception as e:
                    self.alarm_write('循环接收终端数据:异常断开连接错误 -800')
                    break
            # 如果data_0有内容
            if data_0:
                # 收到任何指令都打印到面板
                data1 = 'Re:' + data_0.decode('utf-8') + ' Fr:' + '终端{}'.format(str_sta)
                self.mianban_xianshi(data1)
                data_0_0 = data_0.decode('utf-8')
                # 如果为192.168.0.101^0123456789AB^001^002^OK!1^1
                if len(data_0_0) == 41:
                    res_ter = data_0_0[-6:-4]  # OK
                    sta_xue = data_0_0[12]  # 1穴
                    ip_ter = data_0_0[0: 11]  # 192.168.0.1
                    zhan_0 = int(ip_ter[-1])
                    you_wu_0 = data_0_0[-1]
                    men_zt_0 = data_0_0[-3]
                    # 更新面板->门状态/料有无
                    if you_wu_0 == '1':
                        self.you_chanpin(zhan_0)
                    elif you_wu_0 == '0':
                        self.wu_chanpin(zhan_0)
                    if men_zt_0 == '1':
                        self.kaimen_zhuangtai(zhan_0)
                    elif men_zt_0 == '0':
                        self.guanmen_zhuangtai(zhan_0)
                    for k_0, v_0 in self.dict_socket.items():
                        if k_0 == ip_ter:
                            sta_0 = k_0[10]  # '1'
                    sta_1 = int(sta_0)  # 1 字典key
                    # 如果sta_1在字典的键里:
                    if sta_1 in self.dict_yuan:
                        # 如果生成的结果是1穴的
                        if sta_xue == '1':
                            # 如果终端生成结果位OK
                            if res_ter == 'OK':
                                #  用[21]=1表示测试中 =0表示测试完
                                try:  # :   门:1/0         当前站变上一站:002            '00'    当前站     结果
                                    self.dict_yuan[sta_1] = ':' + data_0_0[-3] + self.dict_yuan[sta_1][
                                                                                 5:8] + '00' + sta_0 + res_ter + \
                                                            data_0_0[40] + self.dict_yuan[sta_1][11:21] + '0' + \
                                                            self.dict_yuan[sta_1][22:30]
                                    self.test_result(zhan_0, 'OK')
                                except Exception as e:
                                    self.alarm_write('接收处理终端信息:生成单穴结果错误 -822')
                            # 如果终端生成结果位NG
                            else:
                                # 如果设置当前为1N->1N
                                if self.comboBox_3nshezhi.currentText() == '1N->1N':
                                    # 如果当前的状态为1N,将此站码设为2N
                                    if self.dict_yuan[sta_1][8:10] == '1N':
                                        try:
                                            self.dict_yuan[sta_1] = ':' + data_0_0[-3] + self.dict_yuan[sta_1][
                                                                                         5:8] + '00' + sta_0 + '2N' + \
                                                                    data_0_0[40] + self.dict_yuan[sta_1][11:21] + '0' + \
                                                                    self.dict_yuan[sta_1][22:30]
                                            self.test_result(zhan_0, '2N')
                                        except Exception as e:
                                            self.alarm_write('接收处理终端信息:生成单穴结果错误 -836')
                                    # 如果当前状态为2N,将此站码设为3N
                                    elif self.dict_yuan[sta_1][8:10] == '2N':
                                        try:
                                            self.dict_yuan[sta_1] = ':' + data_0_0[-3] + self.dict_yuan[sta_1][
                                                                                         5:8] + '00' + sta_0 + '3N' + \
                                                                    data_0_0[40] + self.dict_yuan[sta_1][11:21] + '0' + \
                                                                    self.dict_yuan[sta_1][22:30]
                                            self.test_result(zhan_0, '3N')
                                        except Exception as e:
                                            self.alarm_write('接收处理终端信息:生成单穴结果错误 -846')
                                    # 如果为其他状态:00/OK,将此站码设为1N
                                    else:
                                        try:
                                            self.dict_yuan[sta_1] = ':' + data_0_0[-3] + '000' + '00' + sta_0 + '1N' + \
                                                                    data_0_0[40] + self.dict_yuan[sta_1][11:21] + '0' + \
                                                                    self.dict_yuan[sta_1][22:30]
                                            self.test_result(zhan_0, '1N')
                                        except Exception as e:
                                            self.alarm_write('接收处理终端信息:生成单穴结果错误 -855')
                                # 如果设置的是1N->2N
                                elif self.comboBox_3nshezhi.currentText() == '1N->2N':
                                    # 如果当前的状态为1N,将此站码设为3N
                                    if self.dict_yuan[sta_1][8:10] == '1N':
                                        try:
                                            self.dict_yuan[sta_1] = ':' + data_0_0[-3] + self.dict_yuan[sta_1][
                                                                                         5:8] + '00' + sta_0 + '3N' + \
                                                                    data_0_0[40] + self.dict_yuan[sta_1][11:21] + '0' + \
                                                                    self.dict_yuan[sta_1][22:30]
                                            self.test_result(zhan_0, '3N')
                                        except Exception as e:
                                            self.alarm_write('接收处理终端信息:生成单穴结果错误 -867')
                                    # 如果当前状态为2N,将此站码设为3N
                                    elif self.dict_yuan[sta_1][8:10] == '2N':
                                        try:
                                            self.dict_yuan[sta_1] = ':' + data_0_0[-3] + self.dict_yuan[sta_1][
                                                                                         5:8] + '00' + sta_0 + '3N' + \
                                                                    data_0_0[40] + self.dict_yuan[sta_1][11:21] + '0' + \
                                                                    self.dict_yuan[sta_1][22:30]
                                            self.test_result(zhan_0, '3N')
                                        except Exception as e:
                                            self.alarm_write('接收处理终端信息:生成单穴结果错误 -877')
                                    # 如果为其他状态:00/OK,将此站码设为2N
                                    else:
                                        try:
                                            self.dict_yuan[sta_1] = ':' + data_0_0[-3] + '000' + '00' + sta_0 + '2N' + \
                                                                    data_0_0[40] + self.dict_yuan[sta_1][11:21] + '0' + \
                                                                    self.dict_yuan[sta_1][22:30]
                                            self.test_result(zhan_0, '2N')
                                        except Exception as e:
                                            self.alarm_write('接收处理终端信息:生成单穴结果错误 -886')
                                # 如果设置的是1N->3N
                                elif self.comboBox_3nshezhi.currentText() == '1N->3N':
                                    # 无论当前的状态为1N/2N/00/OK,此站码都为3N
                                    try:
                                        self.dict_yuan[sta_1] = ':' + data_0_0[-3] + self.dict_yuan[sta_1][
                                                                                     5:8] + '00' + sta_0 + '3N' + \
                                                                data_0_0[40] + self.dict_yuan[sta_1][11:21] + '0' + \
                                                                self.dict_yuan[sta_1][22:30]
                                        self.test_result(zhan_0, '3N')
                                    except Exception as e:
                                        self.alarm_write('接收处理终端信息:生成单穴结果错误 -897')
                        # 如果生成的结果位2穴的应该输出询问:为什么是二穴
                        elif sta_xue == '2':
                            self.mianban_xianshi('请检查为什么是2穴结果')
                            self.alarm_write('当前是单穴,输出2穴-598')
                    else:
                        self.mianban_xianshi('当前测试机不存在!')
                        self.alarm_write('测试机不存在却收到信息!-904')
                # 如果是双穴的就是43位-->192.168.0.101^0123456789AB^001^002^OK!1^1^1
                elif len(data_0_0) == 43:
                    res_ter = data_0_0[-9:-6]  # OK
                    sta_xue = data_0_0[12]  # 穴位号
                    ip_ter = data_0_0[0: 11]  # 192.168.0.1
                    zhan_0 = int(ip_ter[-1])
                    you_wu_0 = data_0_0[-3]
                    men_zt_0 = data_0_0[-5]
                    # 更新面板->门状态/料有无
                    if you_wu_0 == '1':
                        self.you_chanpin(zhan_0)
                    elif you_wu_0 == '0':
                        self.wu_chanpin(zhan_0)
                    if men_zt_0 == '1':
                        self.kaimen_zhuangtai(zhan_0)
                    elif men_zt_0 == '0':
                        self.guanmen_zhuangtai(zhan_0)
                    for k_0, v_0 in self.dict_socket.items():
                        if k_0 == ip_ter:
                            sta_0 = k_0[10]  # '1'
                    sta_1 = int(sta_0)  # 1
                    # 如果sta_1在字典的键里:
                    if sta_1 in self.dict_yuan:
                        # 如果生成的结果是1穴的
                        if sta_xue == '1':
                            # 如果终端生成结果位OK
                            if res_ter == 'OK':
                                #  用[21]=1表示测试中 =0表示测试完
                                try:  # :   门:1/0         当前站变上一站:002            '00'    当前站     结果
                                    self.dict_yuan[sta_1] = ':' + data_0_0[38] + self.dict_yuan[sta_1][
                                                                                 5:8] + '00' + sta_0 + res_ter + \
                                                            data_0_0[40] + self.dict_yuan[sta_1][11:21] + '0' + \
                                                            self.dict_yuan[sta_1][22:30]
                                    self.test_result(zhan_0, 'OK')
                                except Exception as e:
                                    self.alarm_write('接收处理终端信息43位:生成单穴结果错误 -940')
                            # 如果终端生成结果位NG
                            else:
                                # 如果设置当前为1N->1N
                                if self.comboBox_3nshezhi == '1N->1N':
                                    # 如果当前的状态为1N,将此站码设为2N
                                    if self.dict_yuan[sta_1][8:10] == '1N':
                                        try:
                                            self.dict_yuan[sta_1] = ':' + data_0_0[38] + self.dict_yuan[sta_1][
                                                                                         5:8] + '00' + sta_0 + '2N' + \
                                                                    data_0_0[40] + self.dict_yuan[sta_1][11:21] + '0' + \
                                                                    self.dict_yuan[sta_1][22:30]
                                            self.test_result(zhan_0, '2N')
                                        except Exception as e:
                                            self.alarm_write('接收处理终端信息43位:生成单穴结果错误 -954')
                                    # 如果当前状态为2N,将此站码设为3N
                                    elif self.dict_yuan[sta_1][8:10] == '2N':
                                        try:
                                            self.dict_yuan[sta_1] = ':' + data_0_0[38] + self.dict_yuan[sta_1][
                                                                                         5:8] + '00' + sta_0 + '3N' + \
                                                                    data_0_0[40] + self.dict_yuan[sta_1][11:21] + '0' + \
                                                                    self.dict_yuan[sta_1][22:30]
                                            self.test_result(zhan_0, '3N')
                                        except Exception as e:
                                            self.alarm_write('接收处理终端信息43位:生成单穴结果错误 -964')
                                    # 如果为其他状态:00/OK,将此站码设为1N
                                    else:
                                        try:
                                            self.dict_yuan[sta_1] = ':' + data_0_0[38] + '000' + '00' + sta_0 + '1N' + \
                                                                    data_0_0[40] + self.dict_yuan[sta_1][11:21] + '0' + \
                                                                    self.dict_yuan[sta_1][22:30]
                                            self.test_result(zhan_0, '1N')
                                        except Exception as e:
                                            self.alarm_write(e)
                                # 如果设置的是1N->2N
                                elif self.comboBox_3nshezhi == '1N->2N':
                                    # 如果当前状态为2N,将此站码设为3N
                                    if self.dict_yuan[sta_1][8:10] == '2N':
                                        try:
                                            self.dict_yuan[sta_1] = ':' + data_0_0[38] + self.dict_yuan[sta_1][
                                                                                         5:8] + '00' + sta_0 + '3N' + \
                                                                    data_0_0[40] + self.dict_yuan[sta_1][11:21] + '0' + \
                                                                    self.dict_yuan[sta_1][22:30]
                                            self.test_result(zhan_0, '3N')
                                        except Exception as e:
                                            self.alarm_write(e)
                                    # 如果为其他状态:00/OK/1N,将此站码设为1N
                                    else:
                                        try:
                                            self.dict_yuan[sta_1] = ':' + data_0_0[38] + '000' + '00' + sta_0 + '2N' + \
                                                                    data_0_0[40] + self.dict_yuan[sta_1][11:21] + '0' + \
                                                                    self.dict_yuan[sta_1][22:30]
                                            self.test_result(zhan_0, '2N')
                                        except Exception as e:
                                            self.alarm_write(e)
                                # 如果设置的是1N->3N
                                elif self.comboBox_3nshezhi == '1N->3N':
                                    # 如果为其他状态:00/OK/1N,将此站码设为1N
                                    try:
                                        self.dict_yuan[sta_1] = ':' + data_0_0[
                                            38] + '000' + '00' + sta_0 + '3N' + \
                                                                data_0_0[40] + self.dict_yuan[sta_1][
                                                                               11:21] + '0' + \
                                                                self.dict_yuan[sta_1][22:30]
                                        self.test_result(zhan_0, '3N')
                                        self.test_result(zhan_0, '2N')
                                    except Exception as e:
                                        self.alarm_write(e)
                        # 如果生成的结果位2穴的1^1^1
                        elif sta_xue == '2':
                            if res_ter == 'OK':
                                # 双穴时,一台测试完要等另一台再测试完才可以开门
                                try:
                                    self.dict_yuan[sta_1] = ':' + data_0_0[38] + self.dict_yuan[sta_1][2:10] + data_0_0[
                                        40] + self.dict_yuan[sta_1][14:17] + \
                                                            '00' + sta_0 + res_ter + data_0_0[42] + self.dict_yuan[
                                                                                                        sta_1][
                                                                                                    20:22] + '0' + \
                                                            self.dict_yuan[sta_1][23:30]
                                except Exception as e:
                                    self.alarm_write(e)
                            # 如果终端生成结果位NG
                            else:
                                # 如果设置当前为1N->1N
                                if self.comboBox_3nshezhi == '1N->1N':
                                    # 如果当前的状态为1N,将此站码设为2N
                                    if self.dict_yuan[sta_1][8:10] == '1N':
                                        try:
                                            self.dict_yuan[sta_1] = ':' + data_0_0[38] + self.dict_yuan[sta_1][2:10] + \
                                                                    data_0_0[40] + self.dict_yuan[sta_1][
                                                                                   14:17] + '00' + sta_0 + '2N' + \
                                                                    data_0_0[
                                                                        42] + self.dict_yuan[sta_1][20:22] + '0' + \
                                                                    self.dict_yuan[sta_1][23:30]
                                        except Exception as e:
                                            self.alarm_write(e)
                                    # 如果当前状态为2N,将此站码设为3N
                                    elif self.dict_yuan[sta_1][8:10] == '2N':
                                        try:
                                            self.dict_yuan[sta_1] = ':' + data_0_0[38] + self.dict_yuan[sta_1][2:10] + \
                                                                    data_0_0[40] + self.dict_yuan[sta_1][
                                                                                   14:17] + '00' + sta_0 + '3N' + \
                                                                    data_0_0[
                                                                        42] + self.dict_yuan[sta_1][20:22] + '0' + \
                                                                    self.dict_yuan[sta_1][23:30]
                                        except Exception as e:
                                            self.alarm_write(e)
                                    # 如果当前状态为00/OK,将此站码设为1N
                                    else:
                                        try:
                                            self.dict_yuan[sta_1] = ':' + data_0_0[38] + self.dict_yuan[sta_1][2:10] + \
                                                                    data_0_0[40] + '00000' + sta_0 + '1N' + \
                                                                    data_0_0[42] + self.dict_yuan[sta_1][20:22] + '0' + \
                                                                    self.dict_yuan[sta_1][23:30]
                                        except Exception as e:
                                            self.alarm_write(e)
                                # 如果设置的是1N->2N
                                elif self.comboBox_3nshezhi == '1N->2N':
                                    # 如果当前状态为2N,将此站码设为3N
                                    if self.dict_yuan[sta_1][8:10] == '2N':
                                        try:
                                            self.dict_yuan[sta_1] = ':' + data_0_0[38] + self.dict_yuan[sta_1][2:10] + \
                                                                    data_0_0[40] + self.dict_yuan[sta_1][
                                                                                   14:17] + '00' + sta_0 + '3N' + \
                                                                    data_0_0[
                                                                        42] + self.dict_yuan[sta_1][20:22] + '0' + \
                                                                    self.dict_yuan[sta_1][23:30]
                                        except Exception as e:
                                            self.alarm_write(e)
                                    # 如果当前状态为00/OK/1N,将此站码设为2N
                                    else:
                                        try:
                                            self.dict_yuan[sta_1] = ':' + data_0_0[38] + self.dict_yuan[sta_1][2:10] + \
                                                                    data_0_0[40] + '00000' + sta_0 + '2N' + \
                                                                    data_0_0[42] + self.dict_yuan[sta_1][20:22] + '0' + \
                                                                    self.dict_yuan[sta_1][23:30]
                                        except Exception as e:
                                            self.alarm_write(e)
                                # 如果设置的是1N->3N
                                elif self.comboBox_3nshezhi == '1N->3N':
                                    # 如果当前状态为00/OK/1N/2N,将此站码设为3N
                                    try:
                                        self.dict_yuan[sta_1] = ':' + data_0_0[38] + self.dict_yuan[sta_1][2:10] + \
                                                                data_0_0[40] + '00000' + sta_0 + '3N' + \
                                                                data_0_0[42] + self.dict_yuan[sta_1][20:22] + '0' + \
                                                                self.dict_yuan[sta_1][23:30]
                                    except Exception as e:
                                        self.alarm_write(e)
                    else:
                        self.mianban_xianshi('当前测试机不存在!')
                        self.alarm_write('测试机不存在却收到信息!-516')
                #  如果为192.168.0.101^0123456789AB^001^002^OK!/192.168.0.102^0123456789AB^001^002^NG!
                elif len(data_0_0) == 38:
                    res_ter = data_0_0[-3:-1]  # OK
                    sta_xue = data_0_0[12]  # 穴位号
                    ip_ter = data_0_0[0: 11]  # 192.168.0.1
                    zhan_0 = int(ip_ter[-1])
                    for k_0, v_0 in self.dict_socket.items():
                        if k_0 == ip_ter:
                            sta_0 = k_0[10]  # '1'
                    sta_1 = int(sta_0)
                    # 如果sta_1在字典的键里:
                    if sta_1 in self.dict_yuan:
                        # 如果生成的结果是1穴的
                        if sta_xue == '1':
                            # 如果终端生成结果位OK
                            if res_ter == 'OK':
                                #  用[21]=1表示测试中 =0表示测试完
                                try:
                                    self.dict_yuan[sta_1] = ':0' + self.dict_yuan[sta_1][5:8] + '00' + sta_0 + res_ter + \
                                                            self.dict_yuan[sta_1][10:21] + '0' + self.dict_yuan[sta_1][
                                                                                                 22:30]
                                    self.test_result(zhan_0, 'OK')
                                except Exception as e:
                                    self.alarm_write(e)
                            # 如果终端生成结果位NG
                            else:
                                # 如果设置当前为1N->1N
                                if self.comboBox_3nshezhi == '1N->1N':
                                    # 如果当前的状态为1N,将此站码设为2N
                                    if self.dict_yuan[sta_1][8:10] == '1N':
                                        try:
                                            self.dict_yuan[sta_1] = ':0' + self.dict_yuan[sta_1][
                                                                           5:8] + '00' + sta_0 + '2N' + \
                                                                    self.dict_yuan[sta_1][10:21] + '0' + self.dict_yuan[
                                                                                                             sta_1][
                                                                                                         22:30]
                                            self.test_result(zhan_0, '2N')
                                        except Exception as e:
                                            self.alarm_write(e)
                                    # 如果当前状态为2N,将此站码设为3N
                                    elif self.dict_yuan[sta_1][8:10] == '2N':
                                        try:
                                            self.dict_yuan[sta_1] = ':0' + self.dict_yuan[sta_1][
                                                                           5:8] + '00' + sta_0 + '3N' + \
                                                                    self.dict_yuan[sta_1][10:21] + '0' + self.dict_yuan[
                                                                                                             sta_1][
                                                                                                         22:30]
                                            self.test_result(zhan_0, '3N')
                                        except Exception as e:
                                            self.alarm_write(e)
                                    # 如果为其他状态:00/OK,将此站码设为1N
                                    else:
                                        try:
                                            self.dict_yuan[sta_1] = ':0000' + '00' + sta_0 + '1N' + self.dict_yuan[
                                                                                                        sta_1][
                                                                                                    10:21] + '0' + \
                                                                    self.dict_yuan[sta_1][22:30]
                                            self.test_result(zhan_0, '1N')
                                        except Exception as e:
                                            self.alarm_write(e)
                                # 如果设置当前为1N->2N
                                elif self.comboBox_3nshezhi == '1N->2N':
                                    # 如果当前状态为2N,将此站码设为3N
                                    if self.dict_yuan[sta_1][8:10] == '2N':
                                        try:
                                            self.dict_yuan[sta_1] = ':0' + self.dict_yuan[sta_1][
                                                                           5:8] + '00' + sta_0 + '3N' + \
                                                                    self.dict_yuan[sta_1][10:21] + '0' + self.dict_yuan[
                                                                                                             sta_1][
                                                                                                         22:30]
                                            self.test_result(zhan_0, '3N')
                                        except Exception as e:
                                            self.alarm_write(e)
                                    # 如果为其他状态:00/OK/1N,将此站码设为2N
                                    else:
                                        try:
                                            self.dict_yuan[sta_1] = ':0000' + '00' + sta_0 + '2N' + self.dict_yuan[
                                                                                                        sta_1][
                                                                                                    10:21] + '0' + \
                                                                    self.dict_yuan[sta_1][22:30]
                                            self.test_result(zhan_0, '2N')
                                        except Exception as e:
                                            self.alarm_write(e)
                                # 如果设置当前为1N->3N
                                elif self.comboBox_3nshezhi == '1N->3N':
                                    try:
                                        self.dict_yuan[sta_1] = ':0000' + '00' + sta_0 + '3N' + self.dict_yuan[
                                                                                                    sta_1][
                                                                                                10:21] + '0' + \
                                                                self.dict_yuan[sta_1][22:30]
                                        self.test_result(zhan_0, '3N')
                                    except Exception as e:
                                        self.alarm_write(e)
                            # 如果生成的结果位2穴的
                        elif sta_xue == '2':
                            if res_ter == 'OK':
                                # 双穴时,一台测试完要等另一台再测试完才可以开门
                                try:
                                    self.dict_yuan[sta_1] = self.dict_yuan[sta_1][0:11] + self.dict_yuan[sta_1][14:17] + \
                                                            '00' + sta_0 + res_ter + self.dict_yuan[sta_1][
                                                                                     19:22] + '0' + \
                                                            self.dict_yuan[sta_1][23:30]
                                except Exception as e:
                                    self.alarm_write(e)
                            # 如果终端生成结果位NG
                            else:
                                # 如果设置当前为1N->1N
                                if self.comboBox_3nshezhi == '1N->1N':
                                    # 如果当前的状态为1N,将此站码设为2N
                                    if self.dict_yuan[sta_1][8:10] == '1N':
                                        try:
                                            self.dict_yuan[sta_1] = self.dict_yuan[sta_1][0:11] + self.dict_yuan[sta_1][
                                                                                                  14:17] + \
                                                                    '00' + sta_0 + '2N' + self.dict_yuan[sta_1][
                                                                                          19:22] + '0' + \
                                                                    self.dict_yuan[sta_1][23:30]
                                        except Exception as e:
                                            self.alarm_write(e)
                                    # 如果当前状态为2N,将此站码设为3N
                                    elif self.dict_yuan[sta_1][8:10] == '2N':
                                        try:
                                            self.dict_yuan[sta_1] = self.dict_yuan[sta_1][0:11] + self.dict_yuan[sta_1][
                                                                                                  14:17] + \
                                                                    '00' + sta_0 + '3N' + self.dict_yuan[sta_1][
                                                                                          19:22] + '0' + \
                                                                    self.dict_yuan[sta_1][23:30]
                                        except Exception as e:
                                            self.alarm_write(e)
                                    # 如果当前状态为00/OK,将此站码设为1N
                                    else:
                                        try:
                                            self.dict_yuan[sta_1] = self.dict_yuan[sta_1][0:14] + '00' + sta_0 + '1N' + \
                                                                    self.dict_yuan[sta_1][19:22] + '0' + self.dict_yuan[
                                                                                                             sta_1][
                                                                                                         23:30]
                                        except Exception as e:
                                            self.alarm_write(e)
                                # 如果设置当前为1N->2N
                                elif self.comboBox_3nshezhi == '1N->2N':
                                    # 如果当前状态为2N,将此站码设为3N
                                    if self.dict_yuan[sta_1][8:10] == '2N':
                                        try:
                                            self.dict_yuan[sta_1] = self.dict_yuan[sta_1][0:11] + self.dict_yuan[sta_1][
                                                                                                  14:17] + \
                                                                    '00' + sta_0 + '3N' + self.dict_yuan[sta_1][
                                                                                          19:22] + '0' + \
                                                                    self.dict_yuan[sta_1][23:30]
                                        except Exception as e:
                                            self.alarm_write(e)
                                    # 如果当前状态为00/OK/1N,将此站码设为2N
                                    else:
                                        try:
                                            self.dict_yuan[sta_1] = self.dict_yuan[sta_1][0:14] + '00' + sta_0 + '2N' + \
                                                                    self.dict_yuan[sta_1][19:22] + '0' + self.dict_yuan[
                                                                                                             sta_1][
                                                                                                         23:30]
                                        except Exception as e:
                                            self.alarm_write(e)
                                # 如果设置当前为1N->3N
                                elif self.comboBox_3nshezhi == '1N->3N':
                                    try:
                                        self.dict_yuan[sta_1] = self.dict_yuan[sta_1][0:14] + '00' + sta_0 + '3N' + \
                                                                self.dict_yuan[sta_1][19:22] + '0' + self.dict_yuan[
                                                                                                         sta_1][
                                                                                                     23:30]
                                    except Exception as e:
                                        self.alarm_write(e)
                    else:
                        self.mianban_xianshi('当前测试机不存在!')
                        self.alarm_write('测试机不存在却收到信息!-615')
                # 如果为192.168.0.11^0
                elif len(data_0_0) == 14:
                    ip_ter1 = data_0_0[0:11]
                    zhan_0 = int(ip_ter1[-1])
                    you_wu_0 = data_0_0[-1]
                    men_zt_0 = data_0_0[-3]
                    # 更新面板->门状态/料有无
                    if you_wu_0 == '1':
                        self.you_chanpin(zhan_0)
                    elif you_wu_0 == '0':
                        self.wu_chanpin(zhan_0)
                    if men_zt_0 == '1':
                        self.kaimen_zhuangtai(zhan_0)
                    elif men_zt_0 == '0':
                        self.guanmen_zhuangtai(zhan_0)
                    for k_1, v_1 in self.bind_csj.items():
                        if v_1 == ip_ter1:
                            sta_2 = k_1  # '1'
                    sta_3 = int(sta_2)
                    if sta_3 in self.dict_yuan:
                        self.dict_yuan[sta_3] = ':' + data_0_0[11] + self.dict_yuan[sta_3][2:10] + data_0_0[13] + \
                                                self.dict_yuan[sta_3][11:30]
                    else:
                        self.mianban_xianshi('当前测试机不存在!')
                        self.alarm_write('测试机不存在却收到信息!-628')
                # 如果为192.168.0.11^0^0  双穴模式下1穴和2穴状态都要考虑   3: ':0 000 003 OK 0 000 002 NG 0 000000000!'
                elif len(data_0_0) == 16:
                    ip_ter1 = data_0_0[0:11]
                    zhan_0 = int(ip_ter1[-1])
                    you_wu_0 = data_0_0[-3]
                    men_zt_0 = data_0_0[-5]
                    # 更新面板->门状态/料有无
                    if you_wu_0 == '1':
                        self.you_chanpin(zhan_0)
                    elif you_wu_0 == '0':
                        self.wu_chanpin(zhan_0)
                    if men_zt_0 == '1':
                        self.kaimen_zhuangtai(zhan_0)
                    elif men_zt_0 == '0':
                        self.guanmen_zhuangtai(zhan_0)
                    for k_2, v_2 in self.bind_csj.items():
                        if v_2 == ip_ter1:
                            sta_3 = k_2  # '1'
                    sta_4 = int(sta_3)
                    if sta_4 in self.dict_yuan:
                        self.dict_yuan[sta_4] = ':' + data_0_0[11] + self.dict_yuan[sta_4][2:10] + data_0_0[13] + \
                                                self.dict_yuan[sta_4][11:19] + data_0_0[15] + self.dict_yuan[sta_4][
                                                                                              21:30]
                    else:
                        self.mianban_xianshi('当前测试机不存在!')
                        self.alarm_write('测试机不存在却收到信息!-643')
                # 192.168.0.1OF  测试机回复的收到开门指令,同时更新开门状态
                elif len(data_0_0) == 13:
                    if data_0_0[11:13] == 'OF':
                        kai_sta = int(data_0_0[-3])
                        # 面板开门状态更新和字典值更新
                        self.kaimen_zhuangtai(kai_sta)
                        self.dict_yuan[kai_sta] = ':1' + self.dict_yuan[kai_sta][2:]
                    # 192.168.0.1CF 测试机回复的收到关门指令-->中控收到关门信息后开始对门进行计时
                    elif data_0_0[11:13] == 'CF':
                        # 更新关门状态和字典值
                        guan_sta = int(data_0_0[-3])
                        self.guanmen_zhuangtai(guan_sta)
                        self.dict_yuan[guan_sta] = ':0' + self.dict_yuan[guan_sta][2:]
                        # 开启计时
                        ji_shi = self.comboBox_yanshi.currentText()
                        if ji_shi == '延时':
                            jishi_ip = data_0_0[0:11]
                            self.calu_time(jishi_ip)
                    # 192.168.0.1pb 终端回复的连续三次fail需要屏蔽-->中控收到后开始对测试机屏蔽
                    elif data_0_0[11:13] == 'pb':
                        int_sta = int(data_0_0[10])
                        self.ping_bi(int_sta)
                    # 192.168.0.1pb 终端回复的连续三次fail需要屏蔽-->中控收到后开始对测试机屏蔽
                    elif data_0_0[11:13] == 'jc':
                        int_sta = int(data_0_0[10])
                        self.re_pingbi(int_sta)
                # 获取当前所有30码,'终端状态'
                elif data_0_0 == 'ZDZT':
                    try:
                        str_0 = '当前测试机{},当前机械手{}'.format(self.dict_yuan, self.code_jxs)
                        self.send_to_client(new_client, str_0)
                    except Exception as e:
                        self.sendxx_plc.emit(str(e))
                # 获取当前所有socket,'通讯状态'
                elif data_0_0 == 'TXZT':
                    try:
                        str_1 = '当前所有socket:{}'.format(self.dict_socket)
                        self.send_to_client(new_client, str_1)
                    except Exception as e:
                        self.sendxx_plc.emit(str(e))
            # 如果data_0没有内容,说明客户端断开连接
            else:
                try:
                    int_1 = int(str_ip_port[-1])
                    # 清空面板显示
                    self.qingkong_lianjie(int_1)
                    # 将dict_socket里的ip地址删除,因为len(dict_socket)是当前在线终端数
                    del self.dict_socket[str_ip_port]
                    data2 = '终端{}断开'.format(str_sta) + ',当前在线:{}台'.format(len(self.dict_socket))
                    # 将dict_yuan里的对应码删除,避免客户端退出后还返回其30码
                    del self.dict_yuan[int_1]
                    self.mianban_xianshi(data2)
                    break
                except Exception as e:
                    self.alarm_write('循环接收终端数据:断开连接错误 -1367')
                    break
        new_client.close()

    # 对当前产品进行计时,超时后发送信息给对应的终端
    def calu_time(self, ip):
        sec = self.lineEdit_chaoshi.text()
        socket = self.dict_socket[ip]
        int_sec = int(sec)
        ji_shi = self.comboBox_yanshi.currentText()
        if ji_shi == '延时':
            while True:
                time.sleep(int_sec)
                # 需要将当前产品更新为1N/2N/3N
                ip_0 = int(ip[-1])
                # 如果当前的状态为1N,将此站码设为2N
                if self.dict_yuan[ip_0][8:10] == '1N':
                    try:
                        self.dict_yuan[ip_0] = ':0' + self.dict_yuan[ip_0][5:8] + '00' + str(ip_0) + '2N' + \
                                               self.dict_yuan[ip_0][10:21] + '0' + self.dict_yuan[ip_0][
                                                                                   22:30]
                    except Exception as e:
                        self.alarm_write('产品计时错误 -1389')
                # 如果当前状态为2N,将此站码设为3N
                elif self.dict_yuan[ip_0][8:10] == '2N':
                    try:
                        self.dict_yuan[ip_0] = ':0' + self.dict_yuan[ip_0][5:8] + '00' + str(ip_0) + '3N' + \
                                               self.dict_yuan[ip_0][10:21] + '0' + self.dict_yuan[ip_0][
                                                                                   22:30]
                    except Exception as e:
                        self.alarm_write('产品计时错误 -1397')
                # 如果为其他状态:00/OK,将此站码设为1N
                else:
                    try:
                        self.dict_yuan[ip_0] = ':0000' + '00' + str(ip_0) + '1N' + self.dict_yuan[ip_0][
                                                                                   10:21] + '0' + \
                                               self.dict_yuan[ip_0][22:30]
                        self.send_to_client(socket, '终端{}已超时'.format(ip[-1]))
                    except Exception as e:
                        self.alarm_write('产品计时错误 -1406')
                break

    # 网口发送信息(多客户端)
    def send_to_client(self, new_socket, msg):
        if new_socket:
            try:
                new_socket.send(msg.encode('utf-8'))
                # data2 = 'send:' + msg + ' to' + ':终端:{}'.format(self.sta_num) 不能满足所有场景
                data2 = 'To:' + msg
                self.mianban_xianshi(data2)
            except Exception as e:
                # data2 = 'send:' + msg + ' to' + ':终端:{}'.format(self.sta_num) + '发送失败!'
                data2 = 'ERR! ' + 'To:' + msg + '失败!'
                self.mianban_xianshi(data2)
                self.alarm_write('网口发送信息错误: -1421')
                return
        else:
            print('没有客户端连接')

    # 线程启动服务器
    def thread_server_start(self):
        threading.Thread(target=self.server_start, daemon=True).start()

    # 保存配置文件
    def save_peizhi(self):
        danshu_xue = self.comboBox_danshxue.currentText()
        shifou_sl = self.comboBox_shifousl.currentText()
        shifou_ys = self.comboBox_yanshi.currentText()
        ys_shijian = self.lineEdit_chaoshi.text()
        shezhi_3n = self.comboBox_3nshezhi.currentText()
        plc_baoji = self.lineEdit_toPlcMa.text()
        plc_com = self.comboBox_com_plc.currentText()
        plc_btlv = self.comboBox_botelv_plc.currentText()
        plc_jywe = self.comboBox_jiaoyan_plc.currentText()
        plc_sjwe = self.comboBox_shujuwei_plc.currentText()
        plc_tzwe = self.comboBox_tingzhiwei_plc.currentText()
        jxs_com = self.comboBox_com_jxs.currentText()
        jxs_btlv = self.comboBox_botelv_jxs.currentText()
        jxs_jywe = self.comboBox_jiaoyan_jxs.currentText()
        jxs_sjwe = self.comboBox_shujuwei_jxs.currentText()
        jxs_tzwe = self.comboBox_tingzhiwei_jxs.currentText()
        config = ConfigParser()
        config.set('DEFAULT', 'danshu_xue', danshu_xue)
        config.set('DEFAULT', 'shifou_sl', shifou_sl)
        config.set('DEFAULT', 'shifou_ys', shifou_ys)
        config.set('DEFAULT', 'ys_shijian', ys_shijian)
        config.set('DEFAULT', 'shezhi_3n', shezhi_3n)
        config.set('DEFAULT', 'plc_baoji', plc_baoji)
        config.set('DEFAULT', 'plc_com', plc_com)
        config.set('DEFAULT', 'plc_btlv', plc_btlv)
        config.set('DEFAULT', 'plc_jywe', plc_jywe)
        config.set('DEFAULT', 'plc_sjwe', plc_sjwe)
        config.set('DEFAULT', 'plc_tzwe', plc_tzwe)
        config.set('DEFAULT', 'jxs_com', jxs_com)
        config.set('DEFAULT', 'jxs_btlv', jxs_btlv)
        config.set('DEFAULT', 'jxs_jywe', jxs_jywe)
        config.set('DEFAULT', 'jxs_sjwe', jxs_sjwe)
        config.set('DEFAULT', 'jxs_tzwe', jxs_tzwe)
        # app_path = os.path.dirname(sys.executable)
        # config_path = app_path + '\\config.ini'
        try:
            with open('.\config_zk.ini', 'w') as stream:
                config.write(stream)
            stream.close()
        except:
            self.alarm_write('保存中控配置文件错误')

    # 读取配置文件
    def set_default(self):
        config = ConfigParser()
        try:
            config.read(".\config_zk.ini", encoding='gbk')
            danshu_xue = config.get('DEFAULT', 'danshu_xue')
            shifou_sl = config.get('DEFAULT', 'shifou_sl')
            shifou_ys = config.get('DEFAULT', 'shifou_ys')
            ys_shijian = config.get('DEFAULT', 'ys_shijian')
            shezhi_3n = config.get('DEFAULT', 'shezhi_3n')
            plc_baoji = config.get('DEFAULT', 'plc_baoji')
            plc_com = config.get('DEFAULT', 'plc_com')
            plc_btlv = config.get('DEFAULT', 'plc_btlv')
            plc_jywe = config.get('DEFAULT', 'plc_jywe')
            plc_sjwe = config.get('DEFAULT', 'plc_sjwe')
            plc_tzwe = config.get('DEFAULT', 'plc_tzwe')
            jxs_com = config.get('DEFAULT', 'jxs_com')
            jxs_btlv = config.get('DEFAULT', 'jxs_btlv')
            jxs_jywe = config.get('DEFAULT', 'jxs_jywe')
            jxs_sjwe = config.get('DEFAULT', 'jxs_sjwe')
            jxs_tzwe = config.get('DEFAULT', 'jxs_tzwe')
            self.comboBox_danshxue.setCurrentText(danshu_xue)
            self.comboBox_shifousl.setCurrentText(shifou_sl)
            self.comboBox_yanshi.setCurrentText(shifou_ys)
            self.lineEdit_chaoshi.setText(ys_shijian)
            self.comboBox_3nshezhi.setCurrentText(shezhi_3n)
            self.lineEdit_toPlcMa.setText(plc_baoji)
            self.comboBox_com_plc.setCurrentText(plc_com)
            self.comboBox_botelv_plc.setCurrentText(plc_btlv)
            self.comboBox_jiaoyan_plc.setCurrentText(plc_jywe)
            self.comboBox_shujuwei_plc.setCurrentText(plc_sjwe)
            self.comboBox_tingzhiwei_plc.setCurrentText(plc_tzwe)
            self.comboBox_com_jxs.setCurrentText(jxs_com)
            self.comboBox_botelv_jxs.setCurrentText(jxs_btlv)
            self.comboBox_jiaoyan_jxs.setCurrentText(jxs_jywe)
            self.comboBox_shujuwei_jxs.setCurrentText(jxs_sjwe)
            self.comboBox_tingzhiwei_jxs.setCurrentText(jxs_tzwe)
        except:
            self.alarm_write('读取中控配置文件错误')

    # 更新面板连接状态
    def lianjie_zhaungtai(self, sta):
        if sta == 1:
            self.lineEdit_1lian.setText('1站联机')
            self.lineEdit_1lian.setStyleSheet('color: rgb(0, 0, 0)')
        elif sta == 2:
            self.lineEdit_2lian.setText('2站联机')
            self.lineEdit_2lian.setStyleSheet('color: rgb(0, 0, 0)')
        elif sta == 3:
            self.lineEdit_3lian.setText('3站联机')
            self.lineEdit_3lian.setStyleSheet('color: rgb(0, 0, 0)')
        elif sta == 4:
            self.lineEdit_4lian.setText('4站联机')
            self.lineEdit_4lian.setStyleSheet('color: rgb(0, 0, 0)')

    # 清空连接状态
    def qingkong_lianjie(self, sta):
        if sta == 1:
            self.lineEdit_1lian.clear()
            self.lineEdit_1lian.setStyleSheet('color: rgb(127, 127, 127)')
            self.lineEdit_1kaimen.clear()
            self.lineEdit_1kaimen.setStyleSheet('color: rgb(127, 127, 127)')
            self.lineEdit_1youwu.clear()
            self.lineEdit_1youwu.setStyleSheet('color: rgb(127, 127, 127)')
        elif sta == 2:
            self.lineEdit_2lian.clear()
            self.lineEdit_2lian.setStyleSheet('color: rgb(127, 127, 127)')
            self.lineEdit_2kaimen.clear()
            self.lineEdit_2kaimen.setStyleSheet('color: rgb(127, 127, 127)')
            self.lineEdit_2youwu.clear()
            self.lineEdit_2youwu.setStyleSheet('color: rgb(127, 127, 127)')
        elif sta == 3:
            self.lineEdit_3lian.clear()
            self.lineEdit_3lian.setStyleSheet('color: rgb(127, 127, 127)')
            self.lineEdit_3kaimen.clear()
            self.lineEdit_3kaimen.setStyleSheet('color: rgb(127, 127, 127)')
            self.lineEdit_3youwu.clear()
            self.lineEdit_3youwu.setStyleSheet('color: rgb(127, 127, 127)')
        elif sta == 4:
            self.lineEdit_4lian.clear()
            self.lineEdit_4lian.setStyleSheet('color: rgb(127, 127, 127)')
            self.lineEdit_4kaimen.clear()
            self.lineEdit_4kaimen.setStyleSheet('color: rgb(127, 127, 127)')
            self.lineEdit_4youwu.clear()
            self.lineEdit_4youwu.setStyleSheet('color: rgb(127, 127, 127)')
        self.del_test_result(sta)
        self.jiechu_pingb(sta)

    # 更新开门状态
    def kaimen_zhuangtai(self, sta):
        if sta == 1:
            self.lineEdit_1kaimen.setText('开门')
            self.lineEdit_1kaimen.setStyleSheet('color: rgb(0, 0, 0)')
        elif sta == 2:
            self.lineEdit_2kaimen.setText('开门')
            self.lineEdit_2kaimen.setStyleSheet('color: rgb(0, 0, 0)')
        elif sta == 3:
            self.lineEdit_3kaimen.setText('开门')
            self.lineEdit_3kaimen.setStyleSheet('color: rgb(0, 0, 0)')
        elif sta == 4:
            self.lineEdit_4kaimen.setText('开门')
            self.lineEdit_4kaimen.setStyleSheet('color: rgb(0, 0, 0)')

    # 更新开门状态
    def guanmen_zhuangtai(self, sta):
        if sta == 1:
            self.lineEdit_1kaimen.setText('关门')
            self.lineEdit_1kaimen.setStyleSheet('color: rgb(0, 0, 0)')
        elif sta == 2:
            self.lineEdit_2kaimen.setText('关门')
            self.lineEdit_2kaimen.setStyleSheet('color: rgb(0, 0, 0)')
        elif sta == 3:
            self.lineEdit_3kaimen.setText('关门')
            self.lineEdit_3kaimen.setStyleSheet('color: rgb(0, 0, 0)')
        elif sta == 4:
            self.lineEdit_4kaimen.setText('关门')
            self.lineEdit_4kaimen.setStyleSheet('color: rgb(0, 0, 0)')

    # 更新产品有状态
    def you_chanpin(self, sta):
        if sta == 1:
            self.lineEdit_1youwu.setText('有料')
            self.lineEdit_1youwu.setStyleSheet('color: rgb(0, 0, 0)')
        elif sta == 2:
            self.lineEdit_2youwu.setText('有料')
            self.lineEdit_2youwu.setStyleSheet('color: rgb(0, 0, 0)')
        elif sta == 3:
            self.lineEdit_3youwu.setText('有料')
            self.lineEdit_3youwu.setStyleSheet('color: rgb(0, 0, 0)')
        elif sta == 4:
            self.lineEdit_4youwu.setText('有料')
            self.lineEdit_4youwu.setStyleSheet('color: rgb(0, 0, 0)')

    # 更新产品无状态
    def wu_chanpin(self, sta):
        if sta == 1:
            self.lineEdit_1youwu.setText('无料')
            self.lineEdit_1youwu.setStyleSheet('color: rgb(0, 0, 0)')
        elif sta == 2:
            self.lineEdit_2youwu.setText('无料')
            self.lineEdit_2youwu.setStyleSheet('color: rgb(0, 0, 0)')
        elif sta == 3:
            self.lineEdit_3youwu.setText('无料')
            self.lineEdit_3youwu.setStyleSheet('color: rgb(0, 0, 0)')
        elif sta == 4:
            self.lineEdit_4youwu.setText('无料')
            self.lineEdit_4youwu.setStyleSheet('color: rgb(0, 0, 0)')

    # 更新测试结果->当合成NG/OK后调用,无双穴
    def test_result(self, sta, result):
        if sta == 1:
            self.lineEdit_1jieguo.setText(result)
            self.lineEdit_1jieguo.setStyleSheet('color: rgb(0, 0, 0)')
        elif sta == 2:
            self.lineEdit_2jieguo.setText(result)
            self.lineEdit_2jieguo.setStyleSheet('color: rgb(0, 0, 0)')
        elif sta == 3:
            self.lineEdit_3jieguo.setText(result)
            self.lineEdit_3jieguo.setStyleSheet('color: rgb(0, 0, 0)')
        elif sta == 4:
            self.lineEdit_4jieguo.setText(result)
            self.lineEdit_4jieguo.setStyleSheet('color: rgb(0, 0, 0)')

    # 删除测试结果 ->当将本站置位测试中时调用,无双穴
    def del_test_result(self, sta):
        if sta == 1:
            self.lineEdit_1jieguo.clear()
            self.lineEdit_1jieguo.setStyleSheet('color: rgb(127, 127, 127)')
        elif sta == 2:
            self.lineEdit_2jieguo.clear()
            self.lineEdit_2jieguo.setStyleSheet('color: rgb(127, 127, 127)')
        elif sta == 3:
            self.lineEdit_3jieguo.clear()
            self.lineEdit_3jieguo.setStyleSheet('color: rgb(127, 127, 127)')
        elif sta == 4:
            self.lineEdit_4jieguo.clear()
            self.lineEdit_4jieguo.setStyleSheet('color: rgb(127, 127, 127)')

    # 面板显示屏蔽
    def xianshi_pingb(self, sta):
        if sta == 1:
            self.lineEdit_1pingb.setText('已屏蔽')
            self.lineEdit_1pingb.setStyleSheet('color: rgb(255, 0, 0)')
            self.lineEdit_1kaimen.clear()
            self.lineEdit_1kaimen.setStyleSheet('color: rgb(127, 127, 127)')
            self.lineEdit_1youwu.clear()
            self.lineEdit_1youwu.setStyleSheet('color: rgb(127, 127, 127)')
            self.lineEdit_1jieguo.clear()
            self.lineEdit_1youwu.setStyleSheet('color: rgb(127, 127, 127)')
        elif sta == 2:
            self.lineEdit_2pingb.setText('已屏蔽')
            self.lineEdit_2pingb.setStyleSheet('color: rgb(255, 0, 0)')
            self.lineEdit_2kaimen.clear()
            self.lineEdit_2kaimen.setStyleSheet('color: rgb(127, 127, 127)')
            self.lineEdit_2youwu.clear()
            self.lineEdit_2youwu.setStyleSheet('color: rgb(127, 127, 127)')
            self.lineEdit_2jieguo.clear()
            self.lineEdit_2youwu.setStyleSheet('color: rgb(127, 127, 127)')
        elif sta == 3:
            self.lineEdit_3pingb.setText('已屏蔽')
            self.lineEdit_3pingb.setStyleSheet('color: rgb(255, 0, 0)')
            self.lineEdit_3kaimen.clear()
            self.lineEdit_3kaimen.setStyleSheet('color: rgb(127, 127, 127)')
            self.lineEdit_3youwu.clear()
            self.lineEdit_3youwu.setStyleSheet('color: rgb(127, 127, 127)')
            self.lineEdit_3jieguo.clear()
            self.lineEdit_3youwu.setStyleSheet('color: rgb(127, 127, 127)')
        elif sta == 4:
            self.lineEdit_4pingb.setText('已屏蔽')
            self.lineEdit_4pingb.setStyleSheet('color: rgb(255, 0, 0)')
            self.lineEdit_4kaimen.clear()
            self.lineEdit_4kaimen.setStyleSheet('color: rgb(127, 127, 127)')
            self.lineEdit_4youwu.clear()
            self.lineEdit_4youwu.setStyleSheet('color: rgb(127, 127, 127)')
            self.lineEdit_4jieguo.clear()
            self.lineEdit_4youwu.setStyleSheet('color: rgb(127, 127, 127)')

    # 面板解除屏蔽
    def jiechu_pingb(self, sta):
        if sta == 1:
            self.lineEdit_1pingb.clear()
            self.lineEdit_1pingb.setStyleSheet('color: rgb(127, 127, 127)')
        elif sta == 2:
            self.lineEdit_2pingb.clear()
            self.lineEdit_2pingb.setStyleSheet('color: rgb(127, 127, 127)')
        elif sta == 3:
            self.lineEdit_3pingb.clear()
            self.lineEdit_3pingb.setStyleSheet('color: rgb(127, 127, 127)')
        elif sta == 4:
            self.lineEdit_4pingb.clear()
            self.lineEdit_4pingb.setStyleSheet('color: rgb(127, 127, 127)')

    # 生产面板显示终端状态
    def display_30ma(self):
        time1 = QDateTime.currentDateTime()
        time_display = time1.toString('hh:mm:ss ')
        try:
            str_0 = time_display + '当前测试机{},当前机械手{}'.format(self.dict_yuan, self.code_jxs)
            self.send_signal.emit(str_0)
        except Exception as e:
            self.send_signal.emit(str(e))

    # 生产面板显示socket
    def socket_display(self):
        time1 = QDateTime.currentDateTime()
        time_display = time1.toString('hh:mm:ss ')
        try:
            str_1 = time_display + '当前所有socket:{}'.format(self.dict_socket)
            self.send_signal.emit(str_1)
        except Exception as e:
            self.send_signal.emit(str(e))

    # 生产面板显示配置
    def config_display(self):
        try:
            with open('.\config_zk.ini', encoding='gbk') as f:
                for line in f.readlines():
                    self.send_signal.emit(line)
        except Exception as e:
            self.send_signal.emit('无配置文件,请生成!')


if __name__ == "__main__":
    App = QApplication(sys.argv)
    aw = ZhongKong()
    aw.show()
    sys.exit(App.exec_())
