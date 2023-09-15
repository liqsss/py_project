# -- coding: utf-8 --**

import os
import time
import json
import random
import paramiko
from pywinauto import mouse
import paho.mqtt.client as mqtt
from pywinauto.application import Application


class TestTools:
    def __init__(self):
        os.chdir(r"D:/code/space/platform/system/build-lfi_tools-111-Debug/")
        os.environ.update({"__COMPAT_LAYER": "RUnAsInvoker"})  # windows中文路径
        self.tool_path = u"D:/code/space/platform/system/build-lfi_tools-111-Debug/lfi_tools.exe"
        self.app = Application(backend="uia").start(self.tool_path, wait_for_idle=False).connect(path=self.tool_path)

    def mqtt_Client(self):
        self.mqtthost = "119.23.212.113"    # 阿里云mqtt服务
        self.mqttport = 1883
        self.pul_topic = "tools/charging_send_mqtt/LFIC2230400035"
        self.mqttClient = mqtt.Client()

    def on_mqtt_connect(self):
        self.mqttClient.connect(self.mqtthost, self.mqttport, 60)
        self.mqttClient.loop_start()
        # self.mqttClient.loop_forever()

    def on_publish(self, topic, payload, qos):
        self.mqttClient.publish(topic, payload, qos)

    def on_message_come(self, client, userdata, msg):
        self.submsg = msg.payload.decode("utf-8")
        if self.submsg != "":
            print(self.submsg, type(self.submsg))

    def on_subscribe(self):
        self.mqttClient.subscribe("tools/charging_receive_mqtt/LFIC2230400035")
        self.mqttClient.on_message = self.on_message_come  # 消息到来处理函数

    def mqtt_send(self):
        self.mqttjson = {"set_test_info": {"id": 3, "value": "null"}}
        self.mqttmsg = json.dumps(self.mqttjson)
        self.mqtt_Client()
        self.on_mqtt_connect()
        self.on_publish(self.pul_topic, self.mqttmsg, 2)
        print("删除充电桩SN指令已发送！")
        self.on_subscribe()
        while True:
            return 0

    # 清除单板检测SN及MAC记录
    def delete_singe_data(self):
        self.json_path = r'D:\workspace_tools\test_s2\single.json'
        self.read_data = open(self.json_path, encoding='utf-8').read()
        self.save_json = json.loads(self.read_data)
        self.save_json["single"]["charge"] = []
        self.save_json["single"]["x3"] = []
        self.save_json["panoramic"] = []
        self.save_json["charging"] = []
        with open(self.json_path, "w") as f:
            json.dump(self.save_json, f, sort_keys=True, indent=4, separators=(',', ':'))
            print("清除SN及MAC记录")
        f.close()
        print(self.save_json)

    # 单板测试项 0:SN编码管理 1:相机内参写入 4:外参标定 5:充电桩检测
    def deal_singe_data(self):
        self.json_path = r"D:\software\test1\Debug\savedata\singe\space_config.json"
        self.read_data = open(self.json_path, encoding='utf-8').read()
        self.save_json = json.loads(self.read_data)
        self.save_json["work_id"] = [0, 1, 4, 5]
        with open(self.json_path, "w") as f:
            json.dump(self.save_json, f, sort_keys=True, indent=4, separators=(',', ':'))
            print("单测试项")
        f.close()
        print(self.save_json["work_id"])

    # 打开单板检测工程
    def test_open_project(self):
        # self.app["LFI_Tools"]["最大化"].click()  # 主界面最大化
        self.app["LFI_Tools"]["工程"].click_input()  # 下拉工程菜单
        self.app["LFI_Tools"]["打开工程"].click_input()  # 打开工程
        self.app["LFI_Tools"].child_window(best_match='文件夹:Edit').type_keys(r'D:\workspace_tools\test_s2', with_spaces=True) # 单板检测路径
        self.app["LFI_Tools"]["选择文件夹"].click()
        time.sleep(2)

    # 单板-写入充电桩SN
    def test_charge_sn(self):
        self.app["LFI_Tools"].child_window(best_match='清除Button').click()  # 清除
        time.sleep(2)
        self.app["LFI_Tools"].child_window(best_match='Edit2').type_keys(r'LFIC2230400035', with_spaces=True)   # 输入充电桩SN
        time.sleep(1)
        self.app["LFI_Tools"].child_window(best_match='选择串口Button').click_input()  # 下拉串口列表
        time.sleep(1)
        self.app["LFI_Tools"].child_window(best_match='COM9').click_input()  # 选择串口
        time.sleep(2)
        self.app["LFI_Tools"]["SN写入充电桩"].click()  # 写入充电桩SN
        time.sleep(3)
        while True:
            self.text = self.app["LFI_Tools"].child_window(best_match='Static2').window_text()  # 提示信息
            print(self.text)
            if self.text == "写入成功":
                print("充电桩SN写入成功")
                time.sleep(3)
                break
            elif self.text == "请等待...":
                print(self.text)
                self.app["LFI_Tools"]["SN写入充电桩"].click()  # 写入充电桩SN
                time.sleep(2)

    # 单板-写入整机SN
    def test_x3_sn(self):
        self.app["LFI_Tools"].child_window(best_match='清除Button2').click()     # 清除
        time.sleep(2)
        self.app["LFI_Tools"].child_window(best_match='Edit3').type_keys(r'LFIN2230400021', with_spaces=True)   # 输入机器SN
        time.sleep(1)
        self.app["LFI_Tools"]["SN写入X3板"].click()   # 写入X3板SN
        time.sleep(3)
        timeout = 0
        bret = False
        while True:
            self.text = self.app["LFI_Tools"].child_window(best_match='Static6').window_text()
            if self.text == "写入成功":
                print("整机SN写入成功")
                bret = True
                time.sleep(5)
                break
            elif timeout == 60:
                print(self.text)
                print("超时1分钟，断开操作")  # 超时
                break
            time.sleep(5)
            timeout += 5
            print("等待时间: %sS" % timeout)
        return bret

    # 单板-写入相机内参
    def test_camera_parameters(self):
        self.app["LFI_Tools"].child_window(best_match='相机内参写入').click_input()    # 相机内参写入
        # self.app.YourDialog.print_control_identifiers()
        self.app["LFI_Tools"].child_window(best_match='清除Button2').click()  # 清除1
        time.sleep(2)
        self.app["LFI_Tools"].child_window(best_match='Edit3').type_keys(r'LFIN2230400021', with_spaces=True)  # 扫描X3二维码
        time.sleep(1)
        self.app["LFI_Tools"].child_window(best_match='清除Button1').click()  # 清除2
        time.sleep(1)
        self.app["LFI_Tools"].child_window(best_match='Edit2').type_keys(r'HJN12330143', with_spaces=True)  # 扫描全景相机二维码
        time.sleep(1)
        self.app["LFI_Tools"].child_window(best_match='清除Button3').click()  # 清除3
        time.sleep(1)
        self.app["LFI_Tools"].child_window(best_match='Edit4').type_keys(r'HJQZ2330159', with_spaces=True)  # 扫描前置相机二维码
        time.sleep(1)
        self.app["LFI_Tools"]["写入X3板"].click()  # 写入X3相机内参
        while True:
            self.text = self.app["LFI_Tools"].child_window(best_match='Static6').window_text()
            if self.text == "写入文件成功":
                print("相机内参写入成功")
                time.sleep(3)
                break

    # 单板-相机点亮
    def test_camera_on(self):
        self.app["LFI_Tools"].child_window(best_match='相机点亮').click_input()  # 相机点亮
        time.sleep(2)
        self.app["LFI_Tools"].child_window(best_match='开始检测Button').click()  # 开始检测
        time.sleep(5)
        # self.app.YourDialog.print_control_identifiers()
        while True:
            self.text = self.app["LFI_Tools"].child_window(best_match='Static5').window_text()
            if self.text == "检测完成":
                print("相机点亮成功")
                time.sleep(1)
                self.app["LFI_Tools"]["工程"].click_input()
                time.sleep(1)
                self.app["LFI_Tools"]["关闭工程"].click_input()
                time.sleep(5)
                print("关闭工程")
                break
            elif self.text == "下载超时，测试失败":
                self.app["LFI_Tools"].child_window(best_match='开始检测Button').click()  # 开始检测
                time.sleep(2)

    # 单板-充电桩检测
    def test_charge_detection(self):
        self.app["LFI_Tools"]["最大化"].click()  # 主界面最大化
        self.app["LFI_Tools"].child_window(best_match='充电桩检测').click_input()  # 充电桩检测
        time.sleep(1)
        self.app["LFI_Tools"].child_window(best_match='清除Button').click()  # 清除
        time.sleep(1)
        self.app["LFI_Tools"].child_window(best_match='Edit2').type_keys('LFIC2230400035', with_spaces=True)  # 输入充电桩SN
        time.sleep(2)
        self.app["LFI_Tools"].child_window(best_match='开始检测Button').click()  # 开始检测
        time.sleep(1)
        # self.app["LFI_Tools"].child_window(best_match='停止检测Button').click()  # 停止检测
        # time.sleep(1)
        # self.app["LFI_Tools"].child_window(best_match='切换到用户模式Button').click()  # 切换到用户模式
        # time.sleep(1)
        while True:
            self.text = self.app["LFI_Tools"].child_window(best_match='Static2').window_text()
            if self.text == "该充电桩检测结果已更新":
                print("充电桩检测成功")
                time.sleep(3)
                break
        mouse.click(coords=(3111, 388))    # 勾选复选框
        num1 = self.app["LFI_Tools"].child_window(best_match='DataItem1').window_text()   # SN编码
        num2 = self.app["LFI_Tools"].child_window(best_match='DataItem2').window_text()   # LORA
        num3 = self.app["LFI_Tools"].child_window(best_match='DataItem3').window_text()   # 蓝牙
        num4 = self.app["LFI_Tools"].child_window(best_match='DataItem4').window_text()   # WIFI
        num5 = self.app["LFI_Tools"].child_window(best_match='DataItem5').window_text()   # RTK
        num6 = self.app["LFI_Tools"].child_window(best_match='DataItem6').window_text()   # 充电
        num7 = self.app["LFI_Tools"].child_window(best_match='DataItem7').window_text()   # NTC
        num8 = self.app["LFI_Tools"].child_window(best_match='DataItem8').window_text()   # 霍尔
        num9 = self.app["LFI_Tools"].child_window(best_match='DataItem9').window_text()   # 模式
        num10 = self.app["LFI_Tools"].child_window(best_match='DataItem10').window_text()   # LED灯
        print("SN LORA 蓝牙 WIFI RTK 充电 NTC 霍尔 模式 LED灯")
        print(num1, num2, num3, num4, num5, num6, num7, num8, num9, num10)
        # self.app.YourDialog.print_control_identifiers()

    # 创建工程
    def test_creat_project(self):
        self.app["LFI_Tools"]["工程"].click_input()  # 下拉工程菜单
        time.sleep(1)
        self.app["LFI_Tools"]["创建工程"].click_input()  # 打开工程
        self.bnum = int(time.time())  # 获取秒级时间戳
        self.name = "Test" + str(self.bnum)   # 组合工程名
        self.app["创建工程"].child_window(best_match='工程名Edit').type_keys(self.name, with_spaces=True)  # 输入工程名
        time.sleep(1)
        self.app["创建工程"].child_window(best_match='工程路径Edit').type_keys(r'C:\Users\admin\Desktop\tets\1', with_spaces=True)  # 输入工程路径
        time.sleep(1)
        self.app["创建工程"].child_window(best_match='工程类型ComboBox').click_input()  # 下拉列表
        time.sleep(1)
        self.testnum = random.sample([1, 2, 3], 1)
        if self.testnum == [1]:
            self.app["创建工程"].child_window(best_match='单板检测').click_input()  # 选择单板检测
            self.cjtext = "单板检测"
            time.sleep(1)
        elif self.testnum == [2]:
            self.app["创建工程"].child_window(best_match='整机检测').click_input()  # 选择整机检测
            self.cjtext = "整机检测"
            time.sleep(1)
        elif self.testnum == [3]:
            self.app["创建工程"].child_window(best_match='抽样检测').click_input()  # 选择抽样检测
            self.cjtext = "抽样检测"
            time.sleep(1)
        self.app["创建工程"].child_window(best_match='创建者Edit').type_keys(r'test', with_spaces=True)   # 输入创建者
        time.sleep(1)
        self.app["创建工程"]["确认"].click()   # 确认
        time.sleep(3)
        # self.app.YourDialog.print_control_identifiers()
        while True:
            self.text = self.app["LFI_Tools"].child_window(best_match='Edit0').window_text()
            if "保存配置文件成功" in self.text and self.name in self.text:
                print("创建%s工程成功" % self.cjtext)
                time.sleep(3)
                break

    # 关闭工程
    def test_close_project(self):
        self.app["LFI_Tools"]["工程"].click_input()
        time.sleep(2)
        self.app["LFI_Tools"]["关闭工程"].click_input()
        time.sleep(5)   # 必须关闭时会保存工程
        print("关闭工程成功")

    # 保存工程
    def test_save_project(self):
        self.app["LFI_Tools"]["工程"].click_input()
        time.sleep(2)
        self.app["LFI_Tools"]["保存工程"].click_input()
        time.sleep(5)   # 保存工程需要时间
        print("保存工程成功")

    # 打开整机检测工程
    def test_open_complete(self):
        self.app["LFI_Tools"]["工程"].click_input()  # 下拉工程菜单
        self.app["LFI_Tools"]["打开工程"].click_input()  # 打开工程
        self.app["LFI_Tools"].child_window(best_match='文件夹:Edit').type_keys(r'D:\software\test1\Debug\savedata\complete',
                                                                            with_spaces=True)
        self.app["LFI_Tools"]["选择文件夹"].click()
        time.sleep(2)
        # self.app.YourDialog.print_control_identifiers()

    # 整机检测主界面
    def test_complete_main(self):
        self.app["LFI_Tools"]["最大化"].click()  # 主界面最大化
        self.app["LFI_Tools"].child_window(best_match='LFIN2230400021').double_click_input(button="left", coords=(None, None))  # 双击展开
        # self.text = self.app["LFI_Tools"].child_window(class_name='QTreeView').window_text()
        # print(self.text)
        time.sleep(1)
        self.app["LFI_Tools"].child_window(best_match='电子元器件检测').click_input()
        time.sleep(1)
        self.app["LFI_Tools"].child_window(best_match='相机标定').click_input()
        time.sleep(1)
        self.app["LFI_Tools"].child_window(best_match='complete').click_input()

    # 整机-搜索设备
    def test_search_device(self):
        self.app["LFI_Tools"].child_window(best_match='complete').click_input()
        self.app["LFI_Tools"].child_window(best_match='开始搜索CheckBox').click_input()
        time.sleep(1)
        self.app["LFI_Tools"].child_window(best_match='扫描SN:Edit').type_keys('LFIN2230400021', with_spaces=True)
        time.sleep(2)
        self.app["LFI_Tools"].child_window(best_match='匹配Button').click()
        time.sleep(1)
        self.app["LFI_Tools"].child_window(best_match='更新设备IPButton').click()
        time.sleep(1)
        self.app["LFI_Tools"].child_window(best_match='添加设备Button').click()
        self.app["LFI_Tools"].child_window(best_match='关闭搜索CheckBox').click_input()
        # self.app.YourDialog.print_control_identifiers()

    # 整机-设备界面
    def test_device_interface(self):
        self.app["LFI_Tools"].child_window(best_match='LFIN2230400021').double_click_input(button="left", coords=(None, None))  # 双击展开
        time.sleep(2)
        self.sntext = self.app["LFI_Tools"].child_window(best_match='Static2').window_text()   # 整机SN
        self.iptext = self.app["LFI_Tools"].child_window(best_match='Static4').window_text()   # 整机IP
        print(self.sntext, self.iptext)
        self.app["LFI_Tools"].child_window(best_match='N2000RadioButton').click_input()       # N2000
        self.app["LFI_Tools"].child_window(best_match='N1000RadioButton').click_input()       # N1000
        self.app["LFI_Tools"].child_window(best_match='检查设备连接Button').click()        # 检查设备连接
        time.sleep(1)
        self.text5 = self.app["LFI_Tools"].child_window(best_match='Static5').window_text()  # 检查设备连接
        print(self.text5)
        self.app["LFI_Tools"].child_window(best_match='更新设备IPCheckBox').click()  # 更新设备IP
        time.sleep(1)
        self.text6 = self.app["LFI_Tools"].child_window(best_match='Static6').window_text()  # 更新设备IP
        print(self.text6)
        self.app["LFI_Tools"].child_window(best_match='参数1Edit').type_keys('1', with_spaces=True)   # 参数1
        time.sleep(1)
        self.app["LFI_Tools"].child_window(best_match='参数2Edit').type_keys('2', with_spaces=True)  # 参数2
        time.sleep(1)
        self.app["LFI_Tools"].child_window(best_match='参数3Edit2').type_keys('3', with_spaces=True)  # 参数3
        time.sleep(1)
        self.app["LFI_Tools"].child_window(best_match='保存参数Button').click()      # 保存参数
        time.sleep(1)
        self.app["LFI_Tools"].child_window(best_match='一键保存Button').click()      # 一键保存
        time.sleep(1)
        self.text12 = self.app["LFI_Tools"].child_window(best_match='Static12').window_text()      # 一键保存
        print(self.text12)
        self.app["LFI_Tools"].child_window(best_match='一键检查Button').click()         # 一键检查
        time.sleep(1)
        self.text10 = self.app["LFI_Tools"].child_window(best_match='Static100').window_text()      # 一键检查
        print(self.text10)
        self.app["LFI_Tools"].child_window(best_match='一键清理X3Button').click()               # 一键清理X3
        time.sleep(1)
        self.text11 = self.app["LFI_Tools"].child_window(best_match='Static11').window_text()       # 一键清理X3
        print(self.text11)
        # self.app.YourDialog.print_control_identifiers()

    # 整机-电子元器件检测
    def test_electronic_test(self):
        self.app["LFI_Tools"].child_window(best_match='LFIN2230400021').double_click_input(button="left", coords=(None, None))  # 双击展开
        time.sleep(1)
        self.app["LFI_Tools"].child_window(best_match='电子元器件检测').click_input()
        self.app.YourDialog.print_control_identifiers()

    # 打开抽样工程
    def test_open_sample(self):
        self.json_path = r"D:\software\test1\Debug\savedata\sample\sampling_check.json"
        self.read_data = open(self.json_path, encoding='utf-8').read()
        self.save_json = json.loads(self.read_data)
        self.save_json["autorecharge"] = []
        self.save_json["aging_test"] = []
        self.save_json["shell"] = []
        with open(self.json_path, "w") as f:
            json.dump(self.save_json, f, sort_keys=True, indent=4, separators=(',', ':'))
            print("清除SN记录")
        f.close()
        print(self.save_json)
        time.sleep(1)
        self.app["LFI_Tools"]["工程"].click_input()  # 下拉工程菜单
        self.app["LFI_Tools"]["打开工程"].click_input()  # 打开工程
        self.app["LFI_Tools"].child_window(best_match='文件夹:Edit').type_keys(r'D:\software\test1\Debug\savedata\sample', with_spaces=True)
        self.app["LFI_Tools"]["选择文件夹"].click()
        time.sleep(2)
        # self.app.YourDialog.print_control_identifiers()

    # 抽样-自动回充测试
    def test_auto_charge(self):
        # self.app["LFI_Tools"].child_window(best_match='自动回充测试').click_input()
        # time.sleep(1)
        self.app["LFI_Tools"].child_window(best_match='清除Button').click()  # 清除
        time.sleep(1)
        self.app["LFI_Tools"].child_window(best_match='Edit2').type_keys('LFIN2230400021', with_spaces=True)  # 输入整机SN
        time.sleep(2)
        self.app["LFI_Tools"].child_window(best_match='开始Button').click()  # 开始检测
        time.sleep(1)
        while True:
            self.text = self.app["LFI_Tools"].child_window(best_match='Static3').window_text()
            # print(self.text)
            time.sleep(1)
            if self.text == "开始测试":
                print("开始测试")
                time.sleep(3)
                break

    # 抽样-老化测试
    def test_aging_test(self):
        self.app["LFI_Tools"].child_window(best_match='老化测试').click_input()
        time.sleep(1)
        self.app["LFI_Tools"].child_window(best_match='清除Button').click()  # 清除
        time.sleep(1)
        self.app["LFI_Tools"].child_window(best_match='Edit2').type_keys('LFIN2230400021', with_spaces=True)  # 输入整机SN
        time.sleep(2)
        self.app["LFI_Tools"].child_window(best_match='开始检测Button').click()  # 开始检测
        time.sleep(1)
        while True:
            self.text = self.app["LFI_Tools"].child_window(best_match='Static1').window_text()
            # print(self.text)
            time.sleep(1)
            if self.text == "开始测试":
                print("开始测试")
                time.sleep(3)
                break

    # 抽样-一建远程测试
    def test_one_remote(self):
        self.app["LFI_Tools"].child_window(best_match='一键远程测试').click_input()    # 一键远程测试
        time.sleep(1)
        self.app["LFI_Tools"].child_window(best_match='清除Button').click()             # 清除
        time.sleep(1)
        self.app["LFI_Tools"].child_window(best_match='Edit2').type_keys('LFIN2230400021', with_spaces=True)     # 输入整机SN
        time.sleep(1)
        self.app["LFI_Tools"].child_window(best_match='ComboBox').click_input()                 # 下拉列表
        time.sleep(1)
        self.app["LFI_Tools"].child_window(best_match='一键清理X3机器').click_input()           # 一键清理X3机器
        time.sleep(1)
        self.app["LFI_Tools"].child_window(best_match='执行Button').click()                     # 执行
        time.sleep(1)
        # self.app.YourDialog.print_control_identifiers()
        while True:
            self.text = self.app["LFI_Tools"].child_window(best_match='Edit0').window_text()     # 输出
            time.sleep(2)
            self.last_text= self.text.split()
            print(self.last_text[-1])
            if "远程连接SSH已成功" in self.last_text[-1]:
                print("远程连接SSH已成功")
                time.sleep(3)
                break

    # SSH连接1.10设置flag
    def test_set_flag(self):
        ssh = paramiko.SSHClient()
        try:
            ssh.load_system_host_keys()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(hostname="192.168.1.10", port=22, username="root", password="lFi@NovaBot")  # 创建SSH连接
            stdin, stdout, stderr = ssh.exec_command("sed -i 's/flag=false/flag=true/' /root/novabot/test_scripts/factory_test/start_test.sh")
            time.sleep(2)
            stdin2, stdout2, stderr2 = ssh.exec_command("cat /root/novabot/test_scripts/factory_test/start_test.sh | tail -n +3 | head -n 1")
            file_sum = stdout2.read().decode('utf-8')  # stdout_readlines()
            print("测试前：%s" % file_sum)
        except Exception as e:
            print("%s:%s" % (e.__class__, e))
        finally:
            ssh.close()

    # SSH连接1.10查看flag
    def test_ssh_link(self):
        ssh = paramiko.SSHClient()
        try:
            ssh.load_system_host_keys()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(hostname="192.168.1.10", port=22, username="root", password="lFi@NovaBot")  # 创建SSH连接
            stdin, stdout, stderr = ssh.exec_command("cat /root/novabot/test_scripts/factory_test/start_test.sh | tail -n +3 | head -n 1")
            file_sum = stdout.read().decode('utf-8')  # stdout_readlines()
            print("测试后：%s" % file_sum)
        except Exception as e:
            print("%s:%s" % (e.__class__, e))
        finally:
            ssh.close()

    # 创建工程测试
    def run_creat_project(self):
        for i in range(1000):
            self.test_creat_project()           # 创建工程
            self.test_save_project()            # 保存工程
            self.test_close_project()           # 关闭工程
            i += 1

    # 运行单板检测
    def run_singe_test(self):
        for i in range(1000):
            # self.mqtt_send()                   # 下发清除充电桩SN
            self.delete_singe_data()           # 删除本地json中SN及MAC
            self.test_open_project()           # 打开单板检测工程
            #self.test_charge_sn()              # 写入充电桩SN
            bret = self.test_x3_sn()                  # 写入整机SN
            print("整机写入第:%d 次,%d" % (i, bret))
            # self.test_camera_parameters()      # 写入相机内参
            self.test_close_project()          # 关闭工程
            i += 1

    # 运行相机点亮
    def run_camera_on(self):
        for i in range(1):
            self.test_open_project()  # 打开工程
            for j in range(100):
                self.test_camera_on()  # 相机点亮
                j += 1
            i += 1

    # 运行充电桩检测
    def run_charge_test(self):
        self.delete_singe_data()           # 删除json中SN及MAC
        self.test_open_project()           # 打开单板检测工程
        self.test_charge_detection()       # 充电桩检测
        self.test_save_project()           # 保存工程

    # 运行整机搜索设备
    def run_search_device(self):
        self.test_open_complete()                   # 整机测试工程
        self.test_search_device()                   # 搜索设备

    # 运行整机设备界面
    def run_device_interface(self):
        self.test_open_complete()                   # 整机测试工程
        self.test_device_interface()                # 设备界面

    # 运行整机电子元器件检测
    def run_electronic_test(self):
        self.test_open_complete()                  # 整机测试工程
        self.test_electronic_test()                # 电子元器件检测

    # 运行抽样-自动回充测试
    def run_auto_charge(self):
        self.test_open_sample()                   # 抽样测试工程
        self.test_auto_charge()                   # 自动回充测试
        # print(1234)

    # 运行抽样-老化测试
    def run_aging_test(self):
        self.test_open_sample()                     # 抽样测试工程
        self.test_aging_test()                      # 老化测试

    # 运行抽样-一建远程测试
    def run_one_remote(self):
        for i in range(100):
            self.test_set_flag()                     # 设置flag为true
            self.test_open_sample()                  # 抽样测试工程
            self.test_one_remote()                  # 一建远程测试
            self.test_ssh_link()                    # 查看flag是否为false
            self.test_close_project()               # 关闭工程
            i += 1


if __name__ == '__main__':
    test = TestTools()
    try:
        # test.run_creat_project()                    # 创建工程测试
        test.run_singe_test()                       # 运行单板检测
        # test.run_camera_on()                        # 运行相机点亮
        # test.run_charge_test()                      # 运行充电桩检测
        # test.run_search_device()                    # 运行整机搜索设备
        # test.run_device_interface()                 # 运行整机设备界面
        # test.run_electronic_test()                  # 运行整机电子元器件检测
        # test.run_auto_charge()                      # 运行自动回充测试
        # test.run_aging_test()                       # 运行老化测试
        # test.run_one_remote()                         # 一建远程测试
    except Exception as e:
        print("write error==>", e)
    finally:
        # command = 'taskkill /F /IM lfi_tools.exe'
        # os.system(command)
        print("测试ok！！！")
