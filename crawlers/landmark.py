#!/usr/bin/python
import traceback
import psycopg2
import requests
from bs4 import BeautifulSoup
import re
import sys
reload(sys)
sys.setdefaultencoding("utf-8")
import isbncon
import time
from datetime import datetime

log=open('log6.txt','w')

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

var=requests.get("http://www.landmarkonthenet.com/books/categories/")
soup=BeautifulSoup(var.text)
find1=soup.find('ul',{"class":"sitemap page_listing clearfix"})
f1=open("landmarkcategorylinks.txt",'w')
for link in find1.find_all('a'):
	f1.write("http://www.landmarkonthenet.com"+link.get('href'))
	f1.write('\n')
f1.write('#')
f1.close()

f1=open("landmarkcategorylinks.txt",'r')
f2=open("landmarkbooklinks.txt",'a')
pattern=re.compile(" \d* ")
pattern1=re.compile("/books/")
pattern2=re.compile("\d{13}")
try:
	con=psycopg2.connect(database='compare', user='chaitanya', password='nettem')
	cur=con.cursor()
	while True:
		line=f1.readline()
		if line.startswith('#'):
			break
		var2=request_passable(line)
		if not var2:
			log.write((str(datetime.now())+":{0} skipped").format(line))
			continue
		soup2=BeautifulSoup(var2.text)
		find2=soup2.find('li',{"class":"items"})
		no=re.findall(' \d+ ',str(find2.text))
		pages=int(no[0])
		while (pages%30)!=0:
			pages=pages+1
		pages=pages/30
		print pages
		i=1
		while i<=pages:
			var3=request_passable(line+"?page="+str(i))
			if not var3:
				log.write((str(datetime.now())+":{0} skipped").format(line+"?page="+str(i)))
				continue
			soup3=BeautifulSoup(var3.text)
			i=i+1
			find3=soup3.find('div',{"class":"productblock pb-browselist clearfix"})
			link2=''
			for link in find3.find_all('a'):
				try:
					if (link2==str(link.get('href'))):
						continue
					if pattern1.search(link.get('href')):
						continue
					f2.write(link.get('href'))
					f2.write('\n')
					link2=link.get('href')
					url="http://www.landmarkonthenet.com"+link2
					var4=request_passable(url)
					if not var4:
						log.write((str(datetime.now())+":{0} skipped").format(url))
						continue
					soup4=BeautifulSoup(var4.text)
					find4=soup4.find('div',{"class":"primary"})
					title=find4.h1.text.replace("Paperback","")
					title=title.replace("Hardcover","")
					title=title.strip()
					title=title.replace('\n','')
					print title
					find5=soup4.find('p',{"class":"author"})
					if find5.a is None:
						author=''
					else:
						author=str(find5.a.text)
					print author
					find6=soup4.find('span',{"class":"price-current"})
					if find6 is None:
						continue
					price=str(find6.text)
					price=price.replace(",","")
					price=(re.findall('\d+',str(price))[0])
					print price
					find7=soup4.find('ul',{"class":"blank"})
					if find7 is None:
						continue
					isbn=((re.findall('\d{13}',str(find7.text)))[0])
					if not(isbn):
						continue
					print isbn
					find8=soup4.find('a',{"class":"imagemain ready"})
					if find8 is None:
						img_src=''
					else:
						img_src=str(find8.img.get('src'))
					print img_src
					cur.execute("select * from books_bookdata where isbn=%(isbn)s",{"isbn":isbn})
					row=cur.fetchone()
					if row is None:
						cur.execute("insert into books_bookdata(isbn,book_name,author_name,landmark_price,landmark_booklink,landmark_img_src) values(%s,%s,%s,%s,%s,%s)",(isbn,title,author,price,link2,img_src))
					elif (row[2] is None and not(author is None)):
						cur.execute("update books_bookdata set author_name=%s where isbn=%s",(author,isbn))
						cur.execute("update books_bookdata set landmark_price=%s, landmark_booklink=%s, landmark_img_src=%s where isbn=%s",(price,url,img_src,isbn))
					else:
						cur.execute("update books_bookdata set landmark_price=%s, landmark_booklink=%s, landmark_img_src=%s where isbn=%s",(price,url,img_src,isbn))
					con.commit()
				except IndexError, i:
					traceback.print_exc()
					log.write(str(datetime.now())+":"+traceback.format_exc()+":"+link2)
					continue
				except Exception, e:
					traceback.print_exc()
					log.write(str(datetime.now())+":"+traceback.format_exc()+":"+link2)
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
