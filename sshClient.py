# -*- coding:utf-8 -*-
import paramiko
import time
import httpService
#import paho.mqtt.client as mqtt

hostname = "192.168.1.10"  #网口直连X3机器
mqtt_ip = "119.23.212.113"  # 生产用MQTT服务器
port = 22
username = "root"
password = "lFi@NovaBot"
'''
class Mqtt():
    def on_connect(self, client, userdata, flags, rc):
        print("hello mqtt")

    def on_message(self, client, userdata, msg):
        print(msg.topic + " " + str(msg.payload))

    def connect(self):
        client = mqtt.Client()
        client.on_connect = self.on_connect
        client.on_message = self.on_message
        client.connect(mqtt_ip, 1883, 60)
        client.loop_start()
'''


class RemoteControl():
    def __init__(self, hostname, port, username, password):
        self.hostname = hostname
        self.port = port
        self.username = username
        self.password = password
        self.ssh = paramiko.SSHClient()

    def reconnect(self):
        try:
            # 创建SSH对象
            self.ssh.close()
            self.ssh = paramiko.SSHClient()
            # 允许连接不在~/.ssh/known_hosts文件中的主机
            self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            # 连接服务器
            self.ssh.connect(hostname, port, username, password)
            # 创建SFTP客户端
            self.sftp = paramiko.SFTPClient.from_transport(self.ssh.get_transport())
            print("SSH 连接成功")
            return
        except Exception as e:
            print(e)

    def print(self):
        print(hostname, port, username, password)

    def remoteCmd(self, cmd):
        try:
            print("执行命令：", cmd)
            stdin, stdout, stderr = self.ssh.exec_command(cmd)
            stdin.write("终端等待输入...\n")  # 如果不需要与终端交互，则不写这两行
            stdin.flush()

            # 获取命令结果
            res, err = stdout.read(), stderr.read()
            result = res if res else err
            res = result.decode(encoding="utf-8")
            print(res)
            return "Remote CMD:" + cmd + " execute completed"
        except Exception as e:
            print("执行命令失败：", e)
            self.reconnect()  #断线重连
            self.remoteCmd(cmd) #重新执行该命令

    def uploadFile(self, localPath, remotePath):
        self.sftp.put(localPath, remotePath, confirm=True)

    def downloadFile(self, remotePath, localPath):
        self.sftp.get(remotePath, localPath)

    def interactive(self):
        shell = self.ssh.invoke_shell()
        shell.settimeout(1)
        command = input(">>>") + "\n"
        shell.send(command)

        while True:
            try:
                recv = shell.recv(512).decode()
                if recv:
                    print(recv)
                else:
                    continue
            except:
                command = input(">>>") + "\n"
                shell.send(command)

    def close(self):
        self.sftp.close()
        self.ssh.close()


def genGDC(control):
    control.remoteCmd(" python3 /userdata/lfi/camera_params/gdc_map.py /userdata/lfi/camera_params/preposition_intrinsic.json /userdata/lfi/camera_params/layout_preposition.json /userdata/lfi/camera_params/gdc_map_preposition.txt")


def checkFile(control):
    control.remoteCmd("ls -al /userdata/lfi/camera_params/")
    control.remoteCmd("cat  /userdata/lfi/json_config.json | grep code")


def uploadCameraFile(control):
    preSn, panoSn = httpService.getPrePanoCameraSn()
    preFile = "./camera/preposition/" + preSn + ".json"
    panoFile = "./camera/panoramic/" + panoSn + ".yaml"
    control.reconnect()
    control.uploadFile(preFile, "/userdata/lfi/camera_params/preposition_intrinsic.json")
    control.uploadFile(panoFile, "/userdata/lfi/camera_params/panoramic_intrinsic.yaml")


def copyGDCScript(control):
    control.remoteCmd("cp /root/novabot/ota_lib/camera_params/gdc_map.py  /userdata/lfi/camera_params/")
    control.remoteCmd("cp /root/novabot/ota_lib/camera_params/layout_preposition.json  /userdata/lfi/camera_params/")


