import socket
import time
import logging
import os
import json


def build_local_library(path:str) -> list:
	folder_list = []
	for folder in os.walk(path, topdown=False):
		folder_dict = {
		'name' : folder[0],
		'subdirs' : folder[1],
		'files' : folder[2]
		}
		folder_list.append(folder_dict)

	return folder_list



def client_send_okay_end(client, addr) -> None:
	logging.info(f'Client {addr[0]} is synced')
	client.sendall('okay'.encode())

def client_begin_sync(client, addr) -> None:
	logging.info(f'Client {addr[0]} needs to sync')
	client.sendall('sync'.encode())

	data = client.recv(1024)
	client_library_json = json.loads(data.decode())

	print(local_library == client_library_json)
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