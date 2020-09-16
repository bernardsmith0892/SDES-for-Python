#!/usr/bin/python3.8

import concurrent.futures

SUPPORTED_MODES = ('ecb', 'cbc', 'ctr')

def ecb(input_data, key, F, encrypt=True, blocksize=1):
	""" Encrypt or decrypt the input using electronic code book (ECB) mode.
	
	Parameters
	----------
	input_data : bytearray
		The data to process.
	key : int
		The cipher key to use.
	F : function
		The cipher algorithm to use.
	encrypt : bool
		Whether to encrypt or decrypt the data. Defaults to encryption.
	blocksize : int
		The blocksize of the cipher in bytes
	
	Returns
	-------
	bytearray
		The ECB processed bytes.
	"""	
	
	output = bytearray()
	for i in range(0, len(input_data), blocksize):
		b = int.from_bytes( input_data[i : i + blocksize], 'big' )
		processed_byte = F(b, key, encrypt)
		output += processed_byte.to_bytes(blocksize, 'big')
	
	return bytes(output)


def cbc(input_data, key, iv, F, encrypt=True, blocksize=1):
	""" Encrypt or decrypt the input using cipher block chaining (CBC) mode.
	
	Parameters
	----------
	input_data : bytearray
		The data to process.
	key : int
		The cipher key to use.
	iv : int
		The initialization vector to use.
	F : function
		The cipher algorithm to use.
	encrypt : bool
		Whether to encrypt or decrypt the data. Defaults to encryption.
	blocksize : int
		The blocksize of the cipher in bytes
		
	Returns
	-------
	bytearray
		The CBC processed bytes.
	int
		The IV value to provide to the next chunk of data.
	"""	
	
	output = bytearray()
	for i in range(0, len(input_data), blocksize):
		b = int.from_bytes( input_data[i : i + blocksize], 'big' )
		if( encrypt ):
			intermediate_value = b ^ iv
			processed_byte = F(intermediate_value, key, encrypt)
			iv = processed_byte	
		else:
			intermediate_value = F(b, key, encrypt)
			processed_byte = intermediate_value ^ iv
			iv = b
		output += processed_byte.to_bytes(blocksize, 'big')
		
	return bytes(output), iv
	
def ctr(input_data, key, nonce, F, blocksize=1):
	""" Encrypt or decrypt the input using counter (CTR) mode.
	
	Parameters
	----------
	input_data : bytearray
		The data to process.
	key : int
		The cipher key to use.
	nonce : int
		The nonce value to use.
	F : function
		The cipher algorithm to use.
	blocksize : int
		The blocksize of the cipher in bytes
		 
	Returns
	-------
	bytearray
		The CTR processed bytes.
	int
		The nonce value to provide to the next chunk of data.
	"""	
		
	output = bytearray()
	ctr = 0
	for i in range(0, len(input_data), blocksize):
		b = int.from_bytes( input_data[i : i + blocksize], 'big' )
		
		intermediate_value = F(nonce + ctr, key)
		processed_byte = intermediate_value ^ b
		ctr += 1
		output += processed_byte.to_bytes(blocksize, 'big')
		
	return bytes(output), (nonce + ctr)
	
def ecb_file(input_filename, output_filename, key, F, encrypt=True, blocksize=1, chunk_size=65535, multithreaded=False, max_workers=None):
	""" Encrypt or decrypt the file using ECB and output the result into another file.
	
	Parameters
	----------
	input_filename : string
		The name of the file to process.
	output_filename : string
		The name of the file to write the processed data to.
	key : int
		The cipher key to use.
	F : function
		The cipher algorithm to use.
	encrypt : bool
		Whether to encrypt or decrypt the data. Defaults to encryption.
	multithreaded : bool
		Whether to process the file in parallel. Defaults to single-threaded.
	blocksize : int
		The blocksize of the cipher in bytes
	"""
	
	# Single-threading
	if not multithreaded:
		with open(input_filename, 'rb') as input_file, open(output_filename, 'wb') as output_file:
			# Process the file in 64kB chunks
			while chunk := bytearray(input_file.read(chunk_size)):
				output_file.write( ecb(chunk, key, F, encrypt, blocksize) )
	
	# Multi-threading
	elif multithreaded:
		with open(input_filename, 'rb') as input_file, open(output_filename, 'wb') as output_file, concurrent.futures.ProcessPoolExecutor(max_workers=max_workers) as executor:
			# Create concurrent processes for each 64kB chunk
			ecb_processes = []
			while chunk := bytearray(input_file.read(chunk_size)):
				ecb_processes.append( executor.submit(ecb, chunk, key, F, encrypt, blocksize) )
			
			# Write the results to the output file, in order
			for p in ecb_processes:
				output_file.write( p.result() )

				
