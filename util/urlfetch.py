#!/usr/bin/env python
# encoding: utf-8
"""
urlfetch.py

Created by Brian Voss on 2013-08-08.
Copyright (c) 2013 Yahoo! All rights reserved.
"""

import sys
import os
import urllib
import urllib2

def fetch( url, params, headers, debug=False ):
	if debug == True:
		print '@Fetch: %s' % url
	response = None
	# Only use Request object if headers
	# need to be set
	if headers:
		req = urllib2.Request(url, params, headers)
		req.add_header('Accept', 'application/json;q=0.9,*/*;q=0.8')
		req.add_header('accept-language', 'en-US,en;q=0.8')
		req.add_header('cache-control','max-age=0')
		
		if debug == True:
			print '@Req: full url: %s' % req.get_full_url()
			print '@Req: type: %s' % req.get_type()
			print '@Req: host: %s' % req.get_host()
			print '@Req: selector: %s' % req.get_selector()
		response = urllib2.urlopen(req)
	else:
		response = urllib2.urlopen( url )
		
	return response