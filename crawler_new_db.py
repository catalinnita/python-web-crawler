##################################################
## PART 1 check for files and build urls list
##################################################

## import libraries
import os
import re
import requests
import datetime
import urllib.request
import urllib.error
import pymongo
import unicodedata
import ssl
import http
import time

from urllib.request import urlopen
from urllib.error import HTTPError
from bs4 import BeautifulSoup
from pymongo import MongoClient
from html.parser import HTMLParser
from datetime import timedelta, datetime, tzinfo

class scbdataURLS:

    def __init__(self, URL):

        # connect to DB
        client = MongoClient()
        client = MongoClient('localhost', 27017)
        self.db = client.Crawler
        
        # init vars
        self.all_links = []
        self.pos = 1
        self.index = 0

        # check for db saved so it continues from last parsed URL
        # it updates the self.all_links list
        # it updates the self.pos 
        self.resume_if_existing(URL)

        # get URLs from main page
        self.get_all_urls_from_page(URL, URL)
        
        # start parsing URLs from list
        self.init_parsing(URL)


    def resume_if_existing(self, URL):

        #try:
        saved_urls = self.db.url_list.find({"domain": URL})
        for link in saved_urls:
            self.all_links.append(link['url'])
            if 'parsed' in link.keys():
                self.pos = link['i']

        self.pos += 1

    ## get all urls from html code
    ## --> left 2 do: this is it, last thing add errors in a log file
    def get_all_urls_from_page(self, domain, url):
        
        html = ''
        print(len(self.all_links))
        try:
            ourl = u''+url
            ourl = unicodedata.normalize("NFC", ourl).encode('ASCII', 'ignore')
            ourl = urllib.request.quote(ourl, safe="%/:=&?~#+!$,;'@()*[]")
            print (ourl)
            html = urllib.request.urlopen(ourl).read()
        except urllib.error.HTTPError as err:
            print ("HTTP error:", err.code)
        except urllib.error.URLError as err:
            print ("Some other error happened:", err.reason)
        except UnicodeEncodeError as err:
            print ("Some problems encoding url:", err.reason)
        except ssl.CertificateError as err:
            print ("Some certificate issues")
        except UnicodeError as err:
            print ("Unicode error")
        except http.client.InvalidURL:
            print ("Invalid URL")
        except:
            print ("Unknown error")

        try:
            soup = BeautifulSoup(html, "html.parser")
            c = re.compile(r".*(\.jpg|\.png|\.gif|\.xml|\.pdf|http://|https://|mailto:)")
            links = soup.find_all('a', href=True)
                
            current = 0
            while current < len(links):
                link = links[current]['href'].rstrip('/')
                link = link.replace('www.', '')
                link = link.replace(domain, '')
                link = link.split("?")[0]
                link = link.split("#")[0]

                current += 1

                #print (link)
                #if link.startswith('/'):
                #    print (link)
                #    continue 

                if re.match(c, link) == None:
                    link = domain + link
                    if link not in self.all_links:
                        self.all_links.append(link)
                        self.save_link_in_db(domain, link)
                else:
                    continue
            self.url_parsed(url)
        except:
            print ("html parser error")

    
    ## add timestamp when the URL was parsed
    def url_parsed(self, url):
        self.db.url_list.update_one({"url" : url}, {"$set":{ "parsed" : datetime.now() }})
    

    ## init the parsing loop
    def init_parsing(self, domain):

        while self.pos < len(self.all_links):
            nurl = self.all_links[self.pos]
            self.get_all_urls_from_page(domain, nurl)
            self.pos += 1


    ## save one link in DB
    def save_link_in_db(self, domain, url):

        link_data = { "domain": domain, "url": url, "i" : self.index }
        try:
            self.index += 1
            self.db.url_list.insert_one(link_data)
        except pymongo.errors.DuplicateKeyError:
            print ('Existing link')


url = input('Enter url - ')
u = scbdataURLS( url )