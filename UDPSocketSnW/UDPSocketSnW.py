import socket
import struct
import logging
from logging import debug as db
logging.basicConfig(level=logging.DEBUG, format='%(message)s')
from random import random

class DestinoInaccesible(Exception):
    def __init__(self):
        super().__init__()

def log(msg):
    db(f'[UdpSkt] {msg}')

class UDPSocketSnW:
    def __init__(self, address):
        log(f'(start) conectarse a: {address}')
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.address = address
        self.sequence_number = 0
        self.expected_sequence_num = 0
        self.buffer_size = 1024
        self.header_size = 8
        self.send_retries = 23

    def send(self, data):
        log('send')
        packet = struct.pack('II', self.sequence_number, self.expected_sequence_num) + data
        log(f'(send) {self.sequence_number}, {self.expected_sequence_num}')
        self.socket.sendto(packet, self.address)
        log('(send) Enviado')

        log('(send) Esperando ACK (bucle)')
        for i in range(self.send_retries):
            log(f'(send-ack-loop) Intento: {i + 1}/{self.send_retries}. (1s)')
            self.socket.settimeout(1.0)
            log('(send-ack-loop) Recibir respuesta (ACK)')
            try:
                log('(send-ack-loop) esperando ack')
                data, address = self.socket.recvfrom(self.buffer_size)
                log(f'(send-ack-loop) recibimos de: {address}')
                ack_sequence_number, ack_expected_seq_number = struct.unpack('II', data[:8])
                self.expected_sequence_num += 1
                self.sequence_number += 1
                break
            except socket.timeout:
                log('(send-ack-loop) Timeout! Reenviando')
                self.socket.sendto(packet, self.address)
        else:
            raise DestinoInaccesible

    def recieve(self):
        log('recieve')
        self.socket.settimeout(None)
        data, address = self.socket.recvfrom(self.buffer_size)
        sequence_number, expected_seq_number = struct.unpack('II', data[:8])
        log('(recv) Paquete recibido')
        log(f'(recv) seq_num: {sequence_number}, expected_seq_num: {expected_seq_number}')

        log(f'(recv) Enviando ACK {sequence_number}, {self.expected_sequence_num}')
        ack_packet = struct.pack('II', sequence_number, self.expected_sequence_num)
        self.socket.sendto(ack_packet, address)
        log('(recv) ACK enviado')
        if sequence_number == self.sequence_number and expected_seq_number == self.expected_sequence_num:
            self.expected_sequence_num += 1
            self.sequence_number += 1
            return data[8:], address
        
        log(f'(recv) self.expected_seq_num: {self.expected_sequence_num}, recibimos seq_num: {sequence_number}')
        return None, address

    def bind(self, address):
        log(f'(bind): {address}')
        self.socket.bind(address)

