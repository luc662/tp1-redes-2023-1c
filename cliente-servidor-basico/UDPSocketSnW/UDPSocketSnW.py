import socket
import struct

class UDPSocketSnW:

    def __init__(self, address):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.address = address
        self.sequence_number = 0
        self.acknowledgement_number = 0
        self.buffer_size = 1024
        self.bit_FIN = 0
        self.bit_ACK = 0

    def bind(self,address):
        self.socket.bind(address)

    def send(self, data):
        packet = struct.pack('IIII', self.sequence_number, self.acknowledgement_number, self.bit_ACK, self.bit_FIN) + data
        self.socket.sendto(packet, self.address)

        while True:
            try:
                self.socket.settimeout(1.0)
                data, address = self.socket.recvfrom(self.buffer_size)
                ack_sequence_number, ack_acknowledgement_number, self.bit_ACK, self.bit_FIN = struct.unpack('IIII', data[:16])
                if ack_sequence_number == self.acknowledgement_number:
                    self.acknowledgement_number += 1
                    break
            except socket.timeout:
                self.socket.sendto(packet, self.address)

    def receive(self):
        data, self.address = self.socket.recvfrom(self.buffer_size)
        sequence_number, acknowledgement_number, bit_ACK, bit_FIN = struct.unpack('IIII', data[:16])
        
        if sequence_number == self.acknowledgement_number:
            self.acknowledgement_number += 1
            bit_ACK = 1
            ack_packet = struct.pack('IIII', sequence_number, self.acknowledgement_number, bit_ACK, 0)
            self.socket.sendto(ack_packet, self.address)

        if bit_FIN == 1:
            self.bit_ACK = 1
            self.bit_FIN = 1
            self.send()

        return data[16:]

    def close(self):
        self.bit_FIN = 1
        self.bit_ACK = 0
        self.send()

        self.receive()
        if self.bit_ACK == 1 and self.bit_FIN == 1:
            self.bit_FIN = 0
            self.bit_ACK = 1
            self.send()
        else:
            print('falla algo en la comunicacion de cierre')
