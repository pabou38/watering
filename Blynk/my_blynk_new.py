#!/usr/bin/python3


################################
# new blynk
#################################


import time, sys
import _thread

blynk_server="blynk.cloud" # ping blynk.cloud
#server = "fra1.blynk.com"


######################
# lib patacaisse
#####################

################################## NEW BlynkLib #################################

# https://github.com/vshymanskyy/blynk-library-python is the NEW library
# Note: The library has been updated for Blynk 2.0. Please remain on v0.2.0 for legacy Blynk


# pip install blynk-library-python
##### WARNING: pip only install v0.2.0 and does not install BlynkTimer.py, so MUCH better to install rev 1.0.0 from github  for Python v1.0.0 (linux)
# import BlynkLib
#  -> import BlynkLib_1_0_0 as BlynkLib

# BlynkLib.py, BlynkLibTimer.py


# Python 2, Python 3, MicroPython support . Linux,  Windows,  MacOS support
# 1.0.0
# log_event, set_property
# same lib for python and micropython
# run on ESP
# Edgent_linux_rpi

####### @blynk.on("V3")   (even if README uses @blynk.VIRTUAL_WRITE(1) 
# @blynk.on("connected")@blynk.on("internal:utc")


################################## LEGACY blynklib #################################

# https://github.com/blynkkk/lib-python is legacy
# sudo pip install blynklib
# certificates
# blynklib.py, blynklib_mp.py, blynktimer.py
# 0.2.6
# import blynklib_legacy_0_2_6.py as blynklib
#######################

### for linux, make sure to download latest version 1.0.0 from github

p = sys.platform
if p == "linux":
    sys.path.insert(1, '../Blynk') # this is in above working dir 

# should be in /lib for ESP , or in Blynk for Raspberry
# ASSUMES this module is a sym link in the project directory
import BlynkLib_new as BlynkLib  # for Python v1.0.0 
import BlynkTimer_new as BlynkTimer

# will connect
def create_blynk(token, log=None):
    # log=print
    blynk = BlynkLib.Blynk(token, server=blynk_server, log=log, insecure=False)
    print('blynk initialized')
    return(blynk)

def create_blynk_timer():
    timer = BlynkTimer()
    #timer.set_timeout(2, hello) # run once
    #timer.set_interval(4, power) # run multiple
    return(timer)


def run_blynk(blynk, blynk_timer=None):
    print('start blynk.run() endless loop', blynk, blynk_timer)

    while True:
        blynk.run()
        if blynk_timer is not None:
            blynk_timer.run()


if __name__ == "__main__":

    import secret_test
    import vpin_test

    ############ change to current application
    secret_test = secret_test.blynk_token_victron_remote_operation

    print("blynk token" , secret_test)

    blynk = create_blynk(secret_test, log=None) # connect


    #####################
    # blynk call back
    # connect, disconnect can be generic, but control need application vpin
    #####################

    @blynk.on("connected")
    def blynk_connected(ping):
        print('Blynk connected. Ping:', ping, 'ms')
        blynk.send_internal("utc", "time")
        blynk.send_internal("utc", "tz_name")
        
        #blynk.sync_virtual(v_automation, v_sleep, v_react_to_surplus, v_react_to_soutir)


    @blynk.on("disconnected")
    def blynk_disconnected():
        print('Blynk disconnected')


    # get time from server
    @blynk.on("internal:utc")
    def on_utc(value):
        if value[0] == "time":
            ts = int(value[1])//1000

            if sys.platform in ['esp32', 'esp8266']:
                # on embedded systems, you may need to subtract time difference between 1970 and 2000
                ts -= 946684800
                #tm = time.gmtime(ts) # gmtime not available in micropython
                print("server UTC time: ", time.localtime(ts)) # tuple from sec

            else:
                tm = time.gmtime(ts) 
                print("server UTC time: ", time.asctime(tm)) #UTC time:  Tue Jun  6 05:11:38 2023


        elif value[0] == "tz_name":
            print("server Timezone: ", value[1]) #Timezone:  Europe/Paris


    # control widgets call back
    s = "V%d" %0
    @blynk.on(s)
    def f1(value):
        print(value)
        #call back multi on off: ['0']
        val = int(value[0])

    # start blynk.run thread
    id1= _thread.start_new_thread(run_blynk, (blynk,None))

    # sync
    blynk.sync_virtual(0)

    while True:
  
        #blynk.virtual_write(vpin.vpin_power,200)
        #blynk.set_property(shelly_switch[index], "label", "ON")
        #blynk.set_property(shelly_switch[index], "color", "#D3435C")
        #blynk.log_event("starting", "solar2heater starting") # use event code
        
        time.sleep(10)



"""
Connecting to blynk.cloud:443...
< 29 1 | nIgi4nCJ6yvwXmLqCzD-nq-YdCiIpM3t
blynk initialized
start blynk.run() endless loop
> 0 1 | 200
< 17 2 | ver 1.0.0 h-beat 50 buff-in 1024 dev linux-py
Blynk ready. Ping: 8170 ms
< 17 3 | utc time
< 17 4 | utc tz_name
> 0 2 | 200
> 17 3 | utc,time,1686028215569
UTC time:  Tue Jun  6 05:10:15 2023
> 17 4 | utc,tz_name,Europe/Paris
Timezone:  Europe/Paris
< 16 5 | vr 0
> 20 5 | vw,0,0
['0']
< 20 6 | vw 10 200
< 20 7 | vw 9 test blynk
> 0 7 | 2
"""
