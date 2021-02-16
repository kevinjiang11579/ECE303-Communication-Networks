#Script for processing results of a filter using TShark
#Kevin Jiang

import os
import subprocess

filename = input("Enter .pcap file name:")

command = "tshark -r " + filename + " -Y \"ssl.handshake.type == 1\" -T fields -e ip.src -e ip.dst -e ssl.handshake.extensions_server_name | tee TLSFilter.txt"

os.system(command)

f = open('TLSFilter.txt', 'r')

infolist = []

icount = 0
line = f.readline();
line = line[:-1]
while line:
    infolist.append(line)
    if icount > 0:
        for j in range(icount-1, -1, -1):
            if infolist[icount] == infolist[j]:
                del infolist[icount]
                icount = icount - 1
    icount = icount + 1
    line = f.readline()
    line=line[:-1]

f.close()

print("Without Duplicates:\n")
for details in infolist:
    detailarr = details.split()
    org = subprocess.check_output("whois " + detailarr[1] + " | grep -m 1 -e Organization -e organisation -e descr", shell=True)
    orgstr = str(org)
    orgarr = orgstr.split(':')
    orgwithspace = orgarr[1][:-3]
    orgnospace = orgwithspace.strip()
    print("Source: " + detailarr[0] + ", Destination: " + detailarr[1] + ", Server name: " + detailarr[2] + ", Organization: " + orgnospace + '\n')
