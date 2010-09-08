

import time,os
import urllib2,re,threading,thread,sys
from urlparse import urljoin, urlsplit

'''
Simple webspider/site crawler adapted designed to follow all a links and walk the site in it's entirety
, idealy suited for cache prebuilding, this version hacked to provide AB stats
__author__="David Busby"
__copyright__="David Busby Saiweb.co.uk"
__license__="GNU v3 + part 5d section 7: Redistribution/Reuse of this code is permitted under the GNU v3 license, as an additional term ALL code must carry the original Author(s) credit in comment form." 
'''

done=set()
newpages=set()
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
		print 'parsed',self.page,'got',p,'internal links'
		d = urlsplit(self.page)
		bpl = re.subn('/','-',d.path)[0]
		if len(bpl) == 0:
			bpl = 'homepage'
		try:
			c=urllib2.urlopen(self.page)
			prg = os.system("ab -c 100 -n 100 -g '/root/benchwalk/%s.bpl' %s/ "%(bpl,self.page))
		except:
			return False
		#prg = os.popen("ab -c 100 -n 10 -g ./%s.bpl %s/ "%(self.page,self.page),"r")
		#i=0
		#for line in prg.readlines():
		#	i+=1
			#this is realy just here to make the prog wait during benchmarking
		#thread.exit()	

def threadcheck():
	t=0
    	for thread in crawler.cThreads:
        	if thread.isAlive():
			t+=1
			aThreads=t
		if t > 0:
			return True
		else:
			return False

def _toparse():
	for d in done:
        	newpages.discard(d)
	i = 0
	for page in newpages:
		i += 1
	print i
	if i > 0:
		return True
	else:
		return False
	
 
class crawler:
	cThreads=[]
		
	def crawl(self,pages,mThread=1):
		for page in pages:
			newpages.add(page)
		while _toparse():
			pages = newpages
			for page in pages:
				newpages.add(page)
				p = 0
			for page in newpages:
				p += 1
				c = child(p,page)
				self.cThreads.append(c)
				c.start()
				
				threadcheck()
				while aThreads >= mThreads:
					print 'Reached max threads waiting on some to exit'
					time.sleep(1)
					threadcheck()	

			while threadcheck() == True:
				print 'Waiting for threads to complete'
				time.sleep(1)
			self.cThreads=[]

if __name__ == '__main__':
	if not os.path.isdir('/root/benchwalk'):
		print '/root/benchwalk required, please mkdir /root/benchwalk and retry'
		sys.exit(1)	
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

