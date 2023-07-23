
##################################################
# watering
###################################################

##############
# TO DO
# active but close wifi
# blynk email
##############

version = 1.33 # pîng,  repl error
version = 1.46 # deep sleep. make sure webrepl_cfg.py is synched 
version = 1.51 # deep sleep slider

own_ip="192.168.1.3" # static
own_ip=None  # dhcp

from utime import ticks_ms, ticks_diff
start_time=ticks_ms() # note t=time() is in seconds. to measure execution time

print('\n\n=== watering ESP32 micropython. version %0.2f. ===\n' %(version))

import sys


from utime import sleep, localtime
#from utime import sleep_ms,  sleep_us, gmtime, mktime

from machine import Pin, reset, Timer
#from machine import RTC, I2C, ADC,  DEEPSLEEP, deepsleep, reset_cause, DEEPSLEEP_RESET, PWRON_RESET, HARD_RESET  
import _thread

# globals set by call back, and used in main

# timer in mn (ms when callin Timer())
# default before updated from virtual_sync
max_time_valve = 1
max_time_pump = 1

button_sleep = 0 # will be updated with sync / callback
sleep_has_synced = False # wait for sync to happend before entering main loop (otherwize, test may occurs before value is synched)

############
# GPIO
############
# relay shield D1
valve_gpio = 10 # LOLIN c3 pico

## Victron remote pcb
valve_gpio = 13 # multiplus relay
pump_gpio = 12 

# mppt 14, battery 27, relay 4 12

valve = Pin(valve_gpio,Pin.OUT, value=0)
pump = Pin(pump_gpio,Pin.OUT, value=0)

# The ESP32 port has four hardware timers. Use the machine.Timer class with a timer ID from 0 to 3 (inclusive):
tim_valve = Timer(0)
tim_pump = Timer(1)

repl_started = False 

button_sleep = 0 # will be updated with sync / callback

### deep sleep configuration

# nite 9pm to 6 am
# evening, ie typical watering time 4pm to 9pm

watering_start = 16
watering_end = 21
morning_start = 6

watering_range  = range(watering_start, watering_end)
nite_range = range(watering_end, morning_start)

# in mn
# updated from virtual sync
deep_sleep_duration_mn = {
    "nite": 60,
    "day": 10,
    "watering": 5
}


##############
# logging
##############

import logging 
# from micropython-lib-master  a single logging.py vs logging dir
# https://github.com/micropython/micropython-lib/tree/master/python-stdlib/logging/examples

print('create logger, will display on stdout')
logging.basicConfig(level=logging.DEBUG)

logging.info("watering starting") 
# INFO:root:remote PZEM starting

# seems using logging.  creates problem inside function
log = logging.getLogger("watering")
log.info("starting")
# INFO:pzem:starting


# add with append or insert 
# name of dir in ESP32 file system
# this name exists on Windows file system (in micropython project directory)
# and is symlinked to HOME/Blynk/Blynk_client and HOME/micropython/"my modules" in Windows file system
# those dir are expected to be downloaded  (eg pymakr sync project) to ESP32 to /


# ESP32 file system
sys.path.append("/my_modules")
sys.path.insert(1,"/Blynk")
print("updated import path: ", sys.path)

import my_webrepl

##############
# intro
##############
import deep_sleep
deep_sleep.print_reset_cause()

import intro
            
#############
# wifi
#############

import my_wifi

print('start wifi')
wifi, ssid = my_wifi.start_wifi(own_ip=own_ip)
if wifi == None:
    d = 30
    print('cannot start wifi. reset in a %d sec' %d)
    
    del(wifi)
    sleep(d)
    reset()
else:
    print("wifi ok", ssid)

#################
# ping
#################
import my_ping

ret = my_ping.ping_ip("192.168.1.1")
s = "ping box returned %s" %ret

print(s)
logging.info(s)


#################
# relay
#################

relay_dict = {
    0: "valve",
    1: "pump"
}

def get_stamp():
    (year, month, mday, hour, minute, second, weekday, yearday) = localtime()
    s = "%d %d:%d" %(mday, hour, minute)
    return(s)


###################
# action on relay
# # cause can be user action (ie callback) , or timer (to turn off), or turn valve because pump needs it
###################

