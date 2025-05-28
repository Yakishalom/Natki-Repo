# -*- coding: utf-8 -*-
import base64,json,xbmcvfs,zlib
class source:
    priority = 1
    pack_capable = False
    hasMovies = True
    hasEpisodes = True
    def __init__(self):
        self.language = ['en']
    def script (self,urlpin ):
        urlpin =urlpin .replace ('99999****','')
        import gzip 
        import io
        pin =StringIO .StringIO ()
        pin .write (urlpin .decode ('base64'))
        pin .seek (0 )
        rtx =gzip .GzipFile (fileobj =pin ,mode ='rb').read ()
        qqqq =rtx .split ("$$$$$")
        pin =StringIO .StringIO ()
        pin .write (qqqq [0 ].decode ('base64'))#line:46
        pin .seek (0 )
        rtx =gzip .GzipFile (fileobj =pin ,mode ='rb').read ()#line:52
        return rtx 
    def gdecom(self,url):
        url =url .replace ('99999****','')#line:225
        if '$$$$$' in url:
            url =url .split ("$$$$$")[0]#line:236
        data = url
        json_str = zlib.decompress(base64.b64decode(data), 16 + zlib.MAX_WBITS).decode('utf-8')
        if '$$$$$' in json_str:
            json_str =json_str .split ("$$$$$")[0]#line:236
        try:
            decoded = zlib.decompress(base64.b64decode(json_str), 16 + zlib.MAX_WBITS).decode('utf-8')
        except Exception as e:
            decoded=json_str
        return decoded #line:253
    def sources(self, data, hostDict):
        sources = []
        if not data: return sources
        append = sources.append
        from sqlite3 import dbapi2 as database
        dataDir_vip =(xbmcvfs.translatePath("special://userdata/addon_data/") + 'plugin.video.cobra/data/localfile.txt')
        dataDir_vipc =(xbmcvfs.translatePath("special://userdata/addon_data/") + 'plugin.video.cobra/data/localfile_c.txt')

        dat=[dataDir_vip,dataDir_vipc]
        for i in dat:
            dbcon = database.connect(i)
            dbcur = dbcon.cursor()

            title = data['tvshowtitle'] if 'tvshowtitle' in data else data['title']
            year = data['year']
            id=''#data['tmdb']
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
            
            if 'tvshowtitle' in data:
                dbcur.execute("SELECT * FROM MyTable where father like  '%{0}%' and father like '%{1}%'".format(named,'עונה '+season))
            else:
                dbcur.execute("SELECT * FROM MyTable where name like '%{0}%' and year ='{1}' ".format(named,year))
            match = dbcur.fetchall()
            if len(match)==0 and 'tvshowtitle' in data:
                dbcur.execute("SELECT * FROM MyTable where data like  '%\"tmdb\": \"{0}\"%' and data like '%\"Season\": \"{1}\",  \"Episode\": \"{2}\",%'".format(data['imdb'],season,episode))
                match = dbcur.fetchall()

            for index,name,f_link,icon,fanart,plot,data,date,year,genre,father,type in match:
                try:
                    f_link=self.gdecom(f_link)
                except:
                   pass
                try:
                        data=json.loads(data)
                except:
                        data={'originaltitle':name,'Season':'%20','Episode':'%20'}
                if 'tvshowtitle' in data:
                    if not ((data['Season'].strip()==season and data['Episode'].strip()==episode) or (('עונה#%s#פרק#%s"'%(season,episode)).decode('utf8') in name.replace(' ','#'))):
                        continue
                f_link=f_link.replace('\n',"").replace('\r',"")
                if '$$$' in f_link:
                    f_link_s=f_link.split('$$$')
                    for link_in in f_link_s:
                        size=10
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
                        if 'tvshowtitle' in data:
                            name1=title.replace('FHD','1080').replace('HD','720')+'.S%sE%s'%(season_n,episode_n)
                        else:
                            name1=title.replace('FHD','1080').replace('HD','720')+'.'+year
                        append({'provider': 'vip', 'source': 'vip','seeders': 10000, 'name': name, 'name_info': res, 'quality': res, 'language': 'en', 'url': link_in,
                                    'info': '', 'direct': False, 'debridonly': False, 'size': size})
                        count += 1
                    return sources
                else:
                    size=10
                    if 'tvshowtitle' in data:
                        name1=title.replace('FHD','1080').replace('HD','720')+'.S%sE%s'%(season_n,episode_n)
                    else:
                        name1=title.replace('FHD','1080').replace('HD','720')+'.'+year
                    if "2060" in f_link:
                      res="2060p"
                    elif "1080" in f_link:
                      res="1080p"
                    elif "720" in f_link:
                      res="720p"
                    elif "480" in f_link:
                       res="480p"
                    else:
                        res='1080p'
                    append({'provider': 'vip', 'source': 'vivo.st','seeders': 10000, 'name': name.replace('ישראלי','').replace('מדובב','').replace(')','').replace('(',''), 'name_info': f_link, 'quality': res, 'language': 'en', 'url': f_link,
                                'info': '', 'direct': False, 'debridonly': False, 'size': size})
                    count += 1
        return sources
