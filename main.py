# -*- coding: utf-8 -*-
"""
Created on Tue Nov 27 08:44:58 2012
Modified on 20130918
@author: Leniy
"""

import urllib2
import re
import MySQLdb

def get_host_from_url(url):
	"""
	功能：把url转换为域名
	"""
	root_proto, root_rest = urllib2.splittype(url)
	root_host, root_rest = urllib2.splithost(root_rest)
	return root_host

def get_url_from_host(host):
	"""
	功能：把域名转换为url
	"""
	return "http://" + host

def get_content_from_url(url):
	"""
	功能：获取指定url的内容
	返回值：列表list
		list[0]=页面的url
		list[1]=页面的内容
	"""
	#定义获取的url及对应UA、ref参数
	request = urllib2.Request(url)
	request.add_header('User-Agent', 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.9 Safari/536.5')
	request.add_header('Referer', 'http://blog.leniy.org/')
	#获取内容
	try:
		response = urllib2.urlopen(request)
		html_content = response.read()
	except:
		html_content = "ERROR"

	return [url , html_content]

def regex_external_url(list_in):
	"""
	功能：使用正则检索外部链接
	输入值：列表[页面的url, 页面的内容]
	输出值：字典{外部链接1的域名, 外部链接2的域名, ...]
	"""

	url = list_in[0]
	html = list_in[1]

	#返回值的临时变量，创建为字典，用于去掉重复值，最后再转换为列表
	tempurl = {}

	#获取url的域名，命名为root_host，用于后续排除list_in的内部链接
	root_host = get_host_from_url(url)

	#获取链接
	find_re = re.compile(r'<a .*?href="(.+?)".*?>(.+?)</a>', re.DOTALL)
	for x in find_re.findall(html):
		#排除本站内部链接
		host = get_host_from_url(x[0])
		if(host != root_host and host!=None):
			tempurl.update( {host:"1"} )

	return tempurl

def createDB():
	"""
	功能：创建数据库，只需执行一次
	"""
	try:
		conn=MySQLdb.connect(host='localhost',user='root',passwd='leniy.org',port=3306)
		cur=conn.cursor()
		cur.execute('create database if not exists python')
		conn.select_db('python')
		cur.execute('CREATE TABLE if not exists test(`ID` INT( 10 ) UNSIGNED NOT NULL AUTO_INCREMENT , `host` VARCHAR( 50 ) NOT NULL , `queryornot` INT( 1 ) NOT NULL DEFAULT "0",PRIMARY KEY ( `ID` ) ,UNIQUE KEY  `host` (  `host` )) ENGINE = MYISAM DEFAULT CHARSET = utf8 AUTO_INCREMENT =1;')
		cur.execute('INSERT INTO `test` (`host`, `queryornot`) VALUES ("leniy.org", "0");') #创建一个种子，后续程序从这儿开始检索
		conn.commit()
		cur.close()
		conn.close()
	except:
		print "数据库创建错误"

def GetOneSeed():
	"""
	功能：从数据库中提取一枚种子（即没有检索过的域名，即mysql的queryornot项为0的值）
	输入值：无
	返回值：一个域名
	"""
	try:
		conn=MySQLdb.connect(host='localhost',user='root',passwd='leniy.org',port=3306)
		cur=conn.cursor()
		conn.select_db('python')
		#下面开始提取一枚种子
		cur.execute('SELECT host FROM `test` WHERE `queryornot` =0 LIMIT 1')
		result=cur.fetchone()
		result_host = result[0]
		conn.commit()
		cur.close()
		conn.close()
		return result_host
	except:
		return "None"

def GainSeeds(seedhost):
	"""
	功能：种下种子，然后收获。即检索seedhost的页面，输出外部链接的域名，并写回数据库
	输入：域名
	输出：将匹配的域名写入数据库，返回值是增加的种子的个数，及字典temp_url_dict的长度
	"""
	try:
		temp_url_dict = regex_external_url(get_content_from_url(get_url_from_host(seedhost)))
		conn=MySQLdb.connect(host='localhost',user='root',passwd='leniy.org',port=3306)
		cur=conn.cursor()
		conn.select_db('python')
		for k in temp_url_dict:
			try:
				cur.execute('INSERT INTO `test` (`host`, `queryornot`) VALUES (%s, "0");',k)
			except:
				buzhixing = 1
				#print k + "已经存在，无需重复插入"
		#seedhost这个种子已经被读取过了，防止未来重复读取，需标记其已经读取过（即设置queryornot项为1）
		cur.execute('UPDATE `test` SET `queryornot` =  "1" WHERE `test`.`host` LIKE %s;',seedhost)
		conn.commit()
		cur.close()
		conn.close()
		return len(temp_url_dict)
	except:
		print temp_url_dict

def main():
	a = GetOneSeed()
	len = GainSeeds(a) #开始检索，并获得预计的个数
	print "将增加：" + str(len) + "个种子"

	#再向外扩充一层
	for x in range(1,len+1):
		b = GetOneSeed()
		print str(x) + ":" + b + "（增加个数：" + str(GainSeeds(b)) + "）"

main()