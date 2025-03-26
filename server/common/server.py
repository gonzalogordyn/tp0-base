import socket
import logging
import signal
from common.packet import Packet
from common.utils import *

class Server:
    def __init__(self, port, listen_backlog):
        # Initialize server socket
        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_socket.bind(('', port))
        self._server_socket.listen(listen_backlog)
        self._client_socket = None

    def run(self):
        """
        Dummy Server loop

        Server that accept a new connections and establishes a
        communication with a client. After client with communucation
        finishes, servers starts to accept new connections again
        """

        while True:
            self._client_socket = self.__accept_new_connection()
            self.__handle_client_connection()

    def __recv_all_bytes(self):
        packet_bytes = b''
        packet_length_bytes = self._client_socket.recv(2)
        packet_bytes += packet_length_bytes
        packet_length = int.from_bytes(packet_length_bytes, byteorder='big', signed=False)
        
        while len(packet_bytes) - 2 < packet_length:
            received = self._client_socket.recv(packet_length - len(packet_bytes) + 2)
            if not received:
                return packet_bytes
            packet_bytes += received
        return packet_bytes

    def __write_all_bytes(self, data):
        sent_bytes = 0
        while sent_bytes < len(data):
            sent = self._client_socket.send(data[sent_bytes:])
            if sent == 0:
                logging.error("Error al enviar datos")
                return
            sent_bytes += sent
        return

    def __handle_client_connection(self):
        """
        Read message from a specific client socket and closes the socket

        If a problem arises in the communication with the client, the
        client socket will also be closed
        """
        try:
            received_bytes = self.__recv_all_bytes()
            logging.info(f'Received bytes: {received_bytes}')
            packet = Packet.deserialize(received_bytes)
            
            bet = Bet(0, packet.nombre, packet.apellido, packet.documento, packet.nacimiento, packet.numero)
            store_bets([bet])
            logging.info(f'action: apuesta_almacenada | result: success | dni: {packet.documento} | numero: {packet.numero}')
            
            # Creo la respuesta
            response = b''
            response += "ACK".encode('utf-8')
            response += packet.numero.to_bytes(4, byteorder='big', signed=False)

            self.__write_all_bytes(response)
        except OSError as e:
            logging.error("action: receive_message | result: fail | error: {e}")
        finally:
            self._client_socket.close()

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
        return c
    
    def graceful_shutdown(self):
        logging.info("Cerrando servidor...")
        
        if self._client_socket:
            logging.info(f"Cerrando socket de cliente")
            self._client_socket.close()
        
        logging.info("Cerrando socket del servidor")
        self._server_socket.close()