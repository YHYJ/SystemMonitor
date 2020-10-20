from Crypto.Cipher import AES
from binascii import b2a_hex, a2b_hex
import yaml
import logger

class AqaraEncrypt:
    secretKey = None
    iv = None
    def __init__(self):
        '''
        初始化，从配置文件读取相关加密参数
        '''
        try:
            # 读取配置文件
            f = open("config.yaml","r+",encoding="utf-8")
            fstream = f.read()
            configobj = yaml.safe_load(fstream)
            # self.secretKey = configobj['gateway']['key'].encode('utf-8')
            self.iv =a2b_hex(configobj['gateway']['iv'])
        except Exception as e:
            logger.writeLog("AES加密组件初始化失败" + str(e),'encrypt.log')


    # 加密内容长度不足16位倍数用空格补足
    def add_to_16(self, text):
        if len(text.encode('utf-8')) % 16:
            add = 16 - (len(text.encode('utf-8')) % 16)
        else:
            add = 0
        text = text + ('\0' * add)
        return text.encode('utf-8')

    #加密
    def encrypt(self,key,content):
        mode = AES.MODE_CBC
        text = self.add_to_16(content)
        cryptos = AES.new(key, mode, self.iv)
        cipher_text = cryptos.encrypt(text)
        # 因为AES加密后的字符串不一定是ascii字符集的，输出保存可能存在问题，所以这里转为16进制字符串
        tempres = b2a_hex(cipher_text)
        res = str(tempres, encoding = "utf-8").upper()
        return res

    # 解密后，去掉补足的空格用strip() 去掉
    def decrypt(self,key,text):
        mode = AES.MODE_CBC
        cryptos = AES.new(key, mode, self.iv)
        plain_text = cryptos.decrypt(a2b_hex(text))
        return bytes.decode(plain_text).rstrip('\0')