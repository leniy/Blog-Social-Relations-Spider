# -*- coding: utf-8 -*-
"""
Created on Tue Nov 27 08:44:58 2012

@author: Leniy
"""

import urllib2
import re

def searchurl(root_blog = "http://blog.leniy.info"):
    """
    返回值格式：
        {
            root_blog的域名host_url: 搜索到的外部链接的字典{}
        }

    外链字典的格式：
        {
            外链域名: 外链名字
        }
    """

    #存外链字典的临时变量
    tempurl = {}

    #定义获取的url及对应UA、ref参数
    request = urllib2.Request(root_blog)
    request.add_header('User-Agent', 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.9 Safari/536.5')
    request.add_header('Referer', 'http://blog.leniy.info/')

    #获取root_blog的域名，命名为root_host，用于后续排除本站内部链接
    root_proto, root_rest = urllib2.splittype(root_blog)
    root_host, root_rest = urllib2.splithost(root_rest)

    #获取链接和链接名称
    try:
        response = urllib2.urlopen(request)
        html = response.read()
        find_re = re.compile(r'<li><a .*?href="(.+?)".*?>(.+?)</a></li>', re.DOTALL)
        for x in find_re.findall(html):
            #排除本站内部链接
            proto, rest = urllib2.splittype(x[0])
            host, rest = urllib2.splithost(rest)
            if(host != root_host and host!=None):
                values = {host: x[1]}
                tempurl.update(values)
    #若异常，打印HTTPError返回值
    except:
        print "==================\n",root_blog," can't open\n==================\n"

    return {root_host: tempurl}

def main():
    starturl = 'xiaoxia.org'
    allurl = {}
    temp = searchurl("http://" + starturl)
    allurl.update(temp)
    print allurl,'\n=====================================\n'
    for k in temp[starturl]:
        temptemp = searchurl("http://" + k)
        allurl.update(temptemp)
        print allurl,'\n=====================================\n'


main()
print "=======================\n\n\n OK!!!"
