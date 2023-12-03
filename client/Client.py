import socket
import time
import os
import json
import yaml
import logging
import threading

from ComProtocol import ComProtocol as ComProt
# NOTE : This file doesn't have any modularity as it will become it's own repo
# and application at time some, this should only be used for testing



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

class Client:
	def __init__(self) -> None:
		self._load_config_file()
		self._create_daemon_for_sync()

	def _create_default_config(self) -> None:
		'''Creates a default config and returns a dictionary with the data'''
		logging.info('Config file doesn\'t exist, creating config file')
		default_data = {
			'host' : '192.168.0.120',
			'port' : 9999,
			'uuid' : None,
			'last_sync' : 0
			}
		self._dump_to_yaml_file(default_data, 'client_settings.yaml')
		self._config_file_name = 'client_settings.yaml'

	def _load_config_file_from_name(self, file_name:str) -> None:
		'''Load config file from name'''
		with open(file_name, 'r') as file:
				data_loaded = yaml.safe_load(file)
		self._host_ip = data_loaded['host']
		self._host_port = data_loaded['port']
		self._uuid = data_loaded['uuid']
		self._last_sync = data_loaded['last_sync']
		logging.info('Config file loaded successfully')

	def _dump_to_yaml_file(self, data:dict, file_name:str) -> None:
		'''Dump current config to file'''
		with open(file_name, 'w', encoding='utf8') as file:
			yaml.dump(data, file, default_flow_style=False, allow_unicode=True)

	def _load_config_file(self) -> None:
		'''Checks if the client file configuration file exists and reads config settings,
		Else if it doesn't exist, it creates and loads it with the default values'''
		logging.info('Loading config file...')

		if os.path.isfile('client_settings.yaml'):
			self._config_file_name = 'client_settings.yaml'
		elif os.path.isfile('client_settings.yml'):
			self._config_file_name = 'client_settings.yml'
		else:
			# no configuration file found, create it
			self._create_default_config()
		self._load_config_file_from_name(self._config_file_name)

	def _create_daemon_for_sync(self) -> None:
		'''Starts the Daemon thread for syncing'''
		self._thread = threading.Thread(target=self._thread__sync_main_loop)
		self._thread.start()

	def _thread__sync_main_loop(self) -> None:
		while True:
			self._load_config_file()
			self._sync()
			self._dump_current_config_to_file()
			time.sleep(30)

	def _dump_current_config_to_file(self) -> None:
		data_dict = {}
		data_dict['host'] = self._host_ip
		data_dict['port'] = self._host_port
		data_dict['uuid'] = self._uuid
		data_dict['last_sync'] = self._last_sync
		self._dump_to_yaml_file(data_dict, self._config_file_name)
		logging.info('Dumped current configuration to file')
	
	def _sync(self) -> None:
		'''Takes care of all the server messaging'''
		logging.info('Syncing with server')
		with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as self._socket:
			self._socket.connect((self._host_ip, self._host_port))
			if self._uuid:
				self._send_to_server(ComProt.UUID)
				time.sleep(0.05)
				self._send_to_server(self._uuid)
			else:
				self._send_to_server(ComProt.NO_UUID)
				self._uuid = self._receive_from_server()

			request_to_sync_from_server = self._receive_from_server()
			if request_to_sync_from_server == ComProt.SYNC:
				logging.info('Server requested to sync')
				path = '/music/' # Hardcoded
				temp_lib = build_local_library(path)
				local_library = json.dumps(temp_lib)
				self._send_to_server(local_library)
				self._receive_library_changes_from_server()


		logging.info('Syncing with server done')

	def _send_to_server(self, message:str) -> None:
		self._socket.sendall(message.encode())

	def _receive_from_server(self, _bytes=1024) -> str:
		encoded_string = self._socket.recv(_bytes)
		return encoded_string.decode()

	def _receive_library_changes_from_server(self) -> None:
		while True:
			file_path = os.getcwd() + self._receive_from_server() # Converts it to a local absolute path
			# data is type of current type of syncing file
			# directory or actual file
			if not file_path:
				logging.error('Got empty message, something went wrong')
				break
			print(file_path)
			if file_path[-1] == '/':
				# current syncing file is a directory
				# if it doesnt already exist, create it
				if not os.path.isdir(file_path):
					os.makedirs(file_path)
				continue
			if file_path[-5::] == ComProt.END:
				break
				
			self._receive_file(file_path)

	def receive_file(self, file_path) -> None:
		file = open(file_path, 'w+b')
		# receiving file loop
		while True:
			message = self._receive_from_server(40960) # 40960 is 40kB
			file.write(message)
			# TODO: this is hacky but works, maybe try to find a better alternative
			# probably an EOF tag from server
			if len(message) < 10: 
				if message == ComProt.EOF:
					file.close()
					self._send_to_server(ComProt.SNF)
					#server.sendall(ComProt.SNF.encode())
					break
				else:
					print(message)
def main_old():
	HOST = '192.168.0.120'  # The server's hostname or IP address, currently local ip address
	PORT = 9999  # The port used by the server position

	last_sync = str(time.time())
	with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
		s.connect((HOST, PORT))
		#uuid = '5a015648-ddaa-4198-bc5c-744e670a1a8b'
		s.sendall(ComProt.NO_UUID.encode())
		#s.sendall(uuid.encode())
		#s.sendall(last_sync.encode())
		uuid = s.recv(1024)
		#s.sendall('-2'.encode())
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


def main():
	client = Client()
if __name__ == '__main__':
	logging.basicConfig(format='[%(asctime)s] [%(levelname)s]: %(message)s', 
				datefmt='%d %b %H:%M:%S',
				level=logging.DEBUG)
	main()