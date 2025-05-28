# -*- coding: utf-8 -*-

import re,requests,json,logging


def get_login_cook():

    headers = {
    'authority': 'www.ktuvit.me',
    'accept': 'application/json, text/javascript, */*; q=0.01',
    'x-requested-with': 'XMLHttpRequest',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36',
    'content-type': 'application/json',
    'origin': 'https://www.ktuvit.me',
    'sec-fetch-site': 'same-origin',
    'sec-fetch-mode': 'cors',
    'sec-fetch-dest': 'empty',
    
    'accept-language': 'en-US,en;q=0.9',
    
    }

    data = '{"request":{"Email":"hatzel6969@gmail.com","Password":"Jw1n9nPOZRAHw9aVdarvjMph2L85pKGx79oAAFTCsaE="}}'

    login_cook = requests.post('https://www.ktuvit.me/Services/MembershipService.svc/Login', headers=headers, data=data,timeout=5).cookies
    login_cook_fix={}
    for cookie in login_cook:

            login_cook_fix[cookie.name]=cookie.value

    return login_cook_fix
def extract_imdb_id_from_itt(itt):

    # Extract the IMDb ID from the IMDb link, Remove trailing slash if it exists
    imdb_link_from_ktuvit = str(itt.get('IMDB_Link', '')).rstrip("/")
    # Split the URL by "/", Get the last part of the URL, which should be the IMDb ID (tt123456)
    imdb_parts = imdb_link_from_ktuvit.split("/")
    imdb_id_from_ktuvit = imdb_parts[-1] if imdb_parts else ''
            
    # FALLBACK - Check if imdb_id_from_ktuvit is empty or doesn't start with "tt"
    if not imdb_id_from_ktuvit.startswith("tt"):
        imdb_id_from_ktuvit = str(itt.get('ImdbID', ''))
        
    return imdb_id_from_ktuvit
def ktuvit_Search(item,imdb_id):

    subtitle_list=[]
    login_cook=get_login_cook()
    

    if "tvshow" in item:
        if item["tvshow"]:
            s_type='1'
            s_title=item["tvshow"]
            s_WithSubsOnly = "false"
    else:
        s_type='0'
        s_title=item["title"]
        s_WithSubsOnly = "true"

    headers = {
        'authority': 'www.ktuvit.me',
        'accept': 'application/json, text/javascript, */*; q=0.01',
        'x-requested-with': 'XMLHttpRequest',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36',
        'content-type': 'application/json',
        'origin': 'https://www.ktuvit.me',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-mode': 'cors',
        'sec-fetch-dest': 'empty',
        'referer': 'https://www.ktuvit.me/Search.aspx',
        'accept-language': 'en-US,en;q=0.9',
        
    }
    
    data = '{"request":{"FilmName":"%s","Actors":[],"Studios":null,"Directors":[],"Genres":[],"Countries":[],"Languages":[],"Year":"","Rating":[],"Page":1,"SearchType":"%s","WithSubsOnly":%s}}'%(str(s_title),s_type,s_WithSubsOnly)
    
    response = requests.post('https://www.ktuvit.me/Services/ContentProvider.svc/SearchPage_search', headers=headers, data=data.encode('utf-8'),timeout=5).json()
    
    j_data=json.loads(response['d'])['Films']
    f_id=''
    
    if len(j_data)==0 and 'and' in s_title:
        s_title=s_title.replace('and','&')
        data = '{"request":{"FilmName":"%s","Actors":[],"Studios":null,"Directors":[],"Genres":[],"Countries":[],"Languages":[],"Year":"","Rating":[],"Page":1,"SearchType":"%s","WithSubsOnly":%s}}'%(str(s_title),s_type,s_WithSubsOnly)
    
        response = requests.post('https://www.ktuvit.me/Services/ContentProvider.svc/SearchPage_search', headers=headers, data=data.encode('utf-8'),timeout=5).json()
        j_data=json.loads(response['d'])['Films']

    
    for itt in j_data:
        
        imdb_id_from_ktuvit = extract_imdb_id_from_itt(itt)
        if imdb_id_from_ktuvit in imdb_id:
            f_id=itt['ID']
            
            break

    if f_id!='':
        url='https://www.ktuvit.me/MovieInfo.aspx?ID='+f_id
        
    else:
        
        return []
            
    if "tvshow" in item:
        if item["tvshow"]:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:81.0) Gecko/20100101 Firefox/81.0',
                'Accept': 'text/html, */*; q=0.01',
                'Accept-Language': 'en-US,en;q=0.5',
                'X-Requested-With': 'XMLHttpRequest',
                'Connection': 'keep-alive',
                'Referer': url,
                'Pragma': 'no-cache',
                'Cache-Control': 'no-cache',
                'TE': 'Trailers',
            }

            params = (
                ('moduleName', 'SubtitlesList'),
                ('SeriesID', f_id),
                ('Season', item["season"]),
                ('Episode', item["episode"]),
            )

            response = requests.get('https://www.ktuvit.me/Services/GetModuleAjax.ashx', headers=headers, params=params, cookies=login_cook).content
    else:
        headers = {
            'authority': 'www.ktuvit.me',
            'cache-control': 'max-age=0',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-user': '?1',
            'sec-fetch-dest': 'document',
            'referer': 'https://www.ktuvit.me/MovieInfo.aspx?ID='+f_id,
            'accept-language': 'en-US,en;q=0.9',
            
        }
        params = (
            ('ID', f_id),
        )
       
        response = requests.get('https://www.ktuvit.me/MovieInfo.aspx', headers=headers, params=params, cookies=login_cook).content
        
    
    regex='<tr>(.+?)</tr>'
    m_pre=re.compile(regex,re.DOTALL).findall(response.decode('utf-8'))

    subtitle=' '

    for itt in m_pre:
  
        regex='<div style="float.+?>(.+?)<br />.+?data-subtitle-id="(.+?)"'
        m=re.compile(regex,re.DOTALL).findall(itt)
        if len(m)==0:
            continue
        if ('i class' in m[0][0]):    #burekas fix for KT titles
            regex='כתובית מתוקנת\'></i>(.+?)$'
            n=re.compile(regex,re.DOTALL).findall(m[0][0])
            nm=n[0].replace('\n','').replace('\r','').replace('\t','').replace(' ','.').replace('................................................','')        
        else:
            nm=m[0][0].replace('\n','').replace('\r','').replace('\t','').replace(' ','.').replace('................................................','')        


        subtitle_list.append(nm)

    return subtitle_list
