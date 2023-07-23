
version = 2.1
# 9 juillet 2023 add wait_blynk, global to stop thread
# 12 juillet clean ctrlC

# https://github.com/blynkkk/lib-python

################### LEGACY, PRIVATE ##############

# WINDOWS
# DEEP/Blynk/my_blynk_private.py
# DEEP/Blynk/my_blynk_new.py

# WINDOWS projects in DEEP/<project> 
#  so import ../Blynk

# MICROPYTHON projects in micropython/<project>
# sym link to micropython/MY MODULES 
# sym link to DEEP/Blynk

# LINUX
# HOME/Blynk/my_blynk_private.py
# HOME/Blynk/my_blynk_new.py
# projects in HOME/<project> , so import ../Blynk

import sys, random
from time import localtime, sleep
import _thread

stop_run = False # used in blynk.run thread

print("my blynk private v%0.1f" %version)

p = sys.platform

# ESP* client legacy library, as this code, should be in a windows dir, to be uploaded on ESP, and which is included in micropython sys.path


# import client legacy library

if p == 'esp8266':
  import blynklib_legacy_mpy as blynklib 
  print("running on esp8266. blynklib_mpy, ie frozen version. should be in sys.path")

if p == 'esp32':
  import blynklib_legacy_mp as blynklib 
  print("running on esp32. import blynklib_mp. should be in sys.path")

if p == 'linux':
  print("running on Linux. import blynklib_legacy_0_2_6 from ../Blynk/Blynk_client")
  # asume we are in APP/<project>. 
  sys.path.insert(1, '../Blynk/Blynk_client') # this is in above working dir 
  import blynklib_legacy_0_2_6 as blynklib # in Blynk


import blynktimer_legacy as blynktimer

try:
  from machine import reset
except Exception as e:
  pass


# micropython v1.19 required mpy v6  
# xxd , on windows PS> format-hex *.mpy 00000000   4D 06 02 ...  0x4d (ASCII ‘M’)   2nd byte is version 6
# make sure byte code consistent with micropython

# blynklib_mp.py  blynklib_mpy.mpy
# either rename blynklib_mp.mpy to blynklib_mpy.mpy
# or delete blynklib_mp.py

# use mpy version of blynklib on esp8266 # .mpy version ok for esp8266 


####### 
# blynk.run as thread (ESP32, linux) or in main (ESP8266) and use timers
#######

first_connect = True

blynk_server = "192.168.1.206"
blynk_port = 8089

def b_log(x):
  print('blynk log:' , x)
  pass

"""
blynk log: Connected to blynk server
blynk log: Authenticating device...

start blynk.run endless loop
blynk log: Access granted
blynk log: Heartbeat = 60 sec. MaxCmdBuffer = 1024 bytes
blynk log: Registered events: ['connect', 'disconnect', 'internal_rtc']

blynk log: Event: ['connect'] -> ()

blynk log: Event: ['write v14'] -> (14, ['0.019339999999999996'])

"""

def create_blynk(token, blynk_server=blynk_server, blynk_port=blynk_port, log = True):

  # token in secret.py
  print ('\nBLYNK: create private server. auth token: ' , token)

  # ssl argument not available 
  # for Python v0.2.6
  # log is Blynk log. omit to get rid
  if log:
    blynk_con = blynklib.Blynk(token,server=blynk_server, port=blynk_port, heartbeat=60, log=b_log)
  else:
    blynk_con = blynklib.Blynk(token,server=blynk_server, port=blynk_port, heartbeat=60)

  ##### NOTE: system call back defined here will be executed.
  # if defined in main, not executed ??

  ###################
  # system call backs
  # define here if generic (no need to trigger specific processing)
  # define in main , or use return code from .connect() in main otherwize
  ###################
    
  @blynk_con.handle_event("connect")
  def connect_handler():
    global first_connect
    print("BLYNK: connect call back. localtime: ", localtime())

    if first_connect: # avoid connect, disconnect
      print('BLYNK: first connect')
      first_connect = False  

      # RTC sync request was sent
      print('BLYNK: sync RTC in first connect')
      blynk_con.internal("rtc", "sync")


  @blynk_con.handle_event("disconnect")
  def disconnect_handler():
    print("BLYNK: disconnect call back: localtime ", localtime())

  # https://docs.micropython.org/en/latest/library/time.html
  @blynk_con.handle_event('internal_rtc')
  def rtc_handler(rtc_data_list):
    print("BLYNK: rtc call back: localtime ", localtime())
    print("BLYNK: rtc from server ", rtc_data_list)
    # datetime not available in micropython
    #hr_rtc_value = datetime.utcfromtimestamp(int(rtc_data_list[0])).strftime('%Y-%m-%d %H:%M:%S')
    #print('Raw RTC value from server: {}'.format(rtc_data_list[0]))
    #print('Human readable RTC value: {}'.format(hr_rtc_value))
  
  return(blynk_con)


