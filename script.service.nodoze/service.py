from os import popen
import xbmc

ports = ['22', '8081', '8082', '8083', '8084', '9091']

if __name__ == '__main__':
    monitor = xbmc.Monitor()
 
    while not monitor.abortRequested():
        if monitor.waitForAbort(10):
            xbmc.executebuiltin('InhibitIdleShutdown(false)')
            break

        active = popen('netstat -tn | grep -E \'' + ''.join([':{} .*192.168.0.*ESTABLISHED|'.format(x) for x in ports]).rstrip('|') + '\'').read()

        if active:
            xbmc.executebuiltin('InhibitIdleShutdown(true)')
            xbmc.log('nodoze: Preventing sleep', level=xbmc.LOGDEBUG)
        else:
            xbmc.executebuiltin('InhibitIdleShutdown(false)')
            xbmc.log('nodoze: Not preventing sleep', level=xbmc.LOGDEBUG)
