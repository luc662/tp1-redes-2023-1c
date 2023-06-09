import socket
import struct
import logging
import threading
import queue
from math import ceil
from logging import debug as db

logging.basicConfig(level=logging.DEBUG, format='%(message)s')

def log(msg):
    db(f'[UdpSkt] {msg}')


class UDPSocketSelectiveRepeat:

    def __init__(self, address):
        log(f'(start) address: {address}')
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.address = address
        self.sequence_number = 0
        self.expected_sequence_num = 0
        self.buffer_size = 1024
        self.header_size = 8
        self.send_retries = 15

    def enviar_archivo(self, tamanio_archivo, archivo):
        header_size = 8
        cantidad_paquetes = ceil(tamanio_archivo / (self.buffer_size - header_size))
        # creo todas las pilas que escuchan los threads
        ventanas = {}
        for i in range(cantidad_paquetes):
            ventanas[i + self.sequence_number] = queue.Queue()

        iters_inicial = min(cantidad_paquetes, 5)
        log(f'Iters Inicial, Cantidad de paquetes  {iters_inicial, cantidad_paquetes}')
        # queue que este thread se queda escuchando
        queue_respuestas = queue.Queue()

        threads = []
        # crear el thread que se queda escuchando los acks
        thread_respuestas = threading.Thread(target=self.escuchar_acks,
                                             args=(ventanas, queue_respuestas))
        threads.append(thread_respuestas)
        thread_respuestas.start()
        # primera parte del envio, abro un thread por cada iter inicial
        for i in range(iters_inicial):
            log(f'Iters Inicial, Cantidad de paquetes  {i + 1, cantidad_paquetes}')
            log(f'Leer {self.buffer_size - header_size}B {i + 1}/{cantidad_paquetes}')
            bytes = archivo.read(self.buffer_size - header_size)
            log('Enviando')
            packet = struct.pack('II', self.sequence_number, self.expected_sequence_num) + bytes
            thread = threading.Thread(target=self.enviar_bloque, args=(packet, ventanas[self.sequence_number]))
            threads.append(thread)
            thread.start()
            self.sequence_number += 1
            self.expected_sequence_num += 1
            log('Enviado!')
        # mando el resto de los paquetes cuando se libere un thread
        for i in range(iters_inicial, cantidad_paquetes):
            respuesta = queue_respuestas.get(block=True)
            # si me llego un timeout, no creo mas threads
            if "TIMEOUT" in respuesta:
                break

            log(f'(send) {respuesta}')
            log(f'Leer {self.buffer_size - header_size}B {i + 1}/{cantidad_paquetes}')
            bytes = archivo.read(self.buffer_size - header_size)
            packet = struct.pack('II', self.sequence_number, self.expected_sequence_num) + bytes
            log('Enviando')

            thread = threading.Thread(target=self.enviar_bloque, args=(packet, ventanas[self.sequence_number]))
            threads.append(thread)
            thread.start()
            self.sequence_number += 1
            self.expected_sequence_num += 1
            # abro otro paquete y lo agrego a la pila.

        log('espero que los threads hijos se cierren')

        for t in threads:
            t.join()

        # esta parte es best effort, no importa tanto que nos llegue el ack
        # sino que el receptor del archivo sepa que no trataremos de enviar mas
        # bloques donde fallo los ACKs y seguimos intentando mandarlos
        log('mandando FINALDEARCHIVO')
        mensaje = 'FINALDEARCHIVO'
        self.send_and_wait_for_ack(mensaje.encode())

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
        log('(send) fin send')

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
                data, address = self.socket.recvfrom(self.buffer_size)
                ack_sequence_number, ack_expected_seq_number = struct.unpack('II', data[:8])
                log(f'ack_seq_num {ack_sequence_number}, self.expected_sequence_num {self.expected_sequence_num}')
                if ack_sequence_number == self.expected_sequence_num:
                    self.expected_sequence_num += 1
                    self.sequence_number += 1
                    break

            except socket.timeout:
                log('(send-ack-loop) Timeout!')
                self.socket.sendto(packet, self.address)
        else:
            raise Exception
        log('(send) fin send')

    # esta parte va a tratar de enviar un bloque de datos y se queda escuchando a su queue por respuestas de acks
    def enviar_bloque(self, packet, queue_ventana):
        self.socket.sendto(packet, self.address)
        for i in range(self.send_retries):
            log(f'(send-ack-loop) Intento: {i + 1}/{self.send_retries}')
            log('(send-ack-loop) Recibir respuesta (ACK Hopefully)')

            try:
                # me quedo escuchando a la queue
                log('(send-ack-loop) Recibir respuesta de pila')
                data = queue_ventana.get(block=True, timeout=1)
                ack_sequence_number, ack_expected_seq_number = struct.unpack('II', data[:8])
                log(f'(send-ack-loop) ack_seq_num: {ack_sequence_number}, ack_expected_seq_num: {ack_expected_seq_number}')
                log('(send-ack-loop) Desempaquetar')
                break
            except queue.Empty:
                # no se escucho a la queue y lanzo un timeout
                log('(send-ack-loop) Timeout!')
                self.socket.sendto(packet, self.address)
        else:
            raise Exception

    # esta parte escucha la llegada de acks a la estructura
    # funciona como un cartero, recibe las cartas y las envia a quien corresponda
    def escuchar_acks(self, canales_ventanas, canal_respuestas):
        log('(get-ack-loop) thread que escucha respuestas (ACK)')
        # Tiemout alto, por si se cae la conexion
        self.socket.settimeout(15.0)
        ventanas_escuchadas = {}
        try:
            log(f'(ACKs listener) Empiezo a escuchar ACKs')
            # usamos un dic para contar asi validamos que se sume solo si el valor es nuevo
            # while len(ventanas_escuchadas) != len(canales_ventanas):
            while ventanas_escuchadas.keys() != canales_ventanas.keys():
                log(f'ventanas_escuchadas: {len(ventanas_escuchadas)}, canales_ventanas: {len(canales_ventanas)}')
                log(f'{ventanas_escuchadas.keys()} ---- {canales_ventanas.keys()}')
                data, address = self.socket.recvfrom(self.buffer_size)
                log('(send-ack-loop) Desempaquetar')
                ack_sequence_number, ack_expected_seq_number = struct.unpack('II', data[:8])
                canal_respuestas.put("me llego el ACK de : " + str(ack_sequence_number))
                canal = canales_ventanas[ack_sequence_number]
                canal.put(data)
                # quizas hay una mejor forma de contar cuantos mensajes hay
                #  pero asi nos aseguramos que sume sii es un nuevo mensaje
                ventanas_escuchadas[ack_sequence_number] = True
                log(
                    f'(ACKs listener) escuche la siguiente cantidad de ACKs {len(ventanas_escuchadas)} / {len(canales_ventanas)}'
                )
        except socket.timeout:
            canal_respuestas.put("TIMEOUT")
            log('(ACKs listener) no llego ningun ACK en mucho tiempo, cierro el thread e inicio protocolo de cierre')

        log(f'ventanas_escuchadas: {len(ventanas_escuchadas)}, canales_ventanas: {len(canales_ventanas)}')

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
        log('(recv) Enviado')
        log('(recv) fin recv')
        # tenemos que mandar tambien el seq number para que se ordene despues
        return data[8:], address, sequence_number

    def bind(self, address):
        log(f'(bind): {address}')
        self.socket.bind(address)
