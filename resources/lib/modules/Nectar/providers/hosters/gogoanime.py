# -*- coding: UTF-8 -*-

#Coded by C0nvert for the Hummingbird addon
#Based on the Exodus standard but is incompatible with other scrapers without modification

#Scraper: GogoAnime
#Site: gogoanime.so

#Creation Date: 07/12/2020
#Last Update: 07/12/2020

import requests
import json
import web_pdb


from resources.lib.modules.cloudscraper import cloudscraper as cfscrape
from resources.lib.modules import tools

class source:
    def __init__(self):
        
        self.priority = 1
        self.language = ['en']
        self.domains = ['gogoanime']
        self.base_link = 'https://gogoanimeapi.herokuapp.com/api/'
        self.api_search = 'search/%s'
        self.api_sources = 'watch/%s/%s'
        
        self.scraper = cfscrape.create_scraper()
        
    def tvshow(self, data):
        link = self.base_link + self.api_search % (data['titles']['romaji'].replace(" ", "%20"))
        #web_pdb.set_trace()
        resp = self.scraper.get(link)
        load = json.loads(resp.content)
        
        correctItem =''

        #titles = data['mal_titles']
        
        for a in load:
            for b in data['mal_titles']:
                if a['anime_title'] == data['mal_titles'][b]:
                    correctItem = a
            break
        
        source_link = self.base_link + self.api_sources %(correctItem['anime_id'], data['episode'])
        print("HALLO")
        print(source_link)
        return source_link


                
    def sources(self, link):
        print("Link Before:")
        print(link)
        
        resp = self.scraper.get(link)
        info = json.loads(resp.content)
        sources = []
        #Get Link (not Resolved)
        for x in range(len(info)):
            if 'gogo-play.net/streaming' in info[x]: 
                link=info[x]
            #elif 'cloud9' in info[x]: 
                #link=info[x]

        print('Link after:')
        print(link)
        print('Print JSON')
        print(info)
        # url_link=link.replace('https://cloud9.to/embed/', 'https://api.cloud9.to/stream/')
        # resp = self.scraper.get(url_link)
        # load = json.loads(resp.content)
        # info2=''
        # print('Extr_URL')
        # print(info2)

        # for a in range(len(load['data']['sources'])):
        #     if load['data']['sources'][a]['label'] == 'HD' or load['data']['sources'][a]['label'] == 'FHD':
        #         #print(load['data']['sources'][a]['file'])
        #         info2=load['data']['sources'][a]['file']

        
        #info[2]='https:'+info[2]
 
        source = {'site': 'GogoAnime',
                'source': 'gogoanime.so',
                'link': link,
                'quality': 1080,
                'audio_type': 'Sub',
                'adaptive': False,
                'subtitles': None}         
        
        sources.append(source)
        print("NEW GOGO SOURCES")
        print(sources)
        return sources