import sys
import threading
import os
from configparser import ConfigParser
from PyQt5.QtCore import QDateTime, QTimer, pyqtSignal, Qt
from PyQt5.QtGui import QCursor
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox, QLabel, QMenu, QAction
from Terminal import Ui_mainWindow
import socket
import time
import serial.tools.list_ports


class ZhongDuan(QMainWindow, Ui_mainWindow):
    # 自定义信号
    send_date = pyqtSignal(str)

    def __init__(self, parent=None, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.setupUi(self)
        self.actiondakaipeizhiwenjian.triggered.connect(self.clicked)
        self.dakai_plc.clicked.connect(self.Csj_conn)
        self.actioncaozuoPLC_O.triggered.connect(self.clicked)
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
        self.statusShowTime()
        self.pushButton_lian.clicked.connect(self.thread_conn_ser)
        self.pushButton_duan.clicked.connect(self.close_ser)
        self.pushButton_fasong.clicked.connect(self.send_xinxi)
        self.pushButton_pingbi.clicked.connect(self.jm_pingbi)
        self.pushButton_jiepingbi.clicked.connect(self.jm_jcpingbi)
        # self.actionduqurizhi.triggered.connect(self.thread_du_qu)
        # self.pushButton_xunhuanxieru.clicked.connect(self.clicked)
        self.pushButton_xieru.clicked.connect(self.write_mb_log)
        self.pushButton_shanchu.clicked.connect(self.remove_mb_log)
        self.save_buton.clicked.connect(self.save_peizhi)
        self.set_default()
        self.slot_sing()
        # 创建整体菜单并返回当前值
        self.tab.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tab.customContextMenuRequested.connect(self.tab_rightmenu)
        # 隐藏主窗口边界
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.pushButton_close.pressed.connect(self.close)
        self.pushButton_min.pressed.connect(self.showMinimized)
        # 连续fail三次计时
        self.fail_time = 0
        self.str_1 = self.lineEdit_4.text() or '192.168.0.88'
        self.str_ip = self.comboBox_kehu.currentText()
        self.CG_ma = ''  # 1^1  1^1^1

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

    # tab右键菜单
    def tab_rightmenu(self):
        self.tab_menu = QMenu(self)
        self.actionA = QAction(U'读取Log', self)
        self.tab_menu.addAction(self.actionA)
        self.actionB = QAction(u'功能1', self)
        self.tab_menu.addAction(self.actionB)
        self.actionC = QAction(u'功能2', self)
        self.tab_menu.addAction(self.actionC)
        self.actionD = QAction(u'功能3', self)
        self.tab_menu.addAction(self.actionD)
        self.tab_menu.popup(QCursor.pos())
        self.actionA.triggered.connect(self.thread_du_qu)
        self.actionB.triggered.connect(self.clicked)
        self.actionC.triggered.connect(self.clicked)
        self.actionD.triggered.connect(self.clicked)

    # 将消息打印在面板
    def mianban_xianshi(self, data):
        str_data = str(data)
        time1 = QDateTime.currentDateTime()
        time_on = time1.toString('MM/dd hh:mm:ss')
        try:
            self.send_date.emit(time_on + str_data)
        except Exception as e:
            self.send_date.emit(str(e))

    # 将接受消息的信号和槽连接起来
    def slot_sing(self):
        self.send_date.connect(self.handle_display)

    # 将接受的消息显示在对应的窗口上
    def handle_display(self, msg):
        self.textEdit.append(msg)
        self.textEdit.setStyleSheet('color:rgb(0, 0, 255)')

    # 连接服务器
    def conn_ser(self):
        # 对输入的IP地址防呆
        if len(self.str_1) == 12:
            try:
                self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # 端口复用
                self.client_socket.bind((self.str_ip, 0))
                self.client_socket.connect((self.str_1, 8888))
                self.thread_receive_zk()
                data = '连接成功'
                self.mianban_xianshi(data)
                self.lianjie_zhaungtai()
            except Exception as e:
                self.mianban_xianshi(str(e))
        else:
            self.mianban_xianshi('请输入正确的IP地址')

    # 线程连接服务器
    def thread_conn_ser(self):
        threading.Thread(target=self.conn_ser(), daemon=True).start()

    # 打开与测试机通讯串口
    def Csj_conn(self):
        com_0 = self.comboBox_com.currentText()
        bo_te = self.comboBox_botelv.currentText()
        bo_telv = int(bo_te)
        jiao_yan = self.comboBox_jiaoyan.currentText()
        shu_1 = self.comboBox_shujuwei.currentText()
        shu_2 = int(shu_1)
        ting_0 = self.comboBox_tingzhiwei.currentText()
        ting_1 = int(ting_0)
        try:
            self.ser_csj = serial.Serial(port='{}'.format(com_0), baudrate=bo_telv,
                                         bytesize=shu_2, parity='{}'.format(jiao_yan),
                                         stopbits=ting_1, timeout=0.1)
            self.thread_receive_csj()
            self.mianban_xianshi('串口打开成功！')
        except Exception as e:
            self.mianban_xianshi(str(e))

    # 循环读取串口数据
    def receive_csj(self):
        while True:
            num = self.ser_csj.inWaiting()
            if num:
                data = self.ser_csj.readline()
                re_data = data.decode('utf-8')
                str_data = ' Fr: ' + re_data
                self.mianban_xianshi(str_data)
                # 如果收到OF/CF就直接返回给中控
                if len(re_data) == 2:
                    self.send_zhongk('{}{}'.format(self.str_ip, re_data))
                    if re_data == 'OF':
                        self.kaimen_zhuangtai()
                    elif re_data == 'CF':
                        self.guanmen_zhuangtai()
                        self.del_test_result()
                # 如果收到1^1或1^1^0后就保存在变量里
                elif len(re_data) == 3 or len(re_data) == 5:
                    self.CG_ma = re_data
                    self.send_zhongk('{}{}'.format(self.str_ip, re_data))
                    if re_data[0] == '1':
                        self.kaimen_zhuangtai()
                        if re_data[2] == '1':
                            self.you_chanpin()
                        elif re_data[2] == '0':
                            self.wu_chanpin()
                    elif re_data[0] == '0':
                        self.guanmen_zhuangtai()
                        if re_data[2] == '1':
                            self.you_chanpin()
                        elif re_data[2] == '0':
                            self.wu_chanpin()

    # 线程接收串口信息,只能点击一次这个函数
    def thread_receive_csj(self):
        threading.Thread(target=self.receive_csj, daemon=True).start()

    # 断开客户端
    def close_ser(self):
        try:
            self.client_socket.shutdown(socket.SHUT_RDWR)
            self.client_socket.close()
            data = '已断开连接'
            self.mianban_xianshi(data)
            self.qingkong_lianjie()
        except Exception as e:
            self.mianban_xianshi(str(e))

    # 点击触发
    def clicked(self):
        QMessageBox.information(self, "功能开发中", "功能开发中!")

    #  确认退出？
    def closeEvent(self, event):
        reply = QMessageBox.question(self, '退出询问', '是否确认退出？', QMessageBox.Yes, QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.close_ser()
            event.accept()
        else:
            event.ignore()

    # label显示当前时间
    def showCurrentTime(self, timeLabel):
        time = QDateTime.currentDateTime()
        timeDisplay = time.toString('yyyy/MM/dd hh:mm:ss dddd')
        timeLabel.setText(timeDisplay)

    # 面板显示当前时间
    def statusShowTime(self):
        self.timer = QTimer()
        self.timeLabel = QLabel()
        self.message = QLabel('承制单位:自动化设备开发处')
        self.statusbar.addPermanentWidget(self.timeLabel, 400)
        self.statusbar.addPermanentWidget(self.message, 0)
        self.timer.timeout.connect(lambda: self.showCurrentTime(self.timeLabel))  # 这个通过调用槽函数来刷新时间
        self.timer.start(1000)  # 每隔一秒刷新一次

    # 循环读取本地文件,读取到就发送给服务器
    def du_qu(self):
        log_dizhi = self.lineEdit_log.text()
        while True:
            time.sleep(2)
            if os.path.exists(r'{}'.format(log_dizhi)):
                try:
                    str1 = self.comboBox_kehu.currentText()
                    with open(r'{}'.format(log_dizhi), 'rb') as stream:
                        stream_read = stream.read()
                        str_read = stream_read.decode('utf-8')
                        if 'NG' in str_read:
                            self.fail_time += 1
                            self.test_result('NG')
                        if 'NG' not in str_read:
                            self.fail_time = 0
                            self.test_result('OK')
                        self.mianban_xianshi('扫描到{}'.format(str_read))
                        # 扫描到文件后等待0.5秒询问门状态
                        time.sleep(0.5)
                        self.send_data('CG!')
                        # 需要等待0.5后再将CG状态一起发送过去
                        time.sleep(0.5)
                        data_1 = str1 + str_read + self.CG_ma
                        try:
                            self.send_zhongk(data_1)  # 192.168.0.101^0123456789AB^001^002^NG!1^1^1
                        except:
                            pass
                        stream.close()
                        # C:\Users\Administrator\Desktop
                        os.remove(r'{}'.format(log_dizhi))
                        self.send_pingbi()
                except Exception as e:
                    self.mianban_xianshi(str(e))

    # 当连续Fail三次以上发送PB给中控
    def send_pingbi(self):
        str1 = self.comboBox_kehu.currentText() + 'pb'
        if self.fail_time >= 3:
            try:
                self.mianban_xianshi(str1)
                self.send_zhongk(str1)
                self.lineEdit_pingbi.setText('已屏蔽')
            except Exception as e:
                self.mianban_xianshi(str(e))

    # 线程开启循环读取
    def thread_du_qu(self):
        threading.Thread(target=self.du_qu, daemon=True).start()

    # 循环接收中控信息
    def receive_zk(self):
        try:
            while True:
                recv_data = self.client_socket.recv(1024)
                if recv_data:
                    recv_re = recv_data.decode('utf-8')
                    data = ' Re ZK:' + recv_re
                    self.mianban_xianshi(data)
                    # 这里要判断什么情况发送给测试机，不然中控和终端手动通讯业要发给测试机；如果测试机不在线就会报警
                    if len(recv_re) < 5:
                        try:
                            self.send_data(recv_re)
                        except:
                            self.mianban_xianshi('ERR：发送到测试机失败！')
                    else:
                        if recv_re == '0000PB':
                            self.mianban_xianshi('中控执行屏蔽当前站')
                            self.lineEdit_pingbi.setText('已屏蔽')
                            self.lineEdit_pingbi.setStyleSheet('color: rgb(255, 0, 0);')
                        elif recv_re == '0000JCPB':
                            self.mianban_xianshi('中控执行解除当前站屏蔽')
                            self.lineEdit_pingbi.clear()
                            self.lineEdit_pingbi.setStyleSheet('color: rgb(127, 127, 127);')
                else:
                    self.mianban_xianshi('网络断开！')
                    break
        except Exception as e:
            self.mianban_xianshi(str(e))

    # 线程开启循环接收中控
    def thread_receive_zk(self):
        threading.Thread(target=self.receive_zk, daemon=True).start()

    # 串口发送数据
    def send_data(self, data):
        try:
            send_ = data.encode('UTF-8')
            self.ser_csj.write(send_)
            send_data = ' To: ' + send_.decode('UTF-8')
            self.mianban_xianshi(send_data)
        except Exception as e:
            self.mianban_xianshi(str(e))

    # 网口发送信息给中控
    def send_zhongk(self, msg):
        if self.client_socket:
            try:
                self.client_socket.send(msg.encode('utf-8'))
            except Exception as e:
                self.mianban_xianshi(str(e))

    # 面板发送信息
    def send_xinxi(self):
        str_fasong = self.lineEdit_fasong.text()
        if self.radioButton_zk.isChecked():
            try:
                self.send_zhongk(str_fasong)
            except:
                self.mianban_xianshi('请检查网口!')
        elif self.radioButton_csj.isChecked():
            try:
                self.send_data(str_fasong)
            except:
                self.mianban_xianshi('请检查串口!')

    # 循环写入log日志
    def write_log(self):
        log_dizhi = self.lineEdit_log.text()
        while True:
            time.sleep(50)
            if not os.path.exists(r'{}'.format(log_dizhi)):
                try:
                    with open(r'{}'.format(log_dizhi), 'w') as stream:
                        stream.write('01^0123456789AB^005^006^NG!')
                except:
                    continue
            else:
                os.remove(r'{}'.format(log_dizhi))

    # 线程循环写入log日志
    def thread_write_log(self):
        threading.Thread(target=self.write_log, daemon=True).start()

    # 面板写入log日志
    def write_mb_log(self):
        xuewei = self.comboBox.currentText()
        before_ = self.comboBox_2.currentText()
        now_ = self.comboBox_3.currentText()
        p_id = self.comboBox_4.currentText()
        res_ult = self.comboBox_5.currentText()
        log_dizhi = self.lineEdit_log.text()
        # '01^0123456789AB^005^006^NG!'
        str_1 = xuewei + '^' + p_id + '^' + before_ + '^' + now_ + '^' + res_ult + '!'
        if not os.path.exists(r'{}'.format(log_dizhi)):
            try:
                with open(r'{}'.format(log_dizhi), 'w') as stream:
                    stream.write(str_1)
                    data = '写入log成功'
                    self.mianban_xianshi(data)
            except Exception as e:
                self.mianban_xianshi(str(e))
        else:
            os.remove(r'{}'.format(log_dizhi))

    # 删除面板写入的log日志
    def remove_mb_log(self):
        log_dizhi = self.lineEdit_log.text()
        if os.path.exists(r'{}'.format(log_dizhi)):
            try:
                os.remove(r'{}'.format(log_dizhi))
                data = '删除log成功'
                self.mianban_xianshi(data)
            except Exception as e:
                self.mianban_xianshi(str(e))

    # 将报警写入本地
    def alarm_write(self, msg):
        # app_path = os.path.dirname(sys.executable)
        time1 = QDateTime.currentDateTime()
        time_display = time1.toString('MM/dd hh:mm:ss ')
        str_msg = str(msg)
        try:
            # with open('{}:\Alarm.txt'.format(app_path), 'a') as stream:
            with open('.\Alarm.txt', 'a') as stream:
                stream.write(time_display + str_msg + ' ' + '\n')
        except Exception as e:
            self.send_date.emit(str(e))

    # 保存配置文件
    def save_peizhi(self):
        kehu_ip = self.comboBox_kehu.currentText()
        zd_com = self.comboBox_com.currentText()
        zd_btlv = self.comboBox_botelv.currentText()
        zd_jywe = self.comboBox_jiaoyan.currentText()
        zd_sjwe = self.comboBox_shujuwei.currentText()
        zd_tzwe = self.comboBox_tingzhiwei.currentText()
        log_dizhi = self.lineEdit_log.text()
        config = ConfigParser()
        config.set('DEFAULT', 'kehu_ip', kehu_ip)
        config.set('DEFAULT', 'zd_com', zd_com)
        config.set('DEFAULT', 'zd_btlv', zd_btlv)
        config.set('DEFAULT', 'zd_jywe', zd_jywe)
        config.set('DEFAULT', 'zd_sjwe', zd_sjwe)
        config.set('DEFAULT', 'zd_tzwe', zd_tzwe)
        config.set('DEFAULT', 'log_dizhi', log_dizhi)
        # app_path = os.path.dirname(sys.executable)
        # config_path = app_path + '\\config.ini'
        try:
            with open('.\config_zd.ini', 'w') as stream:
                config.write(stream)
        except:
            self.alarm_write('保存终端配置文件错误')

    # 读取配置文件a
    def set_default(self):
        config = ConfigParser()
        try:
            config.read('.\config_zd.ini', encoding='utf-8-sig')
            kehu_ip = config.get('DEFAULT', 'kehu_ip')
            zd_com = config.get('DEFAULT', 'zd_com')
            zd_btlv = config.get('DEFAULT', 'zd_btlv')
            zd_jywe = config.get('DEFAULT', 'zd_jywe')
            zd_sjwe = config.get('DEFAULT', 'zd_sjwe')
            zd_tzwe = config.get('DEFAULT', 'zd_tzwe')
            log_dizhi = config.get('DEFAULT', 'log_dizhi')
            self.comboBox_kehu.setCurrentText(kehu_ip)
            self.comboBox_com.setCurrentText(zd_com)
            self.comboBox_botelv.setCurrentText(zd_btlv)
            self.comboBox_jiaoyan.setCurrentText(zd_jywe)
            self.comboBox_shujuwei.setCurrentText(zd_sjwe)
            self.comboBox_tingzhiwei.setCurrentText(zd_tzwe)
            self.lineEdit_log.setText(log_dizhi)
        except:
            self.alarm_write('读取终端配置文件错误')

    # 界面操作->打开治具
    def dakai_zhiju(self):
        self.send_data('KM!')

    # 界面操作->关闭治具
    def guanbi_zhiju(self):
        self.send_data('GM!')

    # 界面操作->测试机状态
    def csj_zhuangtai(self):
        self.send_data('CG!')

    # 界面操作->屏蔽
    def jm_pingbi(self):
        str1 = self.comboBox_kehu.currentText() + 'pb'
        try:
            self.mianban_xianshi(str1)
            self.send_zhongk(str1)
            self.mianban_xianshi('屏蔽当前站')
            self.lineEdit_pingbi.setText('已屏蔽')
            self.lineEdit_pingbi.setStyleSheet('color: rgb(255, 0, 0);')
        except Exception as e:
            self.mianban_xianshi(str(e))

    # 界面操作->解除屏蔽
    def jm_jcpingbi(self):
        str1 = self.comboBox_kehu.currentText() + 'jc'
        try:
            self.mianban_xianshi(str1)
            self.send_zhongk(str1)
            self.mianban_xianshi('解除当前站屏蔽')
            self.lineEdit_pingbi.clear()
            self.lineEdit_pingbi.setStyleSheet('color: rgb(127, 127, 127);')
        except Exception as e:
            self.mianban_xianshi(str(e))

    # 更新面板连接状态
    def lianjie_zhaungtai(self):
        self.lineEdit_lian.setText('已联机')
        self.lineEdit_lian.setStyleSheet('color: rgb(0, 0, 0)')

    # 清空连接状态
    def qingkong_lianjie(self):
        self.lineEdit_lian.clear()
        self.lineEdit_lian.setStyleSheet('color: rgb(127, 127, 127)')
        self.lineEdit_kaimen.clear()
        self.lineEdit_kaimen.setStyleSheet('color: rgb(127, 127, 127)')
        self.lineEdit_youwu.clear()
        self.lineEdit_youwu.setStyleSheet('color: rgb(127, 127, 127)')
        self.del_test_result()
        self.lineEdit_pingbi.clear()

    # 更新开门状态
    def kaimen_zhuangtai(self):
        self.lineEdit_kaimen.setText('开门')
        self.lineEdit_kaimen.setStyleSheet('color: rgb(0, 0, 0)')

    # 更新关门状态
    def guanmen_zhuangtai(self):
        self.lineEdit_kaimen.setText('关门')
        self.lineEdit_kaimen.setStyleSheet('color: rgb(0, 0, 0)')

    # 更新产品有状态
    def you_chanpin(self):
        self.lineEdit_youwu.setText('有料')
        self.lineEdit_youwu.setStyleSheet('color: rgb(0, 0, 0)')

    # 更新产品无状态
    def wu_chanpin(self):
        self.lineEdit_youwu.setText('无料')
        self.lineEdit_youwu.setStyleSheet('color: rgb(0, 0, 0)')

    # 更新测试结果->当合成NG/OK后调用,无双穴
    def test_result(self, result):
        self.lineEdit_jieguo.setText(result)
        self.lineEdit_jieguo.setStyleSheet('color: rgb(0, 0, 0)')

    # 删除测试结果 ->当将本站置位测试中时调用,无双穴
    def del_test_result(self):
        self.lineEdit_jieguo.clear()
        self.lineEdit_jieguo.setStyleSheet('color: rgb(127, 127, 127)')


if __name__ == "__main__":
    App = QApplication(sys.argv)
    aw = ZhongDuan()
    aw.show()
    sys.exit(App.exec_())
