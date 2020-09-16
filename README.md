# Simplified DES and AES for Python
A Python implementation of Simplified DES (SDES) and Simplified AES (SAES).

SDES is implemented as seen from Appendix G of Cryptography and Network Security, Fifth Edition by William Stallings, located here: 
http://mercury.webster.edu/aleshunas/COSC%205130/G-SDES.pdf

- The block size is 8-bits (1 byte)
- The key size is 10-bits (1024 possible keys)


SAES is implemented as designed by Mohammad Musa, Edward Schaefer, and Stephen Wedig of Santa Clara University, which is described here:
http://read.pudn.com/downloads222/ebook/1044300/%E9%99%84%E5%BD%95P%20Simplified%20AES%20(S-AES).pdf

- The block size is 16-bits (2 bytes)
- The key size is 16-bits (65,536 possible keys)

Implemented electronic code book (ECB), cipher block chaining (CBC), and counter (CTR) modes.

Also includes a script to calculate the [Shannon entropy (H)](https://en.wikipedia.org/wiki/Entropy_(information_theory)) of a file, modified from:
 https://kennethghartman.com/calculate-file-entropy/

Usage Information:
```text
usage: main.py [-h] [--encrypt] [--decrypt] [-iv NONCE] [-s CHUNK_SIZE]
               [--concurrent] [--max_workers MAX_WORKERS]
               cipher mode key input_filename output_filename

Encrypt or decrypt a file using a Simplified DES (SDES) or Simplified AES (SAES) cipher.

SDES - Implemented as described in Appendix G of Cryptography and Network Security, 
Fifth Edition by William Stallings.

Block-size: 8-bits
Key size: 10-bits (1024 possibilities)

SAES - Implemented as described by Mohammad Musa, Edward Schaefer, and Stephen Wedig 
of Santa Clara University.

Block-size: 16-bits
Key size: 16-bits (65,536 possibilities)

************************************
*** DO NOT USE FOR PRODUCTION!!! *** (That's probably obvious, though)
************************************

positional arguments:
  cipher                The cipher algorithm to use. [SDES, SAES]
  mode                  The cipher mode to use. [ECB, CBC, CTR]
  key                   The cipher key to use. Example: 1010101010 or 0xff
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
                        Defaults to 65536.
  --concurrent, -c      Process file with multiple threads, if possible.
  --max_workers MAX_WORKERS, -w MAX_WORKERS
                        Maximum number of workers to use for multiprocessing.
                        (Defaults to the number of processors on the machine)

Example usage:
Encryption: python3.8 ./main.py SAES cbc -iv 100 -e 0xab plaintext.txt ciphertext.saes
Decryption: python3.8 ./main.py SAES cbc -iv 100 -d 0xab ciphertext.saes plaintext.txt -c
```

## Comparison of Encryption Modes

### Original *[H = 3.382]*
![Original](Tux.bmp "Original Image")

### Electronic Code Book (ECB) *[H = 3.384]*

  SDES ECB                                         |  SAES ECB
:-------------------------------------------------:|:--------------------------------------------------:
![SDES ECB](SDES_Tux/Tux.ecb.bmp "SDES ECB Image") | ![SAES ECB](SAES_Tux/Tux.ecb.bmp "SAES ECB Image")

### Cipher Block Chaining (CBC) *[H = 7.992]*
  SDES CBC                                         |  SAES CBC
:-------------------------------------------------:|:--------------------------------------------------:
![SDES CBC](SDES_Tux/Tux.cbc.bmp "SDES CBC Image") | ![SAES CBC](SAES_Tux/Tux.cbc.bmp "SAES CBC Image")

### Counter (CTR) *[H = 7.999]*
  SDES CTR                                         |  SAES CTR
:-------------------------------------------------:|:--------------------------------------------------:
![SDES CTR](SDES_Tux/Tux.ctr.bmp "SDES CTR Image") | ![SAES CTR](SAES_Tux/Tux.ctr.bmp "SAES CTR Image")

Comparison images created with the following commands:
```text
$ ./main.py ecb -e -c 1010101010 Tux.bmp Tux.ecb.bmp
$ dd bs=108 count=1 conv=notrunc if=Tux.bmp of=Tux.ecb.bmp
1+0 records in
1+0 records out
108 bytes copied, 0.0074432 s, 14.5 kB/s
```

Speed comparison between SAES and SDES (24 MB file):
```text
$ time ./main.py SAES ctr -e 0xab big.pptx big.ctr -c
IV/nonce generated is 27567!

real    1m38.786s
user    10m18.109s
sys     0m1.813s
$ time ./main.py SDES ctr -e 1010101010 big.pptx big.ctr.sdes -c
IV/nonce generated is 164!

real    3m55.430s
user    27m17.781s
sys     0m3.828s
```