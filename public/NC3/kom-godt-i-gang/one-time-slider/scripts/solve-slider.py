import secrets

def xor(a, b):
    return bytes(x ^ y for x, y in zip(a, b))

hex_message = "e9e494dcd1c2c9d3f8d1c6d5f8c3c2d3f8c3d2cad3f8c6d3f8ffe8f5f8c6cbcbc2f8c5ded3c2d4f8cac2c3f8cfd1c2d5f8ccc2def8c5ded3c2989898da"
encrypted_message = bytes.fromhex(hex_message)

n = len(encrypted_message)
otp = secrets.token_bytes(n)

# Convert bytes to a list of integers
encrypted_list = list(encrypted_message)

# Slide OTP over ciphertext and XOR decrypt everything within its range
for i in range(2 * n + 1):
    encrypted_list[max(0, i - n):i] = xor(encrypted_list[max(0, i - n):i], otp[-i:])

# Convert the list of integers back to bytes
decrypted_message = bytes(encrypted_list)

print(decrypted_message.decode('utf-8'))

with open("decrypted_message.txt", "wb") as f:
    f.write(decrypted_message)
