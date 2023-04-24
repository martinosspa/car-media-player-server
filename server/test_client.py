import socket
import time
import os

def main():
	HOST = '192.168.0.63'  # The server's hostname or IP address
	PORT = 9999  # The port used by the server


	last_sync = str(time.time())

	with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
		s.connect((HOST, PORT))
		s.sendall(last_sync.encode())
		data = s.recv(1024)
		decoded_data = data.decode()
		
		if decoded_data == 'okay':
			# update last_sync to file
			return

		path = 'audio/'
		file_names = []
		for file_name in os.listdir(path):
			# audio_file_name = os.path.join(path, file_name)
			file_names.append(file_name)



		for file in file_names:
			s.send(file.encode())
			time.sleep(0.05)
			print(file)
		s.send('<END>'.encode())

		


		print(file_names)

		






	print(f'closed')

if __name__ == '__main__':
	main()