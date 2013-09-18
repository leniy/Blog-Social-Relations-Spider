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

def main():
	starturl = "blog.leniy.org/liuyan"
	temp = regex_external_url(get_content_from_url(get_url_from_host(starturl)))
	print temp
	for k in temp:
		print regex_external_url(get_content_from_url(get_url_from_host(k)))
		print '\n=====================================\n'


#main()

try:
	conn=MySQLdb.connect(host='localhost',user='root',passwd='leniy.org',port=3306)
	cur=conn.cursor()

	cur.execute('create database if not exists python')
	conn.select_db('python')
	cur.execute('create table test(id int,info varchar(20))')

	value=[1,'hi rollen']
	cur.execute('insert into test values(%s,%s)',value)

	values=[]
	for i in range(20):
		values.append((i,'hi rollen'+str(i)))

	cur.executemany('insert into test values(%s,%s)',values)

	cur.execute('update test set info="I am rollen" where id=3')

	conn.commit()
	cur.close()
	conn.close()

except MySQLdb.Error,e:
	print "Mysql Error %d: %s" % (e.args[0], e.args[1])