# -*- coding: utf-8 -*-
import os, string
import urllib, urllib2, re, sys
import xbmcaddon, xbmc, xbmcgui
import xml.etree.ElementTree as ET

scriptID   = sys.modules[ "__main__" ].scriptID
t = sys.modules[ "__main__" ].language
ptv = xbmcaddon.Addon(scriptID)

import sdLog, sdParser, sdCommon

log = sdLog.pLog()

BASE_URL = "http://www.thetvdb.com"
HEADERS = {
	"Referer": BASE_URL,
}
API_URL = "%s/api" % BASE_URL
API_KEY = "79299E039686246B"
LANG = "pl"

class sdTVdb:
	def __init__(self):
		self.cm = sdCommon.common()
		self.parser = sdParser.Parser()

	def search(self, name, complete=True):
		show = {}
		params={"seriesname": name, "language": LANG}
		query_data = { 'url': "%s/api/GetSeries.php%s" % (BASE_URL, self.parser.setParam(params)), 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
		data = self.cm.getURLRequestData(query_data)
		dom = ET.fromstring(data)
		if not len(dom):
			return {}
		meta = self.dom2dict(dom[0])
		#return meta
		if not complete:
			return self.update_image_urls(meta)
		show.update(self.get(meta["id"]))
		return show

	def dom2dict(self, node):
		ret = {}
		for child in node:
			if len(child):
				ret.setdefault(child.tag.lower(), []).append(self.dom2dict(child))
			else:
				ret[child.tag.lower()] = child.text.encode("utf-8") if child.text != None else None
		return ret

	def update_image_urls(self, meta):
		if isinstance(meta, dict):
			for k, v in meta.items():
				if isinstance(v, list):
					map(self.update_image_urls, v)
				elif isinstance(v, dict):
					self.update_image_urls(v)
				elif k in ["banner", "fanart", "poster", "filename", "bannerpath", "vignettepath", "thumbnailpath"] and isinstance(v, basestring):
					meta[k] = self.image_url(v)
		return meta

	def image_url(self, fragment):
		return "%s/banners/%s" % (BASE_URL, fragment)

	def get(self, show_id):
		show = {}
		query_data = { 'url': self.show_url(show_id), 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
		data = self.cm.getURLRequestData(query_data)
		dom = ET.fromstring(data)
		if not len(dom):
			return
		meta = self.dom2dict(dom[0])
		meta = self.split_keys(meta, "actors", "genre", "writer")
		self.update_image_urls(meta)
		show.update(meta)
		return dict(show)

	def get_banners(self, show_id):
		query_data = { 'url': "%s/banners.xml" % self.show_base_url(show_id), 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
		data = self.cm.getURLRequestData(query_data)
		dom = ET.fromstring(data)
		if not len(dom):
			return
		return self.update_image_urls(self.dom2dict(dom))["banner"]

	def get_all_meta(self, show_id):
		query_data = { 'url': "%s/all/%s.xml" % (self.show_base_url(show_id), LANG), 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
		data = self.cm.getURLRequestData(query_data)
		dom = ET.fromstring(data)
		if not len(dom):
			return
		meta = self.update_image_urls(self.dom2dict(dom))
		meta["series"][0]["episodes"] = meta["episode"]
		meta = meta["series"][0]
		meta["banners"] = self.get_banners(show_id) or []
		return meta

	def show_url(self, show_id):
		return "%s/%s/series/%s/%s.xml" % (API_URL, API_KEY, show_id, LANG)

	def show_base_url(self, show_id):
		return "%s/%s/series/%s" % (API_URL, API_KEY, show_id)

	def split_keys(self, meta, *keys):
		for key in keys:
			if meta.get(key):
				meta[key] = filter(None, meta[key].split("|"))
		return meta

	def get_list_item(self, meta):
		m = lambda x: meta.get(x) or ""
		m_list = lambda x: meta.get(x) and ", ".join(meta[x]) or ""
		return {
			"count": meta["id"],
			"title": meta["seriesname"],
			"icon": m("poster"),
			"thumbnail": m("poster"),
			"banner": m("banner"),
			"title": meta["seriesname"],
			"genre": m_list("genre"),
			"plot": m("overview"),
			"plot_outline": m("overview"),
			"tagline": m("overview"),
			"rating": m("rating"),
			"code": m("imdb_id"),
			"mpaa": m("contentrating"),
			"cast": m("actors") or [],
			"castandrole": m("actors") or [],
			"tvshowtitle": meta["seriesname"],
			"studio": m("network"),
			"status": m("status"),
			"premiered": m("firstaired"),
			"duration": m("runtime"),
			"picturepath": m("poster"),
			"year": meta.get("firstaired") and meta["firstaired"].split("-")[0] or "",
			"votes": "%s votes" % meta["ratingcount"],
			"fanart": m("fanart"),
		}

	def get_season_list_item(self, meta, season):
		m = lambda x: meta.get(x) or ""
		m_list = lambda x: meta.get(x) and ", ".join(meta[x]) or ""
		try:
			season_id = filter(lambda ep: int(ep["seasonnumber"]) == season, meta["episodes"])[0]["seasonid"]
		except IndexError:
			return {}
		item = {
			"label": "Sezon %d" % season,
			"count": season_id,
			"tvshowtitle": meta["seriesname"],
			"season": season,
			"fanart": m("fanart"),
		}
		season_banners = [banner for banner in meta["banners"] if banner["bannertype"] == "season" and int(banner["season"]) == season]
		if season_banners:
			item["icon"] = item["thumbnail"] = season_banners[0]["bannerpath"]
		return item

	def get_episode_list_item(self, show_meta, season, episodenumber):
		try:
			episode = [episode for episode in show_meta["episodes"] if (int(episode["seasonnumber"]) == season and int(episode["episodenumber"]) == episodenumber)][0]
		except IndexError:
			return {}
		m = lambda x: episode.get(x) or ""
		item = {
			"label": m("episodename"),
			"icon": m("filename"),
			"thumbnail": m("filename"),
				"count": m("id"),
				"season": season,
				"episode": m("episodenumber"),
				"title": m("episodename"),
				"originaltitle": m("episodename"),
				"plot": m("overview"),
				"plot_outline": m("overview"),
				"tagline": m("overview"),
				"rating": float(m("rating") or 0),
				"code": m("imdb_id"),
				"premiered": m("firstaired"),
				"cast": episode.get("gueststars") and filter(None, episode["gueststars"].split("|")) or [],
				"tvshowtitle": show_meta.get("seriesname") or "",
				"writer": episode.get("writer") and ", ".join(filter(None, episode["writer"].split("|"))) or "",
				"fanart": show_meta.get("fanart") or ""
		}
		return item

	def build_episode_list_items(self, show_meta, season):
		item = []
		episodes = [episode for episode in show_meta["episodes"] if int(episode["seasonnumber"]) == season]
		episodes = sorted(episodes, key=lambda ep: int(ep["episodenumber"]))
		for episode in episodes:
			m = lambda x: episode.get(x) or ""
			item.append({
				"label": m("episodename"),
				"icon": m("filename"),
				"thumbnail": m("filename"),
					"count": m("id"),
					"season": season,
					"episode": m("episodenumber"),
					"title": m("episodename"),
					"originaltitle": m("episodename"),
					"plot": m("overview"),
					"plot_outline": m("overview"),
					"tagline": m("overview"),
					"rating": float(m("rating") or 0),
					"code": m("imdb_id"),
					"premiered": m("firstaired"),
					"cast": episode.get("gueststars") and filter(None, episode["gueststars"].split("|")) or [],
					"tvshowtitle": show_meta.get("seriesname") or "",
					"writer": episode.get("writer") and ", ".join(filter(None, episode["writer"].split("|"))) or "",
					"fanart": show_meta.get("fanart") or ""
			})
		return item