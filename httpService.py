from urllib import request
import datetime
import hashlib
import json

def getPrePanoCameraSn():
	now = datetime.datetime.now()
	strTime = now.strftime("%Y%m%d%H%M%S")
	tokenHeader = "194c57e7-876e-4bd7-89ef-c4f0534ea2f4" + strTime
	md5str = hashlib.md5(tokenHeader.encode('utf8')).hexdigest()

	header = {"validCode": md5str.upper(), "dateTime": strTime, "Content-Type": "application/json"}
	searchUrl = "https://app.lfibot.com/api/nova-user/equipment/queryCameraSn"
	sn = input("请输入SN编码：")#LFIN1230700077
	print("SN机器编码为：", sn)
	body = {"sn": sn}
	jsonObj = json.dumps(body)
	data = jsonObj.encode('utf-8')

	rq = request.Request(url=searchUrl, data=data, headers=header, method='POST')
	resp = request.urlopen(rq)
	retJson = json.load(resp)

	frontCameraSn = retJson["value"]["frontCameraSn"]
	fullViewCameraSn = retJson["value"]["fullViewCameraSn"]
	print(frontCameraSn, fullViewCameraSn)

	return frontCameraSn, fullViewCameraSn

