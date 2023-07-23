
import logging 
# from micropython-lib-master  a single logging.py vs logging dir
# https://github.com/micropython/micropython-lib/tree/master/python-stdlib/logging/examples


def get_log(app, level = "debug"):
    print("init log. app %s, level %s" %(app, level))
    if level == "debug":
        logging.basicConfig(level=logging.DEBUG) #  will display on stdout
    elif level == "info":
        logging.basicConfig(level=logging.INFO) #  will display on stdout
    elif level == "warning":
        logging.basicConfig(level=logging.WARNING) #  will display on stdout
    elif level == "error":
        logging.basicConfig(level=logging.ERROR) #  will display on stdout
    elif level == "critical":
        logging.basicConfig(level=logging.CRITICAL) #  will display on stdout
    else:
        print("%s unknown" %level)
        return(None)


    log = logging.getLogger(app)
    log.info("creating log")
    # INFO:pzem:starting
    return(log)

"""
# same info, just formatted
class MyHandler(logging.Handler):
    def emit(self, record):
        print(record.__dict__)
        print("levelname=%(levelname)s name=%(name)s message=%(message)s" % record.__dict__)


logging.getLogger().addHandler(MyHandler())
logging.info("remote PZEM starting") 
# levelname=INFO name=root message=remote PZEM starting
"""