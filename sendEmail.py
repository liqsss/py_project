import smtplib
from email.mime.text import MIMEText

def sendEmail(name):
	mail_host = "smtp.qq.com" # 邮件服务器地址
	mail_user = "781576063@qq.com"  # 收件人邮箱
	mail_pass = "sauhxypzrhqnbdja" #动态授权码登录

	receiver = "meyers_007@sohu.com"  # 邮箱账号
	msg = name + " 正在使用人脸识别系统"
	print(msg)
	message = MIMEText(msg, _subtype="plain", _charset="utf-8") # 邮件内容
	message["Subject"] = "人脸识别" # 邮件主题
	message["From"] = mail_user # 发件人
	message["To"] = receiver # 收件人

	smtpObj = smtplib.SMTP()
	smtpObj.connect(mail_host, 25) # 连接邮件服务器
	smtpObj.login(mail_user, mail_pass) # 登录邮箱
	smtpObj.sendmail(mail_user, receiver, message.as_string()) # 发送邮件
	smtpObj.quit() # 关闭连接

if __name__ == "__main__":
	sendEmail("hello")