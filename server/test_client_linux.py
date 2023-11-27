import socket
import time
import os
import json
from ComProtocol import ComProtocol as ComProt
# NOTE : This file doesn't have any modularity as it will become it's own repo
# and application at time some, this should only be used for testing

def receive_file(server, file_path) -> None:
	file = open(file_path, 'w+b')
	# receiving file loop
	while True:
		message = server.recv(40960) # 40960 is 40kB
		file.write(message)
		# TODO: this is hacky but works, maybe try to find a better alternative
		# probably an EOF tag from server
		if len(message) < 10: 
			if message.decode() == ComProt.EOF:
				file.close()
				server.sendall(ComProt.SNF.encode())
				break
			else:
				print(message)

def build_local_library(path:str) -> list:
	folder_list = []
	for file in os.listdir(os.getcwd() + path):
		if os.path.isfile(path + file):
			folder_list.append(path + file)
		else:
			folder_list.append(path + file + '/')
			if directory_dict := build_local_library(path + file + '/'):
				folder_list += directory_dict
	return folder_list

def main():
	HOST = '192.168.0.63'  # The server's hostname or IP address, currently local ip address
	PORT = 9999  # The port used by the server position

	last_sync = str(time.time())
	with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
		s.connect((HOST, PORT))
		#uuid = '5a015648-ddaa-4198-bc5c-744e670a1a8b'
		s.sendall(ComProt.NO_UUID.encode())
		#s.sendall(uuid.encode())
		#s.sendall(last_sync.encode())
		uuid = s.recv(1024)
		s.sendall('-2'.encode())
		data = s.recv(1024)
		decoded_data = data.decode()

		print(decoded_data)
		if decoded_data ==  ComProt.OKAY:
			# update last_sync to file
			return
		elif decoded_data == ComProt.SYNC:
			# start sync
			print('started sync from server')
			path = '/music/' # Hardcoded

			temp_lib = build_local_library(path)
			local_library = json.dumps(temp_lib)
			s.sendall(local_library.encode())


			# receive changes
			while True:
				file_path = os.getcwd() + s.recv(1024).decode() # Converts it to a local path
				# data is type of current type of syncing file
				# directory or actual file
				if not file_path:
					print('got empty message, something went wrong')
					break
				print(file_path)

				if file_path[-1] == '/':
					# current syncing file is a directory
					# if it doesnt already exist, create it
					if not os.path.isdir(file_path):
						os.makedirs(file_path)
					continue

				if file_path[-5::] == ComProt.END:
					print('got <END>')
					break

				
				receive_file(s, file_path)

					#print(len(message))

		print('done')
	print('closed')

if __name__ == '__main__':
	main()