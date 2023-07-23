
from machine import DEEPSLEEP, deepsleep, reset_cause, DEEPSLEEP_RESET, PWRON_RESET, HARD_RESET  

##### RTC GPIO

# Some ESP32 pins (0, 2, 4, 12-15, 25-27, 32-39) are connected to the RTC during deep-sleep 
# and can be used to wake the device with the wake_on_ functions
# Pins 34-39 are input only, and also do not have internal pull-up resistors

# Lolin D32
# 0,2,4 , 12,13,14,15, 25,26,27 32,33   RTC and input/output. RETAIN pull, disable to save power
# 34,36,39   RTC and input only
# 35 internaly connected


##### PULL
# The output-capable RTC pins (all except 34-39) will retain their pull-up or pull-down resistor configuration when entering deep-sleep.
# If the pull resistors are not actively required during deep-sleep and are likely to cause current leakage (for example a pull-up resistor is connected to ground through a switch), 
# then they should be disabled to save power before entering deep-sleep mode:
# pin.init(pull=None)

##### PAD HOLD
# https://docs.micropython.org/en/latest/esp32/quickref.html#pins-and-gpio
# https://docs.micropython.org/en/latest/esp32/quickref.html#deep-sleep-mode

"""
hold =
The hold= keyword argument to Pin() and Pin.init() will enable the ESP32 “pad hold” feature. 
When set to True, the pin configuration (direction, pull resistors and output value) will be held 
and any further changes (including changing the output level) will not be applied. 
Setting hold=False will immediately apply any outstanding pin configuration changes and release the pin. 
Using hold=True while a pin is already held will apply any configuration changes and then immediately 
reapply the hold.

opin = Pin(19, Pin.OUT, value=1, hold=True) # hold output level
ipin = Pin(21, Pin.IN, Pin.PULL_UP, hold=True) # hold pull-up


use in deep sleep
Output-configured RTC pins will also retain their output direction and level in deep-sleep if pad hold is enabled with the hold=True argument to Pin.init().

Non-RTC GPIO pins will be disconnected by default on entering deep-sleep. 
Configuration of non-RTC pins - including output level - can be retained by enabling pad hold 
on the pin  and enabling GPIO pad hold during deep-sleep:
# enable pad hold in deep-sleep for non-RTC GPIO
esp32.gpio_deep_sleep_hold(True)
"""

def print_reset_cause():
	cause = reset_cause()

	"""
	machine.DEEPSLEEP_RESET 5
	machine.PWRON_RESET 0
	machine.HARD_RESET 6
	machine.WDT_RESET 1
	machine.SOFT_RESET 4
	"""
	rst = ["PWRON RESET", "WDT RESET", "cause 2", "cause 3", "SOFT RESET", "DEEP SLEEP RESET", "HARD RESET"]

	# rst:0xc (SW_CPU_RESET),boot:0x13 (SPI_FAST_FLASH_BOOT)
	# rst:0x5 (DEEPSLEEP_RESET),boot:0x13 (SPI_FAST_FLASH_BOOT)
	# rst:0x1 (POWERON_RESET),boot:0x13 (SPI_FAST_FLASH_BOOT)


	if cause == DEEPSLEEP_RESET:
		print('BOOT: woke from a deep sleep')
	else:
		print('BOOT cause: %s (%d) ' %(rst[cause], cause))

	return(cause)

def enter_deep_sleep(ms:int, pull_to_disable=[]):
	for p in pull_to_disable:
		print("disable pull on pin %s to save power" %p)
		p.init(pull=None)

	print ("enter deep sleep %d ms" %ms)
	deepsleep(ms)
	  
  