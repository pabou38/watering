from machine import RTC

####################################
#  RTC
####################################

def init_RTC(init):
    # pass list of bytes eg  [1, 1, 0, 0, 0]
    # passing 0 just init an empty b''

    ###########################################
    # RTC 16KB of SRAM
    ###########################################

    # index into RTC memory, 2 bytes
    # r.memory()[0] 

    r = RTC()
    mem = r.memory()  # content survives deep sleep
    print('RTC memory: ', mem)

    if (mem == b''):
        print('RTC memory empty. initializing..')
        #r.memory(bytearray(0b00000000)) # need object with buffer protocol

        # store x bytes in RTC  
        r.memory(bytes(init)) # need object with buffer protocol
        mem = r.memory() # type bytes, immutable
        print('RTC memory: ', mem) #  b'\x01\x01\x00\x00\x00'

    else:
        print("RTC already initialized")

    return(r)


# return RTC at index i
def read_RTC(r,i):
    return(r.memory() [i])


# set RTC at index i with value
def set_RTC(r, i, value):
  
    x=r.memory()
    x=bytearray(x) #make mutable
    x[i]=value
    r.memory(x)


# to test a value  r.memory() [i]

# to set a value 
# x=r.memory()
# x=bytearray(x) make mutable
# x[i]=1
# r.memory(x)

# bit operation possible as well
# r.memory and wifi_error == 0 , test if bit not set
# r.memory (r.memory() or wifi_error), set bit
# r.memory (r.memory() and not wifi_error) reset bit