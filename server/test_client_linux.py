import socket
import time
import os
import json

def main():
	HOST = '192.168.0.63'  # The server's hostname or IP address, currently local ip address
	PORT = 9999  # The port used by the server


	last_sync = str(time.time())

	with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
		s.connect((HOST, PORT))
		s.sendall(last_sync.encode())
		data = s.recv(1024)
		decoded_data = data.decode()

		print(decoded_data)
		if decoded_data == 'okay':
			# update last_sync to file
			return
		else:
			path = 'audio/'

			folder_list = []
			for folder in os.walk(path, topdown=False):
				folder_dict = {
				'name' : folder[0],
				'subdirs' : folder[1],
				'files' : folder[2]
				}
				folder_list.append(folder_dict)
			json_str = json.dumps(folder_list)
			s.sendall(json_str.encode())
			





		print('done')
	print('closed')

if __name__ == '__main__':
	main()