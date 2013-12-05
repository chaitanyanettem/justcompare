#! /usr/bin/python
import traceback
import psycopg2
import time
import requests
import re
from bs4 import BeautifulSoup
import sys
import isbncon
reload(sys)
sys.setdefaultencoding("utf-8")
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


base_link="http://www.indiaplaza.com"
pattern=re.compile("None")
pattern1=re.compile("books")
isbn_re = re.compile("\d{13}")
isbn10_re = re.compile("\d{10}")
price_re = re.compile("\d+")
#whitespace_re = re.compile("\s\s+")

var1=requests.get("http://www.indiaplaza.com/books/")
soup1=BeautifulSoup(var1.text)
find1=soup1.find('div',{"id":"ip-2-filters"})
f1=open('indiaplazacategorylinks','w')
for link in find1.find_all('a'):
	if pattern.search(str(link.get('href'))):
		continue
	f1.write("http://www.indiaplaza.com"+str(link.get('href')))
	f1.write('\n')
f1.write('#')
f1.close()

con1=psycopg2.connect(database='compare', user='chaitanya', password='nettem')
cur1=con1.cursor()
					
f1=open('indiaplazacategorylinks','r')
f2=open('indiaplazabooklinks','a')
f3=open('indiaplazabooks','a')
f4=open('indiaplazacatpages','a',1)

link2=''
try:
	while True:
		line=f1.readline()
		if line.startswith('#'):
			break
		url1=line[:-1]
		var=request_passable(url1)
		if not var:
			log.write(str(datetime.now())+":{0} skipped".format(line[:-1]))
			continue	
		soup=BeautifulSoup(var.text)
		page=1
		while True:
			i=0
			flag=0
			f4.write(url1+"\n")
			while True:
				try:
					div_id="ContentPlaceHolder1_BrowseControl_dlBrowseView_HyperLink2_"+str(i)
					#book_link = str((soup.find('a',id=div_id)).get('href'))
					book_link = soup.find('a',id=div_id)
					if i!=0 and (not book_link):
						break
					if i==0 and (not book_link):
						flag=1
						break
					book_link = str(book_link.get('href'))
					full_link = str(base_link) + str(book_link)
					full_link=str(full_link)
					i += 1
					f2.write(full_link+'\n')
					book_details=request_passable(full_link)
					if not book_details:
						log.write(str(datetime.now())+":{0} skipped".format(full_link))
						continue
					detail_soup = BeautifulSoup(book_details.text)
					isbn = (detail_soup.find('span',itemprop="isbn"))
					if isbn is None:
						find1=detail_soup.find('div',{"class":"bksfdpltrArea"})
						if find1.ul.li.span.h2 is None:
							continue
						isbn=find1.ul.li.span.h2.text
						isbn13=isbncon.convert(str(isbn))
					else:
						isbn13 = str((isbn_re.findall(isbn.text))[0])
					print isbn13
					book_name = str((detail_soup.find('span',itemprop="name")).text)
					book_name = ' '.join((book_name).split())
					print book_name
					#book_name = whitespace_re.sub("",book_name)
					author = detail_soup.find('a',{"class":"skuAuthorName"})
					if author:
						author = str(author.text)
					else:
						author = ""
					print author
					book_prices = str((detail_soup.find('span',itemprop="price")).text)
					if (detail_soup.find('span',itemprop="price")) is None:
						continue
					book_price = int((price_re.findall(book_prices))[0])
					print book_price
					image=(detail_soup.find('span',itemprop="image"))
					if not(image.img is None):
						img_src=str(image.img.get('src'))
					else:
						img_src=''
					cur1.execute("select * from books_bookdata where isbn=%(isbn)s",{'isbn':isbn13})
					row=cur1.fetchone()
					if row is None:
						cur1.execute("insert into books_bookdata(isbn,book_name,author_name,indiaplaza_price,indiaplaza_img_src,indiaplaza_booklink) values(%s,%s,%s,%s,%s,%s)",(isbn13,book_name,author,book_price,img_src,full_link))
					elif (row[2] is None and not(author is None)):
						cur1.execute("update books_bookdata set author_name=%s where isbn=%s",(author,isbn13))
						cur1.execute("update books_bookdata set indiaplaza_price=%s,indiaplaza_img_src=%s,indiaplaza_booklink=%s where isbn=%s",(book_price,img_src,full_link,isbn13))
					else:
						cur1.execute("update books_bookdata set indiaplaza_price=%s,indiaplaza_img_src=%s,indiaplaza_booklink=%s where isbn=%s",(book_price,img_src,full_link,isbn13))
					con1.commit()
				except Exception, e:
					traceback.print_exc()
					log.write(str(datetime.now())+":"+traceback.format_exc()+":"+full_link)
					continue
			####
			if flag==1:
				break
			page += 1
			url1=line[:-6]+str(page)+".htm"
			try:
				var = requests.get(url1)
				soup = BeautifulSoup(var.text)
			except Exception, e:
				pass
			
	f2.write('#')
	f2.close()
	f1.close()
	f4.close()
except IndexError, i:
	pass
except Exception, e:
	if con1:
		con1.rollback()	
	traceback.print_exc()
	log.write(str(datetime.now())+traceback.format_exc())
finally:
	if con1:
		con1.close() 