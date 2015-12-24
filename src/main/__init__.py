# -*- coding: utf-8 -*- 

import re
import sys
import logging
from time import sleep
import codecs
import urllib,urllib2,cookielib
from bs4 import BeautifulSoup

class Question():
    id = ''
    def __init__(self, id, name, percent, ac, total, last_update):
        self.id = id
        self.name = name
        self.percent = percent
        self.ac = ac
        self.total = total
        self.last_update = last_update
    def print_question(self):
        print "%-10s%-40s%.2f%%(%7s/%7s)%50s" %(self.id,self.name,self.percent*100,self.ac,self.total,self.last_update)

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

#     def submit(self,pid,language,src):
#         submit_data = dict(
#                 problem_id = pid,
#                 language = POJ.LANGUAGE[language.upper()],
#                 source = src,
#                 submit = 'Submit',)
#         postdata2 = urllib.urlencode(submit_data)
#         try:
#             req2 = urllib2.Request(POJ.URL_SUBMIT,data = postdata2)
#             res = self.opener.open(POJ.URL_SUBMIT,postdata2).read()
#             logging.info('submit successful')
#             return True
#         except:
#             logging.error('submit error')
#             return False
    def getVolumn(self, num):
        url=self.URL_HOME + 'problemlist?volume=%d' % num
        return urllib2.urlopen(url).read()
        
#     def result(self,user_id):
#         url = POJ.URL_STATUS + urllib.urlencode({'user_id':user_id})
#         page = urllib2.urlopen(url)
#         soup = BeautifulSoup(page)
#         table = soup.findAll('table',{'class':'a'}) 
#         pattern = re.compile(r'>[-+: \w]*<')  
#         result = pattern.findall(str(table))
#         wait = ['Running & Judging','Compiling','Waiting']
#         for i in range(3):
#             if result[32][1:-1]==wait[i] or result[32][1:-1] == '':
#                 logging.info(result[32])
#                 sleep(1)
#                 return False
#         num = [21,24,28,32,35,37,40,43,45]
#         for i in range(9):
#             print POJ.INFO[i],':',result[num[i]][1:-1]
#         return True
def save_result(result_list):
    wfile=codecs.open("result.dat", 'a', 'utf-8')
    size=len(result_list)
    for i in result_list:
        wfile.write("%-10s%-40s%.2f%%(%7s/%7s)%50s\n" %(i.id,i.name,i.percent*100,i.ac,i.total,i.last_update))
    wfile.close()

if __name__=='__main__':
    FORMAT = '----%(message)s----'
    logging.basicConfig(level=logging.INFO,format = FORMAT)
    if len(sys.argv) > 1: 
        user_id, pwd, pid, lang, src, = sys.argv[1:]
        src = open(src,'r').read()
    else:  
        user_id = 'username'
        pwd = 'passwd'
        pid = 1000
        lang = 'gcc'
        src = '''
        #include<stdio.h>
        int main()
        {
            int a,b;
            scanf("%d%d",&a,&b);
            printf("%d",a+b);
            return 0;
        }
        '''
    poj = POJ(user_id,pwd)
    q_list = list()
    ID=0
    NAME=0
    PER=0
    AC=0
    TOTAL=0
    LAST_UPDATE=0
    #poj.login()
#         if poj.submit(pid,lang,src):
#             logging.info('getting result')
#             status = poj.result(user_id)
#             while status!=True:  
#                 status = poj.result(user_id)
    page = 0
    while 1:
        page += 1
        #page=17
        print"read page %d.." %page        
        str = poj.getVolumn(page)
        if str.find("problem_id")< 0:
            print "find end page is %d" %(page-1)
            break
        soup = BeautifulSoup(str)
        tr_tags = soup.findAll('tr', align='center')
        for tr in tr_tags:
            i=0
            for st in tr.strings:
                if(i==0):
                    ID=st.string
                elif(i==1):
                    NAME=st.string
                elif(i==3):
                    AC=st.string
                elif(i==5):
                    TOTAL=st.string
                elif(i==7):
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
            
                
            #print "%.2f%%" %(PER*100)
            q_list.append(Question(ID,NAME,PER,AC,TOTAL,LAST_UPDATE))
        sleep(3)
        #break
#     new_q = Question(21, "a加3","324%", "234234", "1234245", "2015-12-24")
#     q_list = list()
#     q_list.append(new_q)
#     new_q = Question(2, "a加b2","324%", "234234", "1234245", "2015-12-24")
#     q_list.append(new_q)
#     new_q = Question(3000, "a加b","55%", "234234", "1234245", "2015-12-24")
#     q_list.append(new_q)
# #    q_list.sort(lambda p1, p2:cmp(p1.id,p2.id))
    q_list.sort(key=lambda Question:Question.percent,reverse=1)
#     for one in q_list:
#         one.print_question()
    save_result(q_list)
    print"save result end!"
#     q_list[0].print_question()
#     q_list[1].print_question()
#     q_list[2].print_question()