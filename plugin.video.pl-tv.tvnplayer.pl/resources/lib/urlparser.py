# -*- coding: utf-8 -*-
import cookielib, os, string, StringIO
import urllib, urllib2, re, sys
import xbmcaddon, xbmc, xbmcgui

scriptID   = sys.modules[ "__main__" ].scriptID
t = sys.modules[ "__main__" ].language
ptv = xbmcaddon.Addon(scriptID)

import sdLog, sdParser, sdSettings, sdCommon
import anyfiles

if sys.version_info >= (2,7): import json as _json
else: import simplejson as _json

log = sdLog.pLog()
sets = sdSettings.TVSettings()
d = xbmcgui.Dialog()

#TODO:
#~ purevid.com
#~ http://iitv.info/gra-o-tron--game-of-thrones/s03e01-valar-dohaeris.html

#~ http://videoslim.net/
#~ http://iitv.info/magic-city/s02e02-angels-of-death.html

#~ vidup.me
#~ http://www.ekino.tv/film,niepamiec-oblivion-2013,15903,subtitles.html?player=5

#~ megavid.co
#~ catshare.net
#~ http://iitv.info/gra-o-tron--game-of-thrones/s03e06-the-climb.html

#~ xage.pl (http://xage.pl/kres/player.swf?file=http://engadget.a.ec.viddler.com/blackart6_14wrweqzc2og21miw50l3lv1jv1gre.mp4&start=0&repeat=list&screencolor=000000&plugins=captions&captions.file=http://xage.pl/kres/nar/319.srt)
#~ http://www.kreskoweczki.pl/kreskowka/63358/naruto-shippuuden_odcinek-319-napisy-pl/
#~ nie tylko film ale także napisy

#~ trilulilu.ro
#~ http://www.kreskoweczki.pl/kreskowka/68597/legends-of-chima_9-goryle-w-akcji/


class urlparser:
    def __init__(self):
        self.cm = sdCommon.common()
        self.pp = pageParser()

    def hostSelect(self, v):
        hostUrl = False
        i = 0
        if len(v) > 0:
            valTab = []
            for e in (v.values() if type(v) is dict else v):
                i=i+1
                valTab.append(str(i) + '. ' + self.getHostName(e, True))
            item = d.select("Wybor hostingu", valTab)
            if item >= 0: hostUrl = v[item]
            else: d.ok ('Brak linkow','Przykro nam, ale nie znalezlismy zadnego linku do video.', 'Sproboj ponownie za jakis czas')
        return hostUrl

    def getItemTitles(self, table):
        out = []
        for i in range(len(table)):
            value = table[i]
            out.append(value[0])
        return out

    def getHostName(self, url, nameOnly = False):
        hostName = ''
        match = re.search('http://(?:www.)?(.+?)/',url)
        if match:
            hostName = match.group(1)
            if (nameOnly):
                n = hostName.split('.')
                hostName = n[-2]
        return hostName

    def getVideoLink(self, url):
	
	#just in case if "http:" is missing
	if url[:2] == '//':
	    url = 'http:' + url	
	
        nUrl=url
        host = self.getHostName(url)
        log.info("video hosted by: " + host)
        log.info(url)
        
        hostMap = {
                    'putlocker.com':        self.pp.parserPUTLOCKER      ,
                    'firedrive.com':        self.pp.parserPUTLOCKER      ,
                    'sockshare.com':        self.pp.parserSOCKSHARE      ,
                    'hd3d.cc':              self.pp.parserHD3D           ,
                    'wgrane.pl':            self.pp.parserWGRANE         ,
                    'cda.pl':               self.pp.parserCDA            ,
                    'video.anyfiles.pl':    self.pp.parserANYFILES       ,
                    'videoweed.es':         self.pp.parserVIDEOWEED      ,
                    'videoweed.com':        self.pp.parserVIDEOWEED      ,
                    'embed.videoweed.es':   self.pp.parserVIDEOWEED      ,
                    'embed.videoweed.com':  self.pp.parserVIDEOWEED      ,
                    'novamov.com':          self.pp.parserNOVAMOV        ,
                    'embed.novamov.com':    self.pp.parserNOVAMOV        ,
                    'nowvideo.eu':          self.pp.parserNOWVIDEO       ,
                    'embed.nowvideo.eu':    self.pp.parserNOWVIDEO       ,
                    'embed.nowvideo.sx':    self.pp.parserNOWVIDEO       ,
                    'nowvideo.sx':          self.pp.parserNOWVIDEO       ,
                    'dailymotion.com':      self.pp.parserDAILYMOTION    ,
                    'video.sibnet.ru':      self.pp.parserSIBNET         ,
                    'vk.com':               self.pp.parserVK             ,
                    'anime-shinden.info':   self.pp.parserANIMESHINDEN   ,
                    'content.peteava.ro':   self.pp.parserPETEAVA        ,
                    'i.vplay.ro':           self.pp.parserVPLAY          ,
                    'nonlimit.pl':          self.pp.parserIITV           ,
                    'streamo.tv':           self.pp.parserIITV           ,
                    'divxstage.eu':         self.pp.parserDIVXSTAGE      ,
                    'movshare.net':         self.pp.parserDIVXSTAGE      ,
                    'embed.movshare.net':   self.pp.parserembedDIVXSTAGE ,
                    'embed.divxstage.eu':   self.pp.parserembedDIVXSTAGE ,
                    'bestreams.net':        self.pp.parserTUBECLOUD      ,
                    'freedisc.pl':          self.pp.parserFREEDISC       ,
                    'dwn.so':               self.pp.parserDWN            ,
                    'st.dwn.so':            self.pp.parserSTDWN          ,
                    'mightyupload.com':     self.pp.parserMIGHTYUPLOAD   ,
                    'streamcloud.eu':       self.pp.parserSTREAMCLOUD    ,
                    'limevideo.net':        self.pp.parserLIMEVIDEO      ,
                    'donevideo.com':        self.pp.parserLIMEVIDEO      , #down? 19.05.14
                    'scs.pl':               self.pp.parserSCS            ,
                    'youwatch.org':         self.pp.parserYOUWATCH       ,
                    'played.to':            self.pp.parserYOUWATCH       ,
                    'allmyvideos.net':      self.pp.parserALLMYVIDEOS    ,
                    'videomega.tv':         self.pp.parserVIDEOMEGA      ,
                    'youtube.com':          self.pp.parserYOUTUBE        ,
                    'youtu.be':             self.pp.parserYOUTUBE        ,
                    'vidto.me':             self.pp.parserVIDTO          ,
                    'vidstream.in':         self.pp.parserVIDSTREAM      ,
                    'faststream.in':        self.pp.parserVIDSTREAM      ,
                    'seositer.com':         self.pp.parserSEOSITER       ,
                    'tinymov.net':          self.pp.parserTINYMOV        ,
                    'video.yandex.ru':      self.pp.parserYANDEX         ,
                    'video.rutube.ru':      self.pp.parserRUTUBE         ,
                    'rutube.ru':            self.pp.parserRUTUBE         ,
                    'videa.hu':             self.pp.parserVIDEA          ,
                    'emb.aliez.tv':         self.pp.parserALIEZ          ,
                    'topupload.tv':         self.pp.parserTOPUPLOAD      ,
                    'vidzer.net':           self.pp.parserVIDZER         ,
                    'vidspot.net':          self.pp.parserVIDSPOT        ,
                    'embed.nowvideo.ch':    self.pp.parserNOWVIDEOCH     ,
                    'nowvideo.ch':          self.pp.parserNOWVIDEOCH     ,
		    'api.video.mail.ru':    self.pp.parserMAILRU         ,
		    'videoapi.my.mail.ru':  self.pp.parserMAILRU         ,
		    'mp4upload.com':        self.pp.parserMP4UPLOAD      ,
		    'myvi.ru':              self.pp.parserMYVI           ,
	}

        if host in hostMap:
            nUrl = hostMap[host](url)
        
        return nUrl

