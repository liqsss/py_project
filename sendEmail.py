import smtplib
from email.mime.text import MIMEText


def send_email(name):
	mail_host = "smtp.qq.com"
	mail_user = "781576063@qq.com"
	mail_pass = "sauhxypzrhqnbdja"

	receiver = "meyers_007@sohu.com"  # 邮箱账号
	msg = name + " 正在使用人脸识别系统"
	print(msg)
	message = MIMEText(msg, _subtype="plain", _charset="utf-8")  # 邮件内容
	message["Subject"] = "人脸识别"  # 邮件主题
	message["From"] = mail_user  # 发件人
	message["To"] = receiver  # 收件人
	smtp_obj = smtplib.SMTP()
	smtp_obj.connect(mail_host, 25)  # 连接邮件服务器
	smtp_obj.login(mail_user, mail_pass)  # 登录邮箱
	smtp_obj.sendmail(mail_user, receiver, message.as_string())  # 发送邮件
	smtp_obj.quit()  # 关闭连接


if __name__ == "__main__":
	send_email("hello")
