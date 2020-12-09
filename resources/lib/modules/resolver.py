# -*- coding: utf-8 -*-

import requests
import resolveurl

import re
import json

from resources.lib.modules import tools
from resources.lib.modules import cloudscraper as cfscrape

from Cryptodome.Cipher import AES
import base64
from hashlib import md5

class Resolver:
    def __init__(self):
        self.resolved_link = ''
        self.test_result = ''

    def resolve(self, link):
        #Test Link for certain providers that need to be done by my own resolver, else use ResolveURL
        
        if 'kwik.cx' in link['link']:
            self.kwik_resolver(link['link'])
        elif 'magictwist.wm' in link['link']:
            self.twist_resolver(link['link'])
        elif 'AnimeFlix' in link['site']:
            self.direct_resolve(link['link'])
        elif 'GogoAnime' in link['site']:
            self.gogoanime_resolve(link['link'])
        elif '4Anime' in link['site']:
            self.fourAnime_resolver(link['link'])
        else:
            self.jsergio_resolver(link['link'])
  
        result = self.link_test(self.resolved_link)
        
        response = {'resolved_url': self.resolved_link, 
                    'test_result': result}
        
        return response    
        
    def direct_resolve(self, link):
        self.resolved_link = link 
    
    def gogoanime_resolve(self,link):
        
        if 'gogo-play.net/streaming' in link:
            r1= re.findall(r'(?://|\.)(gogo-play\.net)/(?:streaming|embed|load)\.php\?id=([a-zA-Z0-9]+)',link)
            link='https://%s/ajax.php?id=%s' % (r1[0][0],r1[0][1])
            scraper = cfscrape.create_scraper()
            resp = scraper.get(link)
            load = json.loads(resp.content)
            resolved_Stream=''
            resolved_Stream=load['source'][0]['file']
            self.resolved_link = resolved_Stream

        elif 'cloud9' in link:
            link=link.replace('https://cloud9.to/embed/', 'https://api.cloud9.to/stream/')
            #create cloudflare scraper, save resp and use json
            scraper = cfscrape.create_scraper()
            resp = scraper.get(link)
            load = json.loads(resp.content)
            resolved_Stream=''

            #search for resolved HD Stream
            for a in range(len(load['data']['sources'])):
                if load['data']['sources'][a]['label'] == 'HD' or load['data']['sources'][a]['label'] == 'FHD':
                    resolved_Stream=load['data']['sources'][a]['file']
            self.resolved_link = resolved_Stream

    def fourAnime_resolver(self, link):
        servers = ['https://v1.', 'https://v2.', 'https://v3.', 'https://v4.', 'https://v5.', 'https://v6.', 'https://v7.']
        
        working_link = ''
        
        index = 0
        for a in servers:
            if working_link != '':
                continue
            resp = requests.head(a + link)
            if resp.status_code == 200:
                working_link = a + link
            if resp.status_code == 302:
                working_link = a + link
                
        self.resolved_link = working_link
        
    def kwik_resolver(self, link):
        scraper = cfscrape.create_scraper()
        download_url = link.replace('kwik.cx/e/', 'kwik.cx/f/')
        kwik_text = scraper.get(download_url, headers={'referer': download_url}).content
        post_url = re.findall(r'action="(.*?)"', kwik_text)
        token = re.findall(r'value="(.*?)"', kwik_text)
        if len(post_url) > 0 and len(token) > 0:
            stream_url = scraper.post(post_url[0], headers={'referer': download_url}, data={'_token': token[0]}, allow_redirects=False).headers['Location']
            self.resolved_link = stream_url
        elif len(post_url) == 0:
            tools.log('Error - No action in kwik scraped url: ' + kwik_text, 'error')
        elif len(token) == 0:
            tools.log('Error - No token in kwik scaped url:' + kwik_text, 'error')
    
    def twist_resolver(self, link):
        #Setup
        new_link = link.replace('magictwist.wm/', '')
        new_link = json.loads(new_link)
        
        #Decrypt
        decrypt_url = TwistDecrypt().decrypt(new_link['source'].encode('utf-8'), b"LXgIVP&PorO68Rq7dTx8N^lP!Fa5sGJ^*XK").decode('utf-8')

        file_name = decrypt_url.split('/')[-1].replace(decrypt_url.split('.')[-1], '')
        decrypt_url = decrypt_url.replace(file_name, tools.quote(file_name))

        stream_url = 'https://at-cdn.bunny.sh' + decrypt_url
        headers = {
            'Referer': tools.quote('https://twist.moe/a/{slug}/{episode}'.format(**new_link)),
            'User-Agent': tools.quote(tools.get_random_ua()),
        }
        location = requests.head(stream_url, headers=headers).headers['location']

        location += '|User-Agent={User-Agent}&Referer={Referer}'.format(**headers)
        
        self.resolved_link = location
        
    def jsergio_resolver(self, link): 
        stream_url = resolveurl.resolve(link)
        if stream_url == False: #If there is an error it decides that it is a direct
            stream_url = link
        
        self.resolved_link = stream_url
        
    def link_test(self, test):
        try:
            if 'cdn.bunny.sh' in test:
                return 'Good'
                
            resp = requests.head(test, timeout=20)
            if resp.status_code == 200:
                return 'Good'
            elif resp.status_code == 302:
                self.resolved_link = resp.headers['location']
                return 'Good'
            else:
                tools.log('Error - Status Code: ' + resp.status_code, 'error')
                return 'Bad'
        except:
            return 'Bad'
        
class TwistDecrypt:
    def __init__(self):
        self.block_size = 16

    def pad(self, data):
        length = self.block_size - (len(data) % self.block_size)
        return data + (chr(length)*length).encode()


    def unpad(self, data):
        return data[:-(data[-1] if type(data[-1]) == int else ord(data[-1]))]


    def bytes_to_key(self, data, salt, output=48):
        # extended from https://gist.github.com/gsakkis/4546068
        assert len(salt) == 8, len(salt)
        data += salt
        key = md5(data).digest()
        final_key = key
        while len(final_key) < output:
            key = md5(key + data).digest()
            final_key += key
        return final_key[:output]


    def decrypt(self, encrypted, passphrase):
        encrypted = base64.b64decode(encrypted)
        assert encrypted[0:8] == b"Salted__"
        salt = encrypted[8:16]
        key_iv = self.bytes_to_key(passphrase, salt, 32+16)
        key = key_iv[:32]
        iv = key_iv[32:]
        aes = AES.new(key, AES.MODE_CBC, iv)
        return self.unpad(aes.decrypt(encrypted[16:]))
