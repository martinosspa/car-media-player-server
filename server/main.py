import socket
import time
import logging


def build_local_library(path:str) -> None:
	#for file in 
	pass
def main():

	
	# main setup
	last_update = '1' # in the future, hacky
	logging.basicConfig(format='[%(asctime)s] [%(levelname)s]: %(message)s', 
						datefmt='%d %b %H:%M:%S',
						level=logging.INFO)

	# build audio library 

	#build_local_library(path)

	
	# start tcp server
	with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
		server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

		server.bind(('192.168.0.63', 9999))
		logging.info('Started succesfully')
		try:
			while True:
				server.listen()

				client, addr = server.accept()

				with client:
					logging.info(f'Connected by {addr[0]}:{addr[1]}')
					last_sync = client.recv(1024)
					last_sync_decoded = last_sync.decode()

					if float(last_sync_decoded) > float(last_update):
						logging.info(f'client {addr[0]} is synced')
						client.sendall('okay'.encode())
						break

					logging.info('Client needs to sync')
					time.sleep(1)
					client.sendall('sync'.encode())
					file_names = []

					while True:
						data = client.recv(1024)
						decoded_data = str(data.decode())
						
						if decoded_data:
							if decoded_data[-5:] == '<END>':
								break
							file_names.append(decoded_data)

					# Check file names against server's 

					logging.info(f'Closing connection with {addr[0]}')

					
					# while True:
					# 	data = client.recv(1024)
						
					# 	if not data:
					# 		break
					# 	client.sendall(data)
		except KeyboardInterrupt:
			print('\n')
			logging.info('closing')

if __name__ == '__main__':
	main()