## import libraries
import os
import re
import requests
import datetime
import urllib.request
import urllib.error
import pymongo
import unicodedata
import string
import operator

from urllib.request import urlopen
from urllib.error import HTTPError
from bs4 import BeautifulSoup
from pymongo import MongoClient
from operator import itemgetter

def get_weights(key):
	weights = {}
	weights['h1'] = 15
	weights['h2'] = 8
	weights['h3'] = 5
	weights['h4'] = 4
	weights['h5'] = 3
	weights['h6'] = 2
	weights['p'] = 1

	return weights[key]

def get_words_list(type):

	with open(type+'-words.txt') as f:
		lines = f.read().splitlines()
	
	return lines

def split_by_words(tags, wtype):

	wordcount={}
	for tag, content in tags.items():

		content = join_all_tags(content).lower()
		words = content.split()
		words = remove_stop_words(words)

		if int(len(words)) > 0:

			if wtype == 'raw':
				weight_val = 1
			elif wtype == 'weights':
				weight_val = get_weights(tag)
			elif wtype == 'normalized':
				weight_val = get_weights(tag)/int(len(words))
			
			for word in words:
				word = word.decode("utf-8")

				if word not in wordcount:
					wordcount[word] = weight_val
				else:
					wordcount[word] += weight_val
	
	wordcount = sorted(wordcount.items(), key=itemgetter(1), reverse=True)

	return wordcount

def clean_up_text(text):

	# punctuation
	text = re.sub('['+string.punctuation+']', '', text)

	return text

def join_all_tags(tags_list):

	text = ''
	for l in tags_list:
		text += str(l.get_text())

	text = clean_up_text(text)
	text = unicodedata.normalize("NFC", text).encode('ASCII', 'ignore')

	return text

def remove_values_from_list(the_list, val):
   return [value for value in the_list if value != val]

def remove_stop_words(words):
	# stop words

	for word in words:
		if word.decode() in get_words_list('stop'):
			words = remove_values_from_list(words, word)
	
	return words

def get_all_tags_from_page(url):

	html = ''
	try:
		ourl = u''+url
		ourl = unicodedata.normalize("NFC", ourl).encode('ASCII', 'ignore')
		ourl = urllib.request.quote(ourl, safe="%/:=&?~#+!$,;'@()*[]")
		html = urllib.request.urlopen(ourl).read()
	except urllib.error.HTTPError as err:
		if err.code == 404:
			print ("Page not found!")
		elif err.code == 403:
			print ("Access denied!")
		else:
			print ("Something happened! Error code", err.code)
	except urllib.error.URLError as err:
		print ("Some other error happened:", err.reason)
	except UnicodeEncodeError as err:
		print ("Some problems encoding url:", err.reason)
	except ssl.CertificateError as err:
		print ("Some certificate issues:")
	except UnicodeError as err:
		print ("Unicode error")
	except http.client.InvalidURL:
		print ("Invalid URL")
    
	tags = {}
	if int(len(html)) > 0:
		soup = BeautifulSoup(html, "html.parser")
		stags = ['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p']
		for key in stags:
			tags[key] = soup.find_all(key)

	return tags


def get_all_metas_from_page(domain, url):

	print ('nothing')

def get_all_url_info(domain, url):

	print ('nothing')

def get_all_urls():

	client = MongoClient()
	client = MongoClient('localhost', 27017)
	db = client.Crawler
    
	urlsp = db.url_list.find()

	return urlsp

## add urls in db
def save_words_in_db(url, words):
    
    client = MongoClient()
    client = MongoClient('localhost', 27017)
    db = client.Crawler

    if int(len(words)) > 0:
    	words_data = {"url": url, "words": words}
    	try:
    		post_id = db.words_list.insert_one(words_data)
    	except pymongo.errors.DuplicateKeyError:
    		print ('Existing link')


urls = get_all_urls()
for doc in urls:

	url = doc['url']
	try:
		print (url)
	except:
		print ("error")

	tags = get_all_tags_from_page(url)

	words = {}
	words['raw'] = split_by_words(tags, 'raw')
	words['weights'] = split_by_words(tags, 'weights')
	words['normalized'] = split_by_words(tags, 'normalized')
	
	save_words_in_db(url, words)