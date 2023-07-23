import ssd1306
from machine import Pin

def create_ssd1306(oled_width, oled_height, i2c):
  # oled 60, 0x3c
  print("create ssd1306 oled")
  try:
    
    # https://github.com/orgs/micropython/discussions/10820
    oled_reset = Pin(18, Pin.OUT, value=1)
    
    #https://randomnerdtutorials.com/micropython-oled-display-esp32-esp8266/
    #oled = ssd1306.SSD1306_I2C(oled_width, oled_height, i2c)
    oled = ssd1306.SSD1306_I2C(oled_width, oled_height, i2c) # using 32 on 64 oled makes char bigger

    # display version and errors counters from RTC memory
    oled.fill(0) # with black , 1 with white
    oled.text("ssd1306", 0, 0) # X,Y
    oled.text("init", 0, 10) # X,Y
    oled.show()
    return(oled)
    

  except Exception as e:
      print('Exception cannot create oled ' , str(e))
      return(None)

#################
# write list of lines 
# oled = None, no oled available
#################

def lines_oled(oled,l): # list of lines
  if oled is None:
    return()

  oled.fill(0)
  space = 10
  y=0
  
  for x in l:
    oled.text(x,0,y,1) # y)
    y = y + space
    
  oled.show()


if __name__ == "__main__":

  W= 128
  H= 64
  i2c = None
  oled = create_ssd1306(W,H,i2c)
  
  lines_oled(oled, ["hello", "esp"])
