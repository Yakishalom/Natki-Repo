# -*- coding: utf-8 -*-
'''
    EzScrapers Project
'''

import urllib,base64,json,random,requests,xbmcvfs,os,xbmc,logging,re,xbmcaddon,shutil,time
resuaddon=xbmcaddon.Addon('plugin.video.telemedia')
listen_port=resuaddon.getSetting('port')
base_header2={
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',

            'Pragma': 'no-cache',
            
           
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:59.0) Gecko/20100101 Firefox/59.0',
            }
headers = {
    'Accept': '*/*',
    'Accept-Language': 'he-IL,he;q=0.9,en-US;q=0.8,en;q=0.7',
    'Cache-Control': 'no-cache',
    'Connection': 'keep-alive',
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
   
    'DNT': '1',
    'Origin': 'https://www.moridimtv.net',
    'Pragma': 'no-cache',
    
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
    'X-Requested-With': 'XMLHttpRequest',
    'sec-ch-ua': '"Not A(Brand";v="99", "Google Chrome";v="121", "Chromium";v="121"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
}
def clear_files():
    db_path=os.path.join(xbmcvfs.translatePath("special://userdata/"),"addon_data","plugin.video.telemedia","files",'temp')

    if os.path.exists(db_path):
        onlyfiles = [f for f in os.listdir(db_path) if os.path.isfile(os.path.join(db_path, f))]
        
        for fl in onlyfiles:
            re_fl=os.path.join(db_path,fl)
            if os.path.exists(re_fl):
              try:
                os.remove(re_fl)
              except:pass
    db_path=os.path.join(xbmcvfs.translatePath("special://userdata/"),"addon_data","plugin.video.telemedia","files",'videos')

    if os.path.exists(db_path):
        onlyfiles = [f for f in os.listdir(db_path) if os.path.isfile(os.path.join(db_path, f))]
        for fl in onlyfiles:
            re_fl=os.path.join(db_path,fl)
            if os.path.exists(re_fl):
              try:
                os.remove(re_fl)
              except:pass


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
    def is_hebrew(self,input_str):    
           try:
            import unicodedata
            input_str=input_str.replace(' ','').replace('\n','').replace('\r','').replace('\t','').replace(' ','')
            nfkd_form = unicodedata.normalize('NFKD', input_str.replace(' ','').replace('\n','').replace('\r','').replace('\t','').replace(' ',''))
            a=False
            for cha in input_str:
                
                a='HEBREW' in unicodedata.name(cha.strip())
                if a:
                    break
            return a
           except:
                return True
    def search(self,tmdb,type,last_id_pre,search_entered_pre,icon_pre,fan_pre,season,episode,no_subs=0,original_title='',heb_name='',dont_return=True,manual=True):

        last_id=last_id_pre.split('$$$')[0]
        last_id_msg=last_id_pre.split('$$$')[1]
        f_lk=''
        f_size2=''
        query=search_entered_pre

        query=query.replace('%20',' ').replace('%27',"'").replace('%3a',":").replace('!','')
        
        filter_size=40*1024*1024# 100*1024*1024 סינון עד 100 מגה
        num=random.randint(1,10001)
        all_links=[]
        data={'type':'td_send',
             'info':json.dumps({'@type': 'searchMessages', 'query': query,'offset_message_id':last_id,'offset_chat_id':last_id_msg,'limit':1000, '@extra': num})
             }

        event=requests.post('http://127.0.0.1:%s/'%listen_port,json=data).json()
        if event==None:

            time.sleep(3)
            data={'type':'td_send',
             'info':json.dumps({'@type': 'searchMessages', 'query': query,'offset_message_id':last_id,'offset_chat_id':last_id_msg,'limit':100, '@extra': num})
             }

            event=requests.post('http://127.0.0.1:%s/'%listen_port,json=data).json()
        if 'messages' not in event:

            time.sleep(0.1)

            data={'type':'td_send',
             'info':json.dumps({'@type': 'searchMessages', 'query': query,'offset_message_id':last_id,'offset_chat_id':last_id_msg,'limit':100, '@extra': num})
             }

            event=requests.post('http://127.0.0.1:%s/'%listen_port,json=data).json()
        loc=''

        for items in event['messages']:  

            if 'document' in items['content']:
                name=items['content']['document']['file_name'].lower()
                if '.mkv' not in name and '.mp4' not in name and '.avi' not in name and '.flv' not in name and '.ts' not in name and '.mov' not in name and '.m4v' not in name and '.M4V' not in name:
                    continue
                size=items['content']['document']['document']['size']
                
                if size<filter_size:
                    continue
                f_size2=''
                f_size2=str(round(float(size)/(1024*1024*1024), 2))+' GB'
                q,loc=self.get_q(name)
                link_data={}
                link_data['id']=str(items['content']['document']['document']['remote']['id'])
                link_data['m_id']=items['id']
                link_data['c_id']=items['chat_id']
                f_lk=json.dumps(link_data)
                all_links.append((name, f_lk,3,q,loc, icon_pre,fan_pre,f_size2,no_subs,tmdb,season,episode,original_title))
                if 'caption' in items['content']:
                        # if size<filter_size:
                            # continue
                        name=items['content']['caption']['text'].replace('\n',' ')#.split('\n')
                        icon=icon_pre
                        fan=fan_pre
                        q,loc=self.get_q(name)
                        all_links.append(( name, f_lk,3,q,loc, icon_pre,fan_pre,f_size2,no_subs,tmdb,season,episode,original_title))
                        
                        
                        txt_lines=items['content']['caption']['text'].split('\n')
                        all_l=[]
                        name=txt_lines[0]
                        rem_lines=[]
                        
                        for lines in txt_lines:
                            if 'upfile' not in lines and 'drive.google' not in lines:
                              rem_lines.append(lines)
                              continue
                            all_l.append(lines)
                        # if len(all_l)==0:
                            # continue
                        # if size<filter_size:
                            # continue
                        q,loc=self.get_q(name)
                        all_links.append(( txt_lines[0], f_lk,3,q,loc, icon_pre,fan_pre,f_size2,no_subs,tmdb,season,episode,original_title))

            if 'video' in items['content']:
                    
                    name=items['content']['video']['file_name'].lower()

                    size=items['content']['video']['video']['size']
                    if size<filter_size:
                        continue
                    f_size2=''
                    f_size2=str(round(float(size)/(1024*1024*1024), 2))+' GB'
                    
                    q,loc=self.get_q(name)
                    link_data={}
                    link_data['id']=str(items['content']['video']['video']['remote']['id'])
                    link_data['m_id']=items['id']
                    link_data['c_id']=items['chat_id']
                    f_lk=json.dumps(link_data)
                    all_links.append(( name, f_lk,3,q,loc, icon_pre,fan_pre,f_size2,no_subs,tmdb,season,episode,original_title))


                    if 'caption' in items['content']:
                            # if size<filter_size:
                                # continue
                            name=items['content']['caption']['text'].replace('\n',' ')#.split('\n')
                            icon=icon_pre
                            fan=fan_pre
                            q,loc=self.get_q(name)
                            all_links.append(( name, f_lk,3,q,loc, icon_pre,fan_pre,f_size2,no_subs,tmdb,season,episode,original_title))
                            
                            
                            txt_lines=items['content']['caption']['text'].split('\n')
                            all_l=[]
                            name=txt_lines[0]
                            rem_lines=[]
                            
                            for lines in txt_lines:
                                if 'upfile' not in lines and 'drive.google' not in lines:
                                  rem_lines.append(lines)
                                  continue
                                all_l.append(lines)
                            # if len(all_l)==0:
                                # continue
                            # if size<filter_size:
                                # continue
                            q,loc=self.get_q(name)
                            all_links.append(( txt_lines[0], f_lk,3,q,loc, icon_pre,fan_pre,f_size2,no_subs,tmdb,season,episode,original_title))

                    
                    
                    

        return all_links
    def sources(self, data, hostDict):
        sources = []
        if not data: return sources
        append = sources.append



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
        original_title=title
        heb_name=name
        if not self.is_hebrew(str(heb_name)):
            try:
                data_moridimtv = {'q': original_title,'index': '0','limit': '10'}
                
                x = requests.post('https://www.moridimtv.net/ajax/search.php',  headers=headers, data=data_moridimtv,timeout=3).text
                regex='<h4>(.+?)</h4>'
                moridimtv=re.compile(regex).findall(x)
                
                if len(moridimtv)>0:
                    heb_name=moridimtv[0]
            except:pass

        o_name=name
        f_all_links=[]
        all_names=[]
        tv_movie='movie'
        id=''
        type='all'
        last_id_pre='0$$$0'
        count = 0
        exclude=[]

        if 'tvshowtitle' in data:
            re_search=False
            
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
            
            sep = ':'
            # heb_name = heb_name.split(sep, 1)[0]
            heb_name=heb_name.replace('ציידי הטרולים: סיפורי ארקדיה','ציידי הטרולים').replace('מיסטר בין: הסדרה המצוירת','מיסטר בין: הסדרה המצויירת').replace('היי סקול מיוזיקל: המחזמר הסדרה','היי סקול מיוזיקל')
            heb_name=heb_name.replace('...?','').replace('\u200f','').replace(':','').replace('%27',"'").replace('-'," ").replace("’","'")#.replace('"','') דופק סדרות מסויימות
            # original_title=original_title.split(sep, 1)[0]
            c_original=original_title.replace('%20','.').replace(' ','.').replace('%27',"'").replace('%3a',":").replace('...?',' ').replace('...',' ').replace('..',' ').replace(':','').replace("'",'')
            

            options=[heb_name+' ע%s פ%s'%(season,episode),heb_name+' ע%sפ%s'%(season,episode),heb_name+' עונה %s פרק %s'%(season,episode),heb_name+' S%sE%s'%(season_n,episode_n),c_original+'.S%sE%s'%(season_n,episode_n),c_original+'.S%sE%s'%(season,episode)]
            options2=[' ע%s פ%s'%(season,episode),'ע%s.פ%s'%(season,episode),' ע%sפ%s'%(season,episode),' עונה %s פרק %s'%(season,episode),'.S%sE%s'%(season_n,episode_n),'.S%sE%s'%(season,episode)]
            all_links=[]
            
            try:
                for items in options:
                    all_links=all_links+self.search(id,'all','0$$$0',items.replace(':',''),'','',season,episode,no_subs=1,original_title=original_title,heb_name=heb_name,dont_return=False,manual=False)
            except Exception as e:
                
                pass
                
            for  name, link,mode,q,loc, icon,fan,plot,no_subs,tmdb,season,episode,original_title in all_links:
                ok=False
                
                if base64.b64encode(name.encode("utf-8")).decode("utf-8") in all_names:
                    continue
                all_names.append(base64.b64encode(name.encode("utf-8")).decode("utf-8"))
                try:
                    xxxx=json.loads(link)
                    if xxxx['id'] in f_all_links:
                        continue
                except:pass

                o_name=heb_name
                # logging.warning('4343434343'+str(link))
                for items in options2:

                        t_items=items.replace('_','.').replace(' ','.').replace(':','').replace("'","").replace('-','.').replace('[','').replace(']','').replace('..','.').lower()
                        t_name=name.replace('_','.').replace('"',"").replace('  ',' ').lower().replace('-','.').replace(' ','.').replace('[','').replace(']','').replace('_','.').replace(':','').replace("'","").replace('..','.').replace('+',' ')
                        t_items2=c_original.replace('_','.').replace(' ','.').replace(':','').replace("'","").replace('-','.').replace('[','').replace(']','').replace('..','.').lower()
                        
                        if (t_items+'.'  in t_name+'.') or (t_items+' '  in t_name+' ') or (t_items+'_'  in t_name+'_') or (t_items.replace('.','_')+'_'  in t_name.replace('.','_')+'_') or (t_items.replace('.','-')+'_'  in t_name.replace('.','-')+'_'):
                           if (o_name in name.replace('_',' ').replace('.',' ')) or (t_items2 in t_name):
                            # if not self.is_hebrew(str(name)):
                                # re_search=True
                            ok=True
                            break
                           else:

                            ok=True
                            break
                            
                            
                if not ok:
                    
                    exclude.append((name, link,mode,q,loc, icon,fan,plot,no_subs,tmdb,season,episode,original_title))
                    
                else:
                    
                    if 'upfile' not in link and 'drive.google' not in link:
                    
                        plot=plot
                    else:
                        plot=plot
                    try:
                         o_size=plot
                         
                         plot=float(o_size.replace('GB','').replace('MB','').replace(",",'').strip())
                         if 'MB' in o_size:
                           plot=plot/1000
                    except Exception as e:
                        
                        plot=0
                        
                    if 'cd1' in name or 'cd2' in name or 'cd3' in name or 'cd4' in name or 'cd5' in name or  'חלק_1' in name or 'חלק_2' in name or 'חלק_3' in name or 'חלק_4' in name or 'חלק_5' in name or 'ח1' in name or 'ח2' in name or 'ח3' in name or 'ח4' in name or 'ח5' in name:
                           continue
                    name=name.replace('_','.')
                    if name == '':
                     continue

                    host='rapidgator.net'
                    name_info=name.replace('_','.')
                    info=plot
                    quality=q

                    url=link
                    try:
                        f_all_links.append(xxxx['id'])
                    except:pass
                    append({'provider': 'telemedia', 'source': host,'seeders': 0, 'name': name.replace('mp4','').replace('mkv','').replace('avi','').replace('900p',''), 'name_info':quality+' '+name_info, 'quality': quality, 'language': 'en', 'url': url,
                                    'info': info, 'direct': False, 'debridonly': None, 'size': plot})
                    count += 1
        else:

            all_links=[]
            season=''
            episode=''

            all_links=self.search(id,type,last_id_pre,heb_name,'','',season,episode,no_subs=0,original_title=original_title,dont_return=False,manual=False)
            
            all_links=all_links+self.search(id,'all','0$$$0',original_title,'','',season,episode,original_title=original_title,dont_return=False,manual=False)

            for  name, link,mode,q,loc, icon,fan,plot,no_subs,tmdb,season,episode,original_title in all_links:
                if base64.b64encode(name.encode("utf-8")).decode("utf-8") in all_names:
                    continue
                all_names.append(base64.b64encode(name.encode("utf-8")).decode("utf-8"))

                try:
                    xxxx=json.loads(link)
                    if xxxx['id'] in f_all_links:
                        continue
                except:pass
                
                try:
                     o_size=plot
                     plot=float(o_size.replace('GB','').replace('MB','').replace(",",'').strip())
                     if 'MB' in o_size:
                       plot=plot/1000
                except Exception as e:
                
                    plot=0
                    
                if 'cd1' in name or 'cd2' in name or 'cd3' in name or 'cd4' in name or 'cd5' in name or  'חלק_1' in name or 'חלק_2' in name or 'חלק_3' in name or 'חלק_4' in name or 'חלק_5' in name or 'ח1' in name or 'ח2' in name or 'ח3' in name or 'ח4' in name or 'ח5' in name:
                       continue
                name=name.replace('_','.')
                
                if name == '':
                 continue
                if name == 'ashley barbie - first bbc #bangbros 1080p.mp4':
                 continue
                
                regex='.*([1-3][0-9]{3})'
                year_pre=re.compile(regex).findall(name.replace(q,''))
                
                year_z=0
                
                if len(year_pre)>0:
                    year_z=year_pre[0]
                    
                    year_z=year_z.replace(q,'')
                    if year_z not in year:
                     continue
                     
                regex='e([0-9]+).'
                mmm=re.compile(regex).findall(name)
                if len(mmm)>0:
                    continue
                regex='עונה(.+?)פרק(.+?)'
                mmm=re.compile(regex).findall(name)

                if len(mmm)>0:
                    continue
                

                if not self.is_hebrew(str(name)):

                    if not original_title.replace(' ','.').replace(':','').lower() in name.replace('_','.').replace(' ','.').replace(q,'').replace(year,'').replace(':','').lower():

                        continue
                host='rapidgator.net'
                name_info=q+' '+name.replace('_','.').lower()
                info=plot
                quality=q
                url=link
                try:
                    f_all_links.append(xxxx['id'])
                except:pass
                append({'provider': 'telemedia', 'source': host,'seeders': 0 ,'name': name.replace('mp4','').replace('mkv','').replace('avi','').replace('900p',''), 'name_info': quality+' '+name_info, 'quality': quality, 'language': 'en', 'url': url,
                                'info': info, 'direct': False, 'debridonly': None, 'size': plot})
                count += 1
        return sources