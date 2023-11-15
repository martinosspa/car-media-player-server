class ComProtocol:
	''' This class holds standards for the simple protocol
		that is used between client and server'''

	SNF = '<SNF>' # [S]end [N]ext [F]ile
	OKAY = '<OKAY>'
	SYNC = '<SYNC>'
	END = '<END>'
	UUID = '<UUID>'
	NO_UUID = '<NO_UUID>'
	EOF = '<EOF>'