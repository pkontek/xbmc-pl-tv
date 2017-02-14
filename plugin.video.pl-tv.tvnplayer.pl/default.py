# -*- coding: utf-8 -*-
import xbmcaddon
import os

__settings__ = xbmcaddon.Addon(id='plugin.video.pl-tv.tvnplayer.pl')
BASE_RESOURCE_PATH = os.path.join(__settings__.getAddonInfo('path'), 'resources')
sys.path.append(os.path.join(BASE_RESOURCE_PATH, 'lib'))

import urllib,urllib2,re,time
import xbmcplugin,xbmcgui
import simplejson, socket
from hashlib import sha1
import crypto.cipher.aes_cbc
import crypto.cipher.base, base64
import binascii

pluginUrl = sys.argv[0]
pluginHandle = int(sys.argv[1])
pluginQuery = sys.argv[2]
#base_url = 'http://api.tvnplayer.pl/api/?platform=ConnectedTV&terminal=Samsung2&format=json&authKey=453198a80ccc99e8485794789292f061&v=3.6&showContentContractor=free%2Csamsung%2Cstandard&m=getItem&android23video=1&deviceType=Tablet&os=4.1.1&playlistType=&connectionType=WIFI&deviceScreenWidth=1920&deviceScreenHeight=1080&appVersion=3.3.4&manufacturer=unknown&model=androVMTablet'
base_url = 'http://tvnplayer.pl/api/?platform=ConnectedTV&terminal=Panasonic&format=json&v=3.1&authKey=064fda5ab26dc1dd936f5c6e84b7d3c2'
#'host' : 'Mozilla/5.0 (Linux; U; Android 2.3.4; en-us; Kindle Fire Build/GINGERBREAD) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1',
android_url = 'http://tvnplayer.pl/api/?platform=Mobile&terminal=Android&format=json&v=3.7&authKey=4dc7b4f711fb9f3d53919ef94c23890c'
scale_url = 'http://redir.atmcdn.pl/scale/o2/tvn/web-content/m/'


socket.setdefaulttimeout(10)

def TVNPlayerAPI(m,type,id,season):
    if m == 'mainInfo':
        GeoIP = urllib2.urlopen(base_url + '&m=checkClientip')
        GeoIPjson = simplejson.loads(GeoIP.read())
        GeoIP.close()
        __settings__.setSetting(id='checkClientip', value=str(GeoIPjson['result']))
        url = base_url + '&m=%s'% (m)

        response = urllib2.urlopen(url)
        json = simplejson.loads(response.read())
        response.close()
        categories = json['categories']
        for item in categories:
            name = item.get('name','')
            type = item.get('type','')
            id = item['id']
            if type != 'titles_of_day' and type != 'favorites' and type != 'pauses':
                addDir(name,'getItems',type,id,'DefaultVideoPlaylists.png','','')
    else:
        urlQuery = '&m=%s&type=%s&id=%s&limit=500&page=1&sort=newest' % (m, type, id)
        if season > 0:
            urlQuery = urlQuery + '&season=' + str(season)
        response = urllib2.urlopen(base_url + urlQuery)
        json = simplejson.loads(response.read())
        response.close()
        if type == "series":
            if json['items'][0]['season'] == season:
                return TVNPlayerItems(json)
            else:
                seasons = json['seasons']
                for item in seasons:
                    name = item.get('name','')
                    season = item.get('id','')
                    xbmcplugin.addSortMethod(pluginHandle, xbmcplugin.SORT_METHOD_LABEL)
                    addDir(name,'getItems',type,id,'DefaultTVShows.png','',season)
                if not seasons:
                    return TVNPlayerItems(json)
        else:
            return TVNPlayerItems(json)

def TVNPlayerItems(json):
        items = json['items']
        for item in items:
            name = item.get('title','')
            type = item.get('type','')
            type_episode = item.get('type_episode','')
            numbering_episodes = item.get('numbering_episodes','')
            clickable = item['clickable']
            payable = item['payable']
            id = item['id']
            thumbnail = item['thumbnail'][0]['url']
            gets = {'type': 1,
                    'quality': 95,
                    'srcmode': 0,
                    'srcx': item['thumbnail'][0]['srcx'],
                    'srcy': item['thumbnail'][0]['srcy'],
                    'srcw': item['thumbnail'][0]['srcw'],
                    'srch': item['thumbnail'][0]['srch'],
                    'dstw': 256,
                    'dsth': 292}
            if type == 'episode':
                if clickable == 1: # and payable == 0:                
                    tvshowtitle = item.get('title','')
                    episode = item.get('episode','')
                    sub_title = item.get('sub_title','')
                    lead = item.get('lead','')
                    season = item.get('season','')
                    start_date = item.get('start_date','')
                    url = pluginUrl+'?m=getItem&id='+str(id)+'&type='+type
                    name = tvshowtitle + ' - ' + sub_title
                    if not sub_title or tvshowtitle == sub_title:
                        name = tvshowtitle
                    if type_episode == 'catchup' or (numbering_episodes == 1 and not sub_title):
                        if str(episode) == '0' :
                            name = name
                        elif str(season) == '0' :
                            name = name + ', odcinek '+ str(episode)
                        else:
                            name = name + ', sezon ' + str(season)+', odcinek '+ str(episode)
                    addLink(name,url,thumbnail,gets,tvshowtitle,lead,episode,season,start_date)
            else:
                addDir(name,'getItems',type,id,thumbnail,gets,'')
                xbmcplugin.addSortMethod(pluginHandle, xbmcplugin.SORT_METHOD_LABEL)

