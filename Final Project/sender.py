# Written by S. Mevawala, modified by Kevin Jiang and Yuecen Wang

import logging
import socket

import channelsimulator
import utils
import sys
import math

class Sender(object):

    def __init__(self, inbound_port=50006, outbound_port=50005, timeout=5, debug_level=logging.INFO):
        self.logger = utils.Logger(self.__class__.__name__, debug_level)

        self.inbound_port = inbound_port
        self.outbound_port = outbound_port
        self.simulator = channelsimulator.ChannelSimulator(inbound_port=inbound_port, outbound_port=outbound_port,
                                                           debug_level=debug_level)
        self.simulator.sndr_setup(timeout)
        self.simulator.rcvr_setup(timeout)

    def send(self, data):
        raise NotImplementedError("The base API class has no implementation. Please override and add your own.")


class BogoSender(Sender):

    def __init__(self):
        super(BogoSender, self).__init__()

    def send(self, data):
        self.logger.info("Sending on port: {} and waiting for ACK on port: {}".format(self.outbound_port, self.inbound_port))
        while True:
            try:
                self.simulator.u_send(data)  # send data
                ack = self.simulator.u_receive()  # receive ACK
                self.logger.info("Got ACK from socket: {}".format(
                    ack.decode('ascii')))  # note that ASCII will only decode bytes in the range 0-127
                break
            except socket.timeout:
                pass


class RDTsender(BogoSender):

    def __init__(self):
        super(RDTsender, self).__init__()
    
    def send(self, data):
        self.logger.info("Sending on port: {} and waiting for ACK on port: {}".format(self.outbound_port, self.inbound_port))
        datalen = len(data)
        checksumlen = 3
        seqnumlen = 1
        framelen = 1024 - checksumlen - seqnumlen
        framenum = datalen/framelen
        print("Frame Number is " + str(framenum) + "\n")
        nextseqNum = 0
        print("Sequence Number is " + str(nextseqNum) + "\n")
        for i in range(1,framenum+2):
            print("Loop " + str(i) + "\n")
            if i < framenum:
                currentframe = data[(i-1)*framelen:i*framelen]
            else:
                currentframe = data[(i-1)*framelen:datalen]
                    
            if nextseqNum == 0:
                checksum = makecs(currentframe, nextseqNum)
                sndpkt = make_pkt(0, currentframe, checksum)
                while nextseqNum == 0:
                    try:
                        self.simulator.u_send(sndpkt)  # send data
                        print("Packet with sequence number " + str(nextseqNum) + " has been sent\n")
                        ack = self.simulator.u_receive()  # receive ACK
                        print("ACK with sequence number " + str(nextseqNum) + " has been received\n")
                        ackData = ack[:1020]
                        if isCorrupted(ack) == False:
                            print("Uncorrupted\n")
                            #self.logger.info("Got ACK from socket:{}".format(ackData.decode('ascii')))
                            if isACK(ack,0) == True:
                                nextseqNum = 1
                            else:
                                print("Wrong Sequence Number, resend\n")
                        else:
                            print("Corrupted, resend\n")
                    except socket.timeout:
                        print("Timeout, resend")
            
            else:
                checksum = makecs(currentframe, nextseqNum)
                sndpkt = make_pkt(1, currentframe, checksum)
                while nextseqNum == 1:
                    try:
                        self.simulator.u_send(sndpkt)  # send data
                        print("Packet with sequence number " + str(nextseqNum) + " has been sent\n")
                        ack = self.simulator.u_receive()  # receive ACK
                        print("ACK with sequence number " + str(nextseqNum) + " has been received\n")
                        ackData = ack[:1020]
                        if isCorrupted(ack) == False:
                            print("Uncorrupted\n")
                            #self.logger.info("Got ACK from socket:{}".format(ackData.decode('ascii')))
                            if isACK(ack,1) == True:
                                nextseqNum = 0
                            else:
                                print("Wrong Sequence Number, resend\n")
                        else:
                            print("Corrupted, resend\n")
                    except socket.timeout:
                        print("Timeout, resend")
                        

def make_pkt(seqNum, frame, checksum):
    framelen = len(frame)
    packet = bytearray(framelen+4)
    packet[:framelen] = frame
    packet[framelen:framelen+3] = checksum
    packet[framelen+3] = seqNum
    return packet
        
    
def isCorrupted(packet):
    framelen = len(packet) - 4
    datasum = sum(packet[:framelen])        
    checksum = bytesToNumber(packet[framelen:framelen+3])
    seqNum = packet[framelen + 3]
    if datasum + checksum - seqNum == 16777215:
        return False
    else:
        return True
    
def isACK(packet, seqNum):
    ackseqNum = packet[len(packet)-1]
    if (ackseqNum == seqNum):
        return True
    else:
        return False
                        
def makecs(frame, nextseqNum):
    datasum = sum(frame)     
    checksum = 16777215 - datasum + nextseqNum
    return numberToByteArray(checksum, 3)	

                      
def bytesToNumber(b):
    total = 0
    multiplier = 1
    for count in xrange(len(b)-1, -1, -1):
        byte = b[count]
        total += multiplier * byte
        multiplier *= 256
    return total

def numberToByteArray(n, howManyBytes=None):
    if howManyBytes == None:
        howManyBytes = numBytes(n)
    b = bytearray(howManyBytes)
    for count in xrange(howManyBytes-1, -1, -1):
        b[count] = int(n % 256)
        n >>= 8
    return b


if __name__ == "__main__":
    # test out BogoSender
    DATA = bytearray(sys.stdin.read())
    sndr = RDTsender()
    sndr.send(DATA)
    sys.exit()
