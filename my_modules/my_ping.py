
import uping
# https://forum.micropython.org/viewtopic.php?t=5287


def ping_ip(ip):

    (a,b) = uping.ping(ip, count=2, timeout=5000, interval=10, quiet=True, size=64)
    # @return: tuple(number of packet transmitted, number of packets received)

    #print(a,b)
    if a!= b:
        return(False)
    else:
        return(True)
    
if __name__ == "__main__":
    print("ping")

    ip = "192.168.1.1"
    ret = ping_ip(ip)
    print("ping returned: %s" %ret)







