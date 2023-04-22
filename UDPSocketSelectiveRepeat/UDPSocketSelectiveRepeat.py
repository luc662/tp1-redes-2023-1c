import socket
import struct
import logging
import threading
import queue
from math import ceil
from logging import debug as db
from manejador_de_ventanas import manejador_de_ventanas

logging.basicConfig(level=logging.DEBUG, format='%(message)s')
from random import random

PACKET_LOSS = 0.3


def log(msg):
    db(f'[UdpSkt] {msg}')


class UDPSocketGBN:

    def __init__(self, address):
        log(f'(start) address: {address}')
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.address = address
        self.sequence_number = 0
        self.expected_sequence_num = 0
        self.buffer_size = 1024
        self.send_retries = 10
        self.packet_loss_counter = 0

    def enviar_archivo(self, tamanio_archivo, archivo):
        header_size = 8
        cantidad_paquetes = ceil(tamanio_archivo / (self.buffer_size - header_size))
        #
        iters_inicial = min(cantidad_paquetes, 10)
        log(f'Iters Inicial, Cantidad de paquetes  {iters_inicial, cantidad_paquetes}')
        # queue que este thread se queda escuchando
        queue_respuestas = queue.Queue()
        my_manejador_de_ventanas = manejador_de_ventanas(cantidad_paquetes, queue_respuestas)
        bloques_restantes = cantidad_paquetes - iters_inicial

        threads = []
        # crear el thread que se queda escuchando los acks
        thread_respuestas = threading.Thread(target=self.escuchar_acks, args=(my_manejador_de_ventanas,))
        threads.append(thread_respuestas)
        thread_respuestas.start()
        # primera parte del envio, abro un thread por cada iter inicial
        for i in range(iters_inicial, cantidad_paquetes):
            queue_de_bloque = queue.Queue()
            log(f'Leer {self.buffer_size - header_size}B {i}/{cantidad_paquetes}')
            bytes = archivo.read(self.buffer_size - header_size)
            my_manejador_de_ventanas.agregar_ventana(i, queue_de_bloque)
            log('Enviando')

            thread = threading.Thread(target=self.enviar_bloque, args=(bytes, queue_de_bloque))
            threads.append(thread)
            thread.start()
            log('Enviado!')

        # mando el resto de los paquetes cuando se libere un thread
        for i in range(iters_inicial):
            # si, me llega el ultimo mensaje por queue_respuestas
            if my_manejador_de_ventanas.respuestas_escuchadas == cantidad_paquetes:

                break
            else:
                respuesta = queue_respuestas.get(block=True)
                log(f'se cerro el thread que enviaba el bloque {respuesta}/{cantidad_paquetes}')
                queue_de_bloque = queue.Queue()
                log(f'Leer {self.buffer_size - header_size}B {i}/{cantidad_paquetes}')
                bytes = archivo.read(self.buffer_size - header_size)
                my_manejador_de_ventanas.agregar_ventana(i, queue_de_bloque)
                log('Enviando')

                thread = threading.Thread(target=self.enviar_bloque, args=(bytes, queue_de_bloque))
                threads.append(thread)
                thread.start()
                # abro otro paquete y lo agrego a la pila.

        log('Cerrar archivo')

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

        log('(send) fin send')

    # esta parte va a
    def enviar_bloque(self, packet, queue_ventana):
        self.socket.sendto(packet, self.address)
        for i in range(self.send_retries):
            log(f'(send-ack-loop) Intento: {i + 1}/{self.send_retries}')

            log('(send-ack-loop) Iniciar timer (1s)')
            log('(send-ack-loop) Recibir respuesta (ACK Hopefully)')

            try:
                #me quedo escuchando a la queue
                data = queue_ventana.get(block=True, timeout=0.1)
                ack_sequence_number, ack_expected_seq_number = struct.unpack('II', data[:8])
                log(f'(send-ack-loop) ack_seq_num: {ack_sequence_number}, ack_expected_seq_num: {ack_expected_seq_number}')
                log('(send-ack-loop) Desempaquetar')
                break
            except queue.Empty:
                #no se escucho a la queue y lanzo un timeout
                log('(send-ack-loop) Timeout!')
                log(f'(send-ack-loop) Reenviando: {packet}')
                log(f'(send-ack-loop) A: {self.address}')
                self.socket.sendto(packet, self.address)
        else:
            print('IMPLEMENTAR EXCEPTION')

    # esta parte escucha la llegada de acks a la estructura
    def escuchar_acks(self, my_manejador_de_ventanas):
        logging.debug('(get-ack-loop) thread que escucha respuestas (ACK)')
        # Tiemout alto, por si se cae la conexion
        self.socket.settimeout(15.0)
        try:
            while not my_manejador_de_ventanas.finalizo():

                data, address = self.socket.recvfrom(self.buffer_size)
                logging.debug('(send-ack-loop) Desempaquetar')
                ack_sequence_number, ack_expected_seq_number = struct.unpack('II', data[:8])
                my_manejador_de_ventanas.pushear_a_ventana(ack_sequence_number, data)
                logging.debug(
                    f'(send-ack-loop) ack_seq_num: {ack_sequence_number}, ack_expected_seq_num: {ack_expected_seq_number}')
        except socket.timeout:
            logging.debug('(get-ack-loop) no llego ningun ACK en mucho tiempo, cierro todo')


    def receive(self):
        self.socket.settimeout(None)
        log(f'(recv-estado) seq_num: {self.sequence_number}')
        log(f'(recv-estado) expected_seq_num: {self.expected_sequence_num}')
        data, address = self.socket.recvfrom(self.buffer_size)
        sequence_number, expected_seq_number = struct.unpack('II', data[:8])
        log(f'(recv) seq_num: {sequence_number}')
        log(f'(recv) expected_seq_num: {expected_seq_number}')
        log(f'(recv) payload: {data[8:]}')
        ## SIMULACION DE PERDIDA DE PAQUETES ack
        # p = random()
        # if p < PACKET_LOSS:
        #    log(f'(RECV) PACKET_LOSS con prob: {p}')
        #    self.packet_loss_counter += 1
        #    log(f'PAQUETES PERDIDOS: {self.packet_loss_counter}')
        #    return None, address
        ## SIMULACION DE PERDIDA DE PAQUETES

        log(f'(recv) Enviar ACK')
        ack_packet = struct.pack('II', sequence_number, self.expected_sequence_num)
        self.socket.sendto(ack_packet, address)
        log(f'(recv) Enviado')
        '''
        if sequence_number == self.expected_sequence_num:
            self.expected_sequence_num += 1
            self.sequence_number += 1
            log(f'(recv) OK. Incrementar secuencia')
            # si nos llega la secuencia de datos deseada, devuelvo la data
            
        '''
        log('(recv) fin recv')
        # tenemos que mandar tambien el seq number para que se ordene despues
        return data[8:], address

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
