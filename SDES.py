#!/usr/bin/python3.8

def left_shift(num, length=5):
	""" Rotates the given number left by one. Defaults to a 5-bit word. """
	
	num = (num << 1) + get_bit(num, 1, length)
	
	mask = 0
	for x in range(length):
		mask = (mask << 1) + 1
	
	return num & mask


def get_bit(num, pos, size=8, little_endian=True):
	""" Returns the bit value of the 'pos'th bit in num.
	
	Parameters
	----------
	num : int
		The integer to grab a bit value from.
	pos : int
		The bit position to grab	
	size : int
		Expected bitsize of the integer. Defaults to a byte (8-bits).
	little_endian : bool
		Whether `num` is in little endian. Defaults to little endian positioning. (MSB is position 1)
	
	Returns
	-------
	int
		The bit value	
	"""
	
	if(little_endian):
		return (num >> (size - pos)) & 1
	else:
		return (num >> pos) & 1

def permutate(input_num, permutation, input_size=8):
	""" Permutate the input's bits according to the given permutation array.

	Parameters
	----------
	input_num : int
		The number to permutate
	permutation : [int]
		Describes which input bits make up the output, and where they're positioned. The n'th index of the list is the n'th bit of the output number. The value of that element is the bitvalue to use from `input_num`, in little endian positioning.
		
		Example - [3, 1, 0, 2] permutates 0110 into 0101.
	input_size : int
		Expected bitsize of the input number. Defaults to a byte (8-bits).
	
	Returns
	-------
	int
		The permutated number

"""
	ret_num = 0
	for p in range(len(permutation)):
		ret_num += get_bit(input_num, permutation[p], input_size) << (len(permutation) - 1 - p)
	
	return ret_num

'''
All permutations performed in SDES.
'''
def P10(num):
	return permutate(num, [3, 5, 2, 7, 4, 10, 1, 9, 8, 6], input_size=10)

def P8(num):
	return permutate(num, [6, 3, 7, 4, 8, 5, 10, 9], input_size=10)

def P4(num):
	return permutate(num, [2, 4, 3, 1], input_size=4)

def IP(num):
	return permutate(num, [2, 6, 3, 1, 4, 8, 5, 7], input_size=8)

def IP_inverse(num):
	return permutate(num, [4, 1, 3, 5, 7, 2, 8, 6], input_size=8)

def E_P(num):
	return permutate(num, [4, 1, 2, 3, 2, 3, 4, 1], input_size=4)

def S0(num):
	""" Performs the S0-box calculation on the 4-bit input 'num'. """

	box = ( (1, 0, 3, 2)
		   ,(3, 2, 1, 0)
		   ,(0, 2, 1, 3) 
		   ,(3, 1, 3, 2) )
		   
	row = (get_bit(num, 1, 4) << 1) + get_bit(num, 4, 4)
	col = (get_bit(num, 2, 4) << 1) + get_bit(num, 3, 4)
	
	return box[row][col]

def S1(num):
	""" Performs the S1-box calculation on the 4-bit input 'num'. """
	
	box = ( (0, 1, 2, 3)
		   ,(2, 0, 1, 3)
		   ,(3, 0, 1, 0) 
		   ,(2, 1, 0, 3) )
		   
	row = (get_bit(num, 1, 4) << 1) + get_bit(num, 4, 4)
	col = (get_bit(num, 2, 4) << 1) + get_bit(num, 3, 4)
	
	return box[row][col]

def SW(num):
	""" Performs the switching function. Switches the left four bits of 'num' with the right four bits. """
	return ((num & (0b1111)) << 4) + (num >> 4)

def generate_subkeys(key):
	""" Generates the two subkeys K1 and K2 for use in the SDES algorithm. Returns the two keys in a tuple. """
	
	key = P10(key)
	
	key = ( left_shift(key >> 5) << 5 ) + ( left_shift(key & 0b11111) )
	
	K1 = P8(key)
	
	key = ( left_shift(key >> 5) << 5 ) + ( left_shift(key & 0b11111) )
	key = ( left_shift(key >> 5) << 5 ) + ( left_shift(key & 0b11111) )
	
	K2 = P8(key)
	
	return (K1, K2)

def f_K(num, subkey):
	""" Performs one round of the Feistel cipher on the provided number. """
	
	left_input = num >> 4
	right_input = num & 0b1111
		
	data = E_P(right_input)	
	data = data ^ subkey
	data = (S0(data >> 4) << 2) + S1(data & 0b1111)	
	data = P4(data)	
	left_output = left_input ^ data
		
	return (left_output << 4) + right_input
	
def F(input, key, encrypt=True):
	""" Encrypts or decrypts the provided byte using the SDES cipher. 
	
	Parameters
	----------
	input : bytearray
		The data to process.
	key : int
		The cipher key to use. (10-bits)
	encrypt : bool
		Whether to encrypt or decrypt the data. Defaults to encryption.
	 
	Returns
	-------
	int
		The encrypted or decrypted byte.
	"""	
	
	ip = IP(input)
	
	if encrypt:
		K1, K2 = generate_subkeys(key)
	else:
		K2, K1 = generate_subkeys(key)
	
	round = f_K(ip, K1)
	round = f_K(SW(round), K2)
	
	output = IP_inverse(round)
	
	return output





