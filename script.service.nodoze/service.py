import xbmc
import xbmcaddon

__addon__ = xbmcaddon.Addon(id='script.service.nodoze')
__scriptname__ = "nodoze"
__author__ = "lsellens"
__url__ = "https://github.com/lsellens/xbmc.addons"
__addonpath__ = xbmc.translatePath(__addon__.getAddonInfo('path'))
__addonhome__ = xbmc.translatePath(__addon__.getAddonInfo('profile'))
ports = __addon__.getSetting('PORTS')
ports = ports.replace(" ", "").split(",")
ipaddress = xbmc.getIPAddress()
inhibit = False
xbmc.log('nodoze: Monitoring port(s) ' + str(ports).strip("[]"), level=xbmc.LOGDEBUG)


class MyMonitor(xbmc.Monitor):
    def __init__(self, *args, **kwargs):
        xbmc.Monitor.__init__(self)
    
    def onSettingsChanged(self):
        global ports
        ports = __addon__.getSetting('PORTS')
        ports = ports.replace(" ", "").split(",")
        xbmc.log('nodoze: Settings Changed. Monitoring port(s) ' + str(ports).strip("[]"), level=xbmc.LOGDEBUG)


def read_proc():
    with open("/proc/net/tcp", 'r') as f:
        content = f.readlines()
        content.pop(0)
    return content


def convert_hex(array):
    ip, port = array.split(':')
    ip = '.'.join(str(int(i, 16)) for i in reversed([ip[i:i+2] for i in range(0, len(ip), 2)]))
    port = str(int(port, 16))
    return ip, port


def tcp_port_connection():
    tcpcontent = read_proc()
    connected_ports = []
    for line in tcpcontent:
        line_array = [x for x in line.split(' ') if x !='']
        local_ip, local_port = convert_hex(line_array[1])
        remote_ip, remote_port = convert_hex(line_array[2])
        state = line_array[3]
        if local_ip == ipaddress and state == '01' and local_port in ports:
            nline = '{0} is connected to port {1}'.format(remote_ip, local_port)
            if nline not in connected_ports:
                connected_ports.append(nline)
    return connected_ports


if __name__ == '__main__':
    monitor = MyMonitor()
    
    while not monitor.abortRequested():
        if monitor.waitForAbort(60):
            xbmc.executebuiltin('InhibitIdleShutdown(false)')
            break
        
        active = tcp_port_connection()
        
        if active:
            xbmc.executebuiltin('InhibitIdleShutdown(true)')
            inhibit = True
            xbmc.log('nodoze: Preventing sleep', level=xbmc.LOGDEBUG)
            for line in active:
                xbmc.log('nodoze: ' + line, level=xbmc.LOGDEBUG)
        elif inhibit:
            xbmc.executebuiltin('InhibitIdleShutdown(false)')
            inhibit = False
            xbmc.log('nodoze: Not preventing sleep. No activity on ports ' + str(ports).strip("[]"), level=xbmc.LOGDEBUG)

