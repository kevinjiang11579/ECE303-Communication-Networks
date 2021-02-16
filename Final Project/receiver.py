# Written by S. Mevawala, modified by Kevin Jiang and Yuecen Wang

import logging

import channelsimulator
import utils
import sys
import socket

class Receiver(object):

    def __init__(self, inbound_port=50005, outbound_port=50006, timeout=15, debug_level=logging.INFO):
        self.logger = utils.Logger(self.__class__.__name__, debug_level)

        self.inbound_port = inbound_port
        self.outbound_port = outbound_port
        self.simulator = channelsimulator.ChannelSimulator(inbound_port=inbound_port, outbound_port=outbound_port,
                                                           debug_level=debug_level)
        self.simulator.rcvr_setup(timeout)
        self.simulator.sndr_setup(timeout)

    def receive(self):
        raise NotImplementedError("The base API class has no implementation. Please override and add your own.")


class BogoReceiver(Receiver):
    ACK_DATA = bytes(123)

    def __init__(self):
        super(BogoReceiver, self).__init__()

    def receive(self):
        self.logger.info("Receiving on port: {} and replying with ACK on port: {}".format(self.inbound_port, self.outbound_port))
        while True:
            try:
                 data = self.simulator.u_receive()  # receive data
                 self.logger.info("Got data from socket: {}".format(
                     data.decode('ascii')))  # note that ASCII will only decode bytes in the range 0-127
	         sys.stdout.write(data)
                 self.simulator.u_send(BogoReceiver.ACK_DATA)  # send ACK
            except socket.timeout:
                sys.exit()
                

class rdtReceiver(Receiver):
    def _init_(self):
        super(rdtReceiver, self)._init_()
    def receive(self):
        self.logger.info("Receiving on port: {} and replying with ACK on port: {}".format(self.inbound_port, self.outbound_port))
        while True:
            try:
                rawData = self.simulator.u_receive()
                #print("Received\n")
                lastCorrect = rawData
                # self.logger.info("Raw data: {}", format(data))
                length = len(rawData)
                checksum = rawData[length-4: length-1]
                seq = rawData[length-1]
                data = rawData[:length-4]
                summing = 0
                summing = sum(data)
                expectedSeq = 0
                if summing + bytesToNumber(checksum) - seq == 16777215:
                    #print("Uncorrupted\n")
                    # message = bytearray("ACK","ascii")
                    # message.append(int(seq))
                    # self.logger.info("sending ACK : {}", format.(list(message)))
                    if seq == expectedSeq:
                        self.logger.info("Got data from socket: {}".format(data.decode('ascii')))
                        sys.stdout.write(data)
                        expectedSeq = 1 - expectedSeq
                        self.simulator.u_send(rawData)
                        #print("ACK sent\n")
                    else:
                        #print("Wrong Sequence Number\n")
                        ACK = bytearray(1024)
                        ACK[:length-4] = numberToByteArray(734582,length-4)
                        ACK[length-4:length-1] = numberToByteArray(16777215 - sum(ACK[:length-4])+1-expectedSeq,3)
                        ACK[length-1] = 1-expectedSeq
                        self.simulator.u_send(ACK)
                        #print("Wrong ACK sent\n")
                else:
                    #print("Corrupted\n")
                    #wrongData = bytearray(1024)
                    #wrongData[1023] = 1-expectedSeq
                    #wrongData[:1020] = data
                    #ackChecksum = 16777215 - summing
                    #wrongData[1020:1023] = numberToByteArray(ackChecksum, 3)
                    ACK = bytearray(1024)
                    ACK[:length-4] = numberToByteArray(734582,length-4)
                    ACK[length-4:length-1] = numberToByteArray(16777215 - sum(ACK[:length-4])+1-expectedSeq,3)
                    ACK[length-1] = 1-expectedSeq
                    self.simulator.u_send(ACK)
                    #print("Wrong ACK sent\n")
            except socket.timeout:
                sys.exit()
                
            

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
    # test out BogoReceiver
   # rcvr = BogoReceiver()
    rcvr = rdtReceiver()
    rcvr.receive()