def relay_onoff(relay_name, value, cause):

    # turn relay
    s = "%s: %s turning %s relay to %d" %(get_stamp(), cause, relay_name, value)
    print(s)

    # action summary on terminal
    blynk_con.virtual_write(vpin_terminal, s)

    # set relay
    if relay_name == "valve":
        vpin_led = vpin_led_valve
        vpin_button = vpin_button_valve

        valve.value(value)

    elif relay_name == "pump":
        vpin_led = vpin_led_pump
        vpin_button = vpin_button_pump
        
        pump.value(value)


    # update led label and value
    blynk_con.set_property(vpin_led, "label", "%s position" %relay_name)
    if value == 1:
        blynk_con.virtual_write(vpin_led, 255)
    else:
        blynk_con.virtual_write(vpin_led, 0)

    # update button label and color
    # style button. content str for ON/OFF, and background color is set in widget
    # seems color property does not work for style button
    if value:
        blynk_con.set_property(vpin_button, "color", "#FF0000") # seems not working
        blynk_con.set_property(vpin_button, "label", "%s OPEN" %cause)
        
    else:
        blynk_con.set_property(vpin_button, "color", "#0000FF") # seems not working
        blynk_con.set_property(vpin_button, "label", "%s CLOSED" %cause)


#########################
# timer call back
# turn off
#########################

def t_valve(t): # timer: max time for pump Timer(3ffe5a20; alarm_en=0, auto_reload=0, counter_en=1)
    global button_valve

    valve.value(0)

    s = "%s: valve timer. closing" %get_stamp()
    print(s)
    logging.info(s)
    blynk_con.virtual_write(vpin_terminal, s)

    relay_onoff("valve", 0, "timer")

    try:
        # seems I can set button also , background color and text will change
        blynk_con.virtual_write(vpin_button_valve, 0)
        button_valve = 0 # make sure
    except:
        print("cannot set valve button value")


def t_pump(t):
    global button_pump

    pump.value(0)

    s = "%s: pump timer. closing" %get_stamp()
    print(s)
    logging.info(s)
    blynk_con.virtual_write(vpin_terminal, s)

    relay_onoff("pump", 0, "timer")

    try:
        blynk_con.virtual_write(vpin_button_pump, 0)
        button_pump = 0
    except:
        print("cannot set pump button value")



#######################
# terminal
# stop blynk run thread
# disconnect
# reset or sleep
########################

def disconnect(s):
    global stop_run

    print(s)
    logging.info(s)
    blynk_con.virtual_write(vpin_terminal, s)
    sleep(5) # time for blynk to run ?

    stop_run= True
    try:
        blynk_con.disconnect(err_msg=s)
    except:
        pass

    try:
        wifi.disconnect()
    except:
        pass

def disconnect_and_reset(s):
    try: # make sure reset ALWAYS executed
        disconnect(s)
    except:
        pass

    sleep(5)
    reset()

def disconnect_and_deepsleep(s,d):  # d in sec
    try:
        disconnect(s)
    except:
        pass

    # enter dep sleep
    deep_sleep.enter_deep_sleep(d*1000, pull_to_disable=[])
    


#################
# ping
#################

def ping_thread(ip, d, logging):
    print("start ping thread", ip, d)

    while True:
        print("*", end='')

        ret = my_ping.ping_ip(ip)
        if ret == False:
            s = "ping failed. clean and exit"
            print(s)
            logging.error(s)

            disconnect_and_reset(s)

        else:
            sleep(d)



##########################
# Blynk
##########################

button_valve = None

import vpin # application specific, in app directory
import secret # application agnostic, in my_modules
import my_blynk_private

blynk_token = secret.blynk_token_ecs

# cannot use log=None. create object with or without log defined is done in my_blynk
# log is blynk library internal log
blynk_con = my_blynk_private.create_blynk(blynk_token, log=False)

###########################
#### start blynk.run thread
###########################
_thread.start_new_thread(my_blynk_private.run_blynk, (blynk_con,))

print("connect to blynk")
ret = my_blynk_private.connect_blynk(blynk_con)
print("connect returned %s" %ret)

