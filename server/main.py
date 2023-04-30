import socket
import time
import logging
import os
import json


def wait_for_client_message(client, message) -> None:
	while True:
		client_message = client.recv(1024).decode()
		if client_message == message: 
			break

def send_file_to_client(client, file_path) -> None:
	full_path = os.getcwd() + '/' + file_path
	with open(full_path, 'rb') as file:
		file_size = os.path.getsize(full_path)
		# print(file_size//40960)
		while message := file.read(40960):
			client.sendall(message)

		time.sleep(0.05)
		client.sendall('<EOF>'.encode())


def send_file_differences(client_file_list, server_file_list, client) -> None:
	'''
	Messages to client from server have the format of:
		/file.mp3
		/folder/
		/folder/file.mp3
	After every file is sent an additional message is sent with the actual file
	'''
	for file in server_file_list:
		if file in client_file_list: # Client already has that file
			continue

		if file[-1] == '/':
			#current file is a directory
			client.sendall(file.encode())
			continue

		client.sendall(file.encode())
		time.sleep(0.05)
		send_file_to_client(client, file)
		wait_for_client_message(client, '<SNF>') # [S]end [N]ext [F]ile

def build_local_library(path:str) -> list:
	'''Builds a list of all directories and files in the path specified
	   Note: directories always come before sub-files in the list'''
	folder_list = []
	for file in os.listdir(path):
		if os.path.isfile(path + file):
			folder_list.append(path + file)
		else:
			folder_list.append(path + file + '/')
			if directory_dict := build_local_library(path + file + '/'):
				folder_list.append(*directory_dict)
	return folder_list



def client_send_okay_end(client, addr) -> None:
	logging.info(f'Client {addr[0]} is synced')
	client.sendall('okay'.encode())

def client_begin_sync(client, addr) -> None:
	logging.info(f'Client {addr[0]} needs to sync')
	client.sendall('sync'.encode())

	data = client.recv(1024)
	client_library_json = json.loads(data.decode())
	

	send_file_differences(client_library_json, local_library, client)
	client.sendall('<END>'.encode()) # <END> Tag completes the sync
	logging.info(f'Client {addr[0]} synced')

def main_socket_loop(server, last_update) -> None:
	try:
		while True:
			server.listen()
			client, addr = server.accept()
			logging.info(f'Connected by {addr[0]}:{addr[1]}')

			last_sync = client.recv(1024)
			last_sync_decoded = last_sync.decode()

			if float(last_sync_decoded) > float(last_update):
				client_send_okay_end(client, addr)
			else:
				client_begin_sync(client, addr)

			logging.debug(f'Closing connection with {addr[0]}')
			client.close()
	except KeyboardInterrupt:
		print('\n')
		logging.info('Closing Server')


def main() -> None:
	# initial setup
	last_update = '99999999999999999999' # in the future, hacky
	logging.basicConfig(format='[%(asctime)s] [%(levelname)s]: %(message)s', 
						datefmt='%d %b %H:%M:%S',
						level=logging.INFO)

	#Builds audio library 
	global local_library
	local_library = build_local_library('audio/')
	
	# start tcp server
	with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
		server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

		server.bind(('192.168.0.63', 9999))
		logging.info('Started succesfully')
		main_socket_loop(server, last_update)
	

if __name__ == '__main__':
	main()