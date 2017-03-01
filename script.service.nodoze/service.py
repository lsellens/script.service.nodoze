from os import popen
import xbmc
import xbmcaddon
import xbmcvfs

__addon__ = xbmcaddon.Addon(id='script.service.nodoze')
__addonpath__ = xbmc.translatePath(__addon__.getAddonInfo('path'))
__addonhome__ = xbmc.translatePath(__addon__.getAddonInfo('profile'))
defaultsettings = xbmc.translatePath(__addonpath__ + '/settings-default.xml')
settings = xbmc.translatePath(__addonhome__ + 'settings.xml')

if not xbmcvfs.exists(settings):
    xbmcvfs.copy(defaultsettings, settings)

ports = __addon__.getSetting('PORTS')
ports = ports.replace(" ", "").split(",")
ipaddress = xbmc.getIPAddress()
# assumes you're on a class c network
ipaddresses = ipaddress.rsplit('.', 1)[0] + '.'
inhibit = False


class MyMonitor(xbmc.Monitor):
    def __init__(self, *args, **kwargs):
        xbmc.Monitor.__init__(self)
    
    def onSettingsChanged(self):
        global ports
        ports = __addon__.getSetting('PORTS')
        ports = ports.replace(" ", "").split(",")

if __name__ == '__main__':
    monitor = MyMonitor()
    
    while not monitor.abortRequested():
        if monitor.waitForAbort(60):
            xbmc.executebuiltin('InhibitIdleShutdown(false)')
            break
        active = popen('netstat -tn | grep -E \'' + ''.join(
            ['{0}:{1}.*{2}.*ESTABLISHED|'.format(ipaddress, x, ipaddresses) for x in ports]).rstrip('|') + '\'').read()

        if active:
            xbmc.executebuiltin('InhibitIdleShutdown(true)')
            inhibit = True
            xbmc.log('nodoze: Preventing sleep\n' + active, level=xbmc.LOGDEBUG)
        elif inhibit:
            xbmc.executebuiltin('InhibitIdleShutdown(false)')
            inhibit = False
            xbmc.log('nodoze: Not preventing sleep. No activity on ports ' + str(ports).strip("[]"), level=xbmc.LOGDEBUG)

