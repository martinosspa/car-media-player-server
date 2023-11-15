import ComProtocol as ComProt
import logging
class MessageHandler:
	'''This class manages all communication with clients'''


	def send_to_client(self, client, message) -> None:
		client.sendall(message.encode())
		logging.info(f'Sent {message} to client {client}')
		
		
	def send_file_to_client(self, client, file_path) -> None:
		full_path = os.getcwd() + '/' + file_path
		with open(full_path, 'rb') as file:
			file_size = os.path.getsize(full_path)
			while message := file.read(40960):
				client.sendall(message)
			time.sleep(0.05)
			client.sendall(ComProt.EOF.encode())

	def wait_for_client_message(self, client, message) -> None:
		''' This is a blocking method
			Note: This can cause big trouble for multiple connections'''

		while True:
			client_message = client.recv(1024).decode()
			if client_message == message: 
				break

	def receive_from_client(self, client, data_amount=1024) -> str:
		'''Receive data from client, optional data_amount with default value of 1024
			Returns a string'''

		data = client.recv(data_amount)
		return data.decode()