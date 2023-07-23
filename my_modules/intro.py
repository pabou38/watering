import sys
import gc
from micropython import mem_info, const, stack_use
import uos
import webrepl 
from machine import freq

from esp import flash_size

try:
  from esp32 import raw_temperature
  print ('ESP32 internal temp %d' %(int(raw_temperature()-32)*5.0/9.0))
except:
  pass


# Determine the .mpy version and flags supported by your MicroPython system
# pip install mpy-cross
# mpy-cross --version MicroPython v1.19.1 on 2022-06-18; mpy-cross emitting mpy v6
# -march=<arch> : set architecture for native emitter; x86, x64, armv6, armv6m, armv7m, armv7em, armv7emsp, armv7emdp, xtensa, xtensawin
try:
  sys_mpy = sys.implementation._mpy # esp32
except:
  sys_mpy = sys.implementation.mpy # esp8266

arch = [None, 'x86', 'x64',
    'armv6', 'armv6m', 'armv7m', 'armv7em', 'armv7emsp', 'armv7emdp',
    'xtensa', 'xtensawin'][sys_mpy >> 10]
print('mpy version:', sys_mpy & 0xff)
print('mpy-cross -march=', end='')
if arch:
    print(arch, end='')
print()


print(uos.uname(), '\n')
#(sysname='esp32', nodename='esp32', release='1.20.0', version='v1.20.0 on 2023-04-26', machine='ESP32C3 module with ESP32C3'

print ("implementation: ",sys.implementation)  # no ()
# implementation:  (name='micropython', version=(1, 20, 0), _machine='ESP32C3 module with ESP32C3', _mpy=262

print ("platform: ", sys.platform) # eg use .mpy if = "esp8266"
# platform:  esp32

print ("version: ",sys.version)
# version:  3.4.0; MicroPython v1.20.0 on 2023-04-26

print ("sys.path: ", sys.path) # list
# sys.path:  ['', '.frozen', '/lib']

print ("modules imported: ", sys.modules) # dict

print('cpu frequency: %d Mhz' %(freq()/1000000))
print('flash size in Mbytes: ', flash_size()/(1024.0*1024.0))

#esp.osdebug(None)
#to display flash size
#import port_diag

# free file system
i= uos.statvfs('/')
fs = i[1]*i[2]/(1024.0*1024.0)
free= i[0]*i[4]/(1024.0*1024.0)
per = (float(free)/float(fs))
print('file system size %0.1f, free %0.1f, free in percent %0.1f' %(fs, free, per))

def start_repl():
    # need to import once webrepl_setup from a usb/ttl connection to set password
    # creates webrepl_cfg.py (not visible in uPyCraft, visible w: os.listdir()
    # cannot just browse to IP, need client http://micropython.org/webrepl/
    print('import webrepl_setup once to set password')
    print('start webrepl: use http://micropython.org/webrepl/ to access or use local webrepl.html')
    print('ws://192.168.1.5:8266/')
    webrepl.start()

for d in ["/", "/lib", "/Blynk", "/my_modules"]:
    
    print('content of %s: ' %d, end=' ')
    try:
      print(uos.listdir(d))
    except Exception as e:
      print(str(e))


#ESP32 4MB, heap is 111168 bytes. note: stack is fixed 15360 / 1024 = 15Kio
gc.collect()
free = gc.mem_free()
alloc = gc.mem_alloc()
print("\nmem free %d, alloc %d, sum %d, percent free %0.2f"  %(free, alloc, free+alloc, free/(free+alloc)))

# garbage collection can be executed manually, if alloc fails, or if 25% of currently free heap becomes occupied
#gc.threshold(gc.mem_free() // 4 + gc.mem_alloc())

print("stack used: ", stack_use())
print("mem info (1 for memory map): ", mem_info()) 
