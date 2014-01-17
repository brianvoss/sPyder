# sPyder - a simple SEO page analysis tool
# author: Brian Voss <bvoss@yahoo-inc.com>
 
import sys
import httplib
import urllib2
import re
import getopt

from BeautifulSoup import BeautifulSoup
from urlparse import urlparse
from util.urlfetch import fetch

# Config options
debug = True
same_domain_only = True
request_headers = [{
	'User-Agent':'Yahoo! sPyder'
}]

# Link / info containers
url = None
depth = 1
baseuri = None
site = {}
pages = {}

errors =[]
url_list = []
unprocessed = []
processed = []


def main( url, depth ):
	global site
	site = parseUrl(url)
	i = 1
	start_page = process(url, None)
	unprocessed.append( start_page )
	
	while ( len( unprocessed ) > 0) and depth > 0:
		
		current_page = unprocessed.pop(0)
		links = current_page['links'][:]
		
		while len(links) > 0:
			link = links.pop(0)
			url = str(link['href'])
			
			new_page = process( url, baseuri )
			if not ( new_page == None ):
				unprocessed.append( new_page )

		processed.append( current_page['url'] )
		pages[current_page['url']] = current_page
		print '=========================================='
		print 'Iteration: %s' % i
		print 'Link Queue: %s' % len(unprocessed)
		print '=========================================='
		depth = depth - 1
		i = i + 1
	
	# Print Some Results
	print 'Crawled %i pages' % len(pages)
	print 'Processed %i pages' % len(processed)
	print processed
	print ' - with %i errors:' % len(errors)
	print errors


def process( url, base_uri=None ):
	
	# only follow links once
	if url in processed:
		print 'Skipping processed url: %s' % url
		return None

	# Parse the url
	linkInfo = parseUrl( url )
	
	# Only follow http[s] links
	if linkInfo['protocol'] not in ['http', 'https']:
		return None
	
	# Enforce same domain only policy
	if ( same_domain_only == True ):
		if ( linkInfo.get('domain') != site.get('domain') ):
			#print 'Skipping non-local link %s' % url
			return None
			
	# Enforce Base URI if provided
	if not ( base_uri == None ):
		if ( linkInfo['uri'].startswith(base_uri) == False ):
			print 'URI %s not in BaseURI: %s' % ( linkInfo['uri'], base_uri )
			return None

	# Create a 'unique' URL (minus query string)
	unique_url = '%s://%s%s' % ( linkInfo['protocol'], linkInfo['domain'], linkInfo['uri'])
	# Only continue if URL has not already been handled
	if not ( unique_url in url_list ):
		url_list.append( unique_url )
	else:
		return None
	
	# Try to retrieve the page contents
	try:
		response = fetch( linkInfo['url'], '', [], debug )
	except urllib2.HTTPError as e:
		print e.code
		print e.msg
		#print e.headers
		#print e.fp.read()
		errors.append({url: e.code})
		return None
	
	if response.getcode() != 200:
		errors.append({url: response.status})
		return
	else:
		print 'processing page: %s' % url
		contents = response.read()
		pageObj = processPage( url, contents )

	return pageObj


def processPage( url, html ):
	# Parse the document
	doc = BeautifulSoup( html )
	# Create an object
	pageObj = {
		'url': url,
		'spidered': False,
		'links': [],
		'no_follow_links': [],
		'images': [],
		'linked_to_from': []
	}
	# Index all images & links
	links = doc.findAll('a')
	images = doc.findAll('img')
	
	# Check link attributes
	for link in links:
		try:
			href = str(link['href'])
		except:
			continue

		if 'rel' in link:
			if str(link['rel']) == 'nofollow':
				pageObj['no_follow_links'].append(link)
			else:
				pageObj['links'].append(link)
		else:
			pageObj['links'].append(link)

	# Check image attributes
	for img in images:
		# todo
		pageObj['images'].append( img )
		
	return pageObj
	

def parseUrl( url ):

	url_info = {}
	
	parse = urlparse(url)
	proto = parse.scheme
	host = parse.netloc
	uri = parse.path
	
	# Fix empty protocol in relative links
	if proto == '':
		proto = 'http'
	
	# Fix empty host in relative links
	if host == '':
		if not site['domain']:
			#print 'Found a local relative link, but cannot resolve local domain.'
			return url_info
		else:
			host = site['domain']
	#print 'host: %s' % host
	
	# Fix relative URI without beginning slash
	if not uri.startswith("/"):
		uri = "/%s" % uri

	#print 'uri: %s' % uri
	
	
	urlinfo = {
		'url': '%s://%s%s' % ( proto, host, uri ),
		'protocol': proto,
		'domain': host,
		'uri': uri
	}
	#print parse
	#print urlinfo
	return urlinfo
	

def usage():
	print '%s -ud' % sys.argv[0]
	print ''
	print '-u URL to be crawled'
	print '-d depth to continue crawl (optional)'

try:
    opts, args = getopt.getopt(sys.argv[1:], "u:dl", ["depth=", "url=", "baseuri="])
except getopt.GetoptError as err:
    # print help information and exit:
    print str(err) # will print something like "option -a not recognized"
    sys.exit(2)

for o, a in opts:
	if o in ("-u", "--url"):
		url = a
	elif o in ("-d", "--depth"):
		depth = int(a)
	elif o in ("-l", "--baseuri"):
		baseuri = a
	else:
		assert False, "unhandled option"

if ( url == None):
	usage()
	sys.exit(2)

if __name__ == '__main__':
	main( url, depth )
