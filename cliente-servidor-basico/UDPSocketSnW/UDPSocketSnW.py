import socket
import struct
import logging
from random import random

PACKET_LOSS=0.3

class UDPSocketSnW:

    def __init__(self, address):
        logging.basicConfig(level=logging.DEBUG, format='%(message)s')
        logging.debug(f'(start) address: {address}') 
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.address = address
        self.sequence_number = 0
        self.expected_sequence_num = 0
        self.buffer_size = 1024
        self.packet_loss_counter = 0
        self.ack_retries = 10

    def send(self, data):
        logging.debug(f'(send-estado) seq_num: {self.sequence_number}')
        logging.debug(f'(send-estado) expected_seq_num: {self.expected_sequence_num}')

        logging.debug(f'(send) Enviar: {data}')
        logging.debug(f'(send) A: {self.address}')
        logging.debug('(send) Encapsulando payload')
        packet = struct.pack('II', self.sequence_number, self.expected_sequence_num) + data
        logging.debug('(send) Enviando paquete (unreliable)')
        self.socket.sendto(packet, self.address)

        logging.debug('(send) Esperando ACK (bucle)')
        for i in range(self.ack_retries):
            logging.debug(f'(send-ack-loop) Intento: {i+1}/{self.ack_retries}')
            try:
                ''' SIMULACION DE PERDIDA DE PAQUETES '''
                p = random()
                if p < PACKET_LOSS:
                    logging.debug(f'(send) PACKET_LOSS con prob: {p}')
                    self.packet_loss_counter += 1
                    logging.debug(f'PAQUETES PERDIDOS: {self.packet_loss_counter}')
                    continue
                ''' SIMULACION DE PERDIDA DE PAQUETES '''

                logging.debug('(send-ack-loop) Iniciar timer')
                self.socket.settimeout(1.0)
                logging.debug('(send-ack-loop) Recibir respuesta (ACK Hopefully)')
                data, address = self.socket.recvfrom(self.buffer_size)
                logging.debug('(send-ack-loop) Desempaquetar')
                ack_sequence_number, ack_expected_seq_number = struct.unpack('II', data[:8])                
                logging.debug(f'(send-ack-loop) ack_seq_num: {ack_sequence_number}, ack_expected_seq_num: {ack_expected_seq_number}')

                if ack_sequence_number == self.expected_sequence_num:
                    self.expected_sequence_num += 1
                    self.sequence_number += 1
                    logging.debug(f'(send-ack-loop) Incrementar sequence_number a: {self.sequence_number}')
                    logging.debug(f'(send-ack-loop) Incrementar expected_sequence_num a: {self.expected_sequence_num}')
                    break

            except socket.timeout:
                logging.debug('(send-ack-loop) Timeout!')
                logging.debug(f'(send-ack-loop) Reenviando: {packet}')
                logging.debug(f'(send-ack-loop) A: {self.address}')
                self.socket.sendto(packet, self.address)
        else:
            print('IMPLEMENTAR EXCEPTION')

        logging.debug('(send) Fin send')

    def receive(self):
        logging.debug(f'(recv-estado) seq_num: {self.sequence_number}')
        logging.debug(f'(recv-estado) expected_seq_num: {self.expected_sequence_num}')
        data, address = self.socket.recvfrom(self.buffer_size)
        
        sequence_number, expected_seq_number = struct.unpack('II', data[:8])
        logging.debug(f'(recv) seq_num: {sequence_number}')
        logging.debug(f'(recv) expected_seq_num: {expected_seq_number}')
        logging.debug(f'(recv) payload: {data[8:]}')

        if sequence_number == self.expected_sequence_num:
            logging.debug(f'(recv) Enviar ACK')
            ack_packet = struct.pack('II', sequence_number, self.expected_sequence_num)
            self.socket.sendto(ack_packet, address)
            logging.debug(f'(recv) Enviado')
            self.expected_sequence_num += 1
            self.sequence_number += 1
            logging.debug(f'(recv) OK. Incrementar secuencia')

        logging.debug('(recv) Fin recv')
        return data[8:], address

    def bind(self, address):
        logging.debug(f'(bind): {address} (deberia ser solo en el servidor, pero no nos metamos en capa de app)')
        self.socket.bind(address)
        logging.debug('(bind) Fin bind')

    def close(self):
        pass