class pageParser:
    def __init__(self):
	self.cm = sdCommon.common()
	self.captcha = captchaParser()

    def parserPUTLOCKER(self,url):
        url = url.replace('putlocker.com','firedrive.com')
	query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
	link = self.cm.getURLRequestData(query_data)

	contents = link
	print contents
        match=re.compile('<input type="hidden" name="confirm" value="(.+?)"/>').findall(contents)
        confirm = match[0]
   
        payload = {
            'confirm': confirm,
            }
        url = url.replace('embed','file')
        print url + ' urlurl'
        data = urllib.urlencode(payload)
        req = urllib2.Request(url, data)
        resp = urllib2.urlopen(req)
        contents = resp.read()
        #print contents
        videoLink = re.search('<a href="(.+?)" target="_blank"', contents).group(1)
        #match=re.compile("\$.post\('(.+?)==").findall(contents)
        #videoLink = match[0]+'=='
        return videoLink

    def parserHD3D(self,url):
	if not 'html' in url:
	    url = url + '.html?i'
	else:
	    url = url
	username = ptv.getSetting('hd3d_login')
	password = ptv.getSetting('hd3d_password')
	
	self.cm.checkDir(ptv.getAddonInfo('path') + os.path.sep + "cookies")
	self.COOKIEFILE = ptv.getAddonInfo('path') + os.path.sep + "cookies" + os.path.sep + "hd3d.cookie"
	
	#logowanie
	if username == '' or password == '':
            loginData = {}
            query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': True, 'return_data': True }
	else:
            loginData = {'user_login': username, 'user_password': password}
            query_data = { 'url': url, 'use_host': False, 'use_cookie': True, 'save_cookie': False, 'load_cookie': True, 'cookiefile': self.COOKIEFILE, 'use_post': True, 'return_data': True }
	self.cm.requestLoginData('http://hd3d.cc/login.html', '<title>Moje pliki - hd3d.cc</title>', self.COOKIEFILE, loginData)
	link = self.cm.getURLRequestData(query_data)
	match = re.compile("""url: ["'](.+?)["'],.+?provider:""").findall(link)
	if len(match) > 0:
	    ret = match[0]
	else:
	 ret = False
	return ret

    def parserWGRANE(self,url):
	nUrl = 'http://m.wgrane.pl/video?v=' + url[-32:]
	query_data = { 'url': nUrl, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
	link = self.cm.getURLRequestData(query_data)
	#<a href='http://s1.wgrane.pl/mobile/video/171545?time=1335636021'>Odtwórz</a>
	match = re.search("""Dodano: <span class='black'>.+?</span></h3><div class='clear'></div><h1><a href='(.+?)'>Odtwórz</a>""",link)
	if match:
	    return match.group(1)
	else:
	    return False

    def parserCDA(self,url):
	query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
	link = self.cm.getURLRequestData(query_data)
	match = re.search("""file: ['"](.+?)['"],""",link)
	if match:
	    return match.group(1)
	else:
	    return False

    def parserDWN(self,url):
	query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
	match = re.compile('src="(.+?)" width=').findall(self.cm.getURLRequestData(query_data))
	if len(match) > 0:
	    query_data1 = { 'url': match[0], 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
	    match1 = re.compile("play4.swf(.+?)',").findall(self.cm.getURLRequestData(query_data1))
	    if len(match1) > 0:
		query_data2 = { 'url': 'http://st.dwn.so/xml/videolink.php' + match1[0], 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
		match2 = re.compile('un="(.+?),0').findall(self.cm.getURLRequestData(query_data2))
		if len(match2) > 0:
		    linkvideo = 'http://' + match2[0]
		    return linkvideo
		else:
		    return False
	    else:
		return False
	else:
	    return False

    def parserSTDWN(self, url):
	match = re.compile(".+?play4.swf(.+?)$").findall(url)
	print "MATCH1: "+str(match)
	if len(match) > 0:
	    query_data = { 'url': 'http://st.dwn.so/xml/videolink.php' + match[0], 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
	    print "QUERY: "+str(query_data)
	    match1 = re.compile('un="(.+?),0').findall(self.cm.getURLRequestData(query_data))
	    if len(match1) > 0:
	        linkvideo = 'http://' + match1[0]
	        return linkvideo
	    else:
	    	return False
	else:
	    return False

    def parserANYFILES(self,url):
	self.anyfiles = anyfiles.serviceParser()
	retVal = self.anyfiles.getVideoUrl(url)
	return retVal

    def parserWOOTLY(self,url):
	query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
	link = self.cm.getURLRequestData(query_data)
	c = re.search("""c.value="(.+?)";""",link)
	if c:
	    cval = c.group(1)
	else:
	    return False
	match = re.compile("""<input type=['"]hidden['"] value=['"](.+?)['"].+?name=['"](.+?)['"]""").findall(link)
	if len(match) > 0:
	    postdata = {};
	    for i in range(len(match)):
		if (len(match[i][0])) > len(cval):
		    postdata[cval] = match[i][1]
		else:
		    postdata[match[i][0]] = match[i][1]
	    self.cm.checkDir(ptv.getAddonInfo('path') + os.path.sep + "cookies")
	    self.COOKIEFILE = ptv.getAddonInfo('path') + os.path.sep + "cookies" + os.path.sep + "wootly.cookie"
	    query_data = { 'url': url, 'use_host': False, 'use_cookie': True, 'save_cookie': True, 'load_cookie': False, 'cookiefile': self.COOKIEFILE, 'use_post': True, 'return_data': True }
	    link = self.cm.getURLRequestData(query_data, postdata)
	    match = re.search("""<video.*\n.*src=['"](.+?)['"]""",link)
	    if match:
		return match.group(1)
	    else:
		return False
	else:
	    return False

    def parserVIDEOWEED(self, url):
	query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
	link = self.cm.getURLRequestData(query_data)
	match_domain = re.compile('flashvars.domain="(.+?)"').findall(link)
	match_file = re.compile('flashvars.file="(.+?)"').findall(link)
	match_filekey = re.compile('flashvars.filekey="(.+?)"').findall(link)
	if len(match_domain) > 0 and len(match_file) > 0 and len(match_filekey) > 0:
	    get_api_url = ('%s/api/player.api.php?user=undefined&codes=1&file=%s&pass=undefined&key=%s') % (match_domain[0], match_file[0], match_filekey[0])
	    link_api = { 'url': get_api_url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
	    link = self.cm.getURLRequestData(link_api)
	    match = re.compile("url=(.+?)&title").findall(link)
	    if len(match) > 0:
		linkVideo = match[0]
		log.info ('linkVideo ' + linkVideo)
		return linkVideo
	    else:
		return False
	else:
	    return False

    def parserNOVAMOV(self, url):
	query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
	link = self.cm.getURLRequestData(query_data)
	match_file = re.compile('flashvars.file="(.+?)";').findall(link)
	match_key = re.compile('flashvars.filekey="(.+?)";').findall(link)
	if len(match_file) > 0 and len(match_key) > 0:
	    get_api_url = ('http://www.novamov.com/api/player.api.php?key=%s&user=undefined&codes=1&pass=undefined&file=%s') % (match_key[0], match_file[0])
	    query_data = { 'url': get_api_url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
	    link = self.cm.getURLRequestData(query_data)
	    match_url = re.compile('url=(.+?)&title').findall(link)
	    if len(match_url) > 0:
		return match_url[0]
	    else:
		return False
	else:
	    return False

    def parserNOWVIDEO(self, url):
	query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
	link = self.cm.getURLRequestData(query_data)
	#print link + 'totu'
	match_file = re.compile('flashvars.file="(.+?)";').findall(link)
	match_key = re.compile('var fkzd="(.+?)";').findall(link)           #zmiana detoyy
	#print match_file 
	#print match_key
	if len(match_file) > 0 and len(match_key) > 0:
	    get_api_url = ('http://www.nowvideo.sx/api/player.api.php?user=undefined&pass=undefined&cid3=kino.pecetowiec.pl&file=%s&numOfErrors=0&cid2=undefined&key=%s&cid=undefined') % (match_file[0],match_key[0])  #zmina detoyy
            #print get_api_url
	    query_data = { 'url': get_api_url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
	    link_api = self.cm.getURLRequestData(query_data)
	    #print link_api 
	    match_url = re.compile('url=(.+?)&title').findall(link_api)
	    if len(match_url) > 0:
		return match_url[0]
	    else:
		return False
	else:
	    return False

    def parserSOCKSHARE(self,url):
	query_data = { 'url': url.replace('file', 'embed'), 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
	link = self.cm.getURLRequestData(query_data)
	r = re.search('value="(.+?)" name="fuck_you"', link)
	if r:
	    self.cm.checkDir(ptv.getAddonInfo('path') + os.path.sep + "cookies")
	    self.COOKIEFILE = ptv.getAddonInfo('path') + os.path.sep + "cookies" + os.path.sep + "sockshare.cookie"
	    postdata = {'fuck_you' : r.group(1), 'confirm' : 'Close Ad and Watch as Free User'}
	    query_data = { 'url': url.replace('file', 'embed'), 'use_host': False, 'use_cookie': True, 'save_cookie': True, 'load_cookie': False, 'cookiefile': self.COOKIEFILE, 'use_post': True, 'return_data': True }
	    link = self.cm.getURLRequestData(query_data, postdata)
	    match = re.compile("playlist: '(.+?)'").findall(link)
	    if len(match) > 0:
		url = "http://www.sockshare.com" + match[0]
		query_data = { 'url': url, 'use_host': False, 'use_cookie': True, 'save_cookie': False, 'load_cookie': True, 'cookiefile': self.COOKIEFILE, 'use_post': False, 'return_data': True }
		link = self.cm.getURLRequestData(query_data)
		match = re.compile('</link><media:content url="(.+?)" type="video').findall(link)
		if len(match) > 0:
		    url = match[0].replace('&amp;','&')
		    return url
		else:
		    return False
	    else:
		return False
	else:
	    return False

    def parserDAILYMOTION(self,url):
        strTab = []
        valTab = []
        videoQ = ''
	query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
	data = self.cm.getURLRequestData(query_data)
	match = re.compile('"stream_h264.+?url":"(.+?)H264-(.+?)/(.+?)"').findall(data)
        if len(match) > 0:
            for i in range(len(match)):
                page = match[i][0] + 'H264-' + match[i][1] + '/' + match[i][2]
		strTab.append(page)
		strTab.append(str(i+1) + '. ' + match[i][1].replace('\\', ''))
		valTab.append(strTab)
		strTab = []
	    d = xbmcgui.Dialog()
	    item = d.select("Wybierz jakość", self.cm.getItemTitles(valTab))
	    if item != -1:
                videoQ = str(valTab[item][0].replace('\\', ''))
                log.info('Q-ID: ' + videoQ)
                return videoQ
            else:
                return False

    def parserSIBNET(self, url):
	mid = re.search('videoid=(.+?)$',url)
	ourl = 'http://video.sibnet.ru'
	movie = 'http://video.sibnet.ru/v/qwerty/'+mid.group(1)+'.mp4?start=0'
	query_data = { 'url': ourl+'/video'+mid.group(1), 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
	link = self.cm.getURLRequestData(query_data)
	match = re.search("'file':'(.+?)'",link)
	if match:
	    return ourl+match.group(1)
	else:
	    return False

    def parserVK(self, url):
	query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
	link = self.cm.getURLRequestData(query_data)
	video_host = re.search("var video_host = '(.+?)';", link)
	video_uid = re.search("var video_uid = '(.+?)';", link)
	video_vtag = re.search("var video_vtag = '(.+?)';", link)
	if video_host and video_uid and video_vtag:
	    movie = video_host.group(1)+'u'+video_uid.group(1)+'/videos/'+video_vtag.group(1)+'.720.mp4'
	    return movie
	else:
	    return False

    def parserPETEAVA(self, url):
	mid = re.search("hd_file=(.+?_high.mp4)&", url)
	movie = "http://content.peteava.ro/video/"+mid.group(1)+"?token=PETEAVARO"
	return movie

    def parserVPLAY(self, url):
	vid = re.search("key=(.+?)$", url)
	query_data = { 'url': 'http://www.vplay.ro/play/dinosaur.do', 'use_host': False, 'use_cookie': False, 'use_post': True, 'return_data': True }
	postdata = {'key':vid.group(1)}
	link = self.cm.getURLRequestData(query_data, postdata)
	movie = re.search("nqURL=(.+?)&", link)
	return movie.group(1)

    def parserIITV(self, url):
	query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
	query_data_non = { 'url': url + '.html?i&e&m=iitv', 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
	if 'streamo' in url:
	    match = re.compile("url: '(.+?)',").findall(self.cm.getURLRequestData(query_data))
	if 'nonlimit' in url:
	    match = re.compile('url: "(.+?)",     provider:').findall(self.cm.getURLRequestData(query_data_non))
	if len(match) > 0:
	    linkVideo = match[0]
	    log.info ('linkVideo ' + linkVideo)
	    return linkVideo
	else:
	    d.ok ('Przepraszamy','Obecnie zbyt dużo osób ogląda film za pomocą', 'darmowego playera premium.', 'Sproboj ponownie za jakis czas')
	return False

    def parserDIVXSTAGE(self,url):
        self.parserNOWVIDEOCH(url)
        query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
        link = self.cm.getURLRequestData(query_data)
        video_host = re.search('flashvars.domain="(.+?)";', link)
        video_file = re.search('flashvars.file="(.+?)";', link)
        video_filekey = re.search('flashvars.filekey="(.+?)";', link)
        video_cid = re.search('flashvars.cid="(.+?)";', link)
        if video_file and video_filekey and video_cid > 0:
            url = video_host.group(1) + "/api/player.api.php?cid2=undefined&file=" + video_file.group(1) + "&key=" + video_filekey.group(1) + "&cid=" + video_cid.group(1) + "&cid3=undefined&user=undefined&pass=undefined"
            query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
            link = self.cm.getURLRequestData(query_data)
            match = re.compile('url=(.+?)&title=').findall(link)
            if len(match) > 0:
                linkvideo = match[0]
                return linkvideo
            else:
                return self.parserNOWVIDEOCH(url)
        else:
            return self.parserNOWVIDEOCH(url)

    def parserembedDIVXSTAGE(self,url):
        self.parserNOWVIDEOCH(url)
        query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
        link = self.cm.getURLRequestData(query_data)
        video_host = re.search('flashvars.domain="(.+?)";', link)
        video_file = re.search('flashvars.file="(.+?)";', link)
        video_filekey = re.search('flashvars.filekey="(.+?)";', link)
        if video_file and video_filekey > 0:
            url = video_host.group(1) + "/api/player.api.php??cid2=undefined&cid3=undefined&cid=undefined&key=" + video_filekey.group(1) + "&user=undefined&pass=undefined&file=" + video_file.group(1)
            query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
            link = self.cm.getURLRequestData(query_data)
            match = re.compile('url=(.+?)&title=').findall(link)
            if len(match) > 0:
                linkvideo = match[0]
                return linkvideo
            else:
                return self.parserNOWVIDEOCH(url)
        else:
            return self.parserNOWVIDEOCH(url)

    def parserTUBECLOUD(self,url):
	self.cm.checkDir(ptv.getAddonInfo('path') + os.path.sep + "cookies")
	self.COOKIEFILE = ptv.getAddonInfo('path') + os.path.sep + "cookies" + os.path.sep + "tubecloud.cookie"
	query_data = { 'url': url, 'use_host': False, 'use_cookie': True, 'save_cookie': True, 'load_cookie': False, 'cookiefile': self.COOKIEFILE, 'use_post': False, 'return_data': True }
	link = self.cm.getURLRequestData(query_data)
	ID = re.search('name="id" value="(.+?)">', link)
	FNAME = re.search('name="fname" value="(.+?)">', link)
	HASH = re.search('name="hash" value="(.+?)">', link)
	if ID and FNAME and HASH > 0:
	    xbmc.sleep(10500)
	    postdata = {'fname' : FNAME.group(1), 'hash' : HASH.group(1), 'id' : ID.group(1), 'imhuman' : 'Proceed to video', 'op' : 'download1', 'referer' : url, 'usr_login' : '' }
	    query_data = { 'url': url, 'use_host': False, 'use_cookie': True, 'save_cookie': False, 'load_cookie': True, 'cookiefile': self.COOKIEFILE, 'use_post': True, 'return_data': True }
	    link = self.cm.getURLRequestData(query_data, postdata)
	    match = re.compile('file: "(.+?)"').findall(link)
	    if len(match) > 0:
		linkvideo = match[0]
		return linkvideo
	    else:
		return False
	else:
	    return False

    def parserFREEDISC(self, url):
	query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
	match = re.compile('controller.player.loadMoviePlayer(.+?);').findall(self.cm.getURLRequestData(query_data))
	if len(match) > 0:
	    linkVideo = 'http://freedisc.pl/streaming/video.mp4?fileID=' + match[0].replace('(', '').replace(')', '') + '&start=0'
	    log.info ('linkVideo ' + linkVideo)
	    return linkVideo
	else:
	    return False

    def parserMIGHTYUPLOAD(self,url):
	query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
	link = self.cm.getURLRequestData(query_data)
	ID = re.search('name="id" value="(.+?)">', link)
	RAND = re.search('name="rand" value="(.+?)">', link)
	if ID and RAND > 0:
	    postdata = {'down_direct' : '1', 'id' : ID.group(1), 'method_free' : '', 'method_premium' : '', 'op' : 'download2', 'rand' : RAND.group(1), 'referer' : url }
	    query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': True, 'return_data': True }
	    link = self.cm.getURLRequestData(query_data, postdata)
	    match = re.compile('<a href="(.+?)">Download the file</a>').findall(link)
	    if len(match) > 0:
		linkvideo = match[0]
		return linkvideo
	    else:
		return False
	else:
	    return False

    def parserSTREAMCLOUD(self,url):
	query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
	link = self.cm.getURLRequestData(query_data)
	ID = re.search('name="id" value="(.+?)">', link)
	FNAME = re.search('name="fname" value="(.+?)">', link)
	if ID and FNAME > 0:
	    xbmc.sleep(10500)
	    postdata = {'fname' : FNAME.group(1), 'hash' : '', 'id' : ID.group(1), 'imhuman' : 'Watch video now', 'op' : 'download1', 'referer' : url, 'usr_login' : '' }
	    query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': True, 'return_data': True }
	    link = self.cm.getURLRequestData(query_data, postdata)
	    match = re.compile('file: "(.+?)"').findall(link)
	    if len(match) > 0:
		linkVideo = match[0]
		log.info ('linkVideo ' + linkVideo)
		return linkVideo
	    else:
		return False
	else:
	    return False

    def parserLIMEVIDEO(self,url):
	query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
	link = self.cm.getURLRequestData(query_data)
	ID = re.search('name="id" value="(.+?)">', link)
	FNAME = re.search('name="fname" value="(.+?)">', link)
	if ID and FNAME > 0:
	    #xbmc.sleep(20500)
	    postdata = {'fname' : FNAME.group(1), 'id' : ID.group(1), 'method_free' : 'Continue to Video', 'op' : 'download1', 'referer' : url, 'usr_login' : '' }
	    query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': True, 'return_data': True }
	    link = self.cm.getURLRequestData(query_data, postdata)
	    ID = re.search('name="id" value="(.+?)">', link)
	    RAND = re.search('name="rand" value="(.+?)">', link)
	    if ID and RAND > 0:
		postdata = {'rand' : RAND.group(1), 'id' : ID.group(1), 'method_free' : 'Continue to Video', 'op' : 'download2', 'referer' : url, 'down_direct' : '1', 'method_premium' : '' }
		query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': True, 'return_data': True }
		link = self.cm.getURLRequestData(query_data, postdata)
		data = link.replace('|', '<>')
		PL = re.search('<>player<>video<>(.+?)<>(.+?)<>(.+?)<><>(.+?)<>flvplayer<>', data)
		HS = re.search('image<>(.+?)<>(.+?)<>(.+?)<>file<>', data)
		if PL and HS > 0:
		    linkVideo = 'http://' + PL.group(4) + '.' + PL.group(3) + '.' + PL.group(2) + '.' + PL.group(1) + ':' + HS.group(3) + '/d/' + HS.group(2) + '/video.' + HS.group(1)
		    log.info ('linkVideo :' + linkVideo)
		    return linkVideo
		else:
		    return False
	    else:
		return False
	else:
	    return False
	
    def parserSCS(self,url):
	query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
	link = self.cm.getURLRequestData(query_data)
	ID = re.search('"(.+?)"; ccc', link)
	if ID > 0:
	    postdata = {'f' : ID.group(1) }
	    query_data = { 'url': 'http://scs.pl/getVideo.html', 'use_host': False, 'use_cookie': False, 'use_post': True, 'return_data': True }
	    link = self.cm.getURLRequestData(query_data, postdata)
	    match = re.compile("url: '(.+?)',").findall(link)
	    if len(match) > 0:
		linkVideo = match[0]
		log.info ('linkVideo ' + linkVideo)
		return linkVideo
	    else:
		d.ok ('Przepraszamy','Obecnie zbyt dużo osób ogląda film za pomocą', 'darmowego playera premium.', 'Sproboj ponownie za jakis czas')
		return False
	else:
	    return False

    def parserYOUWATCH(self,url):
	if 'embed' in url:
	    Url = url
	else:
	    Url = url.replace('org/', 'org/embed-').replace('to/', 'to/embed-') + '-640x360.html'
	query_data = { 'url': Url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
	link = self.cm.getURLRequestData(query_data)
	match = re.compile('file: "(.+?)"').findall(link)
	if len(match) > 0:
	    linkVideo = match[0]
	    log.info ('linkVideo: ' + linkVideo)
	    return linkVideo
	else:
	    return False

    def parserALLMYVIDEOS(self,url):
	query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
	link = self.cm.getURLRequestData(query_data)
	ID = re.search('name="id" value="(.+?)">', link)
	FNAME = re.search('name="fname" value="(.+?)">', link)
	if ID and FNAME > 0:
	    xbmc.sleep(10500)
	    postdata = {'fname' : FNAME.group(1), 'method_free' : '1', 'id' : ID.group(1), 'x' : '82', 'y' : '13', 'op' : 'download1', 'referer' : url, 'usr_login' : '' }
	    query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': True, 'return_data': True }
	    link = self.cm.getURLRequestData(query_data, postdata)
	    match = re.compile('"file" : "(.+?)",').findall(link)
	    if len(match) > 0:
		linkVideo = match[0]
		log.info ('linkVideo ' + linkVideo)
		return linkVideo
	    else:
		return False
	else:
	    return False
	    
    def parserVIDEOMEGA(self,url):
	url = url.replace('?ref','iframe.php?ref')
	query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
	link = self.cm.getURLRequestData(query_data)
	match = re.compile('document.write\(unescape\("(.+?)"\)\);').findall(link)
	if len(match) > 0:
	    match2 = re.compile('file: "(.+?)"').findall(urllib.unquote(match[0]))
	    if len(match2) > 0:
		linkVideo = match2[0]
		log.info ('linkVideo ' + linkVideo)
		return linkVideo
	    else:
		return False
	else:
	    return False
	
    def parserYOUTUBE(self,url):
        url = url.split('/')
	vID = url.pop()
	linkVideo = 'plugin://plugin.video.youtube?path=/root/video&action=play_video&videoid=' + vID
	log.info ('linkVideo ' + linkVideo)
	return linkVideo

    def parserVIDTO(self,url):
	query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
	link = self.cm.getURLRequestData(query_data)
	ID = re.search('name="id" value="(.+?)">', link)
	FNAME = re.search('name="fname" value="(.+?)">', link)
	HASH = re.search('name="hash" value="(.+?)">', link)
	if ID and FNAME and HASH > 0:
	    xbmc.sleep(6500)
	    postdata = {'fname' : FNAME.group(1), 'id' : ID.group(1), 'hash' : HASH.group(1), 'imhuman' : 'Proceed to video', 'op' : 'download1', 'referer' : url, 'usr_login' : '' }
	    query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': True, 'return_data': True }
	    link = self.cm.getURLRequestData(query_data, postdata)
	    match = re.compile('<div class="private-download-link"><h1><a id="lnk_download" href="(.+?)">',re.DOTALL).findall(link)
	    if len(match) > 0: return match[0]
	else:
	    return False

    def parserVIDSTREAM(self,url):
	query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
	link = self.cm.getURLRequestData(query_data)
	ID = re.search('name="id" value="(.+?)">', link)
	FNAME = re.search('name="fname" value="(.+?)">', link)
	HASH = re.search('name="hash" value="(.+?)">', link)
	if ID and FNAME and HASH > 0:
            xbmc.sleep(5500)
	    postdata = {'fname' : FNAME.group(1), 'id' : ID.group(1), 'hash' : HASH.group(1), 'imhuman' : 'Proceed to video', 'op' : 'download1', 'referer' : url, 'usr_login' : '' }
	    query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': True, 'return_data': True }
	    link = self.cm.getURLRequestData(query_data, postdata)
	    match = re.compile('file: "(.+?)",').findall(link)
	    if len(match) > 0:
		linkVideo = match[0]
		log.info ('linkVideo :' + linkVideo)
		return linkVideo
	    else:
		return False
	else:
	    return False

    def parserTINYMOV(self,url):
	query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
	link = self.cm.getURLRequestData(query_data)
	match = re.compile("\$.post\('(.+?)',").findall(link)
	if len(match) > 0:
	    linkVideo = match[0]
	    log.info ('linkVideo :' + linkVideo)
	    return linkVideo
	else:
	    return False

    def parserSEOSITER(self,url):
	nUrl = url.split('?file=')
	return nUrl[1]
	
    def parserYANDEX(self, url):
	r = re.compile('iframe/(.+?)\?|$').findall(url)
	query_data = { 'url': 'http://static.video.yandex.net/get-token/'+r[0]+'/?callback=ct', 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
	link = self.cm.getURLRequestData(query_data)
	r2 = re.compile('"token": "(.+?)"').findall(link)
	query_data = { 'url': 'http://streaming.video.yandex.ru/get-location/'+r[0]+'/medium.flv?token='+r2[0]+'&ref=video.yandex.ru', 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
	link = self.cm.getURLRequestData(query_data)
	r3 = re.compile('<video-location>(.+?)</video-location>').findall(link)
	return r3[0]

    def parserRUTUBE(self, url):
        if url.startswith('http://rutube.ru/video/embed'):
            sts, data = self.cm.getPage(url)
            if not sts: return False
            data = re.search('href="([^"]+?)"', data)
            if not data: return False
            url = data.group(1)
        videoID = ''
        url += '/'

        # get videoID/hash
        match = re.search('http://video.rutube.ru/(\w+?)/', url)
        if match:
            videoID = match.group(1)
        else:
            match = re.search('http://rutube.ru/video/(\w+?)/', url)
            if match:
                videoID = match.group(1)
            else:
                match = re.search('http://rutube.ru/player.swf?hash=(\w+?)/', url)
                if match:
                    videoID = match.group(1)
        if '' != videoID:
            log.info('parserRUTUBE:                 videoID[%s]' % videoID)
            # get videoInfo:
            #vidInfoUrl = 'http://rutube.ru/api/play/trackinfo/%s/?format=json' % videoID
            vidInfoUrl = 'http://rutube.ru/api/play/options/%s/?format=json&referer=&no_404=true&sqr4374_compat=1' % videoID
            query_data = { 'url': vidInfoUrl, 'return_data': True }
            try:
                videoInfo = self.cm.getURLRequestData(query_data)
            except:
                log.info('parserRUTUBE problem with getting video info page')
                return []
            log.info('---------------------------------------------------------')
            log.info(videoInfo)
            log.info('---------------------------------------------------------')
            # "m3u8": "http://bl.rutube.ru/ae8621ff85153a30c398746ed8d6cc03.m3u8"
            # "f4m": "http://bl.rutube.ru/ae8621ff85153a30c398746ed8d6cc03.f4m"
            
            match = re.search('"m3u8":[ ]*?"(http://bl.rutube.ru/.+?)"', videoInfo)
            if match:
                log.info('parserRUTUBE m3u8 link[%s]' % match.group(1))
                videoUrls = match.group(1)
            else:
                log.info('parserRUTUBE there is no m3u8 link in videoInfo:')
                log.info('---------------------------------------------------------')
                log.info(videoInfo)
                log.info('---------------------------------------------------------')
               
            match = re.search('"default":[ ]*?"(http://[^"]+?f4m[^"]*?)"', videoInfo)
            if match:
                log.info('parserRUTUBE f4m link[%s]' % match.group(1))
		#videoUrls = match.group(1)
            return videoUrls
        else:
            log.info('parserRUTUBE ERROR cannot find videoID in link[%s]' % url)
            return []

    def parserVIDEA(self, url):
        query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
        link = self.cm.getURLRequestData(query_data)
	r = re.compile('v=(.+?)&eventHandler').findall(link)
	query_data = { 'url': 'http://videa.hu/flvplayer_get_video_xml.php?v='+r[0], 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
	link = self.cm.getURLRequestData(query_data)
	r2 = re.compile('video_url="(.+?)"').findall(link)
	return r2[0]

    def parserALIEZ(self, url):
        query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
        link = self.cm.getURLRequestData(query_data)
	r = re.compile("file:.+?'(.+?)'").findall(link)
	return r[0]

    def parserTOPUPLOAD(self, url):
        query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
        link = self.cm.getURLRequestData(query_data)
	r = re.compile("'file': '(.+?)'").findall(link)
	videoLink = r[0] + '|Referer=http://www.topupload.tv/media/swf/player/player.swf'
	return videoLink

    def parserVIDZER(self,url):
	query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
	link = self.cm.getURLRequestData(query_data)
      
	match = re.search('href="(http[^"]+?getlink[^"]+?)"', link)
	if match:
	    url = urllib.unquote( match.group(1) )
	    return url
      
	
	r = re.search('value="(.+?)" name="fuck_you"', link)
	r2 = re.search('name="confirm" type="submit" value="(.+?)"', link)
	r3 = re.search('<a href="/file/([^"]+?)" target', link)
	if r:
            print r.group(1)
            print r2.group(1)
	    query_data = { 'url': 'http://www.vidzer.net/e/'+r3.group(1)+'?w=631&h=425', 'use_host': False, 'use_cookie': False, 'use_post': True, 'return_data': True }
	    postdata = {'confirm' : r2.group(1), 'fuck_you' : r.group(1)}
	    link = self.cm.getURLRequestData(query_data, postdata)
	    print link
            match = re.search("url: '([^']+?)'", link)
            if match:
	        url = match.group(1) #+ '|Referer=http://www.vidzer.net/media/flowplayer/flowplayer.commercial-3.2.18.swf'
		return url
	    else:
                return False
        else:
            return False

    def parserVIDSPOT(self,url):
	query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
	link = self.cm.getURLRequestData(query_data)
	ID = re.search('name="id" value="(.+?)">', link)
	FNAME = re.search('name="fname" value="(.+?)">', link)
	if ID and FNAME > 0:
	    postdata = {'fname' : FNAME.group(1), 'id' : ID.group(1), 'method_free' : '1', 'op' : 'download1', 'referer' : url, 'usr_login' : '' }
	    query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': True, 'return_data': True }
	    link = self.cm.getURLRequestData(query_data, postdata)
	    match = re.compile('"file" : "(.+?)",').findall(link)
	    if len(match) > 0:
		linkVideo = match[0]
		log.info ('linkVideo :' + linkVideo)
		return linkVideo
	    else:
		return False
	else:
	    return False
    
    def parserNOWVIDEOCH(self, url):
        try:
            sts, data = self.cm.getPage(url)
            filekey = re.search("flashvars.filekey=([^;]+?);", data).group(1)
            filekey = re.search('var %s="([^"]+?)"' % filekey, data).group(1)
            file    = re.search('flashvars.file="([^"]+?)";', data).group(1)
            domain  = re.search('flashvars.domain="(http[^"]+?)"', data).group(1)
            
            url = domain + '/api/player.api.php?cid2=undefined&cid3=undefined&cid=undefined&user=undefined&pass=undefined&numOfErrors=0'
            url = url + '&key=' + urllib.quote_plus(filekey) + '&file=' + urllib.quote_plus(file)
            sts, data = self.cm.getPage(url)
            
            url = re.search("url=([^&]+?)&", data).group(1)
            return url
        except:
            return False
            
    def parserANIMESHINDEN(self, url):
        query_data = { 'url': url, 'return_data': False }       
        response = self.cm.getURLRequestData(query_data)
        redirectUrl = response.geturl() 
        response.close()
        return redirectUrl
   
      
    def parserMAILRU(self, url):
        try:
	    sts, data = self.cm.getPage(url)
	    match = re.compile('videoSrc = "(.+?)",').findall(data)
	    if len(match) > 0:
	       log.info ('linkVideo :' + match[0])
	       return match[0]
	    else:
	       return False
        except:
            return False
	
    def parserMP4UPLOAD(self, url):
        try:
	    sts, data = self.cm.getPage(url)
	    match = re.compile("'file': '(.+?)',").findall(data)
	    if len(match) > 0:
	       log.info ('linkVideo :' + match[0])
	       return match[0]
	    else:
	       return False
        except:
            return False

	
    def parserMYVI(self, url):
	self.cm.checkDir(ptv.getAddonInfo('path') + os.path.sep + "cookies")
	self.COOKIEFILE = ptv.getAddonInfo('path') + os.path.sep + "cookies" + os.path.sep + "myvi.cookie"
	
        try:
	    sts, data = self.cm.getPage(url)
	    match = re.compile("dataUrl:'(.+?)',").findall(data)
	    if len(match) > 0:
	       query_data = { 'url': url, 'use_host': False, 'use_cookie': True, 'save_cookie': True, 'load_cookie': False, 'cookiefile': self.COOKIEFILE, 'use_post': False, 'return_data': True }
	       sts, data = self.cm.getPage("http://myvi.ru" + match[0],query_data)	       
               result = _json.loads(data)
	       userId = self.cm.getCookieItem(self.COOKIEFILE,'UniversalUserID')

	       #added cookie header 
	       ret = result['sprutoData']['playlist'][0]['video'][0]['url'] + '|Cookie=UniversalUserID=' + userId
	       log.info ('linkVideo :' + ret)
	       return ret
	    else:
	       return False
        except:
            return False
	

class captchaParser:
    def __init__(self):
	pass

    def textCaptcha(self, data):
	strTab = []
	valTab = []
	match = re.compile("padding-(.+?):(.+?)px;padding-top:.+?px;'>(.+?)<").findall(data)
	if len(match) > 0:
	    for i in range(len(match)):
		value = match[i]
		strTab.append(value[2])
		strTab.append(int(value[1]))
		valTab.append(strTab)
		strTab = []
		if match[i][0] == 'left':
		    valTab.sort(key=lambda x: x[1], reverse=False)
		else:
		    valTab.sort(key=lambda x: x[1], reverse=True)
	return valTab

    def reCaptcha(self, data):
	pass
