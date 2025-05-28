import xbmc,json,xbmcgui,xbmcvfs,sys,os,time
DIALOG         = xbmcgui.Dialog()
COLOR1         = 'gold'
COLOR2         = 'white'
icon = xbmcvfs.translatePath('special://home/addons/plugin.video.cobra/resources/media/cobra_icon.png')
def LogNotify(title, message, times=2000, icon=icon,sound=False):
	DIALOG.notification(title, message, icon, int(times), sound)
def ebi(proc):
	xbmc.executebuiltin(proc)
def IsAddonInstalled(addonid):
	return xbmc.getCondVisibility('System.HasAddon({0})'.format(addonid)) == 1

def InstallAddon(addonid):
	xbmc.executebuiltin('InstallAddon({0})'.format(addonid))

def IsAddonEnabled(addonid):

        return json.loads(xbmc.executeJSONRPC('{{"jsonrpc":"2.0","method":"Addons.GetAddonDetails","params":{{"addonid":"{0}", "properties": ["enabled"]}},"id":1}}'.format(addonid)))['result']['addon']['enabled']

def EnableAddon(addonid):
		
		xbmc.executeJSONRPC('{{"jsonrpc":"2.0","method":"Addons.SetAddonEnabled","params":{{"addonid":"{0}","enabled":true}},"id":1}}'.format(addonid))
def fix():
    ebi('UpdateAddonRepos()')
    ebi('UpdateLocalAddons()')
    xbmc.sleep(1000)
    EnableAddon('plugin.video.elementum')
    EnableAddon('script.elementum.burst')
    EnableAddon('script.module.kodi-six')
    LogNotify("[COLOR %s]%s[/COLOR]" % (COLOR1, 'Cobra'), "[COLOR %s]מוריד קבצי הפעלה...[/COLOR]" % COLOR2)
    # xbmc.sleep(2000)
    dp = xbmcgui.DialogProgress()
    dp.create("מוריד קבצי הפעלה", 
    "[COLOR yellow][B]Cobrea Torrent[/B][/COLOR]")
    dp.update(0)
    for s in range(15, -1, -1):
        time.sleep(1)
        dp.update(int((15 - s) / 15.0 * 100), "התוכן עולה"+'\n'+ 'בעוד {0} שניות'.format(s))
        if dp.iscanceled():
            dp.close
            break
    LogNotify("[COLOR %s]%s[/COLOR]" % (COLOR1, 'Cobra'), "[COLOR %s]הושלם[/COLOR]" % COLOR2)

def tord():
    LogNotify("[COLOR %s]%s[/COLOR]" % (COLOR1, 'Cobra'), "[COLOR %s]מוריד קבצים, אנא המתן...[/COLOR]" % COLOR2)
    import platform
    machine= (platform.machine())
    platform= (platform.architecture())
    if sys.platform.lower().startswith('linux'):
        plat = 'linux'
        if 'ANDROID_DATA' in os.environ:
            plat = 'android'
    elif sys.platform.lower().startswith('win'):
        plat = 'windows'
    elif sys.platform.lower().startswith('darwin'):
        plat = 'darwin'
    else:
        plat = None
    import xbmcvfs

    from urllib.request import urlopen
    from urllib.request import Request

    translatepath=xbmcvfs.translatePath
    HOME           = translatepath('special://home/')
    ADDONS         = os.path.join(HOME,     'addons')
    PACKAGES       = os.path.join(ADDONS,   'packages')
    from zipfile import ZipFile

    link= 'https://github.com/vip200/victory/blob/master/ele.zip?raw=true'
    iiI1iIiI = xbmcvfs.translatePath ( os . path . join ( 'special://home/addons' , 'packages' ) )
    OOooO = os . path . join ( PACKAGES , 'isr.zip' )
    req = Request(link)
    remote_file = urlopen(req)
    f = open(OOooO, 'wb')
    try:
      total_size = remote_file.info().getheader('Content-Length').strip()
      header = True
    except AttributeError:
          header = False # a response doesn't always include the "Content-Length" header
    if header:
          total_size = int(total_size)
    bytes_so_far = 0
    start_time=time.time()
    dp = xbmcgui . DialogProgress ( )
    dp.create('Please Wait...','Adding Groups')
    count=0
    while True:
          count+=1
          dp.update(count, 'Please Wait...' )
          buffer = remote_file.read(8192)
          
          if not buffer:
              sys.stdout.write('\n')
              
              break
          if dp.iscanceled():
                      dp.close()
                      break
          bytes_so_far += len(buffer)
          
          f.write(buffer)
    dp.close()
    II111iiii = xbmcvfs.translatePath ( os . path . join ( 'special://home/addons' ) )
    f.close()
    
    try:
        with contextlib.closing(ZipFile(OOooO , "r")) as z:
            z.extractall(II111iiii)
    except:
        with ZipFile(OOooO, 'r') as zip_ref:
            zip_ref.extractall(II111iiii)

    try:
      os.remove(OOooO)
    except:
      pass
