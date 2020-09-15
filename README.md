# SDES for Python
Python implementation of Simplified DES as seen from Appendix G of Cryptography and Network Security, Fifth Edition by William Stallings, located here: (http://mercury.webster.edu/aleshunas/COSC%205130/G-SDES.pdf)

Implemented electronic code book (ECB), cipher block chaining (CBC), and counter (CTR) modes. The block size is 8-bits (1 byte) and the key size is 10-bits (1024 possible keys).

Also includes a script to calculate the Shannon entropy of a file, modified from https://kennethghartman.com/calculate-file-entropy/

Usage Information:
```text
usage: SDES.py [-h] [--encrypt] [--decrypt] [-iv NONCE] mode key input_filename output_filename

Encrypt or decrypt a file using a Simplified DES (SDES) cipher. The block cipher is implemented as described in Appendix G of Cryptography and Network Security, Fifth Edition by William Stallings.

************************************
*** DO NOT USE FOR PRODUCTION!!! *** (That's probably obvious, though)
************************************

positional arguments:
  mode                  The cipher mode to use. [ECB, CBC]
  key                   The 10-bit cipher key to use. Example: 1010101010
  input_filename        The file to process.
  output_filename       The file to store the results into.

optional arguments:
  -h, --help            show this help message and exit
  --encrypt, -e
  --decrypt, -d
  -iv NONCE, --nonce NONCE

Example usage:
Encryption: python3.8 ./SDES.py [ecb/cbc/ctr] [-iv NUM] [--encrypt] 1010101010 plaintext.txt ciphertext.sdes
Decryption: python3.8 ./SDES.py [ecb/cbc/ctr] [-iv NUM] [--decrypt] 1010101010 ciphertext.sdes plaintext.txt
```
## Comparison of Encryption Modes

### Original
![Original](Tux.bmp "Original Image")

### Electronic Code Book (ECB)
![Original](Tux.ecb.bmp "ECB Image")

### Cipher Block Chaining (CBC)
![Original](Tux.cbc.bmp "CBC Image")

### Counter (CTR)
![Original](Tux.ctr.bmp "CTR Image")

Created comparison images with:
```text
$ ./SDES.py ecb -e 1010101010 Tux.bmp Tux.ecb.bmp
$ ./SDES.py cbc -e 1010101010 Tux.bmp Tux.cbc.bmp
IV/nonce generated is 136!
$ ./SDES.py ctr -e 1010101010 Tux.bmp Tux.ctr.bmp
IV/nonce generated is 78!
$ dd bs=108 count=1 conv=notrunc if=Tux.bmp of=Tux.ecb.bmp
1+0 records in
1+0 records out
108 bytes copied, 0.0074432 s, 14.5 kB/s
$ dd bs=108 count=1 conv=notrunc if=Tux.bmp of=Tux.cbc.bmp
1+0 records in
1+0 records out
108 bytes copied, 0.0066555 s, 16.2 kB/s
$ dd bs=108 count=1 conv=notrunc if=Tux.bmp of=Tux.ctr.bmp
1+0 records in
1+0 records out
108 bytes copied, 0.0095254 s, 11.3 kB/s
```