# -*- coding: utf-8 -*-
import os, sys
import xbmcaddon, itertools

import sdLog, sdCommon
log = sdLog.pLog()

import SimpleDownloader as downl
downloader = downl.SimpleDownloader()

scriptID   = sys.modules[ "__main__" ].scriptID
t = sys.modules[ "__main__" ].language
ptv = xbmcaddon.Addon(scriptID)

dbg = sys.modules[ "__main__" ].dbg

INVALID_CHARS = "\\/:*?\"<>|"

class Downloader:
    def __init__(self):
        pass
    
    def getFile(self, opts = {}):
        title = self.fileName(opts['title'])
        params = { 'url': opts['url'], 'download_path': opts['path'] }
        if dbg == True:
            log.info('Downloader - getFile() -> Download path: ' + opts['path'])
            log.info('Downloader - getFile() -> URL: ' + opts['url'])
            log.info('Downloader - getFile() -> Title: ' + title)
        downloader.download(title, params)
        
    def fileName(self, title):
	title = sdCommon.Chars().replaceChars(title)
        filename = "%s-[%s].mp4" % (''.join(c for c in title if c not in INVALID_CHARS), 0)
        return filename
