import webrepl

from utime import sleep
import os

##################################################
# webrepl
# expect webrepl_cfg.py. should be synched with the rest of the project

##################################################

#webrepl_cfg.py
#PASS = 'meaudre'

def start_webrepl(log = None):

    s = "start webrepl"
    print(s)
    if log is not None:
        log.info(s)

    f = "/webrepl_cfg.py"
    try:
        os.stat(f)

    except OSError:
        s = "WARNING!!: %s does not exist" %f
        print(s)
        if log is not None:
            log.error(s)
        return(False)
    
    # need to import once webrepl_setup from a usb/ttl connection to set password
    # creates webrepl_cfg.py (not visible in uPyCraft, visible w: os.listdir()

    # cannot just browse to IP, need client http://micropython.org/webrepl/ 
    # web client from https://github.com/micropython/webrepl 
    # (hosted version available at http://micropython.org/webrepl)

    # The web client has buttons for the corresponding functions, 
    # or you can use the command-line client webrepl_cli.py from the repository above.

    print('import webrepl_setup once to set password')

    print("use WebREPL server started on http://192.168.1.178:8266/ and use ws://192.168.1.9:8266/")
    print('or use http://micropython.org/webrepl/ to connect and use ws://192.168.1.9:8266/') 
    print('or use local webrepl.html, file:///C:/Users/pboud/micropython/webrepl-master/webrepl.html')

    print("cannot use ws://192.168.1.9:8266/ directly in browser")

    webrepl.start() # return None

    #WebREPL server started on http://192.168.1.178:8266/
    #Started webrepl in normal mode

    # WebREPL connection from: ('192.168.1.19', 60214)
    # dupterm: EOF received, deactivating

    return (True)


if __name__ == "__main__":
    print("start webrepl")

    ret = start_webrepl()

    #WebREPL server started on http://192.168.1.178:8266/
    #Started webrepl in normal mode

    # use client to connect to IP:8266
    # repl output appears ; copy file to/from esp32

    print("returning from webrepl", ret)

    while True:
        sleep(10)
        print("repl", end='')

      