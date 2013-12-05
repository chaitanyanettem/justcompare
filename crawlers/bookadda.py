#! /usr/bin/python

import requests
from bs4 import BeautifulSoup
import re
import sys
reload(sys)
sys.setdefaultencoding("utf-8")

var=requests.get("http://www.bookadda.com")
soup=BeautifulSoup(var.text)

find1=soup.find('ul',{"class":"left_menu"})

f=open("bookaddalinks.txt",'w')
for link in find1.find_all('a'):
	f.write(link.get('href'))
	f.write('\n')
f.write('#')
f.close()
pattern=re.compile("filter")
pattern0=re.compile("books")
f=open("bookaddalinks.txt",'r')
while True:
	line=f.readline()
	if line.startswith('#'):
		break
	var2=requests.get(line)
	soup2=BeautifulSoup(var2.text)
	find2=soup2.find('ul',{"class":"left_menu"})
	f2=open("addabooklinks.txt",'a')
	for link in find2.find_all('a'):
		if pattern.search(link.get('href')):
			continue
		f2.write(link.get('href'))
		f2.write('\n')
f2.write('#')
f2.close()
f2=open("addabooklinks.txt",'r')
link2=''
while True:
	line=f2.readline()
	if line.startswith('#'):
		break
	var3=requests.get(line)
	soup3=BeautifulSoup(var3.text)
	lineread=soup3.find('div',{"class":"head"})
	no=re.findall(' \d+ ', str(re.findall(' \d+ ',str(lineread.text))))
	offset=int(no[2])
	while (not(offset%20==0)):
		offset=offset-1
	print offset
	f3=open("booklinks1.txt",'a')
	f4=open("addabookinfo.txt",'a')
	i=0
	while i<=offset:
		line2=(line+"?pager.offset="+str(offset))
		var3=requests.get(line2)
		soup3=BeautifulSoup(var3.text)
	 	find3=soup3.find('ul',{"class":"results"})
		i=i+20
		for link in find3.find_all('a'):
			if pattern0.search(str(link.get('href'))):
				if link.get('href')==link2:
					continue			
				f3.write(link.get('href'))
				f3.write('\n')
				link2=link.get('href')
				var4=requests.get(link2)
				soup4=BeautifulSoup(var4.text)
				find4=soup4.find('table', style="width: 100%; padding: 10px 10px 10px 10px;")
				f4.write(line2)				
				f4.write(find4.text)
				find5=soup4.find('table',{"class":"tbl"})
				find6=find5.find('span',{"class":"actlprc"})
				f4.write(find6.text)
				find7=soup4.find('span',{"class":"stckdtls"})
				f4.write(find7.text)
				find8=soup4.find('span',{"class":"numofdys"})
				f4.write(find8.text)
f3.write('#')
f3.close()
f2.close()
f.close()
pattern1=re.compile("online")
pattern2=re.compile("kits")
pattern3=re.compile("view-books")
pattern4=re.compile("cds")
pattern5=re.compile("competitive-exams")
pattern6=re.compile("schools")

f4=open("acadzonelinks.txt",'w')
find4=soup.find('div',{"id":"smoothmenu2"},{"class":"ddsmoothmenu-v"})

for link in find4.find_all('a'):
	if pattern1.search(link.get('href')):
		continue
	if pattern2.search(link.get('href')):
		continue
	if pattern3.search(link.get('href')):
		continue
	if pattern4.search(link.get('href')):
		continue
	if pattern5.search(link.get('href')):
		continue
	if link.get('href').startswith('#'):
		continue
	if pattern6.search(link.get('href')) and link.get('href')==link2:
		continue
	f4.write(link.get('href'))
	link2=link.get('href')
	f4.write('\n')

f4.close()	


