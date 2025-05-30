import xbmcaddon,xbmc,os

def warning(msg):
    Addon = xbmcaddon.Addon()
    msg=str(msg)
    import inspect
    if Addon.getSetting('show_debug')=='true':
        callerframerecord = inspect.stack()[1] 
        frame = callerframerecord[0]
        info = inspect.getframeinfo(frame)
       
        xbmc.log('/*'+Addon.getAddonInfo('name')+'*/'+' Line: %s-> '%(str(info.lineno)+','+os.path.basename(info.filename))+msg,level=xbmc.LOGWARNING)
def error(msg):
    Addon = xbmcaddon.Addon()
    msg=str(msg)
    import inspect
    callerframerecord = inspect.stack()[1] 
    frame = callerframerecord[0]
    info = inspect.getframeinfo(frame)
    xbmc.log('/*'+Addon.getAddonInfo('name')+'*/'+',Error, Line: %s-> '%(str(info.lineno)+','+os.path.basename(info.filename))+str(msg),level=xbmc.LOGWARNING)