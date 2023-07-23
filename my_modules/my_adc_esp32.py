
from machine import ADC, Pin


# https://randomnerdtutorials.com/esp32-esp8266-analog-readings-micropython/


############
# ADC
#############

# On the ESP32, ADC functionality is available on pins 32-39 (ADC block 1) 
# and pins 0, 2, 4, 12-15 and 25-27 (ADC block 2). 
# ADC block 2 is also used by WiFi and so attempting to read analog values from block 2 pins when WiFi is active will raise an exception.

# Lolin D32
# Analog Input Pins	6 (VP, VN, 32, 33, 34, 35)
#    32, 33  input/output aka ADC1_4, ADC1_4
#    34, input only ADC1_6
#    36, 39  input only, aka SensVP, SensVN, aka ADC1_0, ADC1_3
#    35 not breaked out. 100K 100K voltage divisor Vbat GND

#Analog Output Pins	2 (25, 26)

# Per design the ESP32 ADC reference voltage is 1100 mV, however the true reference voltage can range 
# from 1000 mV to 1200 mV among different chips
#   use attenuation to extend input range 
#   The ADC is less linear close to the reference voltage (particularly at higher attenuations) and has a minimum measurement voltage around 100mV, voltages at or below this will read as 0. 
#   To read voltages accurately, it is recommended to use the read_uv() method (see below).

# The ESP32 ADC pins don’t have a linear behavior. 
# You’ll probably won’t be able to distinguish between 0 and 0.1V, or between 3.2 and 3.3V.
# https://randomnerdtutorials.com/esp32-pinout-reference-gpios/


# ESP 32 ADC 12 bit , ie O to 4095

def esp32_adc(pin=35):

    ref_voltage = 3.3

    adc = ADC(Pin(pin))
    # To read voltages above the reference voltage, apply input attenuation with the atten keyword argument. 
    # Valid values (and approximate linear measurement ranges) are:

    # ADC.ATTN_0DB: No attenuation (100mV - 950mV)
    # ADC.ATTN_2_5DB: 2.5dB attenuation (100mV - 1250mV)
    # ADC.ATTN_6DB: 6dB attenuation (150mV - 1750mV)
    # ADC.ATTN_11DB: 11dB attenuation (150mV - 2450mV)  

    # random nerd 

    #ADC.ATTN_0DB — the full range voltage: 1.2V
    #ADC.ATTN_2_5DB — the full range voltage: 1.5V
    #ADC.ATTN_6DB — the full range voltage: 2.0V
    #ADC.ATTN_11DB — the full range voltage: 3.3V

    adc.atten(ADC.ATTN_11DB)   # 4.2 V /2 = 2.1 Volt  
    
    val1 = adc.read_u16()  # read a raw analog value in the range 0-65535

    #This method uses the known characteristics of the ADC and per-package eFuse values - set during manufacture - to return a calibrated input voltage (before attenuation) in microvolts. The returned value has only millivolt resolution (i.e., will always be a multiple of 1000 microvolts).
    #The calibration is only valid across the linear range of the ADC. In particular, an input tied to ground will read as a value above 0 microvolts. Within the linear range, however, more accurate and consistent results will be obtained than using read_u16() and scaling the result with a constant."""
    val_mv = adc.read_uv()/1000   # read an analog value in microvolts

    adc_read = adc.read() # legacy method. This method returns the raw ADC value ranged according to the resolution of the block, e.g., 0-4095 for 12-bit resolution.
    print ("raw adc value 0 to 4095 %d, analog value in mv %0.1f, u16 %d" %(adc_read, val_mv, val1))

    vbat = round((2*adc_read/4096) * ref_voltage, 2)

    #raw adc value 0 to 4095 2455, analog value in mv 2131.0, u16 39289
    # read vbat with adc: vbat: 3.96


    return(vbat)