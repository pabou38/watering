
import onewire, ds18x20
from machine import Pin
from utime import sleep_ms


##############################################
# DS18B20 aka dallas vcc 3 to 5V 4.7k resistor between vcc and data
# arg is a GPIO number. Pin object created inside
# nb (of sensor) not really used
# return list
##############################################

def read_dallas(gpio, nb=2):

  print('read %d temp sensors on gpio %d' %(nb, gpio) ) # nb not used

  try:
    dat = Pin(gpio, Pin.OUT)

    # create the onewire object
    ds = ds18x20.DS18X20(onewire.OneWire(dat))

    # scan for devices on the bus
    roms = ds.scan()
    print('ds18b20 scan, found devices: ', roms)

    temp = []
    ds.convert_temp()
    sleep_ms(750)
    for rom in roms: # read all sensors on this gpio bus
      
      #2 sensors on same bus (ie data GPIO). how do I know which one is one ? . may be better to have each sensor on a separate bus. 
      
      t = ds.read_temp(rom)
      t = round(t,1)
      #print('dallas: ', t)
      temp.append(t)
    
    print('temp array: ' , temp)

    if len(temp) != nb:
      return(temp) # handle error later
    else:
      return(temp) # seems should be interpreted as (mid, top)

  except Exception as e:
    print('exception reading temp sensors ' , str(e))
    return([])


if __name__ == "_main__":

  gpio_temp = 10


  l = read_dallas(gpio_temp, nb=2) # Pin created in function
  if l != []:
      print(l)
  else:
    print('error temp')