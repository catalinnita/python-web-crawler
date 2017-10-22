# python-web-crawler
This is a webcrawler and indexer working with python and mongodb

1. get urls list
===========================
 - run crawler_new_db.py for indexing all urls from a webpage
 - enter the url of the page where you want to start
 ------
 notes: 
 	- duplicate urls are ignored
 ------
 bugs and improvements: 
 	- improve speed

2. index words for each page
 - run crawler-text.py
 notes:
 	- you can set up weights for headings
 	- wordpres from stop-words.txt are not saved
 bugs and improvements:
    - it's slow, need speed improvements, guardian.com was indexed in 3 days

3. up next
 - sentiment analysis  	