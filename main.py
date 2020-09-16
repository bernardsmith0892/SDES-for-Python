#!/usr/bin/python3.8

import SDES
import SAES
import modes
import argparse
import secrets
import sys
import os

def main():
	SUPPORTED_CIPHERS = ('sdes', 'saes')

	# Setup argument parser
	parser = argparse.ArgumentParser(
		description="""
Encrypt or decrypt a file using a Simplified DES (SDES) or Simplified AES (SAES) cipher.

SDES - Implemented as described in Appendix G of Cryptography and Network Security, Fifth Edition by William Stallings.

Block-size: 8-bits
Key size: 10-bits (1024 possibilities)

SAES - Implemented as described by Mohammad Musa, Edward Schaefer, and Stephen Wedig of Santa Clara University.

Block-size: 16-bits
Key size: 16-bits (65,536 possibilities)

************************************
*** DO NOT USE FOR PRODUCTION!!! *** (That's probably obvious, though)
************************************
""",
		epilog=f"""
Example usage:
Encryption: python3.8 {sys.argv[0]} SAES cbc -iv 100 --encrypt 0xab plaintext.txt ciphertext.saes
Decryption: python3.8 {sys.argv[0]} SAES cbc -iv 100 --decrypt 0xab ciphertext.saes plaintext.txt --concurrent
		""",
		formatter_class=argparse.RawDescriptionHelpFormatter
	)
	
	parser.add_argument('cipher', type=str, help='The cipher algorithm to use. [SDES, SAES]')
	parser.add_argument('mode', type=str, help='The cipher mode to use. [ECB, CBC, CTR]')
	parser.add_argument('--encrypt', '-e', default=False, action='store_true', help='Encrypt the file.')
	parser.add_argument('--decrypt', '-d', default=False, action='store_true', help='Decrypt the file.')
	parser.add_argument('-iv', '--nonce', type=int, default=None, help='IV or nonce value to use.')
	parser.add_argument('key', type=str, help='The cipher key to use. Example: 1010101010 or 0xff')
	parser.add_argument('input_filename', type=str, help='The file to process.')
	parser.add_argument('output_filename', type=str, help='The file to store the results into.')
	parser.add_argument('-s', '--chunk_size', type=int, default=65536, help='The byte-size of chunks to process the files in. Defaults to 65536.')
	parser.add_argument('--concurrent', '-c', default=False, action='store_true', help='Process file with multiple threads, if possible.')
	parser.add_argument('--max_workers', '-w', type=int, default=None, help='Maximum number of workers to use for multiprocessing. (Defaults to the number of processors on the machine)')
	
	args = parser.parse_args()
	
	# Check if provided a valid cipher
	if args.cipher.lower() not in SUPPORTED_CIPHERS:
		print(f"'{args.cipher}' cipher is not supported! Please use one of the following!\n {SUPPORTED_CIPHERS}")
		exit()
	else:
		# Choose the selected cipher and format cipher attributes
		if args.cipher.lower() == 'sdes':
			F = SDES.F
			key = int(args.key, 2)
			blocksize = 1
		elif args.cipher.lower() == 'saes':
			if args.chunk_size % 2 != 0:
				print(f"Chunk size ({args.chunk_size}) cannot be an odd-number when using SAES!")
				exit()
			
			F = SAES.F
			key = int(args.key, 16)
			blocksize = 2
	
	# Check if provided a valid mode
	if args.mode.lower() not in modes.SUPPORTED_MODES:
		print(f"'{args.mode}' mode is not supported! Please use one of the following!\n {modes.SUPPORTED_MODES}")
		exit()
	
	# Determine encrypt or decrypt
	if args.encrypt == args.decrypt and (args.mode.lower() == 'ecb' or args.mode.lower() == 'cbc'): 
		print("Must specify an whether to encrypt or decrypt when using ECB or CBC mode!")
		exit()
	else:
		encrypt = args.encrypt
		
	# Generate an IV or nonce when not using ECB mode
	if args.nonce == None and args.mode.lower() != 'ecb':
		if not encrypt and args.mode.lower() != 'ctr':
			print("Must specify an IV or nonce value when decrypting in non-ECB mode!")
			exit()
		else:
			iv = secrets.randbits(8 * blocksize)
			print(f"IV/nonce generated is {iv}!")
	else:
		iv = args.nonce
	
	# Use ECB mode
	if(args.mode.lower() == "ecb"): 
		modes.ecb_file( args.input_filename, args.output_filename, key, F, encrypt, blocksize, args.chunk_size, args.concurrent, args.max_workers )
	
	# Use CBC mode
	elif(args.mode.lower() == "cbc"): 
		modes.cbc_file( args.input_filename, args.output_filename, key, iv, F, encrypt, blocksize, args.chunk_size, args.concurrent, args.max_workers )
	
	# Use CTR mode
	elif(args.mode.lower() == "ctr"): 
		modes.ctr_file( args.input_filename, args.output_filename, key, iv, F, blocksize, args.chunk_size, args.concurrent, args.max_workers )

			

if __name__ == "__main__":
	main()
