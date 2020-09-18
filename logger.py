import sys
import logging
from logging.handlers import TimedRotatingFileHandler
import os

def writeLog(message, filenames = "runtime.log"):
    # 判断是否有logs文件夹，如果没有,自动在当前文件夹中创建
    if not (os.path.exists(os.getcwd()+'/logs')):
        os.mkdir(os.getcwd()+'/logs')
    logging.basicConfig(level=logging.WARNING,
                        format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                        filemode='a')
    formatter = logging.Formatter('%(asctime)s:%(filename)s:%(funcName)s:[line:%(lineno)d] %(levelname)s %(message)s')
    CURRENT_DIR = os.path.dirname(__file__)
    LOG_FILE = os.path.abspath(os.path.join(CURRENT_DIR, "logs", filenames))
    fileTimeHandler = TimedRotatingFileHandler(LOG_FILE, "D", 1, 0,encoding='utf-8')
    fileTimeHandler.suffix = "%Y%m%d.log"
    fileTimeHandler.setFormatter(formatter)
    loggers = logging.getLogger('')
    loggers.addHandler(fileTimeHandler)
    loggers.warn(message)
    loggers.handlers.pop()