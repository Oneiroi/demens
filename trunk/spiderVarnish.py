
import httplib
import time,os
import urllib2,re,threading,thread,sys
from urlparse import urljoin, urlsplit

'''
Simple webspider/site crawler adapted designed to follow all a links and walk the site in it's entirety
- hacked to death to provide Varnish diagnostics
__author__="David Busby"
__copyright__="David Busby Saiweb.co.uk"
__license__="GNU v3 + part 5d section 7: Redistribution/Reuse of this code is permitted under the GNU v3 license, as an additional term ALL code must carry the original Author(s) credit in comment form." 
'''

done=set()
newpages=set()
aThreads = 0
pCount=0

def parseInfo(inf,page):
	varnish = False
	for item in inf:
		if item == 'x-varnish':
			varnish = True
			vdata = inf[item]
	if varnish == False:
		print '[ERROR] - No varnish cache on %s' % page
	else:
		dat = re.split(' ',vdata)
		if dat[0] == dat[1]:
			print '[WARN] - Varish cache page, generated when requested'	
class child(threading.Thread):
	def __init__(self, threadID, page):
		self.threadID = threadID
       		self.page = page
        	threading.Thread.__init__(self)
	def run(self):
		''' try to open connection '''
		try:
			c = urllib2.urlopen(self.page)
			inf = c.info()
		except:
			print 'Failed to open',self.page
			sys.exit(1)

		''' validate varnish is running on this request '''

		parseInfo(inf,self.page)
	
		''' read the data and parse line by line '''			
		dat = c.read()
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
		print self.page
		done.add(self.page)
        	newpages.discard(self.page)
		#print 'parsed',self.page,'got',p,'internal links'

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
	if i > 0:
		return True
	else:
		return False
	
 
class crawler:
	cThreads=[]
		
	def crawl(self,pages):
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
				while aThreads >= 5:
					print 'Reached max threads waiting on some to exit'
					time.sleep(1)
					threadcheck()	

			while threadcheck() == True:
				print 'Waiting for threads to complete'
				time.sleep(1)
			self.cThreads=[]

if __name__ == "__main__":

	q = 'Please enter the URL to spider (http://yoursite.com):'
	url = raw_input(q)						
	c = crawler()

	c.crawl([url])
			

