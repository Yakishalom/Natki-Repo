# -*- coding: utf-8 -*-
import json,logging
class source:
    priority = 1
    pack_capable = False
    hasMovies = True
    hasEpisodes = True
    def __init__(self):
        self.language = ['en']
    def sources(self, data, hostDict):
        sources = []
        if not data: return sources
        append = sources.append
        title = data['tvshowtitle'] if 'tvshowtitle' in data else data['title']
        year = data['year']

        if 'tvshowtitle' in data:
            season=data['season']
            episode=data['episode']
            if len(episode)==1:
              episode_n="0"+episode
            else:
               episode_n=episode
            if len(season)==1:
              season_n="0"+season
            else:
              season_n=season
        try:
            named=data['title_heb']
        except:
            named=title
        named=named.replace("'","")
        count = 0
        
        import requests

        cookies = {
            'PHPSESSID': '500df8560dbb037a736a52767a22f453',
        }

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:124.0) Gecko/20100101 Firefox/124.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            # 'Accept-Encoding': 'gzip, deflate, br',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Origin': 'https://admin.nachosisrael.com',
            'Alt-Used': 'admin.nachosisrael.com',
            'Connection': 'keep-alive',
            'Referer': 'https://admin.nachosisrael.com/login',
            # 'Cookie': 'PHPSESSID=500df8560dbb037a736a52767a22f453',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-User': '?1',
        }

        response = requests.get(
            'https://admin.nachosisrael.com/api/search/%s/3NP4FZGD2EWR9XYC6BQTSALVJKM8H8/d15abfs-9fe2-4b84-b979-jeff21bcad13/'%named,
            cookies=cookies,
            headers=headers, timeout=5,
        )
        nachos=response.content.decode('utf-8')
        nachos=json.loads(nachos)
        tt='?token=d15abfs-9fe2-4b84-b979-jeff21bcad13'
        import xbmc,logging
        for i in nachos['posters']:
            logging.warning(i)
            if 'tvshowtitle' in data:
                if 'serie'==i['type']:
                    f_link=i['classification']
                    response = requests.get(
                        'https://admin.nachosisrael.com/api/season/by/serie/%s/{email}/3NP4FZGD2EWR9XYC6BQTSALVJKM8H8/d15abfs-9fe2-4b84-b979-jeff21bcad13/'%i['id'],
                        cookies=cookies,
                        headers=headers, timeout=5,
                    )
                    nachos=response.content.decode('utf-8')
                    nachos=json.loads(nachos)
                    for s in nachos:
                        if season==s['title'].replace('עונה ',''):
                            for e in s['episodes']:
                                if episode==e['title'].replace('פרק ',''):
                                    for u in e['sources']:
                                        url=u['url']
                                        size=5
                                        
                                        if "2160" in f_link:
                                          res="2160p"
                                        elif "4k" in f_link:
                                          res="2160p"
                                          
                                        elif "1080" in f_link:
                                          res="1080p"
                                        elif "720" in f_link:
                                          res="720p"
                                        elif "480" in f_link:
                                           res="480p"
                                        else:
                                            res='1080p'
                                        append({'provider': 'speedlink', 'source': 'rg.to','seeders': 10000, 'name': named, 'name_info': res, 'quality': res, 'language': 'en', 'url':  url+tt,
                                                    'info': '', 'direct': False, 'debridonly': False, 'size': size})
                                        count += 1
            else:
                if named==i['title']:
                    f_link=i['classification']

                    for x in i['sources']:
                        
                        url=x['url']
                        size=5
                        if "2160" in f_link:
                          res="2160p"
                        elif "1080" in f_link:
                          res="1080p"
                        elif "720" in f_link:
                          res="720p"
                        elif "480" in f_link:
                           res="480p"
                        else:
                            res='1080p'
                        
                        append({'provider': 'speedlink', 'source': 'rg.to','seeders': 10000, 'name': named, 'name_info': res, 'quality': res, 'language': 'en', 'url':  url+tt,
                                    'info': '', 'direct': False, 'debridonly': False, 'size': size})
                        count += 1
        return sources
