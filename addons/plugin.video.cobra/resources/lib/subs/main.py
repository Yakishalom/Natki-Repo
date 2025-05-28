from threading import Thread
import threading

class ThreadWithReturnValue(threading.Thread):
    def __init__(self, *init_args, **init_kwargs):
        threading.Thread.__init__(self, *init_args, **init_kwargs)
        self._return = None
    def run(self):
        self._return = self._target(*self._args, **self._kwargs)
    def join(self):
        threading.Thread.join(self)
        return self._return
def get_links(tv_movie,original_title,name,season,episode,year,id):
    item={}
    if tv_movie=='movie':
      item["movie"]=original_title.replace("%20"," ").replace("%27","'")
      item["media_type"]='movie'
    else:
      item["tvshow"]=original_title.replace("%20"," ").replace("%27","'")
      item["media_type"]='tv'




    item['title']=original_title.replace("%20"," ").replace("%27","'")
  
    item["season"]=season
    item["episode"]=episode
    item["year"]=year
    item["imdb"]=id


    wizdom=[]
    ktuvit=[]
    telesubs=[]
    from subs.ktuvit import ktuvit_Search
    from subs.wizdom import wizdom_Search
    from subs.telesubs import get_subs



    # start_wizdom = ThreadWithReturnValue(target=wizdom_Search, args=(id,season,episode,))
    # start_ktuvit = ThreadWithReturnValue(target=ktuvit_Search, args=(item,id,))
    # start_tele_subs = ThreadWithReturnValue(target=get_subs, args=(item,))
    
    
    
    # start_wizdom.start()
    # start_ktuvit.start()
    # start_tele_subs.start()
    

    # wizdom=start_wizdom.join()
    # ktuvit=start_ktuvit.join()
    # telesubs=start_tele_subs.join()
    import xbmc
    
    try:
        wizdom=(wizdom_Search(id,season,episode))
    except Exception as e:
        pass
    
    # try:
        # ktuvit=ktuvit_Search(item,id)
    # except Exception as e:
        # pass
        
    try:
        telesubs=get_subs(item)
    except Exception as e:
        pass
    
    all_subs=wizdom+telesubs

    return all_subs