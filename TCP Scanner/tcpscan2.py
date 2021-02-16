#CommNets Project 2
#Kevin Jiang

import sys
import socket
import errno
import subprocess
import os
import signal
import time

def __getOS__(ttl, windowsize):
    if ttl == 64:
        if windowsize == 5840:
            return "Linux"
        elif windowsize == 5720:
            return "Google's customized Linux"
        elif windowsize == 65535:
            return "FreeBSD"
    elif ttl == 128:
        if windowsize == 65535:
            return "Windows XP"
        elif windowsize == 8192:
            return "Windows 7, Vista and Server 2008"
    elif ttl == 255:
        if windowsize == 4128:
            return "Cisco Router"
            
    return "Unknown OS"

def __tcpscan__(host, port):
    try:
        PID = os.fork()
        if PID == 0:
            tcpcommand = "sudo tcpdump src " + host + "-G 0.5 -c 1 -w hostdump.pcap 2> /dev/null &"
            os.system(tcpcommand)
            exit()
            
        elif PID > 0:
            flag = 0
            timecount = 0
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP)
            sock.settimeout(0.2)
            errornum = sock.connect_ex((host, port))
            
            while flag == 0:
                
                if errornum == 0:
                    tshcommand = "tshark -r hostdump.pcap -T fields -e tcp.window_size_value | >> WindowSize.txt"
                    os.system(tshcommand)
                    f = open("WindowSize.txt", 'r')
                    ttl = sock.getsockopt(socket.IPPROTO_IP, socket.IP_TTL)
                    windowsize = f.readline()
                    f.close()
                    service = socket.getservbyport(port)
                    OS = __getOS__(ttl,int(windowsize))
                    print("Port " + str(port) + " is open, default service is: " + service + ", TTL: " + str(ttl) + ", Window Size: " + windowsize + ", OS: " + str(OS))
                    sock.close()
                    flag = 1
                    
                elif errornum != 0:
                    #time.sleep(0.1)
                    #timecount = timecount + 1
                    #if timecount >= 5:
                    flag = 1

    except KeyboardInterrupt:
        print("Error: User terminated program")
        sys.exit()
    except socket.error:
        print("Error: Unable to connect to Host: " + host + ", Port: " + str(port))
    except socket.gaierror:
        print("Error: Host does not exist")
        sys.exit()

if __name__ == "__main__":
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

    print("Please wait while program scans active ports...\n")
    for port in ports:
        __tcpscan__(host,port)
    exit(0)
