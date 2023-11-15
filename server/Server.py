import logging
import socket
import json
import os
import uuid
from MessageHandler import MessageHandler
from DirectoryManager import DirectoryManager

class Server:
	_socket = None
	_message_handler = None
	_directory_manager = None
	_client_data = None


	def __init__(self) -> None:
		self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

		#TODO : remove hardcoded local ip
		self._socket.bind(('192.168.0.63', 9999))
		logging.info('Started succesfully')

		#TODO : remove hardcoded client.json file
		self._load_clients_from_json('clients.json')
		self._message_handler = MessageHandler()

		#TODO : remove hardcoded local library lookup location
		self._directory_manager = DirectoryManager('/music')


		self._start_main_loop()

	def _start_main_loop(self) -> None:
		try:
			while True:
				self._socket.listen()
				client, addr = self._socket.accept()
				logging.info(f'Connected by {addr[0]}:{addr[1]}')

				last_sync_decoded = self._message_handler.receive_from_client(client)
				
				if float(last_sync_decoded) > float(last_update):
					self._message_handler.send_to_client(client, ComProt.OKAY)
					logging.info(f'Client {addr[0]} is synced')
					
				else:
					self._client_begin_sync(client, addr)
					
				logging.debug(f'Closing connection with {addr[0]}')
				client.close()
		# TEMPORARY
		except KeyboardInterrupt:
			print('\n')
			logging.info('Closing Server')

	def _client_begin_sync(self, client, addr) -> None:
		'''This initiates the sync process with a client'''
		logging.info(f'Client {addr[0]} needs to sync')
		self._message_handler.send_to_client(client, ComProt.SYNC)

		# Next step in handshake is for client to send their library
		data = self._message_handler.receive_from_client(client)
		client_library_json = json.loads(data)

		self._send_file_differences_to_client(client, client_library)

		# End the handshake
		self._message_handler.send_to_client(client, ComProt.END)
		logging.info(f'Client {addr[0]} synced')


	def _send_file_differences_to_client(self, client, client_library) -> None:
		''' Compares client library to local and sends differences
			Messages to client from server have the format of:
				/file.mp3
				/folder/
				/folder/file.mp3
			After every file is sent an additional message is sent with the actual file
			'''
		for file in self._directory_manager.get():
			if file in client_file_list: # Client already has that file
				continue

			if file[-1] == '/':
				# current file is a directory
				# that client doesnt have
				# send that difference so client can create the directory
				self._message_handler.send_to_client(client, file)
				continue

			self._message_handler.send_to_client(client, file)
			time.sleep(0.05)
			self._message_handler.send_file_to_client(client, file)
			
			# Wait for client message is a blocking method 
			# that waits for client to confirm that a file was received
			self._message_handler.wait_for_client_message(client, ComProt.SNF)

	def _load_clients_from_json(self, file_name) -> None:
		if not os.path.isfile(file_name):
			with open(file_name, 'w') as file:
				# check if client file exists, if not create it
				data_preload = {'clients':[]}
				json.dump(data_preload, file)

		with open(file_name) as file:
			self._client_data = json.load(file)

	def __del__(self) -> None:
		if self._socket:
			self._socket.close()