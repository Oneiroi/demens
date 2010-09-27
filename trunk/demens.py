#!/usr/bin/env python

import time,os,copy
import httplib,re,threading,thread,sys
from urlparse import urljoin, urlsplit
from signal import signal, SIGTERM, SIGINT, SIGHUP

'''
demens : (dementis ) :  insane, mad, out of one's mind.
The name has been chosen due to the insanity suffered in trying to code this in such a short amount of time.
and trying to get it working,

This "app" is desgined to help with the following:

Spidering an entire site checking varnish cache status, gzip / deflate compatibility, and remoprting dead links

__author__="David Busby"
__copyright__="David Busby Saiweb.co.uk"
__license__="GNU v3 + part 5d section 7: Redistribution/Reuse of this code is permitted under the GNU v3 license, as an additional term ALL code must carry the original Author(s) credit in comment form." 
'''

'''
opts, stub class
'''
class opts:
	slen = 0
	parsed = 0
	lParsed = 0
	lTime = 0
	pStr = ''
	aThreads = 0
	cThreads = []
	done=set()
	newpages=set()
	dead=set()

def run(page):
	u = urlsplit(page)	
	c = httplib.HTTPConnection(u.netloc)
	c.request('GET',u.path)
	r = c.getresponse()
	headers = {'User-Agent':'demens','accept-encoding':'gzip'}
	g = c.request('GET',u.path,{},headers)
	dat = r.read()
	
       	for m in re.finditer('<a([^>]*)/?>',dat,re.DOTALL):
		h = re.match('.*href=[\'|"]([^\'|"]*)[\'|"].*',m.group(1))
		p=0
		if h != None:
               		url = urljoin(page,h.group(1))
        		if re.search(page,url) and url not in opts.done:
        			p+=1
	       			opts.newpages.add(url)
		progress(p)
	opts.done.add(page)
        opts.newpages.discard(page)
        
		
		
'''
progress bar information
'''
def progress(last):
	ctime = time.time()
	cparsed = opts.parsed
	if (ctime - opts.lTime) >= 2:
		opts.pStr = '[%s/s]'	% round((cparsed - opts.lParsed) / (ctime - opts.lTime),2)
	str = " toParse: %s, lastAction: +%s %s" % (len(opts.newpages),last,opts.pStr)
        
        while len(str) < opts.slen:
            str = '%s ' % str    
        opts.slen = len(str)
        sys.stdout.write(str + '\r')
        sys.stdout.flush()

	opts.lTime = ctime	
	opts.lParsed = cparsed

if __name__ == '__main__':
	opts.newpages.add('http://www.worldtravelguide.net/')
	while len(opts.newpages) > 0:
		pages = copy.copy(opts.newpages)
		for page in pages:
			run(page)
	
