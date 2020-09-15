# SDES-for-Python
Python implementation of Simplified DES as seen from Appendix G of Cryptography and Network Security, Fifth Edition by William Stallings, located here: (http://mercury.webster.edu/aleshunas/COSC%205130/G-SDES.pdf)

Implemented electronic code book (ECB) mode and cipher block chaining (CBC) mode.

Also includes a script to calculate the Shannon entropy of a file, modified from https://kennethghartman.com/calculate-file-entropy/

Usage Information:
```
usage: SDES.py [-h] [--encrypt] [--decrypt] mode key input_filename output_filename

Encrypt or decrypt a file using a Simplified DES (SDES) cipher. The block cipher is implemented as described in Appendix G of Cryptography and Network Security, Fifth Edition by William Stallings.

************************************
*** DO NOT USE FOR PRODUCTION!!! *** (That's probably obvious, though)
************************************

positional arguments:
  mode             The cipher mode to use. [ECB, CBC]
  key              The 10-bit cipher key to use. Example: 1010101010
  input_filename   The file to process.
  output_filename  The file to store the results into.

optional arguments:
  -h, --help       show this help message and exit
  --encrypt, -e
  --decrypt, -d

Example usage:
Encryption: python3.8 ./SDES.py [ecb/cbc] --encrypt 1010101010 plaintext.txt ciphertext.sdes
Decryption: python3.8 ./SDES.py [ecb/cbc] --decrypt 1010101010 ciphertext.sdes plaintext.txt
```

Example Usage:
```
$ python3.8 -c "for n in range(100): print(str(n) * 50) " > pattern.txt
$ ./SDES.py --encrypt ecb 1010101010 pattern.txt pattern.ecb
$ ./SDES.py --decrypt ecb 1010101010 pattern.ecb pattern.ecb.txt
$ ./SDES.py --encrypt cbc 1010101010 pattern.txt pattern.cbc
$ ./SDES.py --decrypt cbc 1010101010 pattern.cbc pattern.cbc.txt

$ md5sum pattern*
1082a57f1f5c35019a3c7f5aea146469  pattern.cbc
16a3915cd9a6b52620a02cf579e47e96  pattern.cbc.txt
0f36df2a1278bd614621595b785d5d61  pattern.ecb
16a3915cd9a6b52620a02cf579e47e96  pattern.ecb.txt
16a3915cd9a6b52620a02cf579e47e96  pattern.txt

$ ./entropy.py pattern*
Shannon entropy for pattern.cbc :       7.903461788035961
Shannon entropy for pattern.cbc.txt :   3.3497211568222043
Shannon entropy for pattern.ecb :       3.3497211568222043
Shannon entropy for pattern.ecb.txt :   3.3497211568222043
Shannon entropy for pattern.txt :       3.3497211568222043
```

![Comparison of Encryption Modes](cipher_comparison.png "Comparison of Encryption Modes")