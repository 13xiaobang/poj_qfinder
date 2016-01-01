# -*- coding: utf-8 -*- 
import re
import sys
import logging
import time
from time import sleep
import codecs
import urllib,urllib2,cookielib
from bs4 import BeautifulSoup
from inspect import strseq
import ConfigParser
from ConfigParser import ConfigParser
import string, os, sys

class Question():
    id = ''
    def __init__(self, id, name, percent, ac, total, last_update, page):
        self.id = id
        self.name = name
        self.percent = percent
        self.ac = ac
        self.total = total
        self.last_update = last_update
        self.page = page
    def print_question(self):
        print "%-10s%-40s%.2f%%(%7s/%7s)%20spage:%10s" %(self.id,self.name,self.percent*100,self.ac,self.total,self.last_update,page)

class POJ:
    URL_HOME = 'http://poj.org/'
    URL_LOGIN = URL_HOME + 'login?'
    URL_SUBMIT = URL_HOME + 'submit?'
    URL_STATUS = URL_HOME + 'status?'
    res = ''
    INFO =['RunID','User','Problem','Result','Memory','Time','Language','Code Length','Submit Time']

    LANGUAGE = {
            'G++':'0',
            'GCC':'1',
            'JAVA':'2',
            'PASCAL':'3',
            'C++':'4',
            'C':'5',
            'FORTRAN':'6',
            }

    def __init__(self, user_id, password):
        self.user_id = user_id
        self.password = password
        cj = cookielib.LWPCookieJar()
        self.opener =urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
        urllib2.install_opener(self.opener)

    def login(self):
        data = dict(
                user_id1 = self.user_id,
                password1 = self.password,
                B1 = 'login',
                url = '.')
        postdata = urllib.urlencode(data)
        try:
            req = urllib2.Request(POJ.URL_LOGIN,postdata)
            print req
            self.res = self.opener.open(POJ.URL_LOGIN,postdata).read()
            if self.res.find('loginlog')>0: 
                print "login successful!"
                return True
            else:
                print "login failed"
                return False
        except:
            print 'login failed'
            return False
        
    def getVolumn(self, num):
        url=self.URL_HOME + 'problemlist?volume=%d' % num
        return urllib2.urlopen(url).read()
    
    def getUserState(self):
        url=self.URL_HOME + 'userstatus?user_id=%s' %self.user_id
        return urllib2.urlopen(url).read()
    
def id_in_list(this_list, id):
    for ele in this_list:
        if(ele == id):
            return True
    return False

def save_result(result_list, user_done_list):
    timeArray = time.localtime(int(time.time()))
    filename = time.strftime("%Y-%m-%d_%H_%M_%S", timeArray)
    filename += ".dat"
    wfile=codecs.open(filename, 'w', 'utf-8')
    for i in result_list:
        if(id_in_list(user_done_list, i.id)):
            wfile.write("*%s:%-9s%-70s%.2f%%(%7s/%7s)%15s\n" %(i.id,i.page,i.name,i.percent*100,i.ac,i.total,i.last_update))
        else:
            wfile.write("%s:%-10s%-70s%.2f%%(%7s/%7s)%15s\n" %(i.id,i.page,i.name,i.percent*100,i.ac,i.total,i.last_update))
    wfile.close()
    print"save result to %s" %filename
    
def cal_len(gen_strs):
    a = 0
    for i in gen_strs:
        a+=1
    return a

if __name__=='__main__':
    if os.path.exists('login.config'):
        print "login.config exist"
        cf = ConfigParser()
        cf.read("login.config")
        user_id = cf.get("account", "name")
        pwd = cf.get("account", "passwd")
    else:
        user_id = ''
        pwd = ''
        print "no login.config file"
        
    poj = POJ(user_id,pwd)
    q_list = list()

    page = 0
    while 1:
        page += 1
        #page=28
        str = poj.getVolumn(page)
        if str.find("problem_id")< 0:
            print "find end page is %d" %(page-1)
            break
        print"page %d.." %page
        soup = BeautifulSoup(str)
        tr_tags = soup.findAll('tr', align='center')
        for tr in tr_tags:
            i=0
            st_len = cal_len(tr.strings)
            for st in tr.strings:
                if(i==0):
                    ID=st.string
                elif(i==1):
                    NAME=st.string
                elif(i==st_len-5):
                    AC=st.string
                elif(i==st_len-3):
                    TOTAL=st.string
                elif(i==st_len-1):
                    LAST_UPDATE=st.string
                i += 1
            try:
                PER=float(AC)/float(TOTAL)
            except ValueError:
                print 'value error, ID=%s' %ID
                PER=0.0000
                AC = 100
                TOTAL = 200
                LAST_UPDATE='2015-12-24'
            q_list.append(Question(ID,NAME,PER,AC,TOTAL,LAST_UPDATE,page))
        sleep(1)
        #break
    q_list.sort(key=lambda Question:Question.percent,reverse=1)
    user_done_list = list();
    str = poj.getUserState()
    if(str.find("Sorry")>0):
        print "no such user id: %s in POJ" %poj.user_id
    else: 
        index = str.find('p(')
        if index > 0:
            index += 2; #skip the first "p(id)"
            while 1:
                index = str.find('p(', index)
                if index < 0:
                    break
                user_done_list.append(str[index+2:index+6])
                index += 7

    save_result(q_list,user_done_list)