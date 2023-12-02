import logging
import time
import os
from ComProtocol import ComProtocol as ComProt

class MessageHandler:
	'''This class manages all communication with clients'''

	def send_to_client(self, client, message) -> None:
		client.sendall(message.encode())
		logging.debug(f'Sent {message} to client {client}')

	def send_file_to_client(self, client, file_path) -> None:
		'''Sends a file to client'''
		full_path = os.getcwd() + file_path
		with open(full_path, 'rb') as file:
			while message := file.read(40960):
				client.sendall(message)
			time.sleep(0.05)
			client.sendall(ComProt.EOF.encode())

	def wait_for_client_message(self, client, message) -> None:
		''' This is a blocking method'''
		logging.debug(f'Waiting for {client} to send {message}')
		while True:
			client_message = client.recv(1024).decode()
			if client_message == message: 
				break

	def receive_from_client(self, client, data_amount=1024) -> str:
		'''Receive data from client, optional data_amount with default value of 1024
			Returns a string'''
		data = client.recv(data_amount).decode()
		logging.debug(f'Received {data} from {client}')
		return data
