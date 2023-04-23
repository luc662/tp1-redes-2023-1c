import socket
import struct
import logging
import threading
from multiprocessing import Process
import queue
from math import ceil
from logging import debug as db
from ManejadorDeVentanas import ManejadorDeVentanas

logging.basicConfig(level=logging.DEBUG, format='%(message)s')
from random import random

PACKET_LOSS = 0


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
        self.header_size = 8
        self.send_retries = 5
        self.packet_loss_counter = 0
        self.packet_loss_activated = True

    # LAS PILAS NO SE PUEDEN USAR EN EL MANEJADOR DE VENTANAS, PERO ACA SI
    def enviar_archivo(self, tamanio_archivo, archivo):
        header_size = 8
        cantidad_paquetes = ceil(tamanio_archivo / (self.buffer_size - header_size))
        # creo todas las pilas que escuchan los threads
        ventanas = {}
        for i in range(cantidad_paquetes):
            ventanas[i + self.sequence_number] = queue.Queue()

        iters_inicial = min(cantidad_paquetes, 2)
        log(f'Iters Inicial, Cantidad de paquetes  {iters_inicial, cantidad_paquetes}')
        # queue que este thread se queda escuchando
        queue_respuestas = queue.Queue()

        my_manejador_de_ventanas = ManejadorDeVentanas(cantidad_paquetes, queue_respuestas)
        bloques_restantes = cantidad_paquetes - iters_inicial

        threads = []
        # crear el thread que se queda escuchando los acks
        #thread_respuestas = threading.Thread(target=self.escuchar_acks, args=(ventanas, queue_respuestas))
        thread_respuestas = Process(target=self.escuchar_acks, args=(ventanas, queue_respuestas))

        threads.append(thread_respuestas)
        thread_respuestas.start()
        # primera parte del envio, abro un thread por cada iter inicial
        for i in range(iters_inicial):
            log(f'Iters Inicial, Cantidad de paquetes  {i + 1, cantidad_paquetes}')
            log(f'Leer {self.buffer_size - header_size}B {i + 1}/{cantidad_paquetes}')
            bytes = archivo.read(self.buffer_size - header_size)
            log('Enviando')
            packet = struct.pack('II', self.sequence_number, self.expected_sequence_num) + bytes
            #thread = threading.Thread(target=self.enviar_bloque, args=(packet, ventanas[self.sequence_number]))
            thread = Process(target=self.enviar_bloque, args=(packet, ventanas[self.sequence_number]))
            threads.append(thread)
            thread.start()
            self.sequence_number += 1
            log('Enviado!')
        # mando el resto de los paquetes cuando se libere un thread
        for i in range(iters_inicial, cantidad_paquetes):
            # si, me llega el ultimo mensaje por queue_respuestas
            if my_manejador_de_ventanas.respuestas_escuchadas == cantidad_paquetes:
                break
            else:
                respuesta = queue_respuestas.get(block=True)
                # si me llego un timeout, deberia cortar todas las iteraciones
                if "TIMEOUT" in respuesta:
                    break

                log(f'(send) {respuesta}')
                log(f'Leer {self.buffer_size - header_size}B {i + 1}/{cantidad_paquetes}')
                bytes = archivo.read(self.buffer_size - header_size)
                packet = struct.pack('II', self.sequence_number, self.expected_sequence_num) + bytes
                log('Enviando')

                #thread = threading.Thread(target=self.enviar_bloque, args=(packet, ventanas[self.sequence_number]))
                thread = Process(target=self.enviar_bloque, args=(packet, ventanas[self.sequence_number]))
                threads.append(thread)
                thread.start()
                self.sequence_number += 1
                # abro otro paquete y lo agrego a la pila.

        #for t in threads:
        #    t.join()

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
        #log('(send) Esperando ACK (bucle)')

        log('(send) fin send')

    '''
    def send_and_wait_for_ack(self, data):
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
                self.socket.sendto(packet, self.address)
        else:
            log('IMPLEMENTAR EXCEPTION')
        log('(send) fin send')
    '''
    
    def send_and_wait_for_ack(self, data):
        log('send')
        packet = struct.pack('II', self.sequence_number, self.expected_sequence_num) + data
        self.socket.sendto(packet, self.address)

        log('(send) Esperando ACK (bucle)')
        for i in range(self.send_retries):
            log(f'(send-ack-loop) Intento: {i + 1}/{self.send_retries}. (1s)')
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
                        log(f'(send) Paquetes perdidos: {self.packet_loss_counter}')
            except socket.timeout:
                log('(send-ack-loop) Timeout! Reenviando')
                self.socket.sendto(packet, self.address)
        else:
            raise DestinoInaccesible

    def recieve_and_send_ack(self):
        log('recieve')
        self.socket.settimeout(None)
        data, address = self.socket.recvfrom(self.buffer_size)
        sequence_number, expected_seq_number = struct.unpack('II', data[:8])
        log('(recv) Paquete recibido')

        log(f'(recv) seq_num: {sequence_number}, expected_seq_num: {expected_seq_number}')

        log('(recv) Enviando ACK')
        ack_packet = struct.pack('II', sequence_number, self.expected_sequence_num)
        self.socket.sendto(ack_packet, address)
        log('(recv) ACK enviado')
        if sequence_number == self.expected_sequence_num:
            self.expected_sequence_num += 1
            self.sequence_number += 1
            return data[8:], address
        
        log(f'(recv) Expected_seq_num: {self.expected_sequence_num}, recibimos seq_num: {sequence_number}')
        return None, address

    # esta parte va a tratar de enviar un bloque de datos y se queda escuchando a su queue por respuestas de acks
    def enviar_bloque(self, packet, queue_ventana):
        log('(enviar-bloque)')
        log(f'_____________(enviar-bloque) enviando: {packet}')
        self.socket.sendto(packet, self.address)
        seq_num, exp_seq_num = struct.unpack('II',packet[:8])
        for i in range(self.send_retries):
            log(f'(send-ack-loop) Intento {seq_num},{exp_seq_num}: {i + 1}/{self.send_retries}')
            log('(send-ack-loop) Recibir respuesta (ACK Hopefully)')
            try:
                # me quedo escuchando a la queue
                log('(send-ack-loop) Recibir respuesta de pila')
                data = queue_ventana.get(block=True, timeout=1.5)
                log(f'_________(enviar-bloque) data: {data}')
                ack_sequence_number, ack_expected_seq_number = struct.unpack('II', data[:8])
                log(f'(send-ack-loop) ack_seq_num: {ack_sequence_number}, ack_expected_seq_num: {ack_expected_seq_number}')
                log('(send-ack-loop) Desempaquetar')
                break
            except queue.Empty:
                # no se escucho a la queue y lanzo un timeout
                log('(send-ack-loop) Timeout!')
                self.socket.sendto(packet, self.address)
        else:
            print('IMPLEMENTAR EXCEPTION SELECTIVE REPEAT')

    # esta parte escucha la llegada de acks a la estructura
    # funciona como un cartero, recibe las cartas y las envia a quien corresponda
    def escuchar_acks(self, canales_ventanas, canal_respuestas):
        logging.debug('(get-ack-loop) thread que escucha respuestas (ACK)')
        # Tiemout alto, por si se cae la conexion
        self.socket.settimeout(15.0)
        ventanas_escuchadas = {}
        try:
            log(f'(ACKs listener) Empiezo a escuchar ACKs')
            # usamos un dic para contar asi validamos que se sume solo si el valor es nuevo
            while len(ventanas_escuchadas) < len(canales_ventanas):
                data, address = self.socket.recvfrom(self.buffer_size)
                logging.debug('(send-ack-loop) Desempaquetar')
                ack_sequence_number, ack_expected_seq_number = struct.unpack('II', data[:8])
                canal_respuestas.put("me llego el ACK de : " + str(ack_sequence_number))
                canal = canales_ventanas[ack_sequence_number]
                canal.put(data)
                # quizas hay una mejor forma de contar cuantos mensajes hay
                #  pero asi nos aseguramos  que sume sii es un nuevo mensaje
                ventanas_escuchadas[ack_sequence_number] = True
                log(
                    f'(ACKs listener) escuche la siguiente cantidad de ACKs {len(ventanas_escuchadas)} / {len(canales_ventanas)}'
                )
        except socket.timeout:
            #canal_respuestas.put("TIMEOUT")
            logging.debug('(ACKs listener) no llego ningun ACK en mucho tiempo, cierro todo')

    def receive(self):
        self.socket.settimeout(None)
        log(f'(recv-estado) seq_num: {self.sequence_number}')
        log(f'(recv-estado) expected_seq_num: {self.expected_sequence_num}')
        data, address = self.socket.recvfrom(self.buffer_size)
        sequence_number, expected_seq_number = struct.unpack('II', data[:8])
        log(f'(recv) seq_num: {sequence_number}')
        log(f'(recv) expected_seq_num: {expected_seq_number}')
        ack_packet = struct.pack('II', sequence_number, self.expected_sequence_num)
        log(f'(recv) Enviar ACK: {ack_packet}')

        self.socket.sendto(ack_packet, address)
        log(f'(recv) Enviado')
        log('(recv) fin recv')
        # tenemos que mandar tambien el seq number para que se ordene despues
        return data[8:], address, sequence_number

    def bind(self, address):
        log(f'(bind): {address} (deberia ser solo en el servidor, pero no nos metamos en capa de app)')
        self.socket.bind(address)
        log('(bind) fin bind')