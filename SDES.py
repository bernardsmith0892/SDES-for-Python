#!/usr/bin/python3.7

import sys

'''
Rotates the given number left by one. Defaults to a 5-bit word.
'''
def left_shift(num, length=5):
	num = (num << 1) + get_bit(num, 1, length);
	
	mask = 0;
	for x in range(length):
		mask = (mask << 1) + 1;
	
	return num & mask;

'''
Returns the bit value of the 'pos'th bit in num. Defaults to little endian positioning. (MSB is position 1)
'''
def get_bit(num, pos, size=8, little_endian=True):
	if(little_endian):
		return (num >> (size - pos)) & 1;
	else:
		return (num >> pos) & 1;

'''
Permutate the input's bits according to the given permutation array.
The permutation array describes which input bits make up the output, and where they're positioned.
'''
def permutate(input_num, permutation, input_size=8):
	ret_num = 0;
	for p in range(len(permutation)):
		ret_num += get_bit(input_num, permutation[p], input_size) << (len(permutation) - 1 - p);
	
	return ret_num;

'''
All permutations performed in SDES.
'''
def P10(num):
	return permutate(num, [3, 5, 2, 7, 4, 10, 1, 9, 8, 6], input_size=10);

def P8(num):
	return permutate(num, [6, 3, 7, 4, 8, 5, 10, 9], input_size=10);

def P4(num):
	return permutate(num, [2, 4, 3, 1], input_size=4);

def IP(num):
	return permutate(num, [2, 6, 3, 1, 4, 8, 5, 7], input_size=8);

def IP_inverse(num):
	return permutate(num, [4, 1, 3, 5, 7, 2, 8, 6], input_size=8);

def E_P(num):
	return permutate(num, [4, 1, 2, 3, 2, 3, 4, 1], input_size=4);

'''
Performs the S0-box calculation on the 4-bit input 'num'.
'''		
def S0(num):
	box = ( (1, 0, 3, 2)
		   ,(3, 2, 1, 0)
		   ,(0, 2, 1, 3) 
		   ,(3, 1, 3, 2) )
		   
	row = (get_bit(num, 1, 4) << 1) + get_bit(num, 4, 4);
	col = (get_bit(num, 2, 4) << 1) + get_bit(num, 3, 4);
	
	return box[row][col];

'''
Performs the S1-box calculation on the 4-bit input 'num'.
'''
def S1(num):
	box = ( (0, 1, 2, 3)
		   ,(2, 0, 1, 3)
		   ,(3, 0, 1, 0) 
		   ,(2, 1, 0, 3) )
		   
	row = (get_bit(num, 1, 4) << 1) + get_bit(num, 4, 4);
	col = (get_bit(num, 2, 4) << 1) + get_bit(num, 3, 4);
	
	return box[row][col];

'''
Performs the switching function. Switches the left four bits of 'num' with the right four bits.
'''
def SW(num):
	return ((num & (0b1111)) << 4) + (num >> 4)

'''
Generates the two subkeys K1 and K2 for use in the SDES algorithm.
Returns the two keys in a tuple.
'''
def generate_subkeys(key):
	key = P10(key);
	
	key = ( left_shift(key >> 5) << 5 ) + ( left_shift(key & 0b11111) )
	
	K1 = P8(key);
	
	key = ( left_shift(key >> 5) << 5 ) + ( left_shift(key & 0b11111) )
	key = ( left_shift(key >> 5) << 5 ) + ( left_shift(key & 0b11111) )
	
	K2 = P8(key);
	
	return (K1, K2);

'''
Performs one round of the Feistel cipher on the provided number.
'''
def f_K(num, subkey):
	left_input = num >> 4;
	right_input = num & 0b1111;
		
	data = E_P(right_input);	
	data = data ^ subkey;
	data = (S0(data >> 4) << 2) + S1(data & 0b1111);	
	data = P4(data);	
	left_output = left_input ^ data;
		
	return (left_output << 4) + right_input;
	
'''
Encrypts the provided plaintext byte using the two subkeys, K1 and K2.
'''	
def encrypt_byte(plaintext, K1, K2):
	ip = IP(plaintext);
	
	round = f_K(ip, K1);
	round = f_K(SW(round), K2);
	
	ciphertext = IP_inverse(round);
	
	return ciphertext;

'''
Decrypts the provided ciphertext byte using the two subkeys, K1 and K2.
'''		
def decrypt_byte(ciphertext, K1, K2):
	ip = IP(ciphertext);
	
	round = f_K(ip, K2);
	round = f_K(SW(round), K1);
	
	plaintext = IP_inverse(round);
	
	return plaintext;

'''
Encrypt or decrypt the input using SDES in electronic code book mode.
  input_data: The data to process. Expects a byte-array.
  key: The cipher key to process with.
  mode: Whether to encrypt or decrypt the data. Defaults to encryption.
'''	
def ecb(input_data, key, mode='encrypt'):
	K1, K2 = generate_subkeys(key);
	
	output = bytearray();
	for b in input_data:
		if(mode.lower() == 'encrypt'):
			processed_byte = encrypt_byte(b, K1, K2);
		else:
			processed_byte = decrypt_byte(b, K1, K2);
		output.append(processed_byte);
	
	return bytes(output);

def main():
	# Help text if not given enough arguments.
	if(len(sys.argv) < 5):
		print("***********************");
		print("* SDES File Encryptor *");
		print("***********************\n");
		print(f"Usage:\n\tEncryption: python3 {sys.argv[0]} -e 'key_in_binary' 'plaintext_file' 'ciphertext_file'\n\tDecryption: python3 {sys.argv[0]} -d 'key_in_binary' 'ciphertext_file' 'plaintext_file'");
		print(f"Example: python3 {sys.argv[0]} -e 1100101010 plaintext.txt cipertext.sdes");
		quit();
	
	# Process the given files
	with open(sys.argv[3], 'rb') as input_file:
		with open(sys.argv[4], 'wb') as output_file:
			chunk = bytearray(input_file.read(65535)); # Process the file in 64kB chunks
			key = int(sys.argv[2], 2); # Grab and decode the provided cipher key
			while chunk: # Process the entire file
				if(sys.argv[1] == "-e"): # Encrypt the data
					output_file.write( ecb(chunk, key) )
				elif(sys.argv[1] == "-d"): # Decrypt the data
					output_file.write( ecb(chunk, key, mode="decrypt") );
				else:
					# Error case if an improper mode is provided.
					sys.stderr.write(f"Mode '{sys.argv[1]}' is not supported! Please use '-e' or '-d'!\n");
					quit();
				chunk = input_file.read(65535);
			

if __name__ == "__main__":
	main()
