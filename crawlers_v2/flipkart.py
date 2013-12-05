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

url_parameters = ['p%5B%5D=sort&','','&start={number}&ajax=true']

def requests_passable(url):
	print "url:",url
	max_repeats = 3
	count = 0
	flag = 0
	headers = {'user-agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko)\
	 Chrome/31.0.1650.57 Safari/537.36'}
	#'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/31.0.1650.57 Safari/537.36'
	while True:
		try:
			page = requests.get(url, timeout=5, headers = headers)
			if page.status_code >= 400:
				return False
			elif page.url == 'http://www.flipkart.com/':
				return False
			else:
				return page

		except Exception, e:
			print "\n"
			traceback.print_exc()
			logging = ''.join([str(datetime.now()),":", traceback.format_exc()])
			log.write(traceback.format_exc())
			while True:
				try:
					page = requests.get("http://www.google.com", 
						timeout=5, headers = headers)
 					if page.status_code == 'http://www.flipkart.com/':
						return False
					else:
						return page
				except requests.exceptions.ConnectionError:
					print "ALERT: Sleeping for 10s.\n"
					logging = ''.join([str(datetime.now()), ": Connection problem. Sleeping for 10 seconds.\n",traceback.format_exc()])
					log.write(logging)
					time.sleep(10)
			count += 1
			if count >= max_repeats:
				return False

def update_categories():	
	category = open('flipkart_categories.txt','w')
	page = requests_passable("http://www.flipkart.com/all-categories-books?\
		otracker=ch_vn_book_filter_Categories in Books_All Categories")
	soup = BeautifulSoup(page.text)
	
	all_category_links = soup.findAll('div',{'class':'fk-acat-item-text'})
	for link in all_category_links:
		category_link = ''.join(['http://www.flipkart.com', link.find('a').get('href')])
		follow_category_link = requests_passable(category_link)
		if follow_category_link:
			category.write(follow_category_link.url)
			category.write("\n")
	category.write("#")
	category.close()


#TO-DO : add command line arguments with *argparse*

#Convert:
#http://www.flipkart.com/books/educational-and-professional/academic-and-professional/pr?sid=bks%2Cenp%2Cq2s
#/books/educational-and-professional/academic-and-professional/pr?p%5B%5D=sort&sid=bks%2Cenp%2Cq2s&start=41&ajax=true


##Using ''.find(str) faster than using regex matching
log = open('flipkart_log.txt','w')

category = open('flipkart_categories.txt','r')
#try:
while True:
	number = 1
	url_manipulate = []
	current_category = category.readline()
	if current_category.startswith('#'):
		break
	print "Current Category:",current_category
	logging = ''.join([str(datetime.now()), " : ", current_category])
	log.write(logging)
	print "i am here!"
	pr_location = current_category.find('pr?')
	url_parameters[1] = current_category[pr_location+3:-1]
	url = ''.join([current_category[:pr_location+3],url_parameters[0],url_parameters[1],url_parameters[2]])
	while True:
		current_category_page = requests_passable(url.format(number=number))
		number += 20
		soup = BeautifulSoup(BeautifulSoup(str(current_category_page.text)).prettify(formatter=None))
		#soup = BeautifulSoup(BeautifulSoup(current_category_page.text).prettify(formatter='none'))
		book_boxes = soup.findAll('div',{'class':'browse-product'})
		for book in book_boxes:
			title_wrapper_div = book.find('div',{'class':'lu-title-wrapper'})
			a_links = book.findAll('a')
			print a_links
			book_name = str(a_links[0].string)
			book_link = a_links[0].get('href')
			author_name = str(a_links[1].string)
			book_price = book.find('div',{'class':'pu-final'}).text
			print book_name,":",author_name,":",book_price,"\n"
			exit()
		soup.findAll('a',)
#except Exception, e:
print "a"
print traceback.print_exc()
