# -*- coding: utf-8 -*-
import xbmcaddon
import re,string
import urllib2
import xbmcgui, xbmcplugin
import simplejson
from time import localtime, strftime, time

__addon_name__ = 'vod.tvp.pl'
__id__ = 'plugin.video.pl-tv.vod.tvp.pl'
__settings__ = xbmcaddon.Addon(__id__)

pluginUrl = sys.argv[0]
pluginHandle = int(sys.argv[1])
pluginQuery = sys.argv[2]
listing_url = 'http://www.api.v3.tvp.pl/shared/listing.php?dump=json'
urlImage = 'http://s.v3.tvp.pl/images/%s/%s/%s/uid_%s_width_%d_gs_0.jpg'

def tvpAPI(parent_id):
    if not parent_id:
        url = listing_url + '&direct=true&count=150&parent_id=%s'% ('1785454')
        response = urllib2.urlopen(url)
        json = simplejson.loads(response.read())
        response.close()
        items = json['items']
        url = listing_url + '&direct=true&count=150&parent_id=%s'% ('12345611')
        response = urllib2.urlopen(url)
        json = simplejson.loads(response.read())
        response.close()
        items = items + json['items']
    else:
        url = listing_url + '&direct=true&count=150&parent_id=%s'% (parent_id)
        response = urllib2.urlopen(url)
        json = simplejson.loads(response.read())
        response.close()
        items = json['items']
    if not items:
        print 'pusta'
        parentlist = []
        parent_id = json['query']['parent_node_id']
        url = listing_url + '&filter=playable=true&direct=false&count=500&page=1&parent_id=%s'% (parent_id)
        response = urllib2.urlopen(url)
        json = simplejson.loads(response.read())
        response.close()
        podkatalogi = json['items']
        title = json['items'][0].get('website_title','')
        for item in podkatalogi:
            parent_id = item.get('parent_node_id','')
            parentlist.append(parent_id)
        parentlist = set(parentlist)
        ct=1;
        for item in parentlist:
            addDir(title+' '+str(ct),item,__settings__.getAddonInfo('icon'))
            ct+=1
        xbmcplugin.endOfDirectory(pluginHandle)
    else:
        lista_pozycji = []
        for item in items:
            title = item.get('title','')
            lista_pozycji.append(title)
        if 'wideo' in lista_pozycji:
            for item in items:
                if 'wideo' in item.get('title',''):
                    filename = str(item.get('_id',''))
                    return tvpAPI(filename)
        elif 'filmy za darmo!' in lista_pozycji:
            for item in items:
                if 'filmy za darmo!' in item.get('title',''):
                    filename = str(item.get('_id',''))
                    return tvpAPI(filename)
        else:
            return listingTVP(items)
        

def listingTVP(items):
#    categories = json['items']
    categories = sorted(items, key=lambda item:item['title'])
    darmowe=[]
    for item in categories:
        if 'samsung_enabled' in item:
            if 'payable' not in item or not item['payable']:
                darmowe.append(item)
        else:
            darmowe.append(item)
    
    if not darmowe:
        dialog = xbmcgui.Dialog()
        ok = dialog.ok('tvp','Niestety, nie ma darmowej zawartości')
    else:
        for item in darmowe:
            if item['playable']:
                if item['release_date'].get('sec','') < time() and item['play_mode'] == 1:
                    filename = str(item.get('_id',''))
                    if 'video/mp4' in (item.get('videoFormatMimes') or []):
                        filename = filename+'&mime_type=video/mp4'
                    title = item.get('title','')
                    TVShowTitle =  item.get('website_title','')
                    desc =  item.get('description_root','')
                    aired =  item.get('publication_start_dt','')
                    date = item['release_date'].get('sec','')
                    if 'image' in item:
                        iconFile = item['image'][0]['file_name']
                        if 'width' in item['image'][0]:
                            iconWidth = item['image'][0]['width']
                        else:
                            iconwidth = 0
                        iconUrl = urlImage %(iconFile[0],iconFile[1],iconFile[2],iconFile[:-4],iconWidth)
                    else:
                        iconUrl = __settings__.getAddonInfo('icon')
                    listitem = xbmcgui.ListItem(title, iconImage=iconUrl, thumbnailImage=iconUrl)
                    listitem.setInfo('video', {'title': title,'tvshowtitle': TVShowTitle,'plot': desc,'aired': aired, 'Date': strftime("%d.%m.%Y", localtime(date)) })
                    listitem.setProperty('fanart_image', __settings__.getAddonInfo('fanart') )
                    listitem.setProperty('IsPlayable', 'true')
                    xbmcplugin.setContent(pluginHandle, 'episodes')
                    xbmcplugin.addDirectoryItem(pluginHandle, pluginUrl+"?odtwarzaj="+filename, listitem, isFolder=False)
                    xbmcplugin.addSortMethod(pluginHandle,xbmcplugin.SORT_METHOD_DATE)
            else:
                if item['types'][1]!='video':
                    title = item.get('title','')
                    filename = str(item.get('asset_id',''))
                    if filename != '1597829' and title!='Start' and filename != '1649991':
                        addDir(title,filename,__settings__.getAddonInfo('icon'))
        xbmcplugin.endOfDirectory(pluginHandle) 
 
