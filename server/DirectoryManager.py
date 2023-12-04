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
		self._files_list = self._build_sub_directories(self._path)

	def _build_sub_directories(self, path) -> list:
		folder_list = []
		parent_path_length = len(os.getcwd())
		for folder_path, directories, files in os.walk(os.getcwd() + path, topdown=True):
			folder_list.append(folder_path[parent_path_length::] + '/')
			if files:
				for file in files:
					folder_list.append(folder_path[parent_path_length::] + '/' + file)
		return folder_list

	def get_files(self) -> list:
		'''Returns all folders list'''
		return self._files_list
