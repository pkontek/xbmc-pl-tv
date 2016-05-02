# -*- coding: utf-8 -*-
import re, os, sys
#import math
import xbmcaddon
import sdLog

log = sdLog.pLog()

scriptID = sys.modules[ "__main__" ].scriptID
scriptname = "Polish Live TV"
ptv = xbmcaddon.Addon(scriptID)

dbg = ptv.getSetting('default_debug')

class Time:
    def __init__(self):
        pass
    
    def totalTime(self, th, tm, ts, tss):
        return float(float(th)*3600) + (float(tm)*60) + float(ts) + (float(tss)/100)
    
    def hour(self, time):
        return int(float(time)/3600)
    
    def minutes(self, time):
        return int((float(time) - (3600*float(self.hour(time))))/60)
    
    def seconds(self, time):
        return int(float(time) - 3600*float(self.hour(time)) - 60*float(self.minutes(time)))
    
    def mili(self, time):
        return int((float(time) - 3600*float(self.hour(time)) - 60*float(self.minutes(time)) - float(self.seconds(time)))*1000)

    def set10(self, t):
        tt = str(t)
        if len(str(t)) == 1:
            tt = "0" + str(t)
        return tt
    
    def set100(self, t):
        tt = str(t)
        if len(str(t)) == 1:
            tt = "00" + str(t)
        elif len(str(t)) == 2:
            tt = "0" + str(t)
        elif len(str(t)) == 3:
            tt = str(t)
        return tt
    

class SubtitleParser:
    def __init__(self):
        pass
  

class MicroDVD:
    def __init__(self, fps):
        self.t = Time()
        self.fps = fps
    
    def getTotalTime(self, frame, fps):
        return float(float(frame)/float(fps))
    
    def setTotalTime(self, frame, fps):
        return float(float(frame)*float(fps))
    
    def getSubtitleTab(self, response):
        pattern = '^\{(\d*)\}\{(\d*)\}(.*)$'
        tab = response.split("\n")
        contentTab = []
        for i in range(len(tab)):
            match = re.compile(pattern).findall(tab[i])
            if len(match) > 0:
                contentTab.append({ 'start_h': self.t.hour(self.getTotalTime(match[0][0], self.fps)),
                                    'start_m': self.t.set10(self.t.minutes(self.getTotalTime(match[0][0], self.fps))),
                                    'start_s': self.t.set10(self.t.seconds(self.getTotalTime(match[0][0], self.fps))),
                                    'start_ss': self.t.set100(self.t.mili(self.getTotalTime(match[0][0], self.fps))),
                                    'end_h': self.t.hour(self.getTotalTime(match[0][1], self.fps)),
                                    'end_m': self.t.set10(self.t.minutes(self.getTotalTime(match[0][1], self.fps))),
                                    'end_s': self.t.set10(self.t.seconds(self.getTotalTime(match[0][1], self.fps))),
                                    'end_ss': self.t.set100(self.t.mili(self.getTotalTime(match[0][1], self.fps))),
                                    'text': match[0][2].strip().encode("utf-8") })
        return contentTab
    
    
class Srt:
    def __init__(self):
        pass
    

class ASS:
    def __init__(self, subtab, args = {}):
        self.subtab = subtab
        self.width = args['width']
        self.height = args['height']
        self.fontcolor = args['fontcolor']
        self.title = args['title']
        
    def content(self):
        ass = self.header()
        for i in range(len(self.subtab)):
            ass += "Dialogue: 0,%s:%s:%s.%s,%s:%s:%s.%s,Default,,0000,0000,0000,,%s\r\n" % (self.subtab[i]['start_h'], self.subtab[i]['start_m'], self.subtab[i]['start_s'], self.subtab[i]['start_ss'][:-1], self.subtab[i]['end_h'], self.subtab[i]['end_m'], self.subtab[i]['end_s'], self.subtab[i]['end_ss'][:-1], self.style(self.subtab[i]['text']))
        return ass
        
    def header(self):
        #fontsize = "15"
        
        out = "[Script Info]\r\n"
        out += "Title: %s\r\n" % (self.title) 
        out += "Original Script: SubEditJava written by Plesken\r\n"
        out += "Original Translation: Python Subtitles written by Plesken\r\n"
        out += "ScriptType: v4.00+\r\n"
        out += "Collisions: Normal\r\n"
        out += "PlayResX: %s\r\n" % (self.width)
        out += "PlayResY: %s\r\n\r\n" % (self.height)
        #"Video Aspect Ratio: " + ssa.getSSAR() + "\r\n\r\n" +
        out += "[V4+ Styles]\r\n"
        out += "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, TertiaryColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\r\n"
        out += "Style: Default,Sans,%s,&H0000FFFF,&H00%s,&H00000000,&H00000000,0,0,0,0,100,100,0.00,0.00,1,2,1,2,0,0,0,238\r\n\r\n" % (str(self.fontsize(self.width)), self.fontcolor)
        out += "[Events]\r\n"
        out += "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\r\n"
        return out
    
    def style(self, text):
        ntext = text
        tabText = text.split('|')
        stext = ""
        for i in range(len(tabText)):
            if '/' in text:
                stext = '{\i1}' + tabText[i].replace("/", "") + '{\i0}'
            elif '<i>' in text:
                stext = '{\i1}' + tabText[i].replace("<i>", "").replace("</i>", "") + '{\i0}'
            else:
                stext = tabText[i]
            if i == 0:
                ntext = stext
            else:
                ntext += "\N" + stext
        return ntext
    
    def fontsize(self, width):
        return int(round((15*float(width))/640))
