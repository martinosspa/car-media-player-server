import os
import time
import json
import uuid
import logging
import threading
from MessageHandler import MessageHandler
from ComProtocol import ComProtocol as ComProt

THREADING_LOCK = threading.Lock()


class ClientHandler(threading.Thread):
	_client_uuid = None
	_is_client_fresh = False

	def __init__(self, client, addr, directory_manager) -> None:
		super().__init__()
		self._client = client
		self._client_addr = addr
		self._directory_manager = directory_manager
		self._message_handler = MessageHandler(self._client)
		self._load_clients_from_json('clients.json')  # TODO : remove hardcoded client.json file
		self.run()

	def run(self) -> None:
		self._check_if_client_is_fresh()
		print(self._is_client_fresh)

		if self._is_client_fresh:
			self._client_begin_sync(self._client_uuid)
		else:
			#client_last_sync = self._message_handler.receive_from_client(self._client)
			self._handle_client_last_sync(self._client_uuid)
		logging.debug(f'Closing connection with {self._client_addr[0]}')
		self._client.close()


	def _check_if_client_is_fresh(self) -> None:
		'''Handles Logic behind uuid creation and saving,
			Changes the _is_client_fresh flag'''

		# Client either sends a uuid message or a no_uuid message
		uuid_message = self._message_handler.receive_from_client()

		if uuid_message == ComProt.UUID:
			logging.debug(f'Client {self._client} has UUID')
			# Client already has a UUID
			# Return True so we skip the exchange of
			# Last Sync
			self._client_uuid = self._message_handler.receive_from_client()
			self._is_client_fresh = False

		elif uuid_message == ComProt.NO_UUID:
			logging.debug(f'Client {self._client} has no UUID')
			# generate a uuid for the client and send it
			self._client_uuid = str(uuid.uuid4())
			self._message_handler.send_to_client(self._client_uuid)
			# save client to clients file
			self._client_data['clients'][self._client_uuid] = {'last_sync':'-1'}
			self._save_client_data_to_file('clients.json')
			self._is_client_fresh = True

		else:
			logging.error(f'Error generating UUID for client at {self._client_addr}')

	def _handle_client_last_sync(self, client_uuid) -> None:
		'''Handles Syncing logic'''
		client_last_sync = self._message_handler.receive_from_client()
		if float(client_last_sync) > float(self._client_data['clients'][client_uuid]['last_sync']):
			self._message_handler.send_to_client(ComProt.OKAY)
			logging.info(f'Client {client_uuid} is synced')			
		else:
			self._client_begin_sync(client_uuid)

	def _client_begin_sync(self, client_uuid) -> None:
		'''This initiates the sync process with a client'''

		# Next step in handshake is for client to send their library
		logging.info(f'Client {client_uuid} needs to sync')
		self._message_handler.send_to_client(ComProt.SYNC)
		data = self._message_handler.receive_from_client()
		if data:
			client_library_json = json.loads(data)
		else: 
			client_library_json = []
		self._send_file_differences_to_client(client_library_json)

		# End the handshake
		self._message_handler.send_to_client(ComProt.END)
		logging.info(f'Client {client_uuid} synced')

	def _send_file_differences_to_client(self, client_library) -> None:
		''' Compares client library to local and sends differences
			Messages to client from server have the format of:
				/file.mp3
				/folder/
				/folder/file.mp3
			After every file is sent an additional message is sent with the actual file
			'''
		for file in self._directory_manager.get_files():
			if file in client_library: # Client already has that file
				continue

			if file[-1] == '/':
				# current file is a directory
				# that client doesnt have
				# send that difference so client can create the directory
				self._message_handler.send_to_client(file)
				time.sleep(0.05)
				continue

			self._message_handler.send_to_client(file)
			time.sleep(0.05)
			self._message_handler.send_file_to_client(file)
			
			# Wait for client message is a blocking method 
			# that waits for client to confirm that a file was received
			self._message_handler.wait_for_client_message(ComProt.SNF)

	def _load_clients_from_json(self, file_name) -> None:
		if not os.path.isfile(file_name):
			with open(file_name, 'w') as file:
				# check if client file exists, if not create it
				data_preload = {'clients': {}}
				json.dump(data_preload, file)

		with open(file_name) as file:
			self._client_data = json.load(file)

	def _save_client_data_to_file(self, file_name) -> None:
		THREADING_LOCK.acquire()
		with open(file_name, 'w') as file:
			json.dump(self._client_data, file)
		THREADING_LOCK.release()
