#!/usr/bin/env python

import time,os
import urllib2,re,threading,thread,sys
from urlparse import urljoin, urlsplit
from signal import signal, SIGTERM, SIGINT, SIGHUP

'''
Simple webspider/site crawler adapted designed to follow all a links and walk the site in it's entirety
, idealy suited for cache prebuilding
__author__="David Busby"
__copyright__="David Busby Saiweb.co.uk"
__license__="GNU v3 + part 5d section 7: Redistribution/Reuse of this code is permitted under the GNU v3 license, as an additional term ALL code must carry the original Author(s) credit in comment form." 
'''

done=set()
newpages=set()

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

class child(threading.Thread):
	def __init__(self, threadID, page):
		self.threadID = threadID
       		self.page = page
        	threading.Thread.__init__(self)
	def run(self):
		try:
        		c=urllib2.urlopen(self.page)
	    	except:
        		print "Could not open %s" % self.page
        		sys.exit()	
    		dat = c.read()
     		#parse line by line
        	lines = re.split('\n',dat)
        	p=0
        	for line in lines:
        		if re.match('.*<a[^>]*/?>.*',line):
            			#grab the atrib str
             			m = re.match('.*<a([^>]*)/?>.*',line)
             			#exclude hashtags if not full urls
             			if not re.search('\'|"#', m.group(1)):
               	 			#grab href
               		 		h = re.match('.*href=[\'|"]([^\'|"]*)[\'|"].*',m.group(1))
                			if h != None:
                    				url = urljoin(self.page,h.group(1))
                    				if re.search(self.page,url) and url not in done:
                        			 	p+=1
	                      				newpages.add(url)
		done.add(self.page)
        	newpages.discard(self.page)
		opts.parsed += 1
		progress(p)
		sys.exit()

'''
Simple enough function returns true if threads are alive (still running) false on none alive
'''
def threadcheck():
	t=0
    	for thread in crawler.cThreads:
        	if thread.isAlive():
			t+=1
			opts.aThreads=t
		if t > 0:
			return True
		else:
			opts.aThreads=0
			return False

'''
This function loops through the "done" set, removing them from newpages to prevent
re-crawling, returns true if after this pages are left to crawl, false on none
'''
def _toparse():
	for d in done:
        	newpages.discard(d)
	i = 0
	for page in newpages:
		i += 1
	if i > 0:
		return True
	else:
		return False
	
'''
crawler class
'''
class crawler:
	cThreads=[]
	
	'''
	the crawler function
	'''
	def crawl(self,pages,mThread=1):
		tID = 0
		for page in pages:
			newpages.add(page)
		while _toparse():
			'''
				need to set cPages due to RuntimeError: Set changed size during iteration when multi threading
			'''
			cPages = list(newpages)
			for page in cPages:
				tID += 1
				c = child(tID,page)
				self.cThreads.append(c)
				c.start()
				threadcheck()
				while opts.aThreads >= mThreads:
					#print 'Reached max threads waiting on some to exit'
					print opts.aThreads
					time.sleep(1)
					threadcheck()
						
			while threadcheck() == True:
				#print 'Waiting for threads to complete'
				time.sleep(1)
			self.cThreads=[]

'''
progress bar information
'''
def progress(last):
	ctime = time.time()
	cparsed = opts.parsed
	if (ctime - opts.lTime) >= 2:
		opts.pStr = '[%s/s]'	% round((cparsed - opts.lParsed) / (ctime - opts.lTime),2)
	threadcheck()        
	str = " toParse: %s, lastAction: +%s, aThreads: %s %s" % (len(newpages),last,opts.aThreads,opts.pStr)
        
        while len(str) < opts.slen:
            str = '%s ' % str    
        opts.slen = len(str)
        sys.stdout.write(str + '\r')
        sys.stdout.flush()

	opts.lTime = ctime	
	opts.lParsed = cparsed

if __name__ == '__main__':

	q = 'How many threads do you want?:'

	try:
		mThreads = int(raw_input(q))
	except:
		print 'Invalid response, aborting'
		sys.exit(1)									
		
	q = 'Please enter the URL to spider (http://yoursite.com):'
        url = raw_input(q)
        c = crawler()
        c.crawl([url])

