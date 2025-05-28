# -*- coding: utf-8 -*-
import sys
import time,xbmc

# from  resources.modules import cache
global global_var,stop_all#global
global_var=[]
stop_all=0

import re,requests

type=['tv','movie']

import urllib,base64,json,logging

import zlib
BASE_URL = "http://www.cinemast.org/he/cinemast/api/"

class URLHandler():
    def __init__(self):
        self.opener = urllib2.build_opener()
        self.opener.addheaders = [('Accept-Encoding', 'gzip'),
                                  ('Accept-Language', 'en-us,en;q=0.5'),
                                  ('Pragma', 'no-cache'),
                                  ('Cache-Control', 'no-cache'),
                                  ('User-Agent',
                                   'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 Kodi/17.2 (KHTML, like Gecko) Chrome/49.0.2526.111 Safari/537.36')]

    def request(self, url, data=None, query_string=None, ajax=False, referrer=None, cookie=None):
        if data is not None:
            data = urllib.urlencode(data)
        if query_string is not None:
            url += '?' + urllib.urlencode(query_string)
        if ajax:
            self.opener.addheaders += [('X-Requested-With', 'XMLHttpRequest')]
        if referrer is not None:
            self.opener.addheaders += [('Referrer', referrer)]
        if cookie is not None:
            self.opener.addheaders += [('Cookie', cookie)]

        content = None
  
        #if data is not None and 'password' not in data:
        #    logging.warning("Post Data: %s" % (data))
        try:
            response = self.opener.open(url, data,timeout=5)
            content = None if response.code != 200 else response.read()

            if response.headers.get('content-encoding', '') == 'gzip':
                try:
                    content = zlib.decompress(content, 16 + zlib.MAX_WBITS)
                except zlib.error:
                    pass

            if response.headers.get('content-type', '') == 'application/json':
                content = json.loads(content, encoding="utf-8")

            response.close()
        except Exception as e:
            pass
            # Second parameter is the filename
        return content

def login( notify_success=True):
        
        urlHandler = URLHandler()
        email = Addon.getSetting("Email")
        password = Addon.getSetting("Password")
        if email=='' or password=='':
          __settings__.openSettings()
          email = Addon.getSetting("Email")
          password = Addon.getSetting("Password")
        post_data = {'username': email, 'password': password}
        content = urlHandler.request(BASE_URL + "login/", post_data)

        if content['result'] == 'success':
            if notify_success:
                notify(32010)

            del content["result"]
            return content
        else:
            notify(32009)
            return None
def get_user_token( force_update=False):
        # results =cache.get(login, 24, False, table='pages')
        results =login(False)
        '''
        if force_update:
            store.delete('credentials')
        
        results = store.get('credentials')
        if results:
            results = json.loads(results)
        else:
            results = login(False)
            if results:
                store.set('credentials', json.dumps(results))
        '''
        return results
def subcenter_search(item,mode_subtitle,subtitle_list,check_one):
        import re
        results = []
        
        id_collection=[]
    
        search_string = re.split(r'\s\(\w+\)$', item["tvshow"])[0] if item["tvshow"] else item["title"]

        
        user_token =  get_user_token()
        
        if user_token:
            query = {"q": search_string.encode("utf-8"), "user": user_token["user"], "token": user_token["token"]}
            if item["tvshow"]:
                query["type"] = "series"
                query["season"] = item["season"]
                query["episode"] = item["episode"]
            else:
                query["type"] = "movies"
                if item["year"]:
                    query["year_start"] = int(item["year"]) 
                    query["year_end"] = int(item["year"])

            search_result =  urlHandler.request( BASE_URL + "search/", query)
   
            if search_result is not None and search_result["result"] == "failed":
                # Update cached token
                user_token =  get_user_token(True)
                query["token"] = user_token["token"]
                search_result =  urlHandler.request( BASE_URL + "search/", query)

            if search_result is not None and search_result["result"] == "failed":
                #xbmc.executebuiltin((u'Notification(%s,%s)' % ('טייפון', 'בעיה בנתוני התחברות')).encode('utf-8'))
  
                return results



            if search_result is None or search_result["result"] != "success" or search_result["count"] < 1:
                
                    return results

            results = search_result# _filter_results(search_result["data"], search_string, item)

        ret = []
        ok=True
        lang=[]
        lang.append('he')
        results2=[]
      
        for result in results['data']:
            total_downloads = 0
            counter = 0
            
            subs_list = result
            
              
            if subs_list is not None:
               

                for language in subs_list['subtitles']:
                        
                        
                       if language in lang:
                    #if xbmc.convertLanguage(language, xbmc.ISO_639_2) in item["3let_language"]:
                        for current in subs_list['subtitles'][language]:
                          title = current["version"]
                          if title not in subtitle_list:
                            counter += 1
                            
                            subtitle_list.append(title)
                            if check_one==True:
                              break
        return subtitle_list
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
def FirstPlace_Search(item,imdb_id,subtitle_list,check_one=False):
    global links_first

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
    
    if 1:
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
        z=0
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
            data='{"request":{"FilmID":"%s","SubtitleID":"%s","FontSize":0,"FontColor":"","PredefinedLayout":-1}}'%(f_id,m[0][1])

            subtitle_list.append(nm)
            if check_one==True:
                   break
            links_first=subtitle_list
           
            z=z+1
    
    return subtitle_list
    

def Caching(filename,url):
    

    try:
      x=requests.get(url).json()
    except:
      x={}
      pass
    return x
def GetJson(imdb,mode_subtitle,season=0,episode=0,version=0,check_one=False,global_var=[]):
    global links_wizdom

    filename = 'wizdom.imdb.%s.%s.%s.json'%(imdb,season,episode)
    url = "http://wizdom.xyz/api/search?action=by_id&imdb=%s&season=%s&episode=%s&version=%s"%(imdb,season,episode,version)
    
    # logging.warning(url)
    
    json_object = Caching(filename,url)
    
    # logging.warning('json_object:'+ str(json_object))
    
    subs_rate = []
    subtitle=' '
    x=0
    id_all_collection=[]
    subtitle_list=global_var
    
    if json_object!=0:
        for item_data in json_object:
       

            if "id" not in item_data:
                continue
            if item_data["id"] not in id_all_collection:
                id_all_collection.append(item_data["id"])
                if item_data["versioname"] in subtitle_list:
                    continue
                subtitle_list.append(item_data["versioname"])

                if check_one==True:
                              break
                links_wizdom=subtitle_list
                x=x+1

    if (json_object)==0:
      return 0,' ',subtitle_list
    else:
        
      return subtitle_list

