import socket
import struct
import logging
from logging import debug as db
logging.basicConfig(level=logging.DEBUG, format='%(message)s')
from random import random

PACKET_LOSS=0.3


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
        self.COUNTER=0

    def send(self, data):
        log(f'(send-estado) seq_num: {self.sequence_number}')
        log(f'(send-estado) expected_seq_num: {self.expected_sequence_num}')

        log(f'(send) Enviar: {data}')
        log(f'(send) A: {self.address}')
        log('(send) Encapsulando payload')
        packet = struct.pack('II', self.sequence_number, self.expected_sequence_num) + data
        log('(send) Enviando paquete (unreliable)')
        self.socket.sendto(packet, self.address)

        log('(send) Esperando ACK (bucle)')
        _intentos = 400
        for i in range(_intentos):
            log(f'(send-ack-loop) Intento: {i+1}/{_intentos}')
            try:
                ''' SIMULACION DE PERDIDA DE PAQUETES '''
                p = random()
                if p<PACKET_LOSS:
                    log(f'(send) PACKET_LOSS con prob: {p}')
                    self.COUNTER+=1
                    log(f'PAQUETES PERDIDOS: {self.COUNTER}')
                    return
                ''' SIMULACION DE PERDIDA DE PAQUETES '''

                log('(send-ack-loop) Iniciar timer')
                self.socket.settimeout(1.0)
                log('(send-ack-loop) Recibir respuesta (ACK Hopefully)')
                data, address = self.socket.recvfrom(self.buffer_size)
                log('(send-ack-loop) Desempaquetar')
                ack_sequence_number, ack_expected_seq_number = struct.unpack('II', data[:8])                
                log(f'(send-ack-loop) ack_seq_num: {ack_sequence_number}, ack_expected_seq_num: {ack_expected_seq_number}')

                if ack_sequence_number == self.expected_sequence_num:
                    self.expected_sequence_num += 1
                    self.sequence_number += 1
                    log(f'(send-ack-loop) Incrementar sequence_number a: {self.sequence_number}')
                    log(f'(send-ack-loop) Incrementar expected_sequence_num a: {self.expected_sequence_num}')
                    break

            except socket.timeout:
                log('(send-ack-loop) Timeout!')
                log(f'(send-ack-loop) Reenviando: {packet}')
                log(f'(send-ack-loop) A: {self.address}')
                self.socket.sendto(packet, self.address)
        else:
            print('IMPLEMENTAR EXCEPTION')

        log('(send) fin send')

    def receive(self):
        log(f'(recv-estado) seq_num: {self.sequence_number}')
        log(f'(recv-estado) expected_seq_num: {self.expected_sequence_num}')
        data, address = self.socket.recvfrom(self.buffer_size)
        #log(f'(recv) de: {address}')
        #log(f'(recv) data: {data}')
        sequence_number, expected_seq_number = struct.unpack('II', data[:8])
        log(f'(recv) seq_num: {sequence_number}')
        log(f'(recv) expected_seq_num: {expected_seq_number}')
        log(f'(recv) payload: {data[8:]}')

        if sequence_number == self.expected_sequence_num:
            log(f'(recv) Enviar ACK')
            ack_packet = struct.pack('II', sequence_number, self.expected_sequence_num)
            self.socket.sendto(ack_packet, address)
            log(f'(recv) Enviado')
            self.expected_sequence_num += 1
            self.sequence_number += 1
            log(f'(recv) OK. Incrementar secuencia')

        log('(recv) fin recv')
        return data[8:],address

    def bind(self, address):
        log(f'(bind): {address} (deberia ser solo en el servidor, pero no nos metamos en capa de app)')
        self.socket.bind(address)
        log('(bind) fin bind')

    def close(self):
        self.send()

        self.receive()
        if self.bit_ACK == 1 and self.bit_FIN == 1:
            self.send()
        else:
            print('falla algo en la comunicacion de cierre')
