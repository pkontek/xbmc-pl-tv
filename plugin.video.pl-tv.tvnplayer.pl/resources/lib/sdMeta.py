# -*- coding: utf-8 -*-
import os, re, sys, StorageServer
import xbmcaddon, xbmc, xbmcgui

scriptID   = sys.modules[ "__main__" ].scriptID
t = sys.modules[ "__main__" ].language
ptv = xbmcaddon.Addon(scriptID)

import sdLog, sdSettings, sdCommon
import sdTVdb

log = sdLog.pLog()

class sdMeta:
	def __init__(self):
		self.cm = sdCommon.common()
		self.TVdb = sdTVdb.sdTVdb()
		self.cache24 = StorageServer.StorageServer('SDXBMC24', 24)
		self.cache6 = StorageServer.StorageServer('SDXBMC6', 6)

	def getShowMeta(self, show):
		meta = self.cache24.cacheFunction(sdTVdb.sdTVdb().search, show)
		if meta != []:
			return self.TVdb.get_list_item(meta)
		else:
			return {}

	def getSeasonMeta(self, show, season):
		if show != None:
			meta = self.cache24.cacheFunction(self.TVdb.get_all_meta, show)
			if meta:
				return self.TVdb.get_season_list_item(meta, season)
		return {}

	def getEpisodesList(self, show, season):
		if show != None and show != "" and show != "None":
			meta = self.cache6.cacheFunction(self.TVdb.get_all_meta, show)
			if meta:
				return self.TVdb.build_episode_list_items(meta, season)
		return {}

	def getEpisodeMeta(self, episodes, episode):
		try:
			return [a for a in episodes if int(a['episode']) == int(episode)][0]
		except IndexError:
			return {}

	def getSingleEpisodeMeta(self, show, season, episode):
		show = self.cache24.cacheFunction(sdTVdb.sdTVdb().search, show, True)
		if show != []:
			allMeta = self.cache6.cacheFunction(self.TVdb.get_all_meta, show['id'])
			meta = self.TVdb.get_episode_list_item(allMeta, int(season), int(episode))
			if meta != {}:
				meta['title'] = show['seriesname']+' - '+meta['title']
				return meta
		return {}