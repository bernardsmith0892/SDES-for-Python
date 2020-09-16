#!/usr/bin/python3.8

import concurrent.futures

SUPPORTED_MODES = ('ecb', 'cbc', 'ctr')

def ecb(input_data, key, F, encrypt=True):
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
	 
	Returns
	-------
	bytearray
		The ECB processed bytes.
	"""	
	
	output = bytearray()
	for b in input_data:
		processed_byte = F(b, key, encrypt)
		output.append(processed_byte)
	
	return bytes(output)


def cbc(input_data, key, iv, F, encrypt=True):
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
	 
	Returns
	-------
	bytearray
		The CBC processed bytes.
	int
		The IV value to provide to the next chunk of data.
	"""	
	
	output = bytearray()
	for b in input_data:
		if( encrypt ):
			intermediate_value = b ^ iv
			processed_byte = F(intermediate_value, key, encrypt)
			iv = processed_byte	
		else:
			intermediate_value = F(b, key, encrypt)
			processed_byte = intermediate_value ^ iv
			iv = b
		output.append(processed_byte)
		
	return bytes(output), iv
	
def ctr(input_data, key, nonce, F):
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
	 
	Returns
	-------
	bytearray
		The CTR processed bytes.
	int
		The nonce value to provide to the next chunk of data.
	"""	
		
	output = bytearray()
	ctr = 0
	for b in input_data:
		intermediate_value = F(nonce + ctr, key)
		processed_byte = intermediate_value ^ b
		ctr += 1
		output.append(processed_byte)
		
	return bytes(output), (nonce + ctr)
	
def ecb_file(input_filename, output_filename, key, F, encrypt=True, chunk_size=65535, multithreaded=False):
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
	"""
	
	# Single-threading
	if not multithreaded:
		with open(input_filename, 'rb') as input_file, open(output_filename, 'wb') as output_file:
			# Process the file in 64kB chunks
			while chunk := bytearray(input_file.read(chunk_size)):
				output_file.write( ecb(chunk, key, F, encrypt) )
	
	# Multi-threading
	elif multithreaded:
		with open(input_filename, 'rb') as input_file, open(output_filename, 'wb') as output_file, concurrent.futures.ProcessPoolExecutor() as executor:
			# Create concurrent processes for each 64kB chunk
			ecb_processes = []
			while chunk := bytearray(input_file.read(chunk_size)):
				ecb_processes.append( executor.submit(ecb, chunk, key, F, encrypt) )
			
			# Write the results to the output file, in order
			for p in ecb_processes:
				output_file.write( p.result() )

				
def cbc_file(input_filename, output_filename, key, iv, F, encrypt=True, chunk_size=65535, multithreaded=False):
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
	multithreaded : bool
		Whether to process the file in parallel. Defaults to single-threaded. (Decryption-only)
	"""	
	
	# Single-threading (encryption and if chosen for decryption)
	if not multithreaded or encrypt:
		with open(input_filename, 'rb') as input_file, open(output_filename, 'wb') as output_file:
			# Process the file in 64kB chunks
			while chunk := bytearray(input_file.read(chunk_size)):
				output_bytes, iv = cbc(chunk, key, iv, F, encrypt)
				output_file.write( output_bytes )
	
	# Multi-threading (decryption-only)
	elif multithreaded:
		with open(input_filename, 'rb') as input_file, open(output_filename, 'wb') as output_file, concurrent.futures.ProcessPoolExecutor() as executor:
			# Create concurrent processes for each 64kB chunk
			cbc_processes = []
			while chunk := bytearray(input_file.read(chunk_size)):
				cbc_processes.append( executor.submit(cbc, chunk, key, iv, F, encrypt) )
				iv = chunk[-1]
			
			# Write the results to the output file, in order
			for p in cbc_processes:
				output_file.write( p.result()[0] )
			
def ctr_file(input_filename, output_filename, key, nonce, F, chunk_size=65535, multithreaded=False):
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
	multithreaded : bool
		Whether to process the file in parallel. Defaults to single-threaded.
	"""	
	
	# Single-threading	
	if not multithreaded:
		with open(input_filename, 'rb') as input_file, open(output_filename, 'wb') as output_file:
			# Process the file in 64kB chunks
			while chunk := bytearray(input_file.read(chunk_size)):
				output_bytes, nonce = ctr(chunk, key, nonce, F)
				output_file.write( output_bytes )
	
	# Multi-threading	
	elif multithreaded:
		with open(input_filename, 'rb') as input_file, open(output_filename, 'wb') as output_file, concurrent.futures.ProcessPoolExecutor() as executor:
			# Create concurrent processes for each 64kB chunk
			ctr_processes = []
			offset = 0
			while chunk := bytearray(input_file.read(chunk_size)):
				ctr_processes.append( executor.submit(ctr, chunk, key, nonce + offset, F) )
				offset += chunk_size
			
			# Write the results to the output file, in order
			for p in ctr_processes:
				output_file.write( p.result()[0] )

	