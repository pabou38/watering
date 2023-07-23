
from machine import Pin, I2C
import i2c_addresses

##########
# i2c
##########

# ESP32
# classmachine.I2C(id, *, scl, sda, freq=400000, timeout=50000)
# There are two hardware I2C peripherals with identifiers 0 and 1. 
# Any available output-capable pins can be used for SCL and SDA but the defaults are given below. 
# default pin
# i2c = I2C(1, scl=Pin(25), sda=Pin(26), freq=400000)
# i2c = I2C(0, scl=Pin(18), sda=Pin(19), freq=400000)


# Software I2C (using bit-banging) works on all output-capable pins, and is accessed via the machine.SoftI2C class:
# classmachine.SoftI2C(scl, sda, *, freq=400000, timeout=50000)

def create_i2c(port, gpio_scl, gpio_sda):
  print("start i2c and scan")

  i2c = I2C(port,scl=Pin(gpio_scl), sda=Pin(gpio_sda))

  #  if not (0, Warning: I2C(-1, ...) is deprecated, use SoftI2C(...) instead

  devices = i2c.scan()

  if len(devices) == 0:
    print("no i2c devices")
    return(None)

  else:
    print ("devices list: ", devices) 
    print ("devices in hexa:", end= " ")
    for x in devices:
      print (hex(x), end= ' ')
    print(' ')

    for x in devices:
      try:
          print("==> found: %s" %i2c_addresses.i2c_addresses[x] , end = ' ')
      except Exception as e:
          pass
      print(' ')

    return(i2c)

if __name__ == "__main__":
  port = 0
  gpio_sda = 21
  gpio_scl = 22

  i2c = create_i2c(0, gpio_scl, gpio_sda) # create and scan
  
  if i2c is None:
    print("cannot create i2c")
  else:
    print("i2c created")