def SelectProfileUrl(video_content):
    if not video_content:
        ok = xbmcgui.Dialog().ok('TVNPlayer', 'Jak używasz proxy', 'to właśnie przestało działać')
        return ok
    else:
        profile_name_list = []
        for item in video_content:
            profile_name = item['profile_name']
            profile_name_list.append(profile_name)
        if __settings__.getSetting('auto_quality') == 'true' :
            if 'HD' in profile_name_list:
                select = profile_name_list.index('HD')
            elif 'Bardzo Wysoka' in profile_name_list:
                select = profile_name_list.index('Bardzo Wysoka')
            elif 'Wysoka' in profile_name_list:
                select = profile_name_list.index('Wysoka')
            else:
                select = xbmcgui.Dialog().select('Wybierz jakość', profile_name_list)
        else:
            select = xbmcgui.Dialog().select('Wybierz jakość', profile_name_list)
        if select >= 0:
            if 'url' in video_content[select]:
                stream_url = video_content[select]['url']
            else:
                stream_url = video_content[select]['src']
            return stream_url


def TVNPlayerItem(type, id):
    urlQuery = '&type=%s&id=%s&sort=newest&m=getItem&deviceScreenHeight=1080&deviceScreenWidth=1920' % (type, id)
    getItem = urlOpen(base_url + urlQuery)
    json = simplejson.loads(getItem.read())
    getItem.close()
    if 'video_content_license_type' in json['item']['videos']['main'] and json['item']['videos']['main']['video_content_license_type'] == 'WIDEVINE':
        #przełączamy się na Android

        getItem = urlOpen(android_url + urlQuery)
        json = simplejson.loads(getItem.read())
        getItem.close()

        video_content = json['item']['videos']['main']['video_content']
        if not video_content:
            ok = xbmcgui.Dialog().ok('TVNPlayer', 'Film zabezpieczony DRM!', 'Wyświetlenie nie jest możliwe.')
            return ok

        stream_url = SelectProfileUrl(video_content)
        if not isinstance(stream_url,int):
            stream_url = generateToken(stream_url).encode('UTF-8')
    else:
        video_content = json['item']['videos']['main']['video_content']
        stream_url = SelectProfileUrl(video_content)
        #getItem = urlOpen(stream_url)
        #stream_url = getItem.read()
        #getItem.close()
    if not isinstance(stream_url,int):
        xbmcplugin.setResolvedUrl(pluginHandle, True, xbmcgui.ListItem(path=stream_url))

            

def generateToken(url):
    # obsługa Android z sd-xbmc.org
    url = url.replace('http://redir.atmcdn.pl/http/','')
    SecretKey = 'AB9843DSAIUDHW87Y3874Q903409QEWA'
    iv = 'ab5ef983454a21bd'
    KeyStr = '0f12f35aa0c542e45926c43a39ee2a7b38ec2f26975c00a30e1292f7e137e120e5ae9d1cfe10dd682834e3754efc1733'
    salt = sha1()
    salt.update(os.urandom(16))
    salt = salt.hexdigest()[:32]

    tvncrypt = crypto.cipher.aes_cbc.AES_CBC(SecretKey, padding=crypto.cipher.base.noPadding(), keySize=32)
    key = tvncrypt.decrypt(binascii.unhexlify(KeyStr), iv=iv)[:32]

    expire = 3600000L + long(time.time()*1000) - 946684800000L

    unencryptedToken = "name=%s&expire=%s\0" % (url, expire)

    pkcs5_pad = lambda s: s + (16 - len(s) % 16) * chr(16 - len(s) % 16)
    pkcs5_unpad = lambda s : s[0:-ord(s[-1])]

    unencryptedToken = pkcs5_pad(unencryptedToken)

    tvncrypt = crypto.cipher.aes_cbc.AES_CBC(binascii.unhexlify(key), padding=crypto.cipher.base.noPadding(), keySize=16)
    encryptedToken = tvncrypt.encrypt(unencryptedToken, iv=binascii.unhexlify(salt))
    encryptedTokenHEX = binascii.hexlify(encryptedToken).upper()

    return "http://redir.atmcdn.pl/http/%s?salt=%s&token=%s" % (url, salt, encryptedTokenHEX)


def htmlToText(html):
    html = re.sub('<.*?>','',html)
    return html .replace("&lt;", "<")\
                .replace("&gt;", ">")\
                .replace("&amp;", "&")\
                .replace("&quot;",'"')\
                .replace("&apos;","'")

