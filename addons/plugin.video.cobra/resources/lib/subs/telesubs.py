# Import necessary libraries
import random
import shutil
import xbmcaddon,os,xbmc
global global_var
global_var=[]
import logging as log
import requests,json,re
import urllib
import xbmcvfs


########### Constants ###################


AllSubsNew_CHANNEL_ID = -1002086580511


#########################################
#########################################

def extract_season_episode_numbers(telegram_message_file_name):

    optional_separators = r'[\s._\-x+,&:]{0,2}' # 0-2 occurrences
    optional_middle_separators = r'[\s._\-x+,&:]{0,4}' # 0-4 occurrences

    regex_pattern = re.compile(r'S[e]?(?:ason)?' + optional_separators + '(?P<season_number>\d{1,2})' + optional_middle_separators + 'E[p]?(?:isode)?' + optional_separators + '(?P<episode_number>\d{1,3})', re.IGNORECASE)
    
    match = regex_pattern.search(telegram_message_file_name)
    if match:
        extracted_season_number = match.group('season_number').zfill(2) # Fill leading zero if needed
        extracted_episode_number = match.group('episode_number').zfill(2) # Fill leading zero if needed
        return extracted_season_number, extracted_episode_number

    return None, None
       
def get_subs(item):

    global global_var
    
    media_type = item["media_type"]
    
    title = item.get('title', '').lower().replace(' ', '.')
    season = item.get('season', '')
    episode = item.get('episode', '')
    imdb_id = item.get('imdb', '')
    year = item.get('year', '')
    import xbmc
    
    if item['media_type']=='tv':
        
        if len(str(episode))==1:
          
          episode_n="0"+str(episode)

        else:
           episode_n=episode
        if len(str(season))==1:
          season_n="0"+str(season)
        else:
          season_n=season
        title=title+'.S%sE%s'%(season_n,episode_n)
    search_query_list = [title, imdb_id] # Example: ["No Way Up", "tt16253418"]

    
    num=random.randint(1,1001)
    resuaddon=xbmcaddon.Addon('plugin.video.telemedia')
    listen_port=resuaddon.getSetting('port')
    all_telegram_search_results=[]
    for search_query in search_query_list:
        
        data={'type':'td_send',
             'info':json.dumps({'@type': 'searchChatMessages','chat_id':(AllSubsNew_CHANNEL_ID), 'query': search_query,'from_message_id':0,'offset':0,'filter':{'@type': 'searchMessagesFilterDocument'},'limit':100, '@extra': num})
             }

        event=requests.post('http://127.0.0.1:%s/'%listen_port,json=data).json()

        if 'status' in event:
            return
        all_telegram_search_results.extend(event['messages'])

            

    telegram_found_subtitles_files=[]
    subtitle_list=[]
    # import logging
    for telegram_message in all_telegram_search_results:
        # logging.warning('documentdocument '+str(telegram_message['content']))
        telegram_message_file_name = telegram_message['content']['document']['file_name'].replace('_', '.').replace(' ', '.')
        
        # Skip over already added subtitles
        # Skip over ZIP files from @ScrewZiraBot (always contains more than 1 subtitles)
        if (telegram_message_file_name in telegram_found_subtitles_files) or (telegram_message_file_name.startswith('@ScrewZiraBot') and telegram_message_file_name.endswith('.zip')):
            continue
        if telegram_message_file_name.endswith('.zip'):
            continue
        telegram_found_subtitles_files.append(telegram_message_file_name)

        #####################################################################################################################
        # TV Shows Season/Episode Number Matching

        if media_type == 'tv':
            extracted_season_number, extracted_episode_number = extract_season_episode_numbers(telegram_message_file_name)
            # Skip subtitle on "None" values - no season/episode extraction found
            if not extracted_season_number and not extracted_episode_number:
                continue
            
            # Check if season and extracted_season_number are equal (boolean)
            season_matches = int(season) == int(extracted_season_number)
            # Check if episode and extracted_episode_number are equal (boolean)
            episode_matches = int(episode) == int(extracted_episode_number)
            
            if not season_matches or not episode_matches:
                continue

        else:
            regex=r'(?ix)(?:E|e|episode)(\d{1})'
            m=re.compile(regex).findall(telegram_message_file_name)
            if len(m)>0:
                continue    

            regex='.*([1-3][0-9]{3})'
            year_pre=re.compile(regex).findall(telegram_message_file_name)
            
            year_z=0
            
            if len(year_pre)>0:
                year_z=year_pre[0].replace('2160','').replace('1080','').replace('720','').replace('480','')
                if year_z not in year:
                 continue

                ##############################################################################################
        telegram_message_caption = telegram_message['content']['caption']['text'].replace('\n',' ')
        
        file_id=telegram_message['content']['document']['document']['id']
        
        telegram_subtitle_display_name = telegram_message_file_name
        strings_to_replace = [
            'TranslationsMoviesHEB.t.me HEB',
            'TranslationsMoviesHEB HEB',
            'TranslationsMoviesHEB.t.me',
            'TranslationsMoviesHEB',
            '@ScrewZiraBot_',
            '@ScrewZiraBot-',
            '@ScrewZiraBot',
            '.srt',
            '.ass',
            '.sub',
            '.idx',
            '.sup',
        ]
        for string in strings_to_replace:
            telegram_subtitle_display_name = telegram_subtitle_display_name.replace(string, '') # Replace to none
        

        subtitle_list.append(telegram_subtitle_display_name)
        global_var=subtitle_list

    return subtitle_list
    

    


