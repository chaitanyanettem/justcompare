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

var=requests.get("http://www.homeshop18.com/books/category:10000/")
soup=BeautifulSoup(var.text)

l1=soup.find('div',{"class":"filter-box"})

f=open('hs18links.txt','w')
for link in l1.find_all('a'):
    if link.get('href').startswith('#'):		
		break
    f.write(link.get('href')[0:link.get('href').index("?")])
    f.write('\n')
f.write('#')
f.close();
pattern=re.compile("bestseller")
f=open('hs18links.txt','r')
f2=open('hs18booklinks.txt','a')
try:
	i=0
	while True:
		r1=f.readline();
		if r1.startswith('#'):		
			break
		if pattern.search(r1):
			continue
		r1="http://www.homeshop18.com"+r1;
		print r1
		var2=request_passable(r1)
		if not var2:
			log.write(str(datetime.now())+":{0} skipped").format(r1)
			continue
		soup2=BeautifulSoup(var2.text)
        	l2=soup2.find('a',{"title":"Books"})
		no=int(l2.small.text[1:-1])
		while (no%24)!=0:
			no=no-1
		print no
		while i<=no:
			r2=r1[:-1]+'start:'+str(i)
			print r2
			var3=request_passable(r2)
			if not var3:
				log.write(str(datetime.now())+":{0} skipped").format(r2)
				continue
			soup3=BeautifulSoup(var3.text)
			d=soup3.find('div',{"id":"searchResultsDiv"},{"class":"clearfix"})
			l3=d.find_all('a',{"class":"productTitle"})
			for link2 in l3:
				f2.write(link2.get('href')[0:link2.get('href').index("?")])
				f2.write('\n')
				print('\n')
				print(link2.get('href'))
			i=i+24
		i=0
except Exception, e:
	traceback.print_exc()
	log.write(str(datetime.now())+":"+traceback.format_exc()+":"+r2)
	
f2.write('#')
f2.close()
f2=open('hs18booklinks.txt','r')
pattern2=re.compile('\d{13}')
pattern3=re.compile('\d{10}')
pattern4=re.compile('\d+')
con=None
try:
	while True:
		try:
			r3=f2.readline()
			if r3.startswith('#'):		
				break
			r3="http://www.homeshop18.com"+r3
			var4=request_passable(r3)
			if not var4:
				log.write(str(datetime.now())+":{0} skipped").format(r3)
				continue
			soup4=BeautifulSoup(var4.text)
			con =psycopg2.connect(database='compare', user='chaitanya', password='nettem')
			cur=con.cursor()
			i1=soup4.find('table',{'class':'more-detail-tb'})
			i2=(pattern2.findall(i1.text))[0]
			if i2 is None:
				i2=(pattern3.findall(i1.text))[0]
				if i2 is None:
					continue
				i2=isbncon.convert(str(i2))	
			isbn13=str(i2)
			d1=soup4.find('div',{'id':'product-info'},{'class':'product-info'})
			title=d1.h1.span.text
			d2=soup4.find('div',{'class':'costs'})
			if d2.h3.span is None:
				continue
			cost=int((pattern4.findall(d2.h3.span.text))[0])
			d3=soup4.find('table',{'class':'more-detail-tb'})
			d4=d3.find('a',itemprop="author")
			if d4 is None:
				author=''
			else:
				author=d4.text
			d6=soup4.find('div',{"class":"productMeduimImage clearfix"})
			if d6.img is None:
				img_src=''
			else:
				img_src=d6.img.get('src')
			cur.execute("select * from books_bookdata where isbn=%(isbn)s",{'isbn':isbn13})
			row=cur.fetchone()
			if row is None:
				cur.execute("insert into books_bookdata(isbn,book_name,author_name,hs18_price,hs18_img_src,hs18_booklink) values(%s,%s,%s,%s,%s,%s)",(isbn13,title,author[:-1],cost,img_src,r3))
			elif (row[2] is None and not(author is None)):
				cur.execute("update books_bookdata set author_name=%s where isbn=%s",(author,isbn13))
				cur.execute("update books_bookdata set hs18_price=%s,hs18_img_src=%s,hs18_booklink=%s where isbn=%s",(cost,img_src,r3,isbn13))
			else:
				cur.execute("update books_bookdata set hs18_price=%s,hs18_img_src=%s,hs18_booklink=%s where isbn=%s",(cost,img_src,r3,isbn13))
			con.commit()
			d7=soup4.find('span',itemprop="description")
			if d7.p is None or d7.p.span is None:
				cur.execute("insert into description values(%s,%s)",(isbn13,"No Description Available"))
				con.commit()
				continue
			cur.execute("insert into description values(%s,%s)",(isbn13,d7.p.span.text[:999]))
			con.commit()
		except Exception, e:
			traceback.print_exc()
			log.write(str(datetime.now())+":"+traceback.format_exc()+":"+r3)
			continue
except Exception, e:
	if con:
		con.rollback()
	traceback.print_exc()
	log.write(str(datetime.now())+traceback.format_exc())
finally:
	if con:
		con.close()	
f2.close()
f.close()