def get_params():
        param=[]
        paramstring=sys.argv[2]
        if len(paramstring)>=2:
                params=sys.argv[2]
                cleanedparams=params.replace('?','')
                if (params[len(params)-1]=='/'):
                        params=params[0:len(params)-2]
                pairsofparams=cleanedparams.split('&')
                param={}
                for i in range(len(pairsofparams)):
                        splitparams={}
                        splitparams=pairsofparams[i].split('=')
                        if (len(splitparams))==2:
                                param[splitparams[0]]=splitparams[1]
                                
        return param


def addDir(name,m,type,id,thumbnail,gets,season):
        u=sys.argv[0]+"?m="+urllib.quote_plus(m)+"&type="+urllib.quote_plus(type)+"&id="+str(id)+"&season="+str(season)
        if not gets:
            thumbnailimage=''
        else:
            thumbnailimage='%s%s?%s' % (scale_url, thumbnail, urllib.urlencode(gets))
        ok=True
        liz=xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=urllib.unquote(thumbnailimage))
        liz.setInfo( type="video",  infoLabels = {'title' : name })
        ok=xbmcplugin.addDirectoryItem(handle=pluginHandle,url=u,listitem=liz,isFolder=True)
        return ok

def addLink(name,url,thumbnail,gets,serie_title,lead,episode,season,start_date):
        ok=True
        if not gets:
            thumbnailimage=''
        else:
            thumbnailimage='%s%s?%s' % (scale_url, thumbnail, urllib.urlencode(gets))
        liz=xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage=urllib.unquote(thumbnailimage))
        liz.setInfo( type="video",  infoLabels = {
                'tvshowtitle' : serie_title ,
                'title' : name ,
                'plot': htmlToText(lead) ,
                'episode': int(episode) ,
                'season' : int(season) ,
                'aired' : start_date
        })
        if __settings__.getSetting('checkClientip') == 'False' and __settings__.getSetting('pl_proxy') == '':
            liz.setProperty("IsPlayable","false");
        else:
            liz.setProperty("IsPlayable","true");
        liz.setProperty('Fanart_Image', 'http://redir.atmcdn.pl/http/o2/tvn/web-content/m/' + thumbnail)
        ok=xbmcplugin.addDirectoryItem(handle=pluginHandle,url=url,listitem=liz,isFolder=False)
        return ok

def urlOpen(url):
    if __settings__.getSetting('checkClientip') == 'False' and __settings__.getSetting('pl_proxy') == '':
        __settings__.openSettings()
    if __settings__.getSetting('checkClientip') == 'False':
        pl_proxy = 'http://' + __settings__.getSetting('pl_proxy') + ':' + __settings__.getSetting('pl_proxy_port')
        proxy_handler = urllib2.ProxyHandler({'http':pl_proxy})
        if __settings__.getSetting('pl_proxy_pass') <> '' and __settings__.getSetting('pl_proxy_user') <> '':
            password_mgr = urllib2.HTTPPasswordMgrWithDefaultRealm()
            password_mgr.add_password(None, pl_proxy, __settings__.getSetting('pl_proxy_user'), __settings__.getSetting('pl_proxy_pass'))
            proxy_auth_handler = urllib2.ProxyBasicAuthHandler(password_mgr)
            opener = urllib2.build_opener(proxy_handler, proxy_auth_handler)
        else:
            opener = urllib2.build_opener(proxy_handler)
    if __settings__.getSetting('checkClientip') == 'False':
        try:
            getItem = opener.open(url)
        except Exception, ex:
            ok = xbmcgui.Dialog().ok('TVNPlayer', 'Coś nie tak z Twoim proxy', 'error message', str(ex))
            return ok
    else:
        getItem = urllib2.urlopen(url)
    return getItem

params=get_params()

type=None
id=None

limit=None
page=None

try:
        m=urllib.unquote_plus(params["m"])
except:
        m="mainInfo"
        pass
try:
        type=urllib.unquote_plus(params["type"])
except:
        pass
try:
        id=int(params["id"])
except:
        pass
try:
        season=int(params["season"])
except:
        season="0"
        pass

if m == "mainInfo":
        TVNPlayerAPI(m,type,id,season)
       
elif m == "getItems":
        TVNPlayerAPI(m,type,id,season)
        
elif m == "getItem":
        TVNPlayerItem(type,id)

if type == "series":
        xbmcplugin.setContent(pluginHandle, 'episodes')
        xbmcplugin.addSortMethod(pluginHandle, xbmcplugin.SORT_METHOD_EPISODE)
elif type == "catalog":
        xbmcplugin.addSortMethod( pluginHandle, xbmcplugin.SORT_METHOD_UNSORTED )
        xbmcplugin.addSortMethod(pluginHandle, xbmcplugin.SORT_METHOD_LABEL)
        if id == 3:
            xbmcplugin.setContent(pluginHandle, 'movies')
xbmcplugin.endOfDirectory(pluginHandle)
