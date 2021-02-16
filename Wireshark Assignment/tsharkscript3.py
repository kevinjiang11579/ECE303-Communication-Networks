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

infolist = list(dict.fromkeys(infolist))

print("Without duplicates:\n")
print(infolist, sep='\n')
