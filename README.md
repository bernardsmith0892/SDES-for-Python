# SDES-for-Python
Python implementation of Simplified DES as seen here (http://mercury.webster.edu/aleshunas/COSC%205130/G-SDES.pdf)

Only electronic code book mode is implemented as of yet. 

Usage Information:
```
***********************
* SDES File Encryptor *
***********************

Usage:
	Encryption: python3 SDES.py -e 'key_in_binary' 'plaintext_file' 'ciphertext_file'
	Decryption: python3 SDES.py -d 'key_in_binary' 'ciphertext_file' 'plaintext_file'
Example: python3 SDES.py -e 1100101010 plaintext.txt cipertext.sdes
```