def upgrade(control):
    print("开始测试=================")
    #input("随意点击键盘开始测试...")
   # print("测试第", num, "台机器")
    #num += 1
    control.reconnect()
    control.uploadFile("d:/lfimvpfactory20231014475.deb", "/root/lfimvpfactory20231014475.deb")
    print("文件上传成功")
    control.remoteCmd("dpkg -x lfimvpfactory20231014475.deb novabot.new")
    print("文件解压完成")
    control.remoteCmd("ls")
    control.remoteCmd("cp /root/novabot.new/scripts/run_ota.sh /userdata/ota/")
    control.remoteCmd("echo 1 > /userdata/ota/upgrade.txt")
    control.remoteCmd("cat /userdata/ota/upgrade.txt")
    time.sleep(5)
    print("远程命令执行完成，开始重启机器")
    control.remoteCmd("reboot -f")
    print("等待30s后继续执行数据清理...")
    time.sleep(30)
    control.reconnect()
    control.remoteCmd("rm -rf /root/lfimvpfactory20231014475.deb")
    control.remoteCmd("rm -rf /root/novabot.bak")
    control.remoteCmd("cat /userdata/ota/upgrade.txt")
    control.remoteCmd("ls")
    time.sleep(40)
    while(1):
        checkFile(control)
        ret = input("是否结束？0：继续检测，1：结束")
        if(ret == "1"):
            break
    print("机器已完成检测")
    control.close()
    print("完成测试============")


def quit(control):
    print("程序退出")
    exit(0)


def startService(control):
    control.remoteCmd("ps -aux | grep tof_camera_node")
    num = input("是否需要重启StartService 1: 重启，0，不重启")
    if (num == 1):
        print("重启服务")
        control.remoteCmd("~/novabot/scripts/start_service.sh")
    else:
        print("不需要重启服务")
    return


def getMac(control):
    #control.remoteCmd("bash /usr/bin/startbt6212.sh & ")  #获取蓝牙MAC，此处会一直阻塞在这里，需优化执行脚本
    #control.remoteCmd("cat /bl.cfg | grep \"BD Address\"  | awk '{print $3}'")
    control.remoteCmd("cat /userdata/lfi/ble_mac.txt ")


def recharge(control):
    control.remoteCmd("/root/novabot/debug_sh/test_recharge.sh ")


def agingTest(control):
    control.remoteCmd("nohup python3 /root/novabot/debug_sh/chassis_Aging_Test.py&")


def model2User(control):
    control.remoteCmd("sed -i 's/flag=true/flag=false/' /root/novabot/test_scripts/factory_test/start_test.sh ")


def model2Factory(control):
    control.remoteCmd("sed -i 's/flag=false/flag=true/' /root/novabot/test_scripts/factory_test/start_test.sh ")


def modelStatus(control):
    control.remoteCmd("grep 'flag=' /root/novabot/test_scripts/factory_test/start_test.sh ")


def checkGDC(control):
    control.uploadFile("d:/verify_txt.py", "~/verify_txt.py")
    control.remoteCmd("python3 verify_txt.py -g /userdata/lfi/camera_params/gdc_map_preposition.txt")

def main():
    switch_dict = {
        0: quit,
        1: genGDC,
        2: uploadCameraFile,
        3: upgrade,
        4: checkFile,
        5: getMac,
        6: copyGDCScript,
        7: startService,
        8: recharge,
        9: agingTest,
        10: model2User,
        11: model2Factory,
        12: modelStatus
    }

    control = RemoteControl(hostname, port, username, password)
    # 通过SSH网口直连机器
    print("请先通过网口直连Novabot机器")
    control.reconnect()
    while (1):
        print("操作说明：\n"
              "0：退出\n"
              "1：生成GDC文件\n"
              "2：上传相机内参文件\n"
              "3：手动OTA升级\n"
              "4：文件完整性检测\n"
              "5: 获取X3蓝牙MAC\n"
              "6: 拷贝GDC执行脚本文件\n"
              "7: 检查是否需要重启Service\n"
              "8: TTT===自动回充测试\n"
              "9: TTT===老化测试\n"
              "10: ===>切换到用户模式\n"
              "11: ===>切换到工厂模式\n"
              "12: ===>工作模式状态查询")
        num = input("请输入操作项ID：")
        switch_dict.get(int(num), quit)(control)


if __name__ == "__main__":
    main()
