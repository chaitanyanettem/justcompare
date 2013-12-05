#! /usr/bin/python
import traceback
import psycopg2
import requests
from bs4 import BeautifulSoup
import re
import sys
import isbncon
from datetime import datetime
import time
reload(sys)
sys.setdefaultencoding("utf-8")

log=open('log.txt','w')

def request_passable(url):
	max_repeats = 3
	count = 0
	flag = 0
	while True:
		try:
			page = requests.get(url,timeout=10)
			flag = 1
			break
		except Exception, e:
			print "\n"
			traceback.print_exc()
			while True:
				try:
					page = requests.get("http://www.google.com",timeout=5)
					break
				except requests.exceptions.ConnectionError:
					print "!!Sleeping for 30s.!!\n"
					logging = str(datetime.now())+": Connection problem. Sleeping for 30 seconds."
					log.write(logging)
					time.sleep(30)
			count += 1
			if count >= max_repeats:
				break
	if flag==1:
		return page
	else:
		return False

pattern=re.compile("books")
var1=requests.get("http://www.crossword.in/")
soup1=BeautifulSoup(var1.text)

addr="http://www.crossword.in"
find1=soup1.find('div',{"class":"navigation_links"})
f1=open('crosswordlinks.txt','w')
for link in find1.find_all('a'):
	f1.write(addr+link.get('href'))
	f1.write('\n')
f1.write('#')
f1.close()
link2=''
f1=open('crosswordlinks.txt','r')
f2=open('crosswordbooklinks.txt','a')
pattern2=re.compile("\d{9}[\dXx]")
try:
	con=psycopg2.connect(database='compare', user='chaitanya', password='nettem')
	cur=con.cursor()
	while True:
		line=f1.readline()
		if line.startswith('#'):
			break
		print "***********************\n\n{0}\n\n******************".format(line)   
		var2=request_passable(line)
		if not var2:
			logging = (str(datetime.now())+":{0} skipped"+"\n").format(line)
			log.write(logging)
			continue
		soup2=BeautifulSoup(var2.text)
		line2=soup2.find('div',{"class":"search-summary"})
		no=re.findall(' \d+ ',str(re.findall(' \d+ ',line2.text)))
		pages=int(no[0])
		print "o"
		while pages%16!=0:
			pages=pages+1
		print "o"
		pages=pages/16
		i=1
		while i<=pages:
			req_url=line+"?page="+str(i)
			var2=request_passable(req_url)
			i=i+1
			if not var2:
				logging =str(datetime.now())+(":{0} skipped".format(req_url))+"\n"
				log.write(logging)
				continue
			print "########\n\n{0}\n\n########".format(req_url) 
			soup2=BeautifulSoup(var2.text)
			find2=soup2.find('ul',{"id":"search-result-items"},{"class":"list-view clearfix"})
			for link in find2.find_all('a'):
				try:
					if pattern.search(str(link.get('href'))): 
						if not(link.get('href')==link2):
							f2.write(link.get('href'))
							f2.write('\n')
							link2=link.get('href')
							url=("http://www.crossword.in"+link2)
							var3=request_passable(url)
							if var3 is False:
								logging = (str(datetime.now())+":{0} skipped"+"\n").format(url)
								log.write(logging)
								continue
							print "@@@ {0} @@@".format(url)
							soup3=BeautifulSoup(var3.text)
							find3=soup3.find('div',{"id":"title"})
							title=find3.h1.text
							print title
							find4=soup3.find('div',{"class":"our_price"})
							if find4 is None:
								find4=soup3.find('div',{"class":"list_price "})
								if find4 is None:
									continue
							cost=((find4.text).split(" "))[3]
							cost=cost.replace(",","")
							print cost
							find5=soup3.find('span',{"class":"ctbr-name"})
							if find5 is None:
								author=''
							else:
								author=find5.text
							print(author)
							find6=soup3.find('div',{"id":"features"},{"class":"clearfix"})
							if find6 is None:
								continue
							isbn=(pattern2.findall(find6.text))[0]
							isbn=isbncon.convert(str(isbn))
							print isbn
							cur.execute("select * from books_bookdata where isbn=%(isbn)s",{"isbn":isbn})
							row=cur.fetchone()
							if row is None:
								cur.execute("insert into books_bookdata(isbn,book_name,author_name,crossword_price,crossword_booklink) values(%s,%s,%s,%s,%s)",(isbn,title,author,cost,url))
							elif (row[2] is None and not(author is None)):
								cur.execute("update books_bookdata set author_name=%s where isbn=%s",(author,isbn))
								cur.execute("update books_bookdata set crossword_price=%s, crossword_booklink=%s where isbn=%s",(cost,url,isbn))
							else:
								cur.execute("update books_bookdata set crossword_price=%s, crossword_booklink=%s where isbn=%s",(cost,url,isbn))
							con.commit()    
				except Exception, e:
					traceback.print_exc()
					log.write(str(datetime.now())+":"+traceback.format_exc()+"\n")
					continue		
	f2.write('#')
	f2.close()
	f1.close()
except Exception, e:
	if con:
		con.rollback()
	#print 'error %s', e
	traceback.print_exc()
	log.write(str(datetime.now())+traceback.format_exc())
					
finally:
	if con:
		con.close()
#   print "finally"
#print "asd"