import logging
from Server import Server

class ServerHandler:
	def __init__(self) -> None:
		# logging configuration
		logging.basicConfig(format='[%(asctime)s] [%(levelname)s]: %(message)s', 
						datefmt='%d %b %H:%M:%S',
						level=logging.DEBUG)
		self.server = Server()


if __name__ == '__main__':
	#main()
	server_handler = ServerHandler()