###################################################
    burst_link= 'https://github.com/vip200/Build/blob/master/script.elementum.burst.zip?raw=true'
    iiI1iIiI = xbmcvfs.translatePath ( os . path . join ( 'special://home/addons' , 'packages' ) )
    OOooO = os . path . join ( PACKAGES , 'isr2.zip' )
    req = Request(burst_link)
    remote_file = urlopen(req)
    f = open(OOooO, 'wb')
    try:
      total_size = remote_file.info().getheader('Content-Length').strip()
      header = True
    except AttributeError:
          header = False # a response doesn't always include the "Content-Length" header
    if header:
          total_size = int(total_size)
    bytes_so_far = 0
    start_time=time.time()
    while True:
          LogNotify("[COLOR %s]%s[/COLOR]" % (COLOR1, 'Cobra'), "[COLOR %s]מוריד תוסף...[/COLOR]" % COLOR2)
          buffer = remote_file.read(8192)
          if not buffer:
              sys.stdout.write('\n')
              break

          bytes_so_far += len(buffer)
          f.write(buffer)

    II111iiii = xbmcvfs.translatePath ( os . path . join ( 'special://home/addons' ) )
    f.close()
    try:
        with contextlib.closing(ZipFile(OOooO , "r")) as z:
            z.extractall(II111iiii)
    except:
        with ZipFile(OOooO, 'r') as zip_ref:
            zip_ref.extractall(II111iiii)

    try:
      os.remove(OOooO)
    except:
      pass
#######################################
    burst_link= 'https://github.com/vip200/victory/raw/master/kodi-six.zip'
    iiI1iIiI = xbmcvfs.translatePath ( os . path . join ( 'special://home/addons' , 'packages' ) )
    OOooO = os . path . join ( PACKAGES , 'isr3.zip' )
    req = Request(burst_link)
    remote_file = urlopen(req)
    f = open(OOooO, 'wb')
    try:
      total_size = remote_file.info().getheader('Content-Length').strip()
      header = True
    except AttributeError:
          header = False # a response doesn't always include the "Content-Length" header
    if header:
          total_size = int(total_size)
    bytes_so_far = 0
    start_time=time.time()
    while True:
          LogNotify("[COLOR %s]%s[/COLOR]" % (COLOR1, 'Cobra'), "[COLOR %s]מוריד תוסף 2...[/COLOR]" % COLOR2)
          buffer = remote_file.read(8192)
          if not buffer:
              sys.stdout.write('\n')
              break

          bytes_so_far += len(buffer)
          f.write(buffer)

    II111iiii = xbmcvfs.translatePath ( os . path . join ( 'special://home/addons' ) )
    f.close()
    try:
        with contextlib.closing(ZipFile(OOooO , "r")) as z:
            z.extractall(II111iiii)
    except:
        with ZipFile(OOooO, 'r') as zip_ref:
            zip_ref.extractall(II111iiii)

    try:
      os.remove(OOooO)
    except:
      pass
    fix()
tord()