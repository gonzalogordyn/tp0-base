import os
import socket
import logging
import signal
from multiprocessing import Process, Manager, Lock, Queue, Value
from common.packet import Packet
from common.batch import Batch
from common.utils import *
from common.winners_packet import WinnersPacket
import sys

class Server:
    NOTIFY_FINISHED = 9000

    def __init__(self, port, listen_backlog):
        # Initialize server socket
        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_socket.settimeout(1)
        self._server_socket.bind(('', port))
        self._server_socket.listen(listen_backlog)
        self._clients = {}
        self._queue = Queue()
        self._notified = Value('i', 0)

        try:
            self._num_agencias = int(os.getenv("AGENCIAS", 5))
        except ValueError:
            logging.error("Valor inválido.")
            raise
        with Manager() as manager:
            self._ganadores = manager.dict({str(i): [] for i in range(1, self._num_agencias + 1)})

        self._lock = Lock()

    def run(self):
        """
        Por cada conexión se lanza un nuevo proceso.
        El main process se va a encargar de comunicarle al resto los ganadores.
        """
        while True:
            logging.debug("queue size: %s", self._queue.qsize())
            if not self._queue.empty():
                message = self._queue.get()
                if message == "EXIT":
                    logging.debug("Sorteo terminado")
                    break

            client_id, client_socket = self.__accept_new_connection()
            
            if client_id is not None and client_socket is not None:
                process = Process(target=self.__handle_client_connection, args=(client_id, client_socket))
                process.start()
        
        for agency, winners in self._ganadores.items():
            winners_packet = WinnersPacket(winners)
            winners_bytes = winners_packet.serialize()
            self.__write_all_bytes(winners_bytes, agency)
        
        self.graceful_shutdown()
        

    def __recv_all_bytes(self, client_socket):
        packet_bytes = b''
        packet_length_bytes = client_socket.recv(2)
        packet_bytes += packet_length_bytes
        packet_length = int.from_bytes(packet_length_bytes, byteorder='big', signed=False)

        logging.debug(f"Longitud del paquete recibido: {packet_length}")
        if packet_length == self.NOTIFY_FINISHED:
            return packet_bytes, "FINISHED"
        
        while len(packet_bytes) - 2 < packet_length:
            received = client_socket.recv(packet_length - len(packet_bytes) + 2)
            if not received:
                return packet_bytes
            packet_bytes += received
        return packet_bytes, "OK"

    def __write_all_bytes(self, data, client_socket):
        sent_bytes = 0
        while sent_bytes < len(data):
            sent = client_socket.send(data[sent_bytes:])
            if sent == 0:
                logging.error("Error al enviar datos")
                return
            sent_bytes += sent

    def __handle_notificaciones(self):
        with self._lock:
            self._notified.value += 1
            logging.debug("Notificacion recibida | total: %s | numero agencias: %s", self._notified.value, self._num_agencias)
            if self._notified.value == self._num_agencias:
                logging.info("action: sorteo | result: success")
                self.__handle_sorteo()

    def __handle_sorteo(self):
        bets = load_bets()
        for bet in bets:
            if has_won(bet):
                agency_key = str(bet.agency)
                with self._lock:
                    self._ganadores[agency_key].append(bet.document)
        logging.debug(f"Poniendo EXIT en queue")
        self._queue.put("EXIT")

    def __handle_client_connection(self, client_id, client_socket):
        """
        Read message from a specific client socket and closes the socket

        If a problem arises in the communication with the client, the
        client socket will also be closed
        """
        try:
            while True:
                received_bytes, status = self.__recv_all_bytes(client_socket)

                if status == "FINISHED":
                    self.__handle_notificaciones()
                    break
                else:
                    batch, failed_packets = Batch.deserialize(received_bytes)
                    bets = []
                    for packet in batch.packets:
                        bet = Bet(client_id, packet.nombre, packet.apellido, packet.documento, packet.nacimiento, packet.numero)
                        bets = []
                        bets.append(bet)
                    
                    with self._lock:
                        store_bets([bet])

                    if failed_packets > 0:
                        logging.error(f'action: apuesta_recibida | result: fail | cantidad: {failed_packets}')
                        response = "ERR".encode('utf-8')
                        self.__write_all_bytes(response, client_socket)
                    else:
                        logging.info(f'action: apuesta_recibida | result: success | cantidad: {len(batch.packets)}')
                        response = "ACK".encode('utf-8')
                        self.__write_all_bytes(response, client_socket)
        except OSError as e:
            logging.error(f"action: receive_message | result: fail | error: {e}")

    def __accept_new_connection(self):
        """
        Acepta nuevas conexiones, y tiene un timeout.
        """
        try:
            logging.info('action: accept_connections | result: in_progress')
            client_socket, addr = self._server_socket.accept()
            logging.info(f'action: accept_connections | result: success | ip: {addr[0]}')
            
            client_id_bytes = client_socket.recv(1)
            client_id = int.from_bytes(client_id_bytes, byteorder='big', signed=False)
            client_id_str = str(client_id)

            logging.debug(f"ID de cliente recibido: {client_id_str}")
            self._clients[client_id_str] = client_socket
            
            return client_id_str, client_socket
        
        except socket.timeout:
            return None, None

    def graceful_shutdown(self):
        logging.debug("Cerrando servidor...")
        
        for client_id, client_socket in self._clients.items():
            try:
                logging.debug(f"Cerrando socket del cliente con ID: {client_id}")
                client_socket.close()
            except Exception as e:
                logging.error(f"Error cerrando socket del cliente con ID: {client_id} | Error: {e}")
        
        self._clients.clear()
        logging.debug("Cerrando socket del servidor")
        self._server_socket.close()
        sys.exit(0)