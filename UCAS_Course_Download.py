# -*- coding:utf8 -*-
import requests
import re
from bs4 import BeautifulSoup
import os
import time
import urllib.parse
import json

def file_download(url, fileName, className, session, folder):
   dir_base = os.getcwd() + "/" + className
   dir = dir_base + "/"  + folder
   dir = urllib.parse.unquote(dir)
   file = dir + fileName
   file = urllib.parse.unquote(file)
   # create folder
   if not os.path.exists(dir_base):
      os.mkdir(dir_base)
   if not os.path.exists(dir):
      os.mkdir(dir)
   # have such file
   if os.path.exists(file):
      print("File already exists: " + fileName )
      return
   print("Start download: " + fileName )
   try:
      s = session.get(url)
      with open(file, "wb") as data:
         data.write(s.content)
   except:
      print("Link invalid. Skip link: ", url)


def errorExit(msg):
	print(msg)
	os.system("pause")
	exit()


def getClass(currentClass, url, session, data, base_url):

	#file
	s = session.get(url)
	file_indexs = BeautifulSoup(s.text, "html.parser").find_all("li", {"class":"file"})
	for file_index in file_indexs:
		file_index_base = file_index.a.get("href")
		download_url = url + file_index_base
		folder = url.replace(base_url , "")
		file_download(download_url, file_index_base, currentClass, session , folder)

	#folder
	s = session.get(url)
	folder_indexs = BeautifulSoup(s.text, "html.parser").find_all("li", {"class":"folder"})
	for folder_index in folder_indexs:
		folder_index_base = folder_index.a.get("href")
		next_url = url + folder_index_base
		getClass(currentClass, next_url, session, data, base_url)

if __name__ == '__main__':
	username = ''
	password = ''
	id_flag = 0
	for line in open("./config.txt",encoding="utf-8"):
		if id_flag == 0:
			username = line.replace("\n","").replace(" ","")
			id_flag = 1
		else:
			password = line.replace("\n","").replace(" ","")
	print("Your Login ID：" + username)
	try:
		onestop_data = {'username': '',  # 填入用户名
		                'password': '',  # 填入密码
		                'remember': 'checked'}
		onestop_data['username'] = username
		onestop_data['password'] = password
		# ------------------- login onestop -------------------------
		onestop_link = "http://onestop.ucas.ac.cn/Ajax/Login/0"

		headers = {  # 请求头信息
			'X-Requested-With': 'XMLHttpRequest'
		}

		o = requests.Session()
		Onestop_Login = o.post(url=onestop_link, data=onestop_data, headers=headers, verify=False, timeout=10)
		res = json.loads(Onestop_Login.text)

		if (res['f'] == False):  # check login status
			raise Exception(res['msg'])
		else:
			print("Welcome, {}".format(onestop_data['username']))
		# -------------------------------------------------------

		# ------------------- login sep -------------------------
		s = requests.Session()
		Sep_Login = s.get(url=res['msg'], verify=False, timeout=10)  # login
		sl = BeautifulSoup(Sep_Login.text, 'lxml')

		if (sl.find('a', title='退出系统') == None):  # check login status
			raise Exception("Sep Login Error")
		else:
			print("SEP LOGIN SUCCESS")
		session = s
		# -------------------------------------------------------

		s = session.get("http://sep.ucas.ac.cn/portal/site/16/801")
		bsObj = BeautifulSoup(s.text, "html.parser")

		newUrl = bsObj.find("noscript").meta.get("content")[6:]
		s = session.get(newUrl)
		try:
			bsObj = BeautifulSoup(s.text, "html.parser").find("a", {"class": "Mrphs-toolsNav__menuitem--link","title":"我的课程 - 查看或加入站点"})
			newUrl = bsObj.get("href")
		except:
			bsObj = BeautifulSoup(s.text, "html.parser").find_all("a", {"class": "Mrphs-toolsNav__menuitem--link"})[2]
			newUrl = bsObj.get("href")
		s = session.get(newUrl)
		classList = []
		trList = BeautifulSoup(s.text, "html.parser").findAll("tr")
		del trList[0]
		for tr in trList:
			tdList = tr.findAll("th")
			className = tr.find("a").get_text().strip()
			classWebsite = tr.find("a").get("href")
			class_source_num = re.findall(r"site/(.+)", classWebsite)[0]
			classList.append((className, classWebsite,class_source_num));
		print("You have such " + str(len(classList)) + " classes: ")

		for c in classList:
			dir_base = os.getcwd() + "/" + c[0]
			if not os.path.exists(dir_base):
				os.mkdir(dir_base)
			print("(" + c[0] + ")")
		print("\n")
		print("Start download......")
		for c in classList:
			url = "http://course.ucas.ac.cn/access/content/group/" + c[2] + "/"
			s = session.get(url)
			getClass(c[0], url, session, None, url)
	except NameError:
		errorExit("Down failed")
	print("\n")
