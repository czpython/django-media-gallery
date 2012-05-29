import base64

def encode_string(string):
	"""
		Encrypts the string.
	"""
	return base64.b64encode(string)

def decode_string(string):
	return base64.b64decode(string)