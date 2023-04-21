import socket
import struct
import logging
from logging import debug as db
logging.basicConfig(level=logging.DEBUG, format='%(message)s')
from random import random

PACKET_LOSS = 0

def log(msg):
    db(f'[UdpSkt] {msg}')

class UDPSocketSnW:
    def __init__(self, address):
        log(f'(start) address: {address}')
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.address = address
        self.sequence_number = 0
        self.expected_sequence_num = 0
        self.buffer_size = 1024
        self.header_size = 8
        self.send_retries = 500
        self.packet_loss_counter = 0
        self.packet_loss_activated = True

    def send(self, data):
        log('send')
        packet = struct.pack('II', self.sequence_number, self.expected_sequence_num) + data
        self.socket.sendto(packet, self.address)
        log('(send) Esperando ACK (bucle)')
        for i in range(self.send_retries):
            log(f'(send-ack-loop) Intento: {i + 1}/{self.send_retries}')
            log('(send-ack-loop) Iniciar timer (1s)')
            self.socket.settimeout(1.0)
            log('(send-ack-loop) Recibir respuesta (ACK)')
            try:
                if self.packet_loss_activated:
                    r = random()
                    if r > PACKET_LOSS:
                        data, address = self.socket.recvfrom(self.buffer_size)
                        ack_sequence_number, ack_expected_seq_number = struct.unpack('II', data[:8])
                        if ack_sequence_number == self.expected_sequence_num:
                            self.expected_sequence_num += 1
                            self.sequence_number += 1
                            break
                    else:
                        log(f'(send) PACKET_LOSS con prob: {r}')
                        self.packet_loss_counter += 1
                        log(f'(send) PAQUETES PERDIDOS: {self.packet_loss_counter}')
            except socket.timeout:
                log('(send-ack-loop) Timeout!')
                log(f'(send-ack-loop) Reenviando: {packet}')
                #log(f'(send-ack-loop) A: {self.address}')
                self.socket.sendto(packet, self.address)
        else:
            log('IMPLEMENTAR EXCEPTION')
        log('(send) fin send')

    def recieve(self):
        log('recieve')
        data, address = self.socket.recvfrom(self.buffer_size)
        sequence_number, expected_seq_number = struct.unpack('II', data[:8])

        log(f'(recv) {sequence_number}:{expected_seq_number}')
        log(f'{data}')

        ack_packet = struct.pack('II', sequence_number, self.expected_sequence_num)
        self.socket.sendto(ack_packet, address)
        if sequence_number == self.expected_sequence_num:
            self.expected_sequence_num += 1
            self.sequence_number += 1
            return data[8:], address
        return None, address

    def bind(self, address):
        log(f'(bind): {address}')
        self.socket.bind(address)

    def close(self):
        log('close')
        self.send()
        self.recieve()
        if self.bit_ACK == 1 and self.bit_FIN == 1:
            self.send()
        else:
            print('falla algo en la comunicacion de cierre')
