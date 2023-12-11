import logging
import time
import os
from ComProtocol import ComProtocol as ComProt

class MessageHandler:
	'''This class manages all communication with clients'''

	def __init__(self, client, uuid) -> None:
		'''Message handler class takes a client as a required paramater'''
		self._client = client
		self._client_uuid = uuid

	def send_to_client(self, message) -> None:
		self._client.sendall(message.encode())
		if self._client_uuid:
			logging.debug(f'Sent {message} to client {self._client_uuid}')
		else:
			logging.debug(f'Sent {message} to client {self._client.addr}')
		time.sleep(0.05)

	def send_file_to_client(self, file_path) -> None:
		'''Sends a file to client, needs a file path'''
		full_path = os.getcwd() + file_path
		with open(full_path, 'rb') as file:
			while message := file.read(40960):
				self.send_to_client(message)
			self.send_to_client(ComProt.EOF)

	def wait_for_client_message(self, message) -> None:
		''' This is a blocking method'''
		logging.debug(f'Waiting for {self._client} to send {message}')
		while True:
			client_message = self._client.recv(1024).decode()
			if client_message == message: 
				break

	def receive_from_client(self, data_amount=1024) -> str:
		'''Receive data from client, optional data_amount with default value of 1024
			Returns a string'''
		data = self._client.recv(data_amount).decode()
		logging.debug(f'Received {data} from {self._client}')
		return data