def connect_blynk(blynk_con):

  ### looks like return code from connect is not reliable. can return None. check connected explicitly

  timeout=30
  print("BLYNK: connecting to server. timeout %d" %timeout)
  ret= blynk_con.connect(timeout=timeout)
  print("blynk connect returned: %s" %ret)
  return(ret)


def wait_blynk(blynk_con):
  i = 0
  max = 30

  while not blynk_con.connected():

    i = i + 1
    if i > max:
      print("blynk server not connected after %d wait" %i)
      return(False)
    else:
      sleep(1)

  print("blynk.connected: %s" %blynk_con.connected())
  return(True)
  
# endless loop
# run in main or separate thread
def run_blynk(blynk_con):
  global stop_run
  print("\nstart blynk.run endless loop")
  while True:
    # blynk.run will make call back happen need to call Blynk.run to have callback read start button value
    # need while true around .run()
    try:
      blynk_con.run()
      #timer.run()
      ##### can also check global 
      if stop_run:
        print("blynk run thread must stop")
        break

    except Exception as e: 
      print('BLYNK: blynk.run exception %s', str(e))

      try:
        reset()
      except Exception as e:
        pass

  # while true
  # break while true based on global var
  print("blynk run thread stopping")


if __name__ == "__main__":


  """
  to test my_blynk_private as stand alone module, run from Blynk dir, and uses test vpin and secret located in Blynk

  when used in app, 
   my_blynk_private is a sym link (to be created) pointing to module in Blynk (to accumulate all edits into a master version)
   import vpin and secret done in app, and use file in app directory (not from Blynk)
   my_blynk_private is imported, not ran as main
  """

  import vpin_test # application specific, in app directory
  import secret_test # application agnostic, in my_modules


  # token for both legacy and new
  blynk_token = secret_test.blynk_token_cloud

  # cannot use log=None. create object with or without log defined is done in my_blynk
  blynk_con = create_blynk(blynk_token, log=True)

  _thread.start_new_thread(run_blynk, (blynk_con,))

  print("connect to blynk")
  ret = connect_blynk(blynk_con)
  print("connect returned %s" %ret)

  print("wait for blynk to connect")

  ret= wait_blynk(blynk_con)
  if ret == False:
    print("cannot connect to blynk")
    sys.exit(1)

  
  ##########
  # control : call back
  # display non push: call back wirtual_write
  # display push: inline wirtual_write
  ##########

  control_vpin = vpin_test.vpin_control # control
  display_vpin = vpin_test.vpin_non_push_display # display non push

  ###############
  # widget call backs
  # defined in my_blynk module, or in main
  ##############

  ### control widget
  # define where the update is needed (eg main) (ie access update event and value)
  s = "write V%d" %control_vpin
  @blynk_con.handle_event(s)
  def write_virtual_pin_handler(pin, value):
      global flag
      print("BLYNK: call back control widget", pin, value)
      flag = value[0] # str
      flag_int = int(value[0])

  ### display widget
  # FOR NON PUSH display widget
  # will be called based on timer, set in widget itself
  @blynk_con.handle_event('read V' + str(display_vpin))
  def read_virtual_pin_handler(pin):
      i = random.randint(0, 255)
      print("BLYNK: call back non push display widget %d. rand %d" %(pin,i))
      blynk_con.virtual_write(pin, i)


  # sync, ie data needed for processing
  # for control widgets
  blynk_con.virtual_sync(control_vpin) # sync can be done after connect or in connect call back
  
  colors = {'#FF00FF': 'Magenta', '#00FF00': 'Lime'}

  while True:

      # uses vpin_test
      try:
        blynk_con.virtual_write(vpin_test.vpin_display, 1000)
        blynk_con.virtual_write(vpin_test.vpin_terminal, "test blynk private")
        blynk_con.set_property(vpin_test.vpin_display, 'color',  '#FF0000')
        blynk_con.set_property(vpin_test.vpin_display, 'label',  'display')

        sleep(5)

      except KeyboardInterrupt:
        s = "got KeyboardInterrupt. disconnect and reset"
        print(s)
        stop_run = True # global in context of this module
        blynk_con.disconnect(err_msg=s) # blynk log: [ERROR]: KeyboardInterrupt: disconnect blynk
        #wifi.disconnect() 
        # reset or exit
        sys.exit(1)

      except Exception as e:
        s = "exception non keyboard interupt %s. disconnect and reset" %str(e)
        print(s)
        stop_run= True
        blynk_con.disconnect(err_msg=s) 
        # wifi.disconnect()
        # reset or exit
        sys.exit(1)



      