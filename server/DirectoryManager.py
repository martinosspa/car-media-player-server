import os



class DirectoryManager:

	def __init__(self, path) -> None:
		self._path = path
		self._folder_list = None

	def build_paths(self) -> list:
		''' Builds a list of all directories and files in the path specified
			This is meant to be called with Linux/Unix file structure in mind
			TODO: Windows file structure

			Note: directories always come before sub-files in the list
			if this order breaks the syncing will break down, this is why the communication
			is setup with TCP
			'''
		path = self._path + '/'
		os.chdir(path)
		local_library = build_local_library(path)

		folder_list = []
		for file in os.listdir(path):
			if os.path.isfile(path + file):
				folder_list.append(path + file)
			else:
				folder_list.append(path + file + '/')
				if directory_dict := build_local_library(path + file + '/'):
					folder_list.append(*directory_dict)
		self._folder_list = folder_list
		return self._folder_list

	def get_folders(self) -> list:
		return self._folder_list