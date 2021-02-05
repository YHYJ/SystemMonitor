import psutil
import yaml
import logger
import copy

class SysMonitor:
    platform = 'linux' #平台/部分参数 windows及 linux不同
    isopen = True
    pubtopic = 'monitor'
    interval = 120
    devid = ''
    devname = ''
    pubcontent = {
        "devid":'',
        "devname":'',
        "cpu":0,
        "disk":{},
        "virtualmemory":{},
        "swapmemory":{},
        "nic":[]
    }
    
    def __init__(self):
        '''
        初始化，从配置文件读取参数
        '''
        try:
            # 读取配置文件
            f = open("config.yaml","r+",encoding="utf-8")
            fstream = f.read()
            configobj = yaml.safe_load(fstream)
            self.platform = configobj['monitor']['platform']
            self.isopen =configobj['monitor']['isopen']
            self.pubtopic = configobj['monitor']['pubtopic']
            self.interval = configobj['monitor']['interval']
            self.devid = configobj['monitor']['devid']
            self.devname = configobj['monitor']['devname']
        except Exception as e:
            logger.writeLog("Monitor组件初始化失败" + str(e))
    
    #获取CPU总使用率    
    def getCpu(self):
        return psutil.cpu_percent(0)
    
    #获取整个硬盘使用情况(GB)  sdiskusage(total=21378641920, used=4809781248, free=15482871808, percent=22.5)
    def getDisk(self):
        diskusage = {"total":0,
                     "used":0,
                     "free":0,
                     "percent":0
                    }
        getinfo = psutil.disk_usage('/')
        diskusage['total'] = round(getinfo[0] / 1024 / 1024 / 1024, 2)
        diskusage['used'] = round(getinfo[1] / 1024 / 1024 / 1024, 2)
        diskusage['free'] = round(getinfo[2] / 1024 / 1024 / 1024, 2)
        diskusage['percent'] =round(getinfo[3],2)
        return diskusage
    
    #获取虚拟内存情况 MB
    # svmem(total=10367352832, available=6472179712, percent=37.6, used=8186245120,
    #       free=2181107712, active=4748992512, inactive=2758115328, buffers=790724608, 
    #      cached=3500347392, shared=787554304)
    def getVirtualMemory(self):
        vmemory = {
            "total": 0,
            "available": 0,
            "percent": 0,
            "used": 0,
            "free": 0,
            "active": 0,
            "inactive": 0,
            "buffers": 0,
            "cached": 0,
            "shared": 0,
            "slab": 0,
        }
        getinfo =  psutil.virtual_memory()
        
        if self.platform == 'linux':
            vmemory['total'] = round(getinfo[0]/1024/1024,2)
            vmemory['available'] = round(getinfo[1]/1024/1024,2)
            vmemory['percent'] = round(getinfo[2],2)
            vmemory['used'] = round(getinfo[3]/1024/1024,2)
            vmemory['free'] = round(getinfo[4]/1024/1024,2)
            vmemory['active'] = round(getinfo[5]/1024/1024,2)
            vmemory['inactive'] = round(getinfo[6]/1024/1024,2)
            vmemory['buffers'] = round(getinfo[7]/1024/1024,2)
            vmemory['cached'] = round(getinfo[8]/1024/1024,2)
            vmemory['shared'] = round(getinfo[9]/1024/1024,2)
            vmemory['slab'] = round(getinfo[10]/1024/1024,2)
        elif self.platform == 'windows':
            vmemory['total'] = round(getinfo[0]/1024/1024,2)
            vmemory['available'] = round(getinfo[1]/1024/1024,2)
            vmemory['percent'] = round(getinfo[2],2)
            vmemory['used'] = round(getinfo[3]/1024/1024,2)
            vmemory['free'] = round(getinfo[4]/1024/1024,2)
        
        return vmemory
        

    
    #获取交换分区情况 MB
    # sswap(total=2097147904, used=296128512, free=1801019392, 
    #       percent=14.1, sin=304193536, sout=677842944)
    def getSwapMemory(self):
        smemory = {
            "total": 0,
            "used": 0,
            "free": 0,
            "percent": 0,
            "sin": 0,
            "sout": 0
        }
        getinfo = psutil.swap_memory()
        smemory['total'] = round(getinfo[0]/1024/1024,2)
        smemory['used'] = round(getinfo[1]/1024/1024,2)
        smemory['free'] = round(getinfo[2]/1024/1024,2)
        smemory['percent'] = round(getinfo[3]/1024/1024,2)
        smemory['sin'] = round(getinfo[4]/1024/1024,2)
        smemory['sout'] = round(getinfo[5]/1024/1024,2)
        return smemory

    #获取网卡详情及IP地址
    '''
    {'lo': [snicaddr(family=<AddressFamily.AF_INET: 2>, address='127.0.0.1', netmask='255.0.0.0', broadcast='127.0.0.1', ptp=None),
        snicaddr(family=<AddressFamily.AF_INET6: 10>, address='::1', netmask='ffff:ffff:ffff:ffff:ffff:ffff:ffff:ffff', broadcast=None, ptp=None),
        snicaddr(family=<AddressFamily.AF_LINK: 17>, address='00:00:00:00:00:00', netmask=None, broadcast='00:00:00:00:00:00', ptp=None)],
     'wlan0': [snicaddr(family=<AddressFamily.AF_INET: 2>, address='192.168.1.3', netmask='255.255.255.0', broadcast='192.168.1.255', ptp=None),
           snicaddr(family=<AddressFamily.AF_INET6: 10>, address='fe80::c685:8ff:fe45:641%wlan0', netmask='ffff:ffff:ffff:ffff::', broadcast=None, ptp=None),
           snicaddr(family=<AddressFamily.AF_LINK: 17>, address='c4:85:08:45:06:41', netmask=None, broadcast='ff:ff:ff:ff:ff:ff', ptp=None)]}
    '''
    def getIfconfig(self):
        lista = []
        tempobj = {"name":"","macaddr":"","ipaddr":"", "netmask":""}
        getinfo = psutil.net_if_addrs()
        if self.platform == 'windows':
            for item in getinfo.items():
                if len(item[1]) > 1:
                    tempobj['name'] = item[0]
                    tempobj['macaddr'] = item[1][0][1]
                    tempobj['ipaddr'] = item[1][1][1]
                    tempobj['netmask'] = item[1][1][2]
                elif len(item[1]) == 1:
                    tempobj['name'] = item[0]
                    tempobj['macaddr'] = item[1][0][1]
                    tempobj['ipaddr'] = ''
                    tempobj['netmask'] = item[1][0][2]
                lista.append(copy.deepcopy(tempobj))
        if self.platform == 'linux':
            for item in getinfo.items():
                if len(item[1]) > 1:
                    tempobj['name'] = item[0]
                    tempobj['macaddr'] = item[1][1][1]
                    tempobj['ipaddr'] = item[1][0][1]
                    tempobj['netmask'] = item[1][1][2]
                elif len(item[1]) == 1:
                    tempobj['name'] = item[0]
                    tempobj['macaddr'] = item[1][0][1]
                    tempobj['ipaddr'] = ''
                    tempobj['netmask'] = item[1][0][2]
                lista.append(copy.deepcopy(tempobj))
        return lista

    def genSystemInfo(self):
        self.pubcontent['devid'] = self.devid
        self.pubcontent['devname'] = self.devname
        self.pubcontent['cpu'] = self.getCpu()
        self.pubcontent['disk'] = self.getDisk()
        self.pubcontent['virtualmemory'] = self.getVirtualMemory()
        self.pubcontent['swapmemory'] = self.getSwapMemory()
        self.pubcontent['nic'] = self.getIfconfig()
        return self.pubcontent