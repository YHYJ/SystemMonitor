import socket
import yaml
import logger

class UDPclient:
    udpsendclient = None
    udpmulticlient = None
    bindaddr = '0.0.0.0'
    desip = '224.0.0.50'
    port = 9898
    
    
    def __init__(self):
        '''
        初始化，从配置文件读取相关UDP参数
        '''
        try:
            # 读取配置文件
            f = open("config.yaml","r+",encoding="utf-8")
            fstream = f.read()
            configobj = yaml.safe_load(fstream)
            self.bindaddr = configobj['udp']['bindaddr']
            self.desip =configobj['udp']['desip']
            self.port = configobj['udp']['port']
            # print(configobj)
        except Exception as e:
            logger.writeLog("UDP组件初始化失败" + str(e),'udp.log')

    # 生成udp发送客户端
    def genUDPClient(self):
        self.udpsendclient = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        self.udpsendclient.setblocking(False)  # 设置为非阻塞模式
        return self.udpsendclient

    # 生成组播客户端
    def genMulitiUDP(self):
        # 创建UDP socket
        self.udpmulticlient = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        # 允许端口复用
        self.udpmulticlient.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # 绑定监听多播数据包的端口
        self.udpmulticlient.bind((self.bindaddr, self.port))
        # 声明该socket为多播类型
        self.udpmulticlient.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 255)
        # 加入多播组，组地址由第三个参数制定
        self.udpmulticlient.setsockopt(
            socket.IPPROTO_IP,
            socket.IP_ADD_MEMBERSHIP,
            socket.inet_aton(self.desip) + socket.inet_aton(self.bindaddr)
        )
        self.udpmulticlient.setblocking(False)
        return self.udpmulticlient