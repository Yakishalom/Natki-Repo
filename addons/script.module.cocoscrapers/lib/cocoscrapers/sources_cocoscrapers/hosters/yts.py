# -*- coding: utf-8 -*-
'''
    EzScrapers Project
'''

import urllib,base64,json,random,requests,xbmcvfs,os,xbmc,logging
import xbmcaddon
from cocoscrapers.modules import source_utils
base_header={
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',

            'Pragma': 'no-cache',
            
           
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:59.0) Gecko/20100101 Firefox/59.0',
            }
class source:
    priority = 1
    pack_capable = False
    cobra=xbmcaddon.Addon('plugin.video.cobra')
    show_torrent=cobra.getSetting('show_torrent')
    if show_torrent=='true':
        hasMovies = True
        hasEpisodes = True
    else:
        hasMovies = False
        hasEpisodes = False
    def __init__(self):
        self.language = ['en']
    def sources(self, data, hostDict):
        sources = []
        if not data: return sources
        append = sources.append
        try:
            title = data['tvshowtitle'] if 'tvshowtitle' in data else data['title']
            title = title.replace('&', 'and').replace('Special Victims Unit', 'SVU').replace('/', ' ')
            aliases = data['aliases']
            episode_title = data['title'] if 'tvshowtitle' in data else None
            year = data['year']
            hdlr = 'S%02dE%02d' % (int(data['season']), int(data['episode'])) if 'tvshowtitle' in data else year
            name=data['title_heb']
            all_names=[]
            tv_movie='movie'
            count = 0
            seed=''
            peer=''
            f_seeds=True
            imdb_id=data['imdb']
            if 'tvshowtitle' in data:
                return
            else:
                x=requests.get('https://yts.mx/api/v2/list_movies.json?query_term=%s&page=1&limit=300&order_by=desc&sort_by=rating'%(title),headers=base_header,timeout=10,verify=False).json()

               
                for items in x['data']['movies']:
                    title=items['slug'].replace('-','.')
                    for te in items['torrents']:
                     hash=te['hash']
                     link='magnet:?xt=urn:btih:%s&dn=%s'%(hash,urllib.parse.quote_plus(title))
                     size=te['size']
                     res=te['quality']
                     if f_seeds:
                        seed=te['seeds']
                        peer=te['peers']
                        if 40>int(seed):
                            continue
                     o_link=link
                     try:
                         o_size=size
                         size=float(o_size.replace('GB','').replace('MB','').replace(",",'').strip())
                         if 'MB' in o_size:
                           size=size/1000
                     except Exception as e:
                        size=0
                     max_size=40
                     if size<max_size:
                        sad='Peer: %s Seed: %s'%(peer,seed)
                        
                        host='load.to'
                        name_info=res#name.replace('_','.')
                        info=''
                        url=link
                        append({'provider': 'torrents', 'source': host, 'seeders': seed, 'name': title+' - '+ sad+' - YTS', 'name_info': name_info, 'quality': res, 'language': 'en', 'url': url,
                                    'info': info, 'direct': 'elementum', 'debridonly': False, 'size': size})
                        count += 1
                    
            return sources
        except:
            source_utils.scraper_error('YTS')
            return sources