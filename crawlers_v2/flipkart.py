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
data = {}
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

def database_insert():
    for isbn in data:
        cur.execute("select * from books_bookdata where isbn=%(isbn)s",{"isbn":isbn})
        row=cur.fetchone()
        if row is None:
            cur.execute("insert into books_bookdata(isbn,book_name,author_name,fk_price,fk_booklink) values(%s,%s,%s,%s,%s)",(isbn,data[isbn][0],data[isbn][1],data[isbn][2],data[isbn][3]))
        else:
            if (row[2] is None and not(data[isbn][1] is '[?]')):
                cur.execute("update books_bookdata set author_name=%s where isbn=%s",(data[isbn][1],isbn))
            cur.execute("update books_bookdata set fk_price=%s, fk_booklink=%s where isbn=%s",(data[isbn][2],data[isbn][3],isbn))
        con.commit()    



#TO-DO : add command line arguments with *argparse*

##Using ''.find(str) faster than using regex matching
log = open('flipkart_log.txt','w')

category = open('flipkart_categories.txt','r')
con=psycopg2.connect(database='compare', user='chaitanya', password='nettem')
cur=con.cursor()

#try:
while True:

    number = 1
    url_manipulate = []
    current_category = category.readline()
    if current_category.startswith('#'):
        break
    #Debug:
    print "Current Category:",current_category
    logging = ''.join([str(datetime.now()), " : ", current_category])
    log.write(logging)
    pr_location = current_category.find('pr?')
    url_parameters[1] = current_category[pr_location+3:-1]
    url = ''.join([current_category[:pr_location+3],url_parameters[0],url_parameters[1],url_parameters[2]])
    while True:
        current_category_page = requests_passable(url.format(number=number))
        number += 20
        soup = BeautifulSoup(BeautifulSoup(str(current_category_page.text)).prettify(formatter=None))
        #soup = BeautifulSoup(BeautifulSoup(current_category_page.text).prettify(formatter='none'))
        book_boxes = soup.findAll('div',{'class':'browse-product'})
        data = {}
        for book in book_boxes:
            #title_wrapper_div = book.find('div',{'class':'lu-title-wrapper'})
            a_links = book.findAll('a')
            book_name = str(a_links[2].string)
            book_link = ''.join(["http://www.flipkart.com",a_links[0].get('href')])
            isbn_pos = book_link.find('pid=') + len('pid=')
            book_isbn = book_link[isbn_pos:isbn_pos+13]
            author_name = str(a_links[1].string)
            book_price = book.find('div',{'class':'pu-final'}).text
            book_price = int((book_price.strip())[3:]) #[3:] removes leading 'Rs. '
            data[book_isbn] = [book_name,author_name,book_price,book_link]
        #Debug:
        #print data
        database_insert()
        #soup.findAll('a',)
#except Exception, e:
    #print traceback.print_exc()
con.close()