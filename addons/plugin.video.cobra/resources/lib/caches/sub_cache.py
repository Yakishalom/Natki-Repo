# -*- coding: utf-8 -*-

'''
    Genesis Add-on
    Copyright (C) 2015 lambda

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''


import re,hashlib,time,os,xbmcvfs,xbmc,logging,xbmcaddon
translatepath=xbmcvfs.translatePath
from sqlite3 import dbapi2 as database


def set_PRAGMAS( dbcon):
        dbcur = dbcon.cursor()
        dbcur.execute('''PRAGMA synchronous = OFF''')
        dbcur.execute('''PRAGMA journal_mode = OFF''')
        return dbcur
def get(function, timeout, *args, **table):
    import linecache,sys
    try:
        response = None

        f = repr(function)
        f = re.sub('.+\smethod\s|.+function\s|\sat\s.+|\sof\s.+', '', f)

        a = hashlib.md5()
        for i in args: a.update(str(i).encode('utf-8'))
        a = str(a.hexdigest())
    except Exception as e:
      
      exc_type, exc_obj, tb = sys.exc_info()
      fail = tb.tb_frame
      lineno = tb.tb_lineno
      filename = fail.f_code.co_filename
      linecache.checkcache(filename)
      line = linecache.getline(filename, lineno, fail.f_globals)
      
      logging.warning('CACHE err:'+str(lineno))
      logging.warning('inline:'+line)
      logging.warning(e)
      
     
    
      
      pass
    
  
    try:
        table = table['table']
    except:
        table = 'rel_list'

    try:
        try:
            import xbmc
            addonInfo = xbmcaddon.Addon().getAddonInfo
            dataPath = translatepath(addonInfo('profile'))
        except:
           
            dataPath = os.path.dirname(os.path.realpath(__file__))
        mypath=os.path.join(dataPath,'cache_f')
        if not os.path.exists(mypath):
          os.mkdir(mypath)
    
           
        dbcon = database.connect(os.path.join(mypath,'sources.db'))
        dbcur = set_PRAGMAS(dbcon)
        dbcur = dbcon.cursor()
        dbcur.execute("SELECT count(*) FROM sqlite_master WHERE type='table' AND name='%s';"%table)
        match = dbcur.fetchone()

        if match[0]!=0:
        
            dbcur.execute("SELECT * FROM %s WHERE func = '%s' AND args = '%s'" % (table, f, a))
            match = dbcur.fetchone()
            if match!=None:
                response = eval(match[2].encode('utf-8'))

                t1 = int(match[3])
                t2 = int(time.time())
                update = (abs(t2 - t1) / 3600) >= int(timeout)
                if update == False:
                    return response
    
    except Exception as e:
        exc_type, exc_obj, tb = sys.exc_info()
        fail = tb.tb_frame
        lineno = tb.tb_lineno
        filename = fail.f_code.co_filename
        linecache.checkcache(filename)
        line = linecache.getline(filename, lineno, fail.f_globals)
      
        logging.warning('CACHE2 err:'+str(lineno))
        logging.warning('inline:'+line)
        logging.warning(e)
        
        pass
    
    try:
        r = function(*args)
        if (r == None or r == []) and not response == None:
            
            return response
        elif (r == None or r == []):
            
            return r
    except Exception as e:
        exc_type, exc_obj, tb = sys.exc_info()
        fail = tb.tb_frame
        lineno = tb.tb_lineno
        filename = fail.f_code.co_filename
        linecache.checkcache(filename)
        line = linecache.getline(filename, lineno, fail.f_globals)
      
        logging.warning('CACHE3 err:'+str(lineno))
        logging.warning('inline:'+line)
        logging.warning(e)
        return

    try:
        r = repr(r)
        t = int(time.time())
      
        dbcur.execute("CREATE TABLE IF NOT EXISTS %s (""func TEXT, ""args TEXT, ""response TEXT, ""added TEXT, ""UNIQUE(func, args)"");" % table)
        dbcur.execute("DELETE FROM %s WHERE func = '%s' AND args = '%s'" % (table, f, a))
        dbcur.execute("INSERT INTO %s Values (?, ?, ?, ?)" % table, (f, a, r, t))
        dbcon.commit()
    except Exception as e:
        exc_type, exc_obj, tb = sys.exc_info()
        fail = tb.tb_frame
        lineno = tb.tb_lineno
        filename = fail.f_code.co_filename
        linecache.checkcache(filename)
        line = linecache.getline(filename, lineno, fail.f_globals)
      
        logging.warning('CACHE4 err:'+str(lineno))
        logging.warning('inline:'+line)
        logging.warning(e)
        pass

    try:
        return eval(r.encode('utf-8'))
    except Exception as e:
        exc_type, exc_obj, tb = sys.exc_info()
        fail = tb.tb_frame
        lineno = tb.tb_lineno
        filename = fail.f_code.co_filename
        linecache.checkcache(filename)
        line = linecache.getline(filename, lineno, fail.f_globals)
      
        logging.warning('CACHE5 err:'+str(lineno))
        logging.warning('inline:'+line)
        logging.warning(e)
        pass


def clear(table=None):
    try:
        

        if table == None: table = ['rel_list']
        elif not type(table) == list: table = [table]
        try:
            import xbmc
            addonInfo = xbmcaddon.Addon().getAddonInfo
            dataPath = translatepath(addonInfo('profile'))
        except:
            dataPath = os.path.dirname(os.path.realpath(__file__))
       
        mypath=os.path.join(dataPath,'cache_f')
        if not os.path.exists(mypath):
          os.mkdir(mypath)
        dbcon = database.connect(os.path.join(mypath,'sources.db'))
        dbcur = dbcon.cursor()

        for t in table:
            try:
                dbcur.execute("DROP TABLE IF EXISTS %s" % t)
                dbcur.execute("VACUUM")
                dbcon.commit()
            except:
                pass
    except Exception as e:
        logging.warning('Error cleaning: '+str(e))
        
        pass