print("wait for blynk to connect")
ret= my_blynk_private.wait_blynk(blynk_con)
if ret == False:
    s = "cannot connect to blynk"
    print(s)
    logging.error(s)
    disconnect_and_reset(s)
    

# control
# label property set in call back
vpin_button_valve = vpin.vpin_button_valve # control
vpin_button_pump = vpin.vpin_button_pump # control

vpin_slider_valve = vpin.vpin_slider_valve # control
vpin_slider_pump = vpin.vpin_slider_pump # control

# display non push

# display push
vpin_led_valve = vpin.vpin_led_valve 
vpin_led_pump = vpin.vpin_led_pump 

vpin_terminal = vpin.vpin_terminal

vpin_reset = vpin.vpin_reset
vpin_repl = vpin.vpin_repl

vpin_sleep = vpin.vpin_sleep
vpin_status = vpin.vpin_status

#### signal starting (now that blynk is up)
blynk_con.virtual_write(vpin_terminal, "%s: v%0.2f starting. %s" %(get_stamp(), version, ssid))

##### WARNING: do not sync yet. does not seem to work. wait after call back definition

# signal deep sleep wake up
if deep_sleep.print_reset_cause() == 5:
    s = "%s. wake up from deep sleep" %get_stamp()
    blynk_con.virtual_write(vpin_status, s)

# write labels
blynk_con.set_property(vpin_slider_valve, "label", "valve open time (mn)")
blynk_con.set_property(vpin_slider_pump, "label", "pump running time (mn)")

blynk_con.set_property(vpin_terminal, "label", "application log")
blynk_con.set_property(vpin_repl, "label", "update")
blynk_con.set_property(vpin_reset, "label", "reboot")

blynk_con.set_property(vpin_sleep, "label", "sleep mode")
blynk_con.set_property(vpin_status, "label", "sleep status")

blynk_con.set_property(vpin.vpin_watering, "label", "sleep watering (mn)")
blynk_con.set_property(vpin.vpin_day, "label", "sleep day (mn)")
blynk_con.set_property(vpin.vpin_nite, "label", "sleep nigth (mn)")



###############
# widget call backs
# defined in my_blynk module, or in main
##############

### control widget
# define where the update is needed (eg main) (ie access update event and value)

#############
# VALVE relay
#############
s = "write V%d" %vpin_button_valve
@blynk_con.handle_event(s)
def f1(pin, value):
    global button_valve # 

    print("BLYNK: call back control widget", pin, value)
    button_valve = int(value[0])

    relay_onoff("valve", button_valve, "user update")

    # set timer
    if button_valve:
        print("set timer %dmn" %max_time_valve)
        period_ms = max_time_valve * 1000* 60 # make sure int blynk log: can't convert float to int
        tim_valve.init(period=period_ms, mode=Timer.ONE_SHOT, callback=t_valve)
        print("timer set")


#############
# PUMP relay
#############
s = "write V%d" %vpin_button_pump
@blynk_con.handle_event(s)
def f2(pin, value):
    global button_pump

    print("BLYNK: call back control widget", pin, value)
    button_pump = int(value[0])

    if button_pump:
        # make sure valve if on
        s = "make sure valve is on for pump"
        print(s)
        logging.info(s) 
        relay_onoff("valve", 1, "pump ")

        blynk_con.virtual_write(vpin_button_valve, 1)

    relay_onoff("pump", button_pump, "user action")

    # set timer
    if button_pump:
        print("set timer %dmn" %max_time_pump)
        period_ms = max_time_pump * 1000* 60
        tim_pump.init(period=period_ms, mode=Timer.ONE_SHOT, callback=t_pump)



#############
# VALVE timer slider
#############
s = "write V%d" %vpin_slider_valve
@blynk_con.handle_event(s)
def f3(pin, value):
    global max_time_valve

    print("BLYNK: call back control widget", pin, value)
    max_time_valve = int(value[0]) # keep as mn
    print("max time for valve mn %d" %(max_time_valve))

#############
# PUMP timer slider
#############
s = "write V%d" %vpin_slider_pump
@blynk_con.handle_event(s)
def f4(pin, value):
    global max_time_pump

    print("BLYNK: call back control widget", pin, value)
    max_time_pump = int(value[0])
    print("max time for pump mn %d" %(max_time_pump))


