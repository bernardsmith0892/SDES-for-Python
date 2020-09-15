#!/usr/bin/python3.8
"""
 entropy.py
 Calculates Shannon entropy of a file. Modified from the code by Kenneth Hartman, found here: https://kennethghartman.com/calculate-file-entropy/

 Modifications:
  - Upgraded to Python 3.8
  - Removed graphing functionality
  - Allowed for multiple files using glob expressions (e.g. *.txt)
"""

import sys 
import math 

if len(sys.argv) < 2: 
    print (f"Usage: {sys.argv[0]} filename")
    sys.exit()


for file in sys.argv[1:]:
	# read the whole file into a byte array
	f = open(file, "rb")
	data = f.read()
	f.close() 
	
	fileSize = len(data)

	# calculate the frequency of each byte value in the file 
	freqList = [] 
	for b in range(256): 
		ctr = 0 
		for byte in data: 
			if byte == b: 
				ctr += 1 
		freqList.append(float(ctr) / fileSize) 

	# Shannon entropy 
	ent = 0.0 
	for freq in freqList: 
		if freq > 0: 
			ent = ent + freq * math.log(freq, 2) 
	ent = -ent 
	print(f"Shannon entropy for {file} :\t{ent}")

