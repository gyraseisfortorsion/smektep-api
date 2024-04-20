from Crypto.Cipher import DES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes
import json

data = {
    1: 10,
    2: 20,
    3: 30,
    4: 40
}

json_data = json.dumps(data)
data_bytes = json_data.encode('utf-8')

key = get_random_bytes(8)  # DES requires an 8-byte key
cipher = DES.new(key, DES.MODE_ECB)

# Encrypt the data
cipher_text = cipher.encrypt(pad(data_bytes, DES.block_size))

# Decrypt the data
decipher = DES.new(key, DES.MODE_ECB)
plain_text = unpad(decipher.decrypt(cipher_text), DES.block_size)

# Decode the bytes back into a string
decrypted_data = plain_text.decode('utf-8')

print(cipher_text)
print('eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0eXBlIjozMCwiY3J1ZCI6NCwic2NvcGUiOjIwfQ.b_97K89qA79IJaNIsSnUpqMP0QhLHzkCKllzj2rtSf0')
print(decrypted_data)