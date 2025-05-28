# -*- coding: utf-8 -*-
'''
    EzScrapers Project
'''

import urllib,base64,json,random,requests,xbmcvfs,os,xbmc,logging,re,xbmcaddon,shutil,time
resuaddon=xbmcaddon.Addon('plugin.video.telemedia')
listen_port=resuaddon.getSetting('port')


class source:
    priority = 1
    pack_capable = False
    hasMovies = True
    hasEpisodes = True
    def __init__(self):
        self.language = ['en']
    def res_q(self,quality):
        f_q='720'

        if '4k' in quality.lower():
          f_q='2160'
        elif '2160' in quality:
          f_q='2160'
        elif '1080' in quality:
          f_q='1080'
        elif '900' in quality:
          f_q='1080'
        elif '720' in quality:
          
          f_q='720'
        elif '480' in quality:
          f_q='SD'
        elif '430' in quality:
          f_q='SD'
        elif '360' in quality or 'sd' in quality.lower():
          f_q='SD'
        elif '240' in quality:
          f_q='SD'
        elif 'hd' in quality.lower() or 'hq' in quality.lower():
          f_q='SD'
        return f_q
    
    def fix_q_links(self,quality):
        f_q=100
        if '4k' in quality.lower():
            quality='2160'
        if '2160' in quality:
          f_q=1
        if '1080' in quality:
          f_q=2
        elif '900' in quality:
          f_q=3
        elif '720' in quality:
          f_q=4
        elif '480' in quality:
          f_q=5
        
        elif '360' in quality or 'sd' in quality.lower():
          f_q=6
        elif '240' in quality:
          f_q=7
        elif 'hd' in quality.lower() or 'hq' in quality.lower():
          f_q=8
        return f_q
    def get_q(self,name):
        q=self.res_q(name)
        loc=self.fix_q_links(q)

        return q,loc
    def extract_season_episode_numbers(self,telegram_message_file_name):

        optional_separators = r'[\s._\-x+,&:]{0,2}' # 0-2 occurrences
        optional_middle_separators = r'[\s._\-x+,&:]{0,4}' # 0-4 occurrences

        regex_pattern = re.compile(r'S[e]?(?:ason)?' + optional_separators + '(?P<season_number>\d{1,2})' + optional_middle_separators + 'E[p]?(?:isode)?' + optional_separators + '(?P<episode_number>\d{1,3})', re.IGNORECASE)
        
        regex_pattern_heb = re.compile(r'ע[ע]?(?:ason)?' + optional_separators + '(?P<season_number>\d{1,2})' + optional_middle_separators + 'פ[פ]?(?:isode)?' + optional_separators + '(?P<episode_number>\d{1,3})', re.IGNORECASE)
        ss=[regex_pattern,regex_pattern_heb]
        for i in ss:
            match = i.search(telegram_message_file_name)
            if match:
                extracted_season_number = match.group('season_number').zfill(2) # Fill leading zero if needed
                extracted_episode_number = match.group('episode_number').zfill(2) # Fill leading zero if needed
                return extracted_season_number, extracted_episode_number

        return None, None

    def sources(self, data, hostDict):
        sources = []
        if not data: return sources
        append = sources.append
        try:
            url='https://rrr333-6d3a84e4ba29.herokuapp.com/'
            herok=requests.get(url).text.strip()
            regex='<title>(.+?)</title>'
            m=re.compile(regex).findall(herok)[0]
            if 'Application Error'==m:

                return 
        except:pass
        title = data['tvshowtitle'] if 'tvshowtitle' in data else data['title']
        title = title.replace('&', 'and').replace('Special Victims Unit', 'SVU').replace('/', ' ')
        aliases = data['aliases']
        episode_title = data['title'] if 'tvshowtitle' in data else None
        year = data['year']
        hdlr = 'S%02dE%02d' % (int(data['season']), int(data['episode'])) if 'tvshowtitle' in data else year

        tmdbKey='653bb8af90162bd98fc7ee32bcbbfb3d'
        try:
            name=data['title_heb']
        except:
            name=title
        original_title=title.lower()
        heb_name=name
        o_name=heb_name
        num=random.randint(1,10001)
        amount_found=100
        pages=0
        countQ=0
        last_id=0   
        count = 0
        link=''
        all_t_links=[]
        exclude=[]
        ok=False
        heb_name=heb_name.replace('...?','').replace('\u200f','').replace(':','').replace('%27',"'").replace('-'," ").replace("’","'").replace(" ",".")
        c_original=original_title.replace('%20','.').replace(' ','.').replace('%27',"'").replace('%3a',":").replace('...?',' ').replace('...',' ').replace('..',' ').replace(':','').replace("'",'')
        search_title=[c_original,heb_name]
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
            #.replace('"','') דופק סדרות מסויימות
            # original_title=original_title.split(sep, 1)[0]
            
            options=[' ע%s פ%s'%(season,episode),'ע%s.פ%s'%(season,episode),' ע%sפ%s'%(season,episode),' עונה %s פרק %s'%(season,episode),'.S%sE%s'%(season_n,episode_n),'.S%sE%s'%(season,episode)]
        # while amount_found>0:
        for query in search_title:
            td={'type':'td_send',
                 'info':json.dumps({'@type': 'searchChatMessages','chat_id':(-1001992629352), 'query': query,'from_message_id':last_id,'offset':0,'message_thread_id':0,'limit':100, '@extra': num})
                 }
            event=requests.post('http://127.0.0.1:%s/'%listen_port,json=td).json()
            # if event==None:
                # while (1):
                    # event=requests.post('http://127.0.0.1:%s/'%listen_port,json=td).json()

                    # if event!=None:
                        # break
            # if 'total_count' not in event:
                # break
            # amount_found=int(event['total_count'])-(100*pages)
            # pages+=1

            # if amount_found==0:
                # continue
            for items in event['messages']:
                # amount_found-=1
                if 'text' in items['content']:
                    # countQ+=1
                    txt_lines=items['content']['text']['text']#.split('\n\n')
                    regex='File Name :(.+?)\n'
                    file_name=re.compile(regex).findall(txt_lines)[0]
                    file_name2=file_name
                    file_name=file_name.replace('.mp4','').replace('.mkv','').replace('.avi','').replace('_','.').replace(' ','.').replace('-','.').lower()

                    if file_name in all_t_links :
                        continue
                    all_t_links.append(file_name)

                        
                    # if query in file_name:
                        
                    regex='File Size :(.+?)\n'
                    file_size=re.compile(regex).findall(txt_lines)[0].replace('GiB','')

                    regex='Download :(.+?)\n'
                    link=re.compile(regex).findall(txt_lines)[0].replace(' ','')
                    q,loc=self.get_q(file_name)
                    host='thevideo.me'
                    name_info=q+' '+file_name.replace('_','.').lower()
                    info=file_name
                    quality=file_name
                    url=link
                    try:
                         o_size=file_size
                         file_size=float(o_size.replace('GB','').replace('MB','').replace(",",'').strip())
                         if 'MB' in o_size:
                           file_size=file_size/1000
                    except Exception as e:
                    
                        file_size=0
                    
                    
                if 'tvshowtitle' in data:
                        extracted_season_number, extracted_episode_number = self.extract_season_episode_numbers(file_name2)
                        # Skip subtitle on "None" values - no season/episode extraction found
                        if not extracted_season_number and not extracted_episode_number:
                            continue

                        # Check if season and extracted_season_number are equal (boolean)
                        season_matches = int(season) == int(extracted_season_number)
                        # Check if episode and extracted_episode_number are equal (boolean)
                        episode_matches = int(episode) == int(extracted_episode_number)
                        
                        if not season_matches or not episode_matches:
                            continue
        

                        append({'provider': 'filestream', 'source': host,'seeders': 0 ,'name': file_name, 'name_info': quality+' '+name_info+'.mp4', 'quality': quality, 'language': 'en', 'url': url,
                                        'info': info, 'direct': False, 'debridonly': None, 'size': file_size})
                        count += 1
                else:
                    append({'provider': 'filestream', 'source': host,'seeders': 0 ,'name': file_name, 'name_info': quality+' '+name_info+'.mp4', 'quality': quality, 'language': 'en', 'url': url,
                                    'info': info, 'direct': False, 'debridonly': None, 'size': file_size})
                    count += 1
        # try:
            # last_id=str(items['id'])
        # except:
            # last_id=''

        return sources