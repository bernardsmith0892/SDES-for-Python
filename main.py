#!/usr/bin/python3.8

import SDES
import modes
import argparse
import secrets
import sys
import os

def main():	
	# Setup argument parser
	parser = argparse.ArgumentParser(
		description="""
Encrypt or decrypt a file using a Simplified DES (SDES) cipher. The block cipher is implemented as described in Appendix G of Cryptography and Network Security, Fifth Edition by William Stallings.

Block-size: 1 byte
Key-size: 10-bits (1024 possibilities)

************************************
*** DO NOT USE FOR PRODUCTION!!! *** (That's probably obvious, though)
************************************
""",
		epilog=f"""
Example usage:
Encryption: python3.8 {sys.argv[0]} cbc -iv 100 --encrypt 1010101010 plaintext.txt ciphertext.sdes
Decryption: python3.8 {sys.argv[0]} cbc -iv 100 --decrypt --concurrent 1010101010 ciphertext.sdes plaintext.txt
		""",
		formatter_class=argparse.RawDescriptionHelpFormatter
	)
	
	parser.add_argument('mode', type=str, help='The cipher mode to use. [ECB, CBC, CTR]')
	parser.add_argument('--encrypt', '-e', default=False, action='store_true', help='Encrypt the file.')
	parser.add_argument('--decrypt', '-d', default=False, action='store_true', help='Decrypt the file.')
	parser.add_argument('-iv', '--nonce', type=int, default=None, help='IV or nonce value to use.')
	parser.add_argument('key', type=str, help='The 10-bit cipher key to use. Example: 1010101010')
	parser.add_argument('input_filename', type=str, help='The file to process.')
	parser.add_argument('output_filename', type=str, help='The file to store the results into.')
	parser.add_argument('-s', '--chunk_size', type=int, default=65535, help='The byte-size of chunks to process the files in. Defaults to 65535.')
	parser.add_argument('--concurrent', '-c', default=False, action='store_true', help='Process file with multiple threads, if possible.')
	
	args = parser.parse_args()
	
	key = int(args.key, 2)
	
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
			iv = secrets.randbits(8)
			print(f"IV/nonce generated is {iv}!")
	else:
		iv = args.nonce
	
	# Use ECB mode
	if(args.mode.lower() == "ecb"): 
		modes.ecb_file( args.input_filename, args.output_filename, key, SDES.F, encrypt, args.chunk_size, args.concurrent )
	
	# Use CBC mode
	elif(args.mode.lower() == "cbc"): 
		modes.cbc_file( args.input_filename, args.output_filename, key, iv, SDES.F, encrypt, args.chunk_size, args.concurrent )
	
	# Use CTR mode
	elif(args.mode.lower() == "ctr"): 
		modes.ctr_file( args.input_filename, args.output_filename, key, iv, SDES.F, args.chunk_size, args.concurrent )

			

if __name__ == "__main__":
	main()
