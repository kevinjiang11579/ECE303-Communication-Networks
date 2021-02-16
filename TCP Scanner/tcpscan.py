#CommNets Project 2
#Kevin Jiang

import sys
import socket
import errno
import subprocess
import os
import signal
import time


def __tcpscan__(host, port):
    try:
        tcpcommand = "sudo tcpdump src " + host + " -c 1 -w hostdump.pcap &"
        os.system(tcpcommand)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP)
        sock.settimeout(0.1)
        errornum = sock.connect_ex((host, port))
        if errornum == 0:
            tshcommand = "tshark -r hostdump.pcap -T fields -e tcp.window_size_value | >> WindowSize.txt"
            os.system(tshcommand)
            f = open("WindowSize.txt", 'r')
            ttl = sock.getsockopt(socket.IPPROTO_IP, socket.IP_TTL)
            windowsize = f.readline()
            f.close()
            service = socket.getservbyport(port)
            print("Port " + str(port) + " is open, default service is: " + service + ", TTL: " + str(ttl) + ", Window Size: " + windowsize)
            sock.close()
        time.sleep(1)    
        os.kill(os.getpid(), signal.SIGTERM)

    except KeyboardInterrupt:
        print("Error: User terminated program")
        sys.exit()
    except socket.error:
        print("Error: Unable to connect to Host: " + host + ", Port: " + str(port))
    except socket.gaierror:
        print("Error: Host does not exist")
        sys.exit()

if __name__ == '__main__':
    arg = sys.argv[1:]
    host = arg[0]
    if (len(arg) == 1):
        first = 1
        last = 1024
    elif (arg[1] == "-p"):
        portnums = arg[2].split(":")
        first = int(portnums[0])
        last = int(portnums[1])

    ports = list(range(first, last + 1))
    for port in ports:
        __tcpscan__(host,port)
    exit(0)
