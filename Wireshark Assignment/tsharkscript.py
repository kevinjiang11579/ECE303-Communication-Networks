#Script for processing results of a filter using TShark
#Kevin Jiang

filename = input("Enter .pcap file name:")

import os

command = "tshark -r " + filename + " -Y \"ssl.handshake.type == 1\" -T fields -e ip.src -e ip.dst -e ssl.handshake.extensions_server_name | tee TLSFilter.txt"

os.system(command)

f = open('TLSFilter.txt', 'r')

infolist = []

icount = 0
line = f.readline();
while line:
    infolist.append(line)
    if icount > 0:
        for j in range(icount-1, 0):
            if infolist[icount] == infolist[j]:
                del infolist[-1]
                icount = icount - 1
                break
    icount = icount + 1
    line = f.readline()

print("Without duplicates:\n")
print(infolist, sep='\n')