#############
# REPL
#############
s = "write V%d" %vpin_repl
@blynk_con.handle_event(s)
def f5(pin, value):
    global button_repl
    global repl_started

    print("BLYNK: call back control widget", pin, value)
    button_repl = int(value[0])

    if button_repl:
        # start webrepl 

        if repl_started: 
            s = "%s REPL already started" %get_stamp()
            print(s)
            logging.info(s)
            blynk_con.virtual_write(vpin_terminal, s)

        else:

            repl_started = True
            s = "%s: start REPL" %get_stamp()
            print(s)
            logging.info(s)
            blynk_con.virtual_write(vpin_terminal, s)

        ret = my_webrepl.start_webrepl(logging) # 

        s = "%s: returns from webrepl: %s" %(get_stamp(), ret)
        print(s)
        logging.info(s)
        blynk_con.virtual_write(vpin_terminal, s)

    else:
        # do nothing 
        pass

#############
# reset
#############
s = "write V%d" %vpin_reset
@blynk_con.handle_event(s)
def f6(pin, value):
    global button_reset
    global stop_run
    print("BLYNK: call back control widget", pin, value)
    button_reset = int(value[0])

    if button_reset:
        s = "%s: reset from app" %get_stamp()
        disconnect_and_reset(s)


#############
# deep sleep
#############
s = "write V%d" %vpin_sleep
@blynk_con.handle_event(s)
def f7(pin, value):
    global button_sleep
    global stop_run
    global sleep_has_synced
    global nb_sync
    nb_sync = nb_sync + 1


    print("BLYNK: call back control widget", pin, value)
    button_sleep = int(value[0])

    sleep_has_synced = True

    if button_sleep:
        x = "ON"
    else:
        x = "OFF"

    s = "%s: sleep mode is set to %s" %(get_stamp(),x)
    print(s)
    logging.info(s)
    blynk_con.virtual_write(vpin_terminal, s)
    

#############
# deep sleep time sliders
#############
s = "write V%d" %vpin.vpin_nite
@blynk_con.handle_event(s)
def f8(pin, value):
    global nb_sync
    nb_sync = nb_sync + 1

    print("BLYNK: call back control widget", pin, value)
    mn = int(value[0])
    deep_sleep_duration_mn["nite"] = mn

    s = "%s: deep sleep nite %d mn" %(get_stamp(),mn)
    print(s)
    log.info(s)
    blynk_con.virtual_write(vpin_terminal, s)

s = "write V%d" %vpin.vpin_day
@blynk_con.handle_event(s)
def f9(pin, value):
    global nb_sync
    nb_sync = nb_sync + 1

    print("BLYNK: call back control widget", pin, value)
    mn = int(value[0])
    deep_sleep_duration_mn["day"] = mn

    s = "%s: deep sleep day %d mn" %(get_stamp(),mn)
    print(s)
    log.info(s)
    blynk_con.virtual_write(vpin_terminal, s)

s = "write V%d" %vpin.vpin_watering
@blynk_con.handle_event(s)
def f10(pin, value):
    global nb_sync
    nb_sync = nb_sync + 1

    print("BLYNK: call back control widget", pin, value)
    mn = int(value[0])
    deep_sleep_duration_mn["watering"] = mn

    s = "%s: deep sleep watering %d mn" %(get_stamp(),mn)
    print(s)
    log.info(s)
    blynk_con.virtual_write(vpin_terminal, s)

""""
### display widget
# FOR NON PUSH display widget
# will be called based on timer, set in widget itself
@blynk_con.handle_event('read V' + str(display_vpin))
def read_virtual_pin_handler(pin):
    i = random.randint(0, 255)
    print("BLYNK: call back non push display widget %d. rand %d" %(pin,i))
    blynk_con.virtual_write(pin, i)
"""


##################
# sync, ie data needed for processing
# do as early as possible ?, to give time to call back to run, before going in loop (which need the value)
# order ?
##################

# do not care synching valve and pump now. not used if going to deep sleep
to_sync = [vpin.vpin_watering, vpin.vpin_day, vpin.vpin_nite, vpin_sleep]
nb_to_sync = len(to_sync)
nb_sync = 0 # global, incremented in virtual_sync call backs

