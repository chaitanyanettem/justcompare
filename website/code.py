import web
import re
import urllib2
import json
import traceback

render = web.template.render('/var/www/justcompare/templates/')
db = web.database(dbn = 'postgres', user = 'chaitanya', pw = 'nettem', db='compare')
urls = (
	'', 'index',
	'/', 'index',
	'/search', 'search',
	'/book/(.*)', 'book',
	'/about', 'about'
) 


class index:
	def GET(self):
		#what = 'count(isbn)'
		#count = db.select('books_bookdata', what=what)
		count = 1200000
		return render.index(count)

class search:
	def GET(self):
		input_q = web.input()
		query = (input_q.q).strip()
		query = re.sub("\s+","|",query)
		query = re.sub("'","''",query)
#SELECT book_name, isbn, ts_rank(fts, to_tsquery('english', 'fashion'), 1) 
#AS rank, fts
#from books_bookdata 
#where fts @@ to_tsquery ('english','fashion')
#order by rank desc;	
		what_essential = "isbn,book_name,author_name,"
		what_prices    = "min_price,"
		what_misc      = "fts, ts_rank(fts,to_tsquery('english', '{0}'), 1) AS rank".format(query)
		what_total     = what_essential+what_prices+what_misc
		whereq 		   = "fts @@ to_tsquery('english','{0}')".format(query) 
		#myvar = dict('lang':'english','query':'input_q','normalization':1)
		ordered = db.select('books_bookdata', what=what_total,where=whereq,order="rank DESC", limit=30)
		return render.search(input_q.q, ordered)

class book:
	def GET(self, isbn):
		what_essential = "isbn,book_name,author_name,"
		what_prices    = "hs18_price,fk_price,infibeam_price,indiaplaza_price,crossword_price,bookadda_price,landmark_price,min_price,"
		what_images    = "hs18_img_src,fk_img_src,infibeam_img_src,indiaplaza_img_src,crossword_img_src,bookadda_img_src,"
		what_links     = "hs18_booklink,fk_booklink,infibeam_booklink,indiaplaza_booklink,bookadda_booklink,crossword_booklink,landmark_booklink"
		what_total     = what_essential+what_prices+what_images+what_links
		price = ["hs18_price","fk_price","infibeam_price","indiaplaza_price","crossword_price","bookadda_price"]
		isbnvar = "isbn = '{0}'".format(isbn)
		book_details = db.select('books_bookdata',what=what_total,where=isbnvar)
		gbooks = "https://www.googleapis.com/books/v1/volumes?q={0}".format(isbn)
		try:
			gbooks = json.load(urllib2.urlopen(gbooks))
			descr = gbooks['items'][0]['volumeInfo']['description']
			if len(descr)>350:
				descr = ''.join([descr,"..."])
		except:
			descr="Sorry! Description currently unavailable."
		return render.book(book_details,descr)

class about:
	def GET(self):
		what = 'count(isbn)'
		count = db.select('books_bookdata', what=what)
		return render.about(count)

if __name__ == "__main__":
	app = web.application(urls, globals())
	app.run()

application = web.application(urls, globals()).wsgifunc()
