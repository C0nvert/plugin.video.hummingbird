# -*- coding: UTF-8 -*-

#Coded by Wilson Magic for the Hummingbird addon
#Added fix by C0nvert
#Based on the Exodus standard but is incompatible with other scrapers without modification

#Scraper: AnimeFlix
#Site: animeflix.io

#Creation Date: 30/08/2019
#Last Update: 02/12/2020

import requests
import json
import urllib

import math

from resources.lib.modules.cloudscraper import cloudscraper as cfscrape
from resources.lib.modules import tools

class source:
    def __init__(self):
        self.priority = 1
        self.language = ['en']
        self.domains = ['animeflix.io']
        self.base_link = 'https://animeflix.io'
        self.api_search = '/api/search?q=%s'
        self.api_episodes = '/api/episodes?anime_id=%s&page=%s&limit=30&sort=ASC'
        self.api_embed = '/api/videos?episode_id=%s'
        
        self.scraper = cfscrape.create_scraper()
        
    def tvshow(self, data):
        link = self.base_link + self.api_search % data['titles']['canon']
    
        resp = self.scraper.get(link)

        load = json.loads(resp.content)
        info = load['data']

        correctItem = ''
        
        titles = data['mal_titles']
        
        for a in info:
            for b in titles:
                if a['title'] == titles[b]:
                    correctItem = a
        
        show_id = correctItem['id']
        
        page = math.ceil(float(int(data['episode']))/30)
        
        link = self.base_link + self.api_episodes % (str(show_id), str(int(page)))
        
        resp = self.scraper.get(link)
        load = json.loads(resp.content)
        info = load['data']

        ep_id = ''
        
        for a in info:
            if int(a['episode_num']) == int(data['episode']):
                ep_id = a['id']
        
        source_link = self.base_link + self.api_embed % ep_id
        
        
        return source_link
        
    def movie(self, data):
        resp = self.scraper.get(self.base_link + self.api_search % data['titles']['canon'])
        load = json.loads(resp.content)
        info = load['data']
        
        correctItem = ''
        
        for a in info:
            for b in data['mal_titles']:
                if a['title'] == data['mal_titles'][b]:
                    correctItem = a
                    
        show_id = correctItem['id']
        
        resp = self.scraper.get(self.base_link + self.api_episodes % (str(show_id), '1'))
        load = json.loads(resp.content)
        info = load['data']

        ep_id = info[0]['id']
                
        source_link = self.base_link + self.api_embed % ep_id
        
        return source_link
                
    def sources(self, link):   
        resp = self.scraper.get(link)
        info = json.loads(resp.content)
        
        sources = []
        
        for a in info:
            adaptive = False
            if a['type'] == 'hls':
                adaptive = 'hls'
            elif a['type'] == 'dash':
                adaptive = 'mpd'
            
            #FastStream Server is using a Crunchyroll Stream with a (non working?) Proxy Server in front of the encoded Stream Link.
            #Stream link get stripped and corrected
            
            corrected_source= a['file']
            corrected_source=corrected_source.split('/',4)
            corrected_source=urllib.unquote(corrected_source[4])
            
            #AUEngine seems not to work anymore. FastStream will be used instead.
            #Only HLS is working.
            #Why is dash not working....? Needs further digging.
            
            if a['provider'] =='FastStream' and a['type'] == 'hls' and a['hardsub'] == True:
                source = {'site': 'AnimeFlix',
                        'source': a['provider'],
                        'link': corrected_source,
                        'quality': int(str(a['resolution']).split('p')[0]),
                        'audio_type': a['lang'].title(),
                        'adaptive': adaptive,
                        'subtitles': None}                          
                sources.append(source)
            
            
            return sources            
