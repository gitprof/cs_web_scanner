__author__ = 'Samuel'
import os
os.environ['http_proxy']=''
import shutil
import ctypes
import urllib
from urlparse import urlparse
from utilities.Misc  import Misc
from utilities.Misc  import TimeoutException

from Global import *

''' ***** WebInspector *****
Interface:
1. user intialize an instance w/o params
2. call config with:
 - the input URLs file.               saved in self.urls_file
 - a base dir for the output reports. saved in self.output_dir

Operation:
1. the Inspector go through the URLs in urls_file, and for every URL:
 - create dir with the domain name of the URL inside output_dir (if not exist)
 - put the report for the this URL inside that dir,
'''

grunt_dir =         os.path.join(BASE_DIR, "node_modules", "grunt-accessibility")
htmls_dir =         os.path.join(grunt_dir, "example")
INSPECTOR_DIR =         os.path.join(BASE_DIR, "data", "inspector")
urls_file =         os.path.join(BASE_DIR, "urls.txt")
urls_file_local =   os.path.join(BASE_DIR, "data", "inspector", "urls_local.txt")
HTML_FILE =         os.path.join(htmls_dir, "check.html")
OUTPUT_DIR =        os.path.join(BASE_DIR, "grunt_reports")
grunt_report_dir =  os.path.join(grunt_dir, "reports", "csv")
report_file =       os.path.join(grunt_report_dir, "report.csv")
GRUNT_LOG_FILE  =   "/dev/null" # os.path.join(BASE_DIR, 'logs', 'grunt.log')
#TMP_FILE_PATH =     os.path.join(BASE_DIR, 'tmp_url_file.txt')

MAX_URL_LEN = 110
GRUNT_TIMEOUT = 9

class WebInspector:
    def __init__(self):
        #set default:
        self.urls_file  = urls_file
        self.output_dir = OUTPUT_DIR
        self.debug    = register_debugger()
        self.misc     = Misc()

    def config(self, urls_file_in, output_dir_in):
        self.urls_file  = urls_file_in
        self.output_dir = output_dir_in
        return self

    ''' 0 - no exit. 1 - exit. 2 - immediate exit '''
    def check_quit_requests(self):
        try:
            workObj = self.inQ.get(False)
        except Queue.Empty:
            return 0
        self.debug.assrt(workObj.workID == WorkID.EXIT, "check_quit_requests: got unrecognized work requests. intergratation is needed!")
        self.debug.logger('check_quit_requests: got exit with type='+str(workObj.param))


    def get_url_domain(self, url):
        parsed_uri = urlparse(url)
        domain = '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_uri)
        domain = domain.replace("\n","").replace("http:","").replace("/","")
        return domain

    def clean_dir(self):
        try:
            filelist = [ f for f in os.listdir(self.output_dir)]
        except:
            filelist = []
        for filename in filelist:
            fullpath = os.path.join(self.output_dir, filename)
            shutil.rmtree(fullpath)

    def file_len(self, fname):
        with open(fname) as f:
    	    for i, l in enumerate(f):
	        pass
	return i + 1


    def url_scan(self):
        self.need_to_quit = 0
        #self.clean_dir()
        if not os.path.exists(INSPECTOR_DIR):
            os.makedirs(INSPECTOR_DIR)
        shutil.copyfile(self.urls_file, urls_file_local)
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
        #if os.path.isfile(HTML_FILE):
        #    os.remove(HTML_FILE)
        os.chdir(grunt_dir)
	url_count = 0

	num_urls = self.file_len(urls_file_local)
        with open(urls_file_local,"r") as f:
            for url in f:
		url_count += 1
		if len(url) > MAX_URL_LEN:
			continue
                if os.path.isfile(report_file):
                    os.remove(report_file)
                if os.path.isfile(HTML_FILE):
                    os.remove(HTML_FILE)
		self.debug.logger("getting html in url: %s" % (url),1)
		try:
	                f = urllib.urlopen(url)
		except:
			self.debug.logger("couldnt retrieve html from: %s" % (url),0)
			continue
                html_data = f.read()
                hf = open(HTML_FILE,"w")
                hf.write(html_data)
                self.debug.logger("(%d/%d) running grunt on: %s" % (url_count, num_urls, url),1)

                ### for debug - replacing grunt with demo report file ###
	        cmd = "sudo grunt accessibility > %s" % (GRUNT_LOG_FILE)
		self.debug.logger(cmd, 0)

		try:
                	self.misc.run_with_timer(os.system, (cmd,), "grunt accessibility timed out on url: "+url, True, GRUNT_TIMEOUT)
        	except TimeoutException:
			continue
            	except (KeyboardInterrupt, SystemExit) as e:
			raise

		#print("OOO GRUNT FAILED! on %s" % (url))
		#continue
                #with open(report_file, "w") as f:
                #    f.write('NOTICE: This line should be printed\n')
                #    f.write('ERROR: This line should be printed\n')
                #    f.write('NOTHING: This line shouldnt!\n')
                ### End Debug ###

                hf.close()
		try:
	                os.remove(HTML_FILE)
		except:
			demo = 0
                #handeling the grunt report
		try:
	            	rf = open(report_file,"r")
		except IOError:
			self.debug.logger("grunt failed on %s" % (url), 2)
			continue
                domain = self.get_url_domain(url)
                curr_output_dir = os.path.join(self.output_dir, domain)
                if not os.path.exists(curr_output_dir):
                    os.makedirs(curr_output_dir)
                of = open(os.path.join(curr_output_dir, url.replace("\n","").replace("http://","").replace("/","_")+".csv"), 'w')
                for line in rf:
                    if line.startswith("NOTICE") or line.startswith("ERROR") or line.startswith("heading, "):
                        of.write(line)
                of.close()
                rf.close()
                if (self.need_to_quit == 2):
                    return



if __name__ == "__main__":
    webInspector = WebInspector()
    webInspector.url_scan()
