import os
import socket
import logging
import signal
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
        self._server_socket.bind(('', port))
        self._server_socket.listen(listen_backlog)
        self._clients = {}
        self._notified = 0

        try:
            self._num_agencias = int(os.getenv("AGENCIAS", 5))
            # logging.debug(f"Cantidad de agencias: {self._num_agencias}")
        except ValueError:
            logging.error("Valor inválido.")
            raise
        self._ganadores = {str(i): [] for i in range(1, self._num_agencias + 1)}

    def run(self):
        """
        Dummy Server loop

        Server that accept a new connections and establishes a
        communication with a client. After client with communucation
        finishes, servers starts to accept new connections again
        """

        while True:
            id = self.__accept_new_connection()
            self.__handle_client_connection(id)

    def __recv_all_bytes(self, id):
        packet_bytes = b''
        packet_length_bytes = self._clients[id].recv(2)
        packet_bytes += packet_length_bytes
        packet_length = int.from_bytes(packet_length_bytes, byteorder='big', signed=False)

        # logging.debug(f"action: receive_message | length: {packet_length}")

        if packet_length == self.NOTIFY_FINISHED:
            # logging.debug(f"action: Recibió un finished")
            return packet_bytes, "FINISHED"
        
        while len(packet_bytes) - 2 < packet_length:
            received = self._clients[id].recv(packet_length - len(packet_bytes) + 2)
            if not received:
                return packet_bytes
            packet_bytes += received
        return packet_bytes, "OK"

    def __write_all_bytes(self, data, id):
        # logging.debug(f"sending message to client {str(id)}")
        # logging.debug(f"clients: {self._clients}")
        sent_bytes = 0
        while sent_bytes < len(data):
            sent = self._clients[id].send(data[sent_bytes:])
            if sent == 0:
                logging.error("Error al enviar datos")
                return
            sent_bytes += sent
        return
    
    def __handle_notificaciones(self):
        self._notified += 1
        if self._notified == self._num_agencias:
            logging.info("action: sorteo | result: success")
            self.__handle_sorteo()

    def __handle_sorteo(self):
        bets = load_bets()
        for bet in bets:
            if has_won(bet):
                agency_key = str(bet.agency)
                self._ganadores[agency_key].append(bet.document)

        for agency, winners in self._ganadores.items():
            winners_packet = WinnersPacket(winners)
            winners_bytes = winners_packet.serialize()
            self.__write_all_bytes(winners_bytes, agency)
        
        self.graceful_shutdown()


    def __handle_client_connection(self, client_id):
        """
        Read message from a specific client socket and closes the socket

        If a problem arises in the communication with the client, the
        client socket will also be closed
        """
        try:
            while True:
                received_bytes, status = self.__recv_all_bytes(client_id)
                # logging.info(f'Received bytes: {received_bytes}')

                if status == "FINISHED":
                    # logging.info(f"action: notificacion | result: success | client: {client_id}")
                    self.__handle_notificaciones()
                    break
                else:
                    batch, failed_packets = Batch.deserialize(received_bytes)
                    # logging.info(f'Batch: {batch.packets}')
                    
                    for packet in batch.packets:
                        bet = Bet(client_id, packet.nombre, packet.apellido, packet.documento, packet.nacimiento, packet.numero)
                        store_bets([bet])
                        # logging.info(f'action: apuesta_almacenada | result: success | client: {client_id} |  nombre: {packet.nombre} {packet.apellido} | dni: {packet.documento} | numero: {packet.numero}')
                    

                    if failed_packets > 0:
                        logging.error(f'action: apuesta_recibida | result: fail | cantidad: {failed_packets}')
                        response = "ERR".encode('utf-8')
                        self.__write_all_bytes(response, client_id)
                    else:
                        logging.info(f'action: apuesta_recibida | result: success | cantidad: {len(batch.packets)}')
                        response = "ACK".encode('utf-8')
                        self.__write_all_bytes(response, client_id)
                
        except OSError as e:
            logging.error("action: receive_message | result: fail | error: {e}")
        # finally:
        #     self._clients[client_id].close()

    def __accept_new_connection(self):
        """
        Accept new connections

        Function blocks until a connection to a client is made.
        Then connection created is printed and returned
        """

        # Connection arrived
        logging.info('action: accept_connections | result: in_progress')
        c, addr = self._server_socket.accept()
        logging.info(f'action: accept_connections | result: success | ip: {addr[0]}')
        
        client_id_bytes = c.recv(1)
        client_id = int.from_bytes(client_id_bytes, byteorder='big', signed=False)
        client_id_str = str(client_id)
        # logging.info(f'id: {client_id_str}')
        
        self._clients[client_id_str] = c

        return client_id_str
    
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