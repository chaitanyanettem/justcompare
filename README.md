Justcompare
===========

Justcompare is a price comparison engine. It functions in a form very similar to search engines.

This project has one scraper for each website which is tracked. Tracked websites are: Flipkart.com, bookadda.com, crossword.in, landmarkonthenet.com, homeshop18.com and indiaplaza.com.

Two of the scrapers (Flipkart.com and bookadda.com) are not functional currently due to large scale changes to those sites since the scrapers were written. Each scraper is built to not stop until all books are covered. Thus all exceptions are caught.

All the data from these scrapers is indexed in a database using the psycopg2 library. The web.py framework is used to present a web site as an interface to the database. Postgresql's full text search capabilities are utilised for providing search.

Effort was put into designing and building a clean website UI from scratch. All of this code is presented here under the MIT license.

Developers
==========

Development was done by Chaitanya Nettem and Deepak Bhagchandani.
