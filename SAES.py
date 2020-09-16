#!/usr/bin/python3.8

def sub_word(word):
	""" Performs the SubNibble transformation on the two nibbles in a word. """
	return sub_nibble(word >> 4 & 0xf) << 4 ^ sub_nibble(word & 0xf)
	
def rot_word(word):
	""" Rotates the two nibbles (4-bits) in a single byte. """
	return (word << 4 & 0xff) ^ (word >> 4)

def expand_key(key):
	""" Performs the key expansion routine, creating three 16-bit round keys from a single 16-bit integer
	
	Parameters
	----------
	key : int
		The 16-bit integer to expand.
	
	Returns
	-------
	[ [int] ]
		A 3x2 integer matrix of the round keys. 
		[ K0, K1, K2 ] where Kn = [ w_2n, w_2n+1 ]
	"""
	w = [0, 0, 0, 0, 0, 0]
	w[0] = key >> 8 & 0xff
	w[1] = key & 0xff
	
	t2 = sub_word( rot_word( w[1] ) ) ^ 0x80
	w[2] = w[0] ^ t2
	w[3] = w[2] ^ w[1]
	
	t4 = sub_word( rot_word( w[3] ) ) ^ 0x30
	w[4] = w[2] ^ t4
	w[5] = w[4] ^ w[3]
	
	return w[0:2], w[2:4], w[4:6]

def add_round_key(state, roundkey):
	""" Performs the AddRoundKey transformation on a 16-bit state. This transformation is its own inverse. """
	return [ state[0] ^ (roundkey[0] >> 4 & 0xf), state[1] ^ (roundkey[0] & 0xf), 
			 state[2] ^ (roundkey[1] >> 4 & 0xf), state[3] ^ (roundkey[1] & 0xf)]

def sub_nibble(nibble, inverse=False):
	""" Performs the substitution transformation on a 4-bit nibble. Used for the table lookup in SubNibbles. """
	# Selects the proper substitution table based on if it's a normal or inverse transformation
	if not inverse:
		table = [\
		[  9,  4,  0xA, 0xB],
		[0xD,  1,    8,   5],
		[  6,  2,    0,   3],
		[0xC, 0xE, 0xF,   7]]
	elif inverse:
		table = [\
		[0xA,  5,   9, 0xB],
		[  1,  7,   8, 0xF],
		[  6,  0,   2,   3],
		[0xC,  4, 0xD, 0xE]]
	
	# Determine the left and right bits in the nibble
	left = (nibble >> 2) & 3
	right = nibble & 3
	
	# Perform the substitution and return the value
	return table[left][right]
	
def sub_nibbles(state, inverse=False):
	""" Performs the SubNibbles transformation on a 16-bit state. """
	sub_state = []
	for n in state:
		sub_state.append( sub_nibble(n, inverse) )
	
	return sub_state
	
def shift_rows(state):
	""" Performs the ShiftRows transformation on a 16-bit state. This transformation is its own inverse. """
	return [ state[0], state[3], state[2], state[1] ]
	
def mix_columns(state, inverse=False):
	""" Performs the MixColumns transformation on a 16-bit state. """
	# Selects the proper constant matrix based on if it's a normal or inverse transformation
	if not inverse:
		C = [1, 4, 4, 1]
	elif inverse:
		C = [9, 2, 2, 9]
	
	# Perform the matrix multiplication between the state and constant matrix
	mix_state = [GF16(C[0], state[0]) ^ GF16(C[2], state[1]),
				 GF16(C[1], state[0]) ^ GF16(C[3], state[1]),
				 GF16(C[0], state[2]) ^ GF16(C[2], state[3]),
				 GF16(C[1], state[2]) ^ GF16(C[3], state[3])]
	
	return mix_state
	
def GF16(a, b):
	""" Galois Field for GF(2**4). Used for multiplication operations in the MixColumns transformation. """
	multiplication_table = [\
	[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
	[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15],
	[0, 2, 4, 6, 8, 10, 12, 14, 3, 1, 7, 5, 11, 9, 15, 13],
	[0, 3, 6, 5, 12, 15, 10, 9, 11, 8, 13, 14, 7, 4, 1, 2],
	[0, 4, 8, 12, 3, 7, 11, 15, 6, 2, 14, 10, 5, 1, 13, 9],
	[0, 5, 10, 15, 7, 2, 13, 8, 14, 11, 4, 1, 9, 12, 3, 6],
	[0, 6, 12, 10, 11, 13, 7, 1, 5, 3, 9, 15, 14, 8, 2, 4],
	[0, 7, 14, 9, 15, 8, 1, 6, 13, 10, 3, 4, 2, 5, 12, 11],
	[0, 8, 3, 11, 6, 14, 5, 13, 12, 4, 15, 7, 10, 2, 9, 1],
	[0, 9, 1, 8, 2, 11, 3, 10, 4, 13, 5, 12, 6, 15, 7, 14],
	[0, 10, 7, 13, 14, 4, 9, 3, 15, 5, 8, 2, 1, 11, 6, 12],
	[0, 11, 5, 14, 10, 1, 15, 4, 7, 12, 2, 9, 13, 6, 8, 3],
	[0, 12, 11, 7, 5, 9, 14, 2, 10, 6, 1, 13, 15, 3, 4, 8],
	[0, 13, 9, 4, 1, 12, 8, 5, 2, 15, 11, 6, 3, 14, 10, 7],
	[0, 14, 15, 1, 13, 3, 2, 12, 9, 7, 6, 8, 4, 10, 11, 5],
	[0, 15, 13, 2, 9, 6, 4, 11, 1, 14, 12, 3, 8, 7, 5, 10]]
	
	return multiplication_table[a][b]

def F(input, key, encrypt=True):
	""" Encrypts or decrypts the provided block (2-bytes) using the SDES cipher. 
	
	Parameters
	----------
	input : bytearray
		The data to process.
	key : int
		The cipher key to use. (16-bits)
	encrypt : bool
		Whether to encrypt or decrypt the data. Defaults to encryption.
	 
	Returns
	-------
	int
		The encrypted or decrypted block.
	"""	

	# Convert input integer into a state array
	state = [ input >> 12 & 0xf, input >> 8 & 0xf, input >> 4 & 0xf, input & 0xf ]
	
	# Key expansion
	roundkeys = expand_key(key)
	
	if encrypt:
		# Pre-round
		state = add_round_key(state, roundkeys[0])
		
		# Round 1
		state = sub_nibbles(state)		
		state = shift_rows(state)
		state = mix_columns(state)		
		state = add_round_key(state, roundkeys[1])

		
		# Round 2
		state = sub_nibbles(state)	
		state = shift_rows(state)		
		state = add_round_key(state, roundkeys[2])
		
	elif not encrypt:
		# Pre-round
		state = add_round_key(state, roundkeys[2])
		
		# Round 1
		state = shift_rows(state)
		state = sub_nibbles(state, inverse=True)
		state = add_round_key(state, roundkeys[1])
		state = mix_columns(state, inverse=True)
		
		# Round 2
		state = shift_rows(state)
		state = sub_nibbles(state, inverse=True)
		state = add_round_key(state, roundkeys[0])
		
	# Convert state array back into an integer
	return (state[0] << 12) ^ (state[1] << 8) ^ (state[2] << 4) ^ (state[3])
	
	