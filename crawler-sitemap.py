
## use this to print a timestamp - useful for optimization
def print_time(text):
    print (text)
    print (int(round(time.time() * 1000)))



## --------
## just check the url type and return it
## this one will be replaced by a var sent by the php I think
def check_url_type(url):
    url_split = url.split(".")[-1]
    if url_split == 'xml':
        return 'sitemap'
    else:
        return 'sitepage'

## ---------
## checks for the existing of robots.txt
def check_robots(url):
    url = url + '/robots.txt'
    
    try:    
        robots_content = urllib.request.urlopen(url).read()
    except:
        return False
    
    if len( re.findall(b'<!DOCTYPE', robots_content) ) == 0 & len( re.findall(b'<html', robots_content) ) == 0 :
        return True
    else:
        return False

## ----------
## parses robots.txt and returns a list with all rules and sitemaps if there is any
def get_robots(url):
    url = url + '/robots.txt'
    txt = urllib.request.urlopen(url).read()
    lines = txt.split(b'\n')
    sitemaps = list()
    disallows = list()
    disallow = 0
    ret = {}

    for line in lines:

        disallow_url = re.findall(b"Disallow: (.*)", line)
        if len(disallow_url) > 0:
            disallows.append(str(disallow_url).strip("'[]'"))
            if disallow_url == '/':
                disallow = 1;

        # find sitemaps urls
        sitemap_url = re.findall(b"^Sitemap: (.*)", line)
        if len(sitemap_url) > 0:
            sitemaps.append(str(sitemap_url).strip("'[]'"))

    ret['disallows'] = disallows;
    ret['sitemaps'] = sitemaps;
    ret['disallow_all'] = disallow;
    
    return ret

## ---------------
## get all urls from sitemap and goes after other sitemaps 
def ck_get_urls(url, dep):
    
    xml = urllib.request.urlopen(url).read()
    soup = BeautifulSoup(xml)
    links = soup.find_all('loc')
    link_urls = list()
    
    for link in links:
        link = link.getText()
        
        if link[-4:] == '.xml':
            new_links = ck_get_urls(link, 2)
            link_urls.extend(new_links)
        else:
            link_urls.append(link)       

    return link_urls

## ------------
## gets and returns all urls from a list of sitemaps
def get_all_urls_from_sitemap(sitemaps, robots):
    articles = list()
    if robots['disallow_all'] != 1:
        for sitemap in sitemaps:
            article_url = ck_get_urls(sitemap, 1)
            articles.extend(article_url)
    
    return articles


sitemaps = []
robots = []

## ====> check if the url is a sitemap or a website page
if check_url_type(url) == 'sitemap':
    sitemaps.append(url)

## ====> if the input is not a sitemap check if robots.txt exists
if check_url_type(url) == 'sitepage':

    ## if robots.txt exists check for sitemaps
    if check_robots(url) == True:
        robots = get_robots(url)

    print (robots);

    ## if there are sitemaps listed in robots.txt assign them to sitemaps var
    if int(len(robots)) > 0:
        sitemaps = robots['sitemaps']

###### Sitemap should exist here if it doesn't the only way is to parse the urls from the front page
        
## if sitemaps exists get all urls from them
if int(len(sitemaps)) > 0:
    urls = get_all_urls_from_sitemap(sitemaps, robots)

## if sitemap is empty parse the main page and get the urls 
if int(len(sitemaps)) < 1:    