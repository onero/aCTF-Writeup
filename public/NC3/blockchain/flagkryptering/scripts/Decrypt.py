import os
from web3 import Web3

class EncryptFlag:
    def __init__(self):
        pass

    def encrypt(self, key, flag):
        ciphertext = bytes([a ^ b for a, b in zip(key, flag)])
        return ciphertext

    def generate_key(self, block_number):
        if block_number > 0:
            minus_one_block_number_bytes = (block_number-1).to_bytes(32, byteorder='big')
            key = Web3.keccak(minus_one_block_number_bytes)
        else:
            block_number_bytes = block_number.to_bytes(32, byteorder='big')
            key = Web3.keccak(block_number_bytes)
        return key

def save_block_number(block_number):
    with open("last_block_number.txt", "w") as file:
        file.write(str(block_number))

def load_last_block_number():
    if os.path.exists("last_block_number.txt"):
        with open("last_block_number.txt", "r") as file:
            return int(file.read().strip())
    return 0

encrypt_flag = EncryptFlag()

hex_string = "0xc3523b9a72a40978afbab042b0b5f2d41167c2760491b52925cd727d581ac802"
flag = bytes.fromhex(hex_string[2:])

block_number = load_last_block_number()

while True:
    key = encrypt_flag.generate_key(block_number)

    ciphertext = encrypt_flag.encrypt(key, flag)
    
    # Convert ciphertext to string to check for 'NC3{' or 'nc3{'
    ciphertext_str = ciphertext.decode('utf-8', errors='ignore')
    if ciphertext_str.startswith('NC3{'):
        print(f"Found at block number: {block_number}, Ciphertext: {ciphertext_str}")
        break

    if block_number % 1000:
        save_block_number(block_number)
        print(f"Searched blocknumbers: {block_number}")

    block_number += 1
