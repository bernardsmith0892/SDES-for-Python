# SDES for Python
Python implementation of Simplified DES as seen from Appendix G of Cryptography and Network Security, Fifth Edition by William Stallings, located here: 
http://mercury.webster.edu/aleshunas/COSC%205130/G-SDES.pdf)

Implemented electronic code book (ECB), cipher block chaining (CBC), and counter (CTR) modes. The block size is 8-bits (1 byte) and the key size is 10-bits (1024 possible keys).

Also includes a script to calculate the [Shannon entropy](https://en.wikipedia.org/wiki/Entropy_(information_theory)) of a file, modified from:
 https://kennethghartman.com/calculate-file-entropy/

Usage Information:
```text
usage: main.py [-h] [--encrypt] [--decrypt] [-iv NONCE] [-s CHUNK_SIZE] [--concurrent]
               mode key input_filename output_filename

Encrypt or decrypt a file using a Simplified DES (SDES) cipher. The block cipher is implemented as described in Appendix G of Cryptography and Network Security, Fifth Edition by William Stallings.

Block-size: 1 byte
Key-size: 10-bits (1024 possibilities)

************************************
*** DO NOT USE FOR PRODUCTION!!! *** (That's probably obvious, though)
************************************

positional arguments:
  mode                  The cipher mode to use. [ECB, CBC, CTR]
  key                   The 10-bit cipher key to use. Example: 1010101010
  input_filename        The file to process.
  output_filename       The file to store the results into.

optional arguments:
  -h, --help            show this help message and exit
  --encrypt, -e         Encrypt the file.
  --decrypt, -d         Decrypt the file.
  -iv NONCE, --nonce NONCE
                        IV or nonce value to use.
  -s CHUNK_SIZE, --chunk_size CHUNK_SIZE
                        The byte-size of chunks to process the files in.
  --concurrent, -c      Process file with multiple threads, if possible.

Example usage:
Encryption: python3.8 ./main.py cbc -iv 100 --encrypt 1010101010 plaintext.txt ciphertext.sdes
Decryption: python3.8 ./main.py cbc -iv 100 --decrypt --concurrent 1010101010 ciphertext.sdes plaintext.txt
```
## Comparison of Encryption Modes

### Original
![Original](Tux.bmp "Original Image")
*Shannon entropy - 3.382765*

### Electronic Code Book (ECB)
![Original](Tux.ecb.bmp "ECB Image")
*Shannon entropy - 3.384269*

### Cipher Block Chaining (CBC)
![Original](Tux.cbc.bmp "CBC Image")
*Shannon entropy - 7.992329*

### Counter (CTR)
![Original](Tux.ctr.bmp "CTR Image")
*Shannon entropy - 7.999841*

Created comparison images with:

```text
$ ./main.py ecb -e -c 1010101010 Tux.bmp Tux.ecb.bmp
$ ./main.py cbc -e -c 1010101010 Tux.bmp Tux.cbc.bmp
IV/nonce generated is 30!
$ ./main.py ctr -c 1010101010 Tux.bmp Tux.ctr.bmp
IV/nonce generated is 158!
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