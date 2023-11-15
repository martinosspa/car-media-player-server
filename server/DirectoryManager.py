import os

class DirectoryManager:
	def __init__(self, path) -> None:
		self._path = path
		self._files_list = None

	def build(self) -> list:
		''' Builds a list of all directories and files in the path specified
			This is meant to be called with Linux/Unix file structure in mind
			TODO: Windows file structure

			Note: directories always come before sub-files in the list
			if this order breaks the syncing will break down, this is why the communication
			is setup with TCP
			'''
		path = os.getcwd() + '/' + self._path
		self._files_list = self._build_sub_directories(self._path)

	def _build_sub_directories(self, path) -> list:
		folder_list = []
		for file in os.listdir(path):
			if os.path.isfile(path + file):
				folder_list.append(path + file)
			else:
				folder_list.append(path + file + '/')
				if directory_dict := self._build_sub_directories(path + file + '/'):
					folder_list += directory_dict # Both are lists
		return folder_list

	def get_files(self) -> list:
		'''Returns all folders list'''
		return self._files_list