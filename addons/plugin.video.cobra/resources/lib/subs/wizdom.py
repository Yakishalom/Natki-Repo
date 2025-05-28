# -*- coding: utf-8 -*-

import requests,json,logging

def wizdom_Search(imdb,season=0,episode=0):


    filename = 'wizdom.imdb.%s.%s.%s.json'%(imdb,season,episode)
    url = "http://wizdom.xyz/api/search?action=by_id&imdb=%s&season=%s&episode=%s" % (imdb, season, episode)

    try:
      x=requests.get(url).json()
    except:
      x={}
      pass
    json_object = x
    
    subtitle_list=[]

    if json_object!=0:
        for item_data in json_object:

            
            if "id" not in item_data:
                continue
            if item_data["versioname"] in subtitle_list:
                continue
            subtitle_list.append(item_data["versioname"])


        return subtitle_list
    else:
        return subtitle_list