def cbc_file(input_filename, output_filename, key, iv, F, encrypt=True, blocksize=1, chunk_size=65535, multithreaded=False, max_workers=None):
	""" Encrypt or decrypt the file using CBC and output the result into another file.
	
	Parameters
	----------
	input_filename : string
		The name of the file to process.
	output_filename : string
		The name of the file to write the processed data to.
	key : int
		The cipher key to use.
	iv : int
		The initialization vector to use.
	F : function
		The cipher algorithm to use.
	encrypt : bool
		Whether to encrypt or decrypt the data. Defaults to encryption.
	blocksize : int
		The blocksize of the cipher in bytes
	multithreaded : bool
		Whether to process the file in parallel. Defaults to single-threaded. (Decryption-only)
	"""	
	
	# Single-threading (encryption and if chosen for decryption)
	if not multithreaded or encrypt:
		with open(input_filename, 'rb') as input_file, open(output_filename, 'wb') as output_file:
			# Process the file in 64kB chunks
			while chunk := bytearray(input_file.read(chunk_size)):
				output_bytes, iv = cbc(chunk, key, iv, F, encrypt, blocksize)
				output_file.write( output_bytes )
	
	# Multi-threading (decryption-only)
	elif multithreaded:
		with open(input_filename, 'rb') as input_file, open(output_filename, 'wb') as output_file, concurrent.futures.ProcessPoolExecutor(max_workers=max_workers) as executor:
			# Create concurrent processes for each 64kB chunk
			cbc_processes = []
			while chunk := bytearray(input_file.read(chunk_size)):
				cbc_processes.append( executor.submit(cbc, chunk, key, iv, F, encrypt, blocksize) )
				iv = int.from_bytes( chunk[-blocksize:], 'big' )
			
			# Write the results to the output file, in order
			for p in cbc_processes:
				output_file.write( p.result()[0] )
			
def ctr_file(input_filename, output_filename, key, nonce, F, blocksize=1, chunk_size=65535, multithreaded=False, max_workers=None):
	""" Encrypt or decrypt the file using CTR and output the result into another file.
	
	Parameters
	----------
	input_filename : string
		The name of the file to process.
	output_filename : string
		The name of the file to write the processed data to.
	key : int
		The cipher key to use.
	nonce : int
		The nonce value to use.
	F : function
		The cipher algorithm to use.
	blocksize : int
		The blocksize of the cipher in bytes
	multithreaded : bool
		Whether to process the file in parallel. Defaults to single-threaded.
	"""	
	
	# Single-threading	
	if not multithreaded:
		with open(input_filename, 'rb') as input_file, open(output_filename, 'wb') as output_file:
			# Process the file in 64kB chunks
			while chunk := bytearray(input_file.read(chunk_size)):
				output_bytes, nonce = ctr(chunk, key, nonce, F, blocksize)
				output_file.write( output_bytes )
	
	# Multi-threading	
	elif multithreaded:
		with open(input_filename, 'rb') as input_file, open(output_filename, 'wb') as output_file, concurrent.futures.ProcessPoolExecutor(max_workers=max_workers) as executor:
			# Create concurrent processes for each 64kB chunk
			ctr_processes = []
			offset = 0
			while chunk := bytearray(input_file.read(chunk_size)):
				ctr_processes.append( executor.submit(ctr, chunk, key, nonce + offset, F, blocksize) )
				offset += chunk_size
			
			# Write the results to the output file, in order
			for p in ctr_processes:
				output_file.write( p.result()[0] )

	