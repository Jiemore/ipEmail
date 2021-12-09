import logging
import requests
import json
import ifcfg
import time
import traceback
import smtplib
from email.mime.text import MIMEText
from email.header import Header

# 程序配置
loopTime = 20 * 60                # 20分钟更新一次

# 发送邮件账号信息
msg_from = '@qq.com'  # 发送方邮箱
passwd = ''    # 填入发送方邮箱的授权码
msg_to = '@qq.com'    # 收件人邮箱

# 错误日志
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
file_handler = logging.FileHandler('ipEmail.log', mode='a+')
file_handler.setLevel(logging.ERROR)
formatter = logging.Formatter(
    "%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s")
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)


class IPHandler:
    def __init__(self) -> None:
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36 QIHU 360SE'
        }

    # 获取公网IP
    def GetPublicNetIP(self):
        result = requests.get(
            url='http://api.ipify.org/?format=json', headers=self.headers)
        return result.json()
    # 获取本地IP

    def GetLocalNetIP(self) -> json:
        device = {
            'device': {},
            'time': time.strftime('%Y-%m-%d %H:%M:%S'),
            # 'name': 'rp'
        }
        for name, interface in ifcfg.interfaces().items():
            # do something with interface
            device['device'][interface['device']] = interface['inet']
            # print interface['inet4']        # List of ips
            # print interface['inet6']
            # print interface['netmask']
            # print interface['broadcast']
        return json.dumps(device)


class EmailHandler:
    def __init__(self) -> None:
        subject = "IP已更新"  # 主题
        # content = "Email Test"  # 正文
        msg = MIMEText(content)
        msg['Subject'] = Header(subject, 'utf-8')
        msg['From'] = Header(msg_from, 'utf-8')
        msg['To'] = Header(msg_to, 'utf-8')

    def SendQQEmail(self, content, content_ip):
        try:
            s = smtplib.SMTP_SSL("smtp.qq.com", 465)  # 邮件服务器及端口号
            s.login(msg_from, passwd)
            message = MIMEText(content, 'plain', 'utf-8')  # 发送的内容
            message['From'] = Header("IP自动更新", 'utf-8')  # 发件人
            message['To'] = Header("大憨批", 'utf-8')  # 收件人
            subject = 'IP最新变动：' + content_ip
            message['Subject'] = Header(subject, 'utf-8')  # 邮件标题
            s.sendmail(msg_from, msg_to, message.as_string())
            print("发送成功")
        except Exception as e:
            print(str(traceback.format_exc()))
            print("发送失败")
        finally:
            s.quit()


if __name__ == '__main__':
    ip = IPHandler()
    email = EmailHandler()
    pubIP = '0.0.0.0'
    locIP = '0.0.0.0'
    # 检查次数记录
    count = 0
    # ip变动次数记录
    change = 0
    while True:
        count = count + 1
        try:
            # 获取当前ip信息
            nowPubIP = ip.GetPublicNetIP()['ip']          # 获取公网IP
            nowlocIP = ip.GetLocalNetIP()                 # 获取局域网IP

            # 有变动更新
            if pubIP != nowPubIP:
                pubIP = nowPubIP
                locIP = nowlocIP
                print(pubIP)
                print(locIP)
                # 构造邮件内容
                content = '公网：{}\r\n局域网:\r\n{}'.format(pubIP, locIP)
                # 发送ip变动邮件
                email.SendQQEmail(content=content, content_ip=pubIP)

        except Exception as e:
            # 写入日志
            logger.error(str(traceback.format_exc()))

        # 每 loopTime 查询一次ip变动情况
        time.sleep(loopTime)