s = "%s. synching" %get_stamp()
print(s)
log.info(s)
blynk_con.virtual_write(vpin_terminal, s)

for x in to_sync:
    blynk_con.virtual_sync(x) 


# thread to reset if ping fails
print("start ping thread")
_thread.start_new_thread(ping_thread, ("192.168.1.1",30, logging))


################
# synching
# DO AFTER CALL BACK DEFINITION ????
# give time to virtual_sync call back to happen, 
# otherwize could enter deep sleep with default value and not widget values
# or test ALL call backs happened
################

# make sure the value of sleep button is valid (ie synched)
print("wait for sleep button to synch")
i = 0
while sleep_has_synced == False:
    sleep(1)
    i = i + 1
    if i>3:
        #blynk_con.virtual_sync(vpin_sleep) # ceinture et bretelles
        pass 

    if i > 20:
        s = "%s: sleep button did not sync. reset" %get_stamp()
        blynk_con.virtual_write(vpin_terminal, s)
        print(s)
        log.error(s)
        disconnect_and_reset(s)

# check call backs needed in case of deep sleep
for i in range(30):
    print("sync'ed: %d out of %d" %(nb_sync, nb_to_sync))
    if nb_to_sync == nb_sync:
        break
    sleep(1) # not a good idea for battery powered and deep sleep .. but well ..


if button_sleep == False:
    # needed if running 
    # assumes call back will happen long before anyone use the app to start ralay
    # sync relay as well. so could start watering as soon as wakes up from deep sleep (and deep sleep was disabled)
    to_sync = [vpin_button_pump, vpin_button_valve, vpin_slider_pump, vpin_slider_valve]
    for x in to_sync:
        blynk_con.virtual_sync(x) 


#########################
# LOOP
#########################

s = "%s. starts processing. sleep mode: %s" %(get_stamp(),bool(button_sleep))
blynk_con.virtual_write(vpin_terminal, s)
print(s)
logging.info(s)

# update status
if button_sleep == False:
    s = "%s. running without sleep" %get_stamp()
    blynk_con.virtual_write(vpin_terminal, s)
    blynk_con.virtual_write(vpin_status, s)
    print(s)
    logging.info(s)
else:
    pass
    # status updated later 

    

while True:

    # if button sleep active, enter deep sleep for a duration depending on the hour of day (more "reactive end of afternoon")
    # ie manage energy

    try:
        if button_sleep:
            
            (year, month, mday, hour, minute, second, weekday, yearday) = localtime()

            # deep sleep duration depends on hour 

            if hour in watering_range:
                d = deep_sleep_duration_mn["watering"]

                s = "%s. sleep for %dmn" %(get_stamp(), d)
                blynk_con.virtual_write(vpin_status, s)

                s = "%s: %d in watering range. deep sleep for %dmn" %(get_stamp(),hour, d)
                disconnect_and_deepsleep(s,d*60)  # d in sec
                

            elif hour in nite_range:
                d = deep_sleep_duration_mn["nite"]

                s = "%s. sleep for %dmn" %(get_stamp(), d)
                blynk_con.virtual_write(vpin_status, s)

                s = "%s: %d in nite range. deep sleep for %dmn" %(get_stamp(),hour, d)
                disconnect_and_deepsleep(s,d*60)  # d in sec
            
            
            else:
                d = deep_sleep_duration_mn["day"]

                s = "%s. sleep for %dmn" %(get_stamp(), d)
                blynk_con.virtual_write(vpin_status, s)

                s = "%s: %d in day range. deep sleep for %dmn" %(get_stamp(),hour, d)
                disconnect_and_deepsleep(s,d*60)  # d in sec
    

        # active sleep
        # could also just turn wifi off
        else:

            sleep(10)
            if repl_started: 
                print('REPL', end="")
            else:
                print('.', end="")

    except KeyboardInterrupt:
        s= "got KeyboardInterrupt. disconnect and reset"
        disconnect_and_reset(s)
        

    except Exception as e:
        s = "%s exception non keyboard interupt %s. disconnect and reset" %(get_stamp(), str(e))
        disconnect_and_reset(s)
