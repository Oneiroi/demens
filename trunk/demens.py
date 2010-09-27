#!/usr/bin/env python

import time,os,copy,getopt
import httplib,re,threading,thread,sys
from urlparse import urljoin, urlsplit
from signal import signal, SIGTERM, SIGINT, SIGHUP

'''
demens : (dementis ) :  insane, mad, out of one's mind.
The name has been chosen due to the insanity suffered in trying to code this in such a short amount of time.
and trying to get it working,

This "app" is desgined to help with cache population of a site using an edge cache such as varnish, it will lookfor and request js,css,html,images

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
	dead={}
	ltParse=0
	version = 1.00*(sys.version_info[0]+(1.00*sys.version_info[1]/10))

def run(page,ip):
	u = urlsplit(page)	
	c = httplib.HTTPConnection(ip)
	if opts.version >= 2.6:
		headers={'host':u.netloc,'User-Agent':'demens - cache populator by D.Busby'}
		gheaders={'host':u.netloc,'User-Agent':'demens - cache populator by D.Busby','accept-encoding':'gzip'}
		uri=u.path
	else:
		headers={'host':u[1],'User-Agent':'demens - cache populator by D.Busby'}
		gheaders={'host':u[1],'User-Agent':'demens - cache populator by D.Busby','accept-encoding':'gzip'}
		uri=u[2]
		
	c.request('GET',uri,{},headers)
	r = c.getresponse()
	g = c.request('GET',uri,{},gheaders)
	if r.status != 200:
		opts.dead.update({'url':page,"code":r.status})

	if not re.search('\.(css|js|jpe?g|png|gif)$',page):
		dat = r .read()
		'''anchor tags'''	
       		for m in re.finditer('<a([^>]*)/?>',dat,re.DOTALL):
			h = re.match('.*href=[\'|"]([^\'|"]*)[\'|"].*',m.group(1))
			p=0
			if h != None:
       	        		url = urljoin(page,h.group(1))
       	 			if re.search(page,url) and url not in opts.done:
       	 				p+=1
	       				opts.newpages.add(url)
		'''link tags'''
		for m in re.finditer('<link([^>]*)/?>',dat,re.DOTALL):
       	        	h = re.match('.*href=[\'|"]([^\'|"]*)[\'|"].*',m.group(1))
       	        	p=0
                	if h != None:
                       		url = urljoin(page,h.group(1))
                        	if re.search(page,url) and url not in opts.done:
                                	p+=1
                                	opts.newpages.add(url)
		'''script tags'''
		for m in re.finditer('<script([^>]*)/?>',dat,re.DOTALL):
                	h = re.match('.*src=[\'|"]([^\'|"]*)[\'|"].*',m.group(1))
                	p=0
                	if h != None:
                        	url = urljoin(page,h.group(1))
                        	if re.search(page,url) and url not in opts.done:
                               		p+=1
                                	opts.newpages.add(url)
		'''img tags'''
                for m in re.finditer('<img([^>]*)/?>',dat,re.DOTALL):
                        h = re.match('.*src=[\'|"]([^\'|"]*)[\'|"].*',m.group(1))
                        p=0
                        if h != None:
                                url = urljoin(page,h.group(1))
                                if re.search(page,url) and url not in opts.done:
                                        p+=1
                                        opts.newpages.add(url)
	opts.parsed+=1
	opts.done.add(page)
        opts.newpages.discard(page)
		
'''
progress bar information
'''
def progress():
	ctime = time.time()
	cparsed = opts.parsed

	if ctime - opts.lTime >=2:
		pStr = '[%s/s]' % round(((1.00*opts.parsed-opts.lParsed)/(1.00*ctime-opts.lTime)),3)
	str = " toParse: %s, parsed: %s, last change: %s %s" % (len(opts.newpages),opts.parsed,(len(opts.newpages)-opts.ltParse),pStr)
        
        while len(str) < opts.slen:
            str = '%s ' % str    

        opts.slen = len(str)
        sys.stdout.write(str + '\r')
        sys.stdout.flush()

	opts.lTime = ctime	
	opts.lParsed = cparsed
	opts.ltParse = len(opts.newpages)

def usage():
	print sys.argv[0],'-u <url entry point> -i <ip of cache server>'
	sys.exit(2)

if __name__ == '__main__':
	try:
       		gOpts, args = getopt.getopt(sys.argv[1:], "hu:i:", ["help", "url=","ip="])
    	except getopt.GetoptError, err:
        	print str(err)
        	usage()
        	sys.exit(2)	
	u = None
	i = None
	for o,a in gOpts:
		if o in ("-h","--help"):
			usage()
		elif o in ("-u","--url"):
			u = a
		elif o in ("-i","--ip"):
			i = a
		else:
			assert False, "unhandled option"
	if u == None or i == None:
		usage()
	opts.newpages.add(u)
	while len(opts.newpages) > 0:
		pages = copy.copy(opts.newpages)
		for page in pages:
			if time.time() - opts.lTime >=2:
				progress()
			run(page,i)
	if len(opts.dead) > 0:
		print opts.dead	
