import socket
import logging
from ClientHandler import ClientHandler
from DirectoryManager import DirectoryManager
from ComProtocol import ComProtocol as ComProt
import time

class Server:
	_socket = None
	_message_handler = None
	_directory_manager = None
	_client_data = None
	_current_clients = []


	def __init__(self) -> None:
		self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

		#TODO : remove hardcoded local ip
		self._socket.bind(('192.168.0.63', 9999))
		logging.info('Started succesfully')
		
		#TODO : remove hardcoded local library lookup location
		self._directory_manager = DirectoryManager('/music/')
		self._directory_manager.build()

		self._start_main_loop()

	def _start_main_loop(self) -> None:
		try:
			while True:
				self._socket.listen()
				client, addr = self._socket.accept()
				logging.info(f'Connected by {addr[0]}:{addr[1]}')
				self._current_clients.append(ClientHandler(client, addr, self._directory_manager))
				
		# TEMPORARY
		except KeyboardInterrupt:
			print('\n')
			logging.info('Closing Server')


	def __del__(self) -> None:
		if self._socket:
			self._socket.close()