def get_stream_url(channel_id):
    print 'http://www.tvp.pl/shared/cdn/tokenizer_v2.php?object_id=' + channel_id
    print 'http://www.tvp.pl/pub/stat/videofileinfo?video_id=' + channel_id
    url = 'http://www.tvp.pl/shared/cdn/tokenizer_v2.php?object_id=' + channel_id
    if __settings__.getSetting('pl_proxy') == '':
        videofileinfo = urllib2.urlopen(url)
    else:
        pl_proxy = 'http://' + __settings__.getSetting('pl_proxy') + ':' + __settings__.getSetting('pl_proxy_port')
        proxy_handler = urllib2.ProxyHandler({'http':pl_proxy})
        if __settings__.getSetting('pl_proxy_pass') <> '' and __settings__.getSetting('pl_proxy_user') <> '':
            password_mgr = urllib2.HTTPPasswordMgrWithDefaultRealm()
            password_mgr.add_password(None, pl_proxy, __settings__.getSetting('pl_proxy_user'), __settings__.getSetting('pl_proxy_pass'))
            proxy_auth_handler = urllib2.ProxyBasicAuthHandler(password_mgr)
            opener = urllib2.build_opener(proxy_handler, proxy_auth_handler)
        else:
            opener = urllib2.build_opener(proxy_handler)
        videofileinfo = opener.open(url)

    json = simplejson.loads(videofileinfo.read())
    videofileinfo.close()

    if __settings__.getSetting('auto_quality') == 'true' :
        quality = int(__settings__.getSetting('quality'))
    else:
        profile_name_list = ['Full HD','HD','Bardzo wysoka','Wysoka','Średnia']
        quality = xbmcgui.Dialog().select('Wybierz jakość', profile_name_list)
    video_url = ''
    if quality > 0:
        quality += 1
    for item in json['formats']:
        if item['url'].find('video-'+str(9-quality)) > 0 and item['mimeType'] == 'video/mp4':
            video_url = item['url']
        if item['url'].find('video-4') > 0 and item['mimeType'] == 'video/mp4' and video_url == '':
            video_url = item['url']
    if video_url == '':
        video_url = item['url']
    return video_url


def addDir(name,parent,iconimage):
    u=pluginUrl+"?parent="+str(parent)
    ok=True
    liz=xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
    liz.setInfo( type="Video", infoLabels={ "Title": name } )
    liz.setProperty('fanart_image', __settings__.getAddonInfo('fanart') )
    ok=xbmcplugin.addDirectoryItem(pluginHandle,url=u,listitem=liz,isFolder=True)
    return ok

if pluginQuery.startswith('?odtwarzaj='):
    channel_id = pluginQuery[11:]
    stream_url = get_stream_url(channel_id)
    xbmcplugin.setResolvedUrl(pluginHandle, True, xbmcgui.ListItem(path=stream_url))

else:
    parent_id = pluginQuery[8:]
    tvpAPI(parent_id